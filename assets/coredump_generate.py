#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把客户端采集的「两件套」组装成 lldb 可以直接加载的 Mach-O core 文件。

    python3 decode.py snapshot_desc.json snapshot_payload.bin [snapshot.core]
    lldb -c snapshot.core 僵尸对象探针.app/僵尸对象探针

生成的 core 与 Xcode 里 `process save-core` 的产物同构，物理布局是：

    0x00  mach_header_64          32B   MH_CORE，ncmds = N线程 + M区间 + 1
    0x20  LC_THREAD        × N   208B   每线程：flavor4(21×u64) + flavor6(16B)
          LC_SEGMENT_64    × M    72B   每块内存：nsects = 0，段名留空
          LC_NOTE          × 1    40B   owner = "all image infos"
          ── 8 字节对齐 ──
          note 负载                   路径 / UUID / 加载地址 / 段地址表 / 路径串
          ── 页对齐 ──
          payload 数据                每块区间按页对齐，按 desc 的 offset 拷进来

两条最容易踩的规则：
  · LC_NOTE 里所有 offset 都是「core 文件内的绝对偏移」，不是相对 note 的偏移；
  · 每个 LC_SEGMENT_64 只表达 vmaddr → fileoff 的映射，不要写 section
    （写了反而会和真机 core 不一致，lldb 也不需要）。
"""

import json
import os
import struct
import sys

MH_MAGIC_64 = 0xFEEDFACF          # 64 位 Mach-O 魔数
MH_CORE = 4                       # filetype：core 文件（不是可执行文件）

# CPU 类型必须和采集端的 desc 一致，lldb 靠它决定用哪个架构的寄存器解释器
CPU_TYPE_X86_64 = 0x01000007
CPU_SUBTYPE_X86_64_ALL = 0x3

# load command 的类型编号（和 <mach-o/loader.h> 里一致）
LC_THREAD = 0x4
LC_SEGMENT_64 = 0x19
LC_NOTE = 0x31

LC_NOTE_OWNER = b"all image infos"   # lldb 只认这个 owner 的 note

# 线程状态 flavor：4 = 通用寄存器(21 个 u64)，6 = 异常状态(16 字节)
X86_THREAD_STATE64 = 4
X86_THREAD_STATE64_COUNT = 42          # 单位是 32 位字：21 个 u64 = 42
X86_EXCEPTION_STATE64 = 6
X86_EXCEPTION_STATE64_COUNT = 4        # 4 个 32 位字 = 16 字节

# LC_NOTE 负载内部的三段结构，尺寸必须和 lldb 的解析器完全对齐
IMAGE_ENTRY_SIZE = 48                  # struct image_entry
SEG_VMADDR_SIZE = 32                   # struct segment_vmaddr
NOTE_HEADER_SIZE = 24                  # struct all_image_infos_header

PAGE = 0x1000                     # x86_64 页大小；arm64 真机是 0x4000
UINT64_MAX = 0xFFFFFFFFFFFFFFFF   # 表示「没有段地址表」的哨兵值

# image_entry.executing：这个镜像是否正在执行（1 = 是）
NOT_EXECUTING = 2
EXECUTING = 1


def align(x, a):
    """把 x 向上取整到 a 的边界（a 是 2 的幂）。"""
    return (x + a - 1) // a * a


def parse_uuid(text):
    """'51623987-FCCC-3B7B-9637-ED335C882F18' -> 16 raw bytes

    解析失败不抛异常，直接给全 0：core 里 UUID 错只影响符号匹配，
    不该让整个组装流程挂掉（用户更需要一份能加载的 core）。
    """
    if not text:
        return b"\x00" * 16
    h = text.replace("-", "").strip()
    if len(h) != 32:
        return b"\x00" * 16
    try:
        return bytes.fromhex(h)
    except ValueError:
        return b"\x00" * 16


def build_thread_commands(threads):
    """每个线程一条 LC_THREAD：flavor 4(42) + flavor 6(4)

    cmdsize 的推导（必须精确到字节，多一个字节 lldb 就拒解析）：
        8(cmd+cmdsize) + 8(flavor+count) + 21*8(寄存器) + 8(flavor+count) + 16(异常) = 208
    Apple 自己 save-core 出来的也是 208，可以拿一份真 core 对一下。
    """
    out = bytearray()
    for t in threads:
        regs = t.get("regs") or []
        if len(regs) != 21:
            raise ValueError("thread %s: regs 需要 21 个寄存器，实际 %d 个"
                             % (t.get("tid"), len(regs)))
        regs = [int(v, 16) if isinstance(v, str) else int(v) for v in regs]
        exc = t.get("exception") or ["0x0"] * 4
        exc = [int(v, 16) if isinstance(v, str) else int(v) for v in exc]
        if len(exc) < 4:
            exc = list(exc) + [0] * (4 - len(exc))

        body = struct.pack("<II", X86_THREAD_STATE64, X86_THREAD_STATE64_COUNT)
        body += struct.pack("<21Q", *regs)
        body += struct.pack("<II", X86_EXCEPTION_STATE64, X86_EXCEPTION_STATE64_COUNT)
        # struct __darwin_x86_exception_state64: u16 trapno, u16 cpu, u32 err, u64 faultvaddr
        body += struct.pack("<HHIQ", exc[0] & 0xFFFF, exc[1] & 0xFFFF,
                            exc[2] & 0xFFFFFFFF, exc[3] & UINT64_MAX)

        out += struct.pack("<II", LC_THREAD, 8 + len(body)) + body
    return bytes(out)


def build_segment_command(vmaddr, vmsize, fileoff, filesize, maxprot, initprot):
    """组装一条 72 字节的 LC_SEGMENT_64。

    字段顺序：cmd, cmdsize, segname[16], vmaddr, vmsize, fileoff, filesize,
              maxprot, initprot, nsects, flags

    · nsects 必须为 0、段名留空 —— core 里的段只承担「虚拟地址 → 文件偏移」的映射，
      lldb 的 MachCore 插件按这个映射去 core 里取内存，不需要符号表或节信息。
    · filesize 可以小于 vmsize：差值就是采集时被页裁剪掉的部分，
      lldb 读那段会失败/读到 0——所以寄存器和栈所在的区间一定要完整。
    """
    return struct.pack(
        "<II16sQQQQiiII",
        LC_SEGMENT_64,
        72,
        b"\x00" * 16,       # 段名留空，与 Apple core 一致
        vmaddr,
        vmsize,
        fileoff,
        filesize,
        maxprot,
        initprot,
        0,                  # nsects
        0,                  # flags
    )


def build_note(images, note_off):
    """组装 'all image infos' 负载，返回 (blob, note_size)。

    内部布局（所有 offset 都是 core 文件内的绝对偏移，lldb 拿到 note_off 后直接按值取）：

        note_off + 0                header        24B  version/count/entries_fileoff/entry_size
        note_off + 24               image_entry[] 48B×n  路径偏移 / UUID / 加载地址 / 段表偏移 / 段数 / executing
        note_off + 24 + 48n         segment_vmaddr[] 32B×(所有镜像段数之和)  段名 + 运行时地址
        紧跟其后                     路径字符串     NUL 结尾，每条一个

    这个 note 是「能不能符号化」的分水岭：没有它，lldb 只能显示裸地址；
    有了它，才有 UIKitCore`-[UIViewController ...] 和行号。
    """
    entries_off = note_off + NOTE_HEADER_SIZE
    segarr_off = entries_off + IMAGE_ENTRY_SIZE * len(images)

    seg_total = sum(len(im.get("segments") or []) for im in images)

    # 路径字符串紧跟在段地址表后面，所以要先知道总段数才能算出路径区的起点
    path_offsets = []
    cursor = segarr_off + SEG_VMADDR_SIZE * seg_total
    path_bytes = bytearray()
    for im in images:
        path_offsets.append(cursor)          # 记的是「这条路径在 core 文件里的绝对偏移」
        raw = (im.get("path") or "").encode("utf-8") + b"\x00"
        path_bytes += raw
        cursor += len(raw)

    note_size = cursor - note_off

    blob = bytearray()
    # header: version=1, image 数量, entries 起始偏移, 单条 entry 大小, unused
    blob += struct.pack("<IIQII", 1, len(images), entries_off,
                        IMAGE_ENTRY_SIZE, 0)

    # image_entry 数组。这里 executing 统一写 1（简化处理）：
    # 真实 crash 时可以按崩溃线程的 PC 落在哪个镜像来精确标记。
    executing = 1
    seg_cursor = segarr_off
    for i, im in enumerate(images):
        segs = im.get("segments") or []
        load_address = int(im.get("load_address") or 0, 0)
        # 没有段信息就给 UINT64_MAX 当哨兵，lldb 见到它就不去读段表
        seg_off = seg_cursor if segs else UINT64_MAX
        blob += struct.pack("<Q", path_offsets[i])
        blob += parse_uuid(im.get("uuid"))
        blob += struct.pack("<QQII", load_address, seg_off, len(segs), executing)
        seg_cursor += SEG_VMADDR_SIZE * len(segs)

    slide = 0
    for im in images:
        # desc 里记的是静态 vmaddr + slide，这里必须换算成运行时地址，
        # 否则 lldb 拿它去匹配 PC 时会整体偏移，截图里的符号就全错了
        slide = int(im.get("slide") or 0, 0)
        for seg in (im.get("segments") or []):
            name = (seg.get("name") or "")[:16].encode("utf-8")
            vmaddr = int(seg.get("vmaddr") or 0, 0) + slide
            blob += struct.pack("<16sQQ", name.ljust(16, b"\x00"), vmaddr, 0)

    blob += path_bytes
    # 自检：算出来的长度必须和前面按公式推的一致，否则 lldb 会读串
    assert len(blob) == note_size, (len(blob), note_size)
    return bytes(blob), note_size


def build_core(desc_path, payload_path, out_path="snapshot.core"):
    """把 desc + payload 重排成一个 Mach-O core。

    这里不做任何「分析」，只做三件事：
        ① 摆 load commands（顺序：header → LC_THREAD → LC_SEGMENT_64 → LC_NOTE）
        ② 算出每块内存在文件里的落点（note 之后按页对齐）
        ③ 写文件：先写头 + 命令，再 seek 到各偏移填 note 和数据
    """
    with open(desc_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    with open(payload_path, "rb") as f:
        payload = f.read()

    fmt = meta.get("format")
    if fmt and fmt != "zombie-snapshot":
        print("⚠️  未知的 desc 格式: %s，按 v1 尝试解析" % fmt)

    threads = meta.get("threads") or []
    regions = meta.get("regions") or []
    images = meta.get("images") or []

    if not threads:
        raise ValueError("desc 里没有线程信息")
    if not regions:
        print("⚠️  没有内存区间，core 里将看不到栈和堆")

    # ---------- 1. 先把 load commands 摆好 ----------
    thread_lcs = build_thread_commands(threads)
    ncmds = len(threads) + len(regions) + 1          # threads + segments + note
    sizeofcmds = len(thread_lcs) + 72 * len(regions) + 40

    # note 数据紧跟在 load commands 之后；对齐到 8 是因为里面全是 u64
    note_off = align(32 + sizeofcmds, 8)
    note_blob, note_size = build_note(images, note_off)

    # ---------- 2. 内存数据从下一个页边界开始 ----------
    # 每块区间单独页对齐：和真机 core 的写法一致，lldb 里按页估算地址也更直观。
    # fileoff 必须等于 layout[i]，LC_SEGMENT_64 就是靠它去文件里找数据的。
    seg_base = align(note_off + note_size, PAGE)
    layout = []
    cursor = seg_base
    for r in regions:
        cursor = align(cursor, PAGE)
        filesize = int(r.get("filesize", r["size"]))
        layout.append(cursor)
        cursor += filesize
    total_size = cursor

    # ---------- 3. 写文件 ----------
    with open(out_path, "wb") as fp:
        # mach_header_64：magic / cputype / cpusubtype / filetype(MH_CORE) / ncmds / sizeofcmds / flags / reserved
        fp.write(struct.pack("<IiiIIIII",
                             MH_MAGIC_64, CPU_TYPE_X86_64, CPU_SUBTYPE_X86_64_ALL,
                             MH_CORE, ncmds, sizeofcmds, 0, 0))
        # 线程命令紧跟在头后面；写完文件位置 = 32 + sizeofcmds
        fp.write(thread_lcs)

        for r, fileoff in zip(regions, layout):
            fp.write(build_segment_command(
                int(r["addr"], 0),
                int(r["size"]),
                fileoff,
                int(r.get("filesize", r["size"])),
                int(r.get("maxprot", r.get("prot", 3))),
                int(r.get("prot", 3)),
            ))

        # LC_NOTE "all image infos"：cmdsize 固定 40 = 8(头) + 16(owner) + 8 + 8
        fp.write(struct.pack("<II16sQQ", LC_NOTE, 40,
                             LC_NOTE_OWNER.ljust(16, b"\x00"),
                             note_off, note_size))

        # 命令区之后可能有 padding（对齐到 8），直接 seek 到算好的位置写 note
        fp.seek(note_off)
        fp.write(note_blob)

        for r, fileoff in zip(regions, layout):
            # desc 里的 offset 是 payload 内偏移，这里只做切片；
            # 长度不够就补 0：说明上传/拼接出过问题，但至少还能生成一份可加载的 core
            off = int(r.get("offset", 0))
            filesize = int(r.get("filesize", r["size"]))
            chunk = payload[off:off + filesize]
            if len(chunk) < filesize:
                chunk = chunk + b"\x00" * (filesize - len(chunk))
            fp.seek(fileoff)
            fp.write(chunk)

    print("✅ core 已生成: %s (%.2f MB)" % (out_path, total_size / 1024.0 / 1024.0))
    print("   mach_header=32B, ncmds=%d, sizeofcmds=%d" % (ncmds, sizeofcmds))
    print("   threads=%d, segments=%d, images=%d, note=%dB @0x%x"
          % (len(threads), len(regions), len(images), note_size, note_off))
    print("")
    print("   加载: lldb -c %s <你的 .app 里的可执行文件>" % out_path)
    print("         (lldb) thread list")
    print("         (lldb) thread select 1")
    print("         (lldb) bt / frame variable / po <对象地址>")
    return out_path


if __name__ == "__main__":
    # 用法：decode.py <desc.json> <payload.bin> [输出路径]
    # 不给输出路径就落在 desc 同目录下的 snapshot.core
    if len(sys.argv) < 3:
        print(__doc__)
        print("Usage: python3 decode.py snapshot_desc.json snapshot_payload.bin [snapshot.core]")
        sys.exit(1)

    desc = sys.argv[1]
    binfile = sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(os.path.abspath(desc)), "snapshot.core")

    build_core(desc, binfile, out)
