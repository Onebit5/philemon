#!/usr/bin/env python3
"""the image writer, written twice, held to one layout.

tools/mkboot.py and tools/mkboot.c both write philemon's image. two
writers of one layout drift apart in the fields added last, so both are
handed the same pieces and have to write the same bytes. the pieces are
made up: neither writer looks inside the kernel or the archives, it only
places them, so any bytes of the right sizes will do.

then the refusals. the assembly and the C describe the same memory in two
files that cannot include each other, and a number that drifts in one of
them is a machine that hangs with nothing on the screen. so both writers
are run against a copy of the tree with one constant drifted, and both
have to refuse.

and the table an image without a source archive carries: zeroes where
the archive would be described, which is how a kernel reading it knows
there is none.

usage: tools/mkbootcheck.py BINDIR     (where `make` put the loader)
"""

import os
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SECTOR = 512
TABLE_LBA = 32


def run(args, env=None):
    return subprocess.run(args, capture_output=True, cwd=ROOT, env=env)


def piece(path, size, seed):
    with open(path, "wb") as f:
        f.write(bytes((seed + i * 7) & 0xff for i in range(size)))


def table(img):
    with open(img, "rb") as f:
        f.seek(TABLE_LBA * SECTOR)
        return struct.unpack("<12Q", f.read(12 * 8))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    bindir = os.path.abspath(sys.argv[1])
    loader = [os.path.join(bindir, "philemon.bin"),
              os.path.join(bindir, "philemon64.bin")]
    ours = os.path.join(bindir, "mkboot")
    for p in loader + [ours]:
        if not os.path.exists(p):
            sys.exit("mkbootcheck: %s is missing, run make first" % p)

    bad = 0
    work = tempfile.mkdtemp(prefix="mkbootcheck.")
    try:
        # sizes that end part way through a sector, so the rounding is
        # tested as well as the placing
        kernel = os.path.join(work, "kernel")
        ramdisk = os.path.join(work, "ramdisk")
        source = os.path.join(work, "source")
        piece(kernel, 300 * 1024 + 17, 1)
        piece(ramdisk, 64 * 1024 + 300, 2)
        piece(source, 900 * 1024 + 5, 3)
        pieces = loader + [kernel, ramdisk, source]

        theirs_img = os.path.join(work, "theirs.img")
        mine_img = os.path.join(work, "mine.img")
        r1 = run(["python3", "tools/mkboot.py", theirs_img] + pieces)
        r2 = run([ours, mine_img] + pieces)
        if r1.returncode != 0 or r2.returncode != 0:
            print("  a writer refused good pieces: python rc=%d, C rc=%d"
                  % (r1.returncode, r2.returncode))
            print("    " + (r1.stderr + r2.stderr).decode().strip())
            bad += 1
        else:
            a = open(theirs_img, "rb").read()
            b = open(mine_img, "rb").read()
            if a != b:
                print("  the images differ (%d bytes vs %d)"
                      % (len(a), len(b)))
                for i in range(min(len(a), len(b))):
                    if a[i] != b[i]:
                        print("    first at 0x%x: python %02x, C %02x"
                              % (i, a[i], b[i]))
                        break
                bad += 1

        # no source archive: three fields of zeroes, from both writers
        for who, cmd in (("python", ["python3", "tools/mkboot.py"]),
                         ("C", [ours])):
            img = os.path.join(work, "nosource-%s.img" % who)
            r = run(cmd + [img] + loader + [kernel, ramdisk])
            if r.returncode != 0:
                print("  %s would not write an image without a source "
                      "archive" % who)
                bad += 1
                continue
            t = table(img)
            if t[9:12] != (0, 0, 0):
                print("  %s described a source archive nobody gave it: "
                      "%r" % (who, t[9:12]))
                bad += 1

        # the refusal, for both writers: a copy of the tree with one
        # constant moved in the assembly's copy and not in the C's
        tree = os.path.join(work, "drifted")
        for rel in ("include/philemon.inc", "include/philemon.h",
                    "src/philemon.asm", "tools/mkboot.py"):
            os.makedirs(os.path.dirname(os.path.join(tree, rel)),
                        exist_ok=True)
            shutil.copy(os.path.join(ROOT, rel), os.path.join(tree, rel))
        inc = os.path.join(tree, "include", "philemon.inc")
        text = open(inc).read().replace("PT_BASE", "PT_BASE_UNUSED", 1)
        open(inc, "w").write(text + "\nPT_BASE equ 0x9999\n")

        r = run([ours, os.path.join(work, "no.img")] + pieces,
                env=dict(os.environ, MKBOOT_ROOT=tree))
        if r.returncode == 0 or b"in the assembly but" not in r.stderr:
            print("  the C writer wrote an image with the constants "
                  "drifted apart")
            bad += 1
        r = run(["python3", os.path.join(tree, "tools", "mkboot.py"),
                 os.path.join(work, "no.img")] + pieces)
        if r.returncode == 0 or b"in the assembly but" not in r.stderr:
            print("  the python writer wrote an image with the constants "
                  "drifted apart")
            bad += 1
    finally:
        shutil.rmtree(work)

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
