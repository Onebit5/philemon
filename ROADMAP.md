# where this is going

philemon's plan, from 1.0.0 on, the release that made him a project of his
own. each entry is a release on its own: built, booted, and worth a
paragraph in the changelog. the numbers run without gaps, and an entry
leaves this file when its release is cut.

this is the loader's plan and only the loader's. what the kernel is handed
is velvet's boot protocol, and it changes in velvet first; what a system
writes onto a disk, and when it says a boot went well, is the system's.
an entry here is the part only a loader can do, and none of them makes him
boot anything but velvet.

## 1.x: a loader a system can trust with its kernels

a system that builds and installs its own kernels needs two things from the
loader: a way to say which kernel to start, and a way back when the one it
said does not come up.

**1.0.1 the early struct, checked.** the assembly writes `struct ph_early`
field by field and stores `boot_drive` at 108, where the C struct puts it
at 112; nothing reads the field yet, which is the only reason nothing has
broken. the writers' agreement check covers the boot table and not this
struct, and covers each field by a multiple of eight rather than by where
it belongs. *ends when both structs are checked field by field against
the header, and the drift that check finds is fixed.*

**1.1.0 a boot it can choose between.** philemon starts the kernel the
table names, which is right while there is only one kernel and wrong the
moment a system can write a second. he learns to read a small record,
written by the system, naming which of two kernels to start, and to say so
when the answer is missing or names nothing that is there. *ends when two
kernels are on one disk, either can be chosen, and neither has to know the
other exists.*

**1.2.0 an update that goes wrong costs one reboot.** a system that
installs its own kernels is, without this, a machine that can brick itself
with one bad build. a new kernel runs on probation: philemon counts the
boots he has given it, and if the system has not said one of them was good
before they run out, the boot after starts the kernel that was there
before. when a boot counts as good is the system's to decide, and it says
so by writing the record 1.1.0 reads. *ends when a deliberately broken
kernel is installed, fails, and the machine comes back up on the old one
without anyone touching it.*

**1.3.0 uefi.** philemon reads the disk through the bios and asks vbe for a
framebuffer, which is `int 10h`, which does not exist on firmware made
after about 2012. so he gets a second front half: a PE application the
firmware loads, GOP for the framebuffer, `GetMemoryMap` where e820 was,
and `ExitBootServices` before the kernel runs. what he must not get is a
second handoff: velvet is handed one struct and knows nothing about
anybody's firmware, and this is the release that finds out whether that
was true. the bios path stays. a machine that only boots on 2012 firmware
is exactly as narrow as one that only boots on 1981's. *ends when the same
kernel, unchanged, boots from the bios and from ovmf.*
