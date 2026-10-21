philemon, the bootloader
========================

philemon is named for the one who grants the power and then steps back. he
does not fight anything and he is not there for the rest of it. that is the
whole job description of a bootloader, and it is more than most of them get.

he was written in velvetOS 0.1.12, to replace a borrowed loader along with
the iso, the uefi path and the boot protocol that came with it, and he lived
in velvet's ``boot/`` from the day the kernel left that tree. from 1.0.0 he
is a project of his own, and velvet and anything built on it fetch him by
version.

he does three things:

#. asks the bios everything it will ever be able to answer, because the
   moment long mode starts it stops answering;
#. turns the kernel from a file into something running at the address it
   was linked for;
#. leaves behind one struct describing the machine.

one program, one sector
-----------------------

the only reason there is a line across the middle of ``src/philemon.asm``
is that the bios reads exactly one sector. 512 bytes ending in ``0x55
0xaa``. drops it at ``0x7c00`` and jumps to it. that is the entire
contract and it is not negotiable. so the first 512 bytes do nothing but
pull in the rest of the same file, to the address immediately after
themselves, and carry on. after that the line is invisible: it is one image
at one address, and nothing below cares where the sector ended.

everything the bios can be asked, he asks while it can still answer:

a20
   the twenty-first address line is still disabled at power on so a machine
   from 1981 could wrap around at one megabyte. it has been forty years.

unreal mode
   the bios cannot write above one megabyte and the kernel does not fit
   below it. so: into protected mode for exactly long enough to load one
   segment register with a descriptor whose limit is the whole address
   space, and back out again. returning to real mode does not reload the
   hidden half of a segment register, so the wide limit survives and 32-bit
   offsets keep working. it goes in ``fs``, not ``es``, and that detail is
   the difference between this working and not.

page tables
   long mode will not start without them. two-megabyte pages, three
   windows: everything identity mapped so the loader keeps working, the
   same memory again in the higher half where the kernel expects a direct
   map, and the kernel's own window at the top.

the 64-bit half is C, ``src/philemon.c``, and that is the point of the
split. once long mode runs there is no reason to stay in assembly, and the
work left (parsing an elf, honouring the distances a linker chose between
segments, zeroing bss, carving everything already spent out of the memory
map) is exacting work where being wrong by eight bytes is a black screen.
all of it compiles for the host and is tested (``tests/test_philemon.c``),
which the assembly cannot be.

the assembly and the C cannot share a header, so ``include/philemon.inc``
is the assembly's copy of the addresses ``include/philemon.h`` declares.
both image writers refuse to write an image while the two disagree, since a
number that drifts in one of them is a machine that hangs with nothing on
the screen.

the handoff
-----------

the handoff is velvet's boot protocol, revision 1: one struct, ``struct
ph_handoff`` in ``include/philemon.h``, and the kernel entered the way any
function is called, with a pointer to it in ``rdi``. there is nothing to
scan for. velvet documents the same protocol from the kernel's side, in its
``docs/subsystems/boot.rst``, under its own names; the layout and the magic
are the same, and a change to one is a change to both.

everything the kernel could only have learned before long mode is in there:

- the direct map offset (``hhdm``). add it to a physical address;
- where the kernel really is and where it thinks it is;
- the memory map, already sorted, with everything spent carved out;
- the ramdisk, through the direct map;
- ``rsdp``, or 0 if the firmware has no acpi tables;
- the framebuffer, or a width of 0 if no video mode was got.

the struct sits in memory the map types as the loader's, which the kernel
may take back once it has finished reading it.

there is a smaller, rawer struct before that, ``struct ph_early``, which is
the bios's own account of the machine: the e820 map and the framebuffer,
left by the 16-bit half for the 64-bit half to make sense of. it never
leaves philemon.

the table on the disk
---------------------

the image writer puts a table at logical block 32, because the first
sectors are spoken for, saying where each piece is: the 64-bit half, the
kernel, the ramdisk, and a **source archive**, which philemon does not load
and never will. the kernel and the ramdisk have to be in memory before
anything runs; the archive only has to be *reachable*, which is a different
and much cheaper requirement, so it stays on the medium for whatever runs
later to read a sector at a time. three fields of zeroes mean there is
none.

the table only ever grows at the end, which is why an image from before the
archive was added still reads. an older loader reads the fields it knows and
stops; a newer reader of an older table finds zeroes, which is the honest
answer. a kernel can find the medium it booted from by the table's magic at
block 32, which velvet does.

the image writer
----------------

``tools/mkboot.py`` writes the layout::

    lba 0..31    philemon, whose first sector is the one the bios reads
    lba 32       the table saying where everything else is
    lba 33..     philemon's 64-bit half
    then         the kernel, as an elf file
    then         the ramdisk tar
    then         the source tar, which nothing loads

::

    tools/mkboot.py out.img bin/philemon.bin bin/philemon64.bin \
                    kernel.elf [ramdisk.tar [source.tar]]

``tools/mkboot.c`` is the same writer in C, for a system that writes images
with nothing but a compiler. ``tools/mkbootcheck.py`` hands both the same
pieces and wants the same bytes back, wants zeroes in the table when there
is no archive, and drifts one constant in a copy of the tree to see both of
them refuse.

the parts worth testing
-----------------------

``ph_load_elf()`` copies an elf's loadable segments to where they belong,
moving all of them by the same amount so the distances the linker chose
survive. ``ph_build_memmap()`` turns the bios's account into the kernel's.
``ph_find_rsdp()`` finds the acpi tables where the firmware leaves them.
these three are the hard ones, and all three take their input as arguments,
so the host suite can fabricate a machine and poke at them.

the assembly says what it is doing at every step, over the serial port, from
the first instruction of the boot sector onwards. a bootloader that fails
silently is one nobody can fix.

philemon has no kernel of his own to boot, so the boot itself is tested
where there is one: velvet's boot test and selftests boot an image this
tree wrote, every time they run.

building from another tree
--------------------------

a tree that boots with philemon names one release of him by version, clones
the tag ``vX.Y.Z``, and builds him into directories of its own::

    make -C philemon BINDIR=... OBJROOT=...

then writes its image with ``philemon/tools/mkboot.py``, which checks that
tree's assembly and C against each other before it writes anything. a
released tag is never moved, so the version is all that tree needs to know
which loader it ships.
