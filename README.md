# philemon

![ci](https://github.com/Onebit5/philemon/actions/workflows/ci.yml/badge.svg)

a bootloader for x86_64 pcs with a bios, small enough to read in an afternoon. it boots
[velvet](https://github.com/Onebit5/velvet).

named for the one who grants the power and then steps back: he asks the bios everything
it will ever answer, turns the kernel from a file into something running where it was
linked, leaves one struct describing the machine, and is gone.

what it boots is a kernel that takes velvet's boot protocol: an elf, entered in long
mode with a pointer in `rdi` to `struct ph_handoff` from [include/philemon.h](include/philemon.h),
with the direct map, the memory map, the ramdisk, the acpi tables and the framebuffer in
it. velvet describes the same protocol from the kernel's side, and the two have to agree.
it does not boot anything else: no multiboot, no linux boot protocol, no uefi.

## the tree

```
src/       the loader: philemon.asm, the 16-bit half the bios reads, and
           philemon.c, the 64-bit half; philemon.ld places the second
include/   philemon.h, the handoff and the table on the disk, and
           philemon.inc, the assembly's copy of the same addresses
tools/     mkboot.py and mkboot.c, the image writer twice; mkbootcheck.py;
           lint.py; hooks/
tests/     the host suite for the 64-bit half
docs/      philemon.rst, how all of it works
```

## building

you need `gcc`, `nasm`, `binutils`, `make` and `python3`.

```
make            # bin/philemon.bin, bin/philemon64.bin and bin/mkboot
make test       # the host suite and the image writer's checks
make lint       # the style lint (whole tree, or FILES=src/philemon.c)
make release    # print the version
```

and an image to boot:

```
tools/mkboot.py out.img bin/philemon.bin bin/philemon64.bin kernel.elf [ramdisk.tar [source.tar]]
```

which boots in qemu as a hard disk:

```
qemu-system-x86_64 -M q35 -serial stdio -drive file=out.img,format=raw
```

philemon has no kernel of his own, so the boot itself is tested where there is one:
velvet's boot test and its selftests boot an image this tree wrote.

## using it from another tree

name a release by its version, clone the tag `vX.Y.Z`, and build it out of its own tree:

```
make -C philemon BINDIR=... OBJROOT=...
python3 philemon/tools/mkboot.py ...
```

## releases

a release is a tag, `vX.Y.Z`, cut from `master` and never moved once it is pushed: a
tree that boots with philemon names a release by its version alone, so a tag that moved
would hand it a different loader under the same name. the major number moves when the
handoff or the table on the disk changes in a way an older kernel or an older image would
notice. [CHANGELOG.md](CHANGELOG.md) has every version.

## contributing

the code is written the way velvet's is, and velvet's `docs/coding-style.rst` is the
guide. `make lint` checks the mechanical half, and so does the ci. the pre-commit hook runs
the same lint on what is staged:

```
git config core.hooksPath tools/hooks
```

[NAMING_STYLE.md](NAMING_STYLE.md) is the naming table. the code philemon brought with
it predates it, so a name that breaks it is a warning; new code follows it.

commits are `subsystem: summary` in the lowercase imperative, under 72 columns, with a
body saying why, and end with a `Signed-off-by:` line.

## license

GPL-2.0-only, the same as velvet. see [LICENSE](LICENSE).
