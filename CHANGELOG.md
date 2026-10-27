# changelog

every version of philemon, newest first.

until 1.0.0 philemon was a directory of somebody else's tree: velvetOS's
`boot/` from 0.1.12, where he replaced a borrowed loader, and velvet's
`boot/` after the kernel left velvetOS. his history up to then is in their
changelogs, written when it happened, and it stays there.

---

- **1.0.1**: a loader for any x86_64. the 64-bit half was built for
  whatever cpu gcc assumed, and the gcc in ubuntu's amd64v3 archive
  assumes bmi2 and avx2. velvet's boot test, on ubuntu 26.04, stopped at
  `kernel at 0x`: the first shift by a variable was a `shrx`, qemu's
  default cpu has none, and with no idt yet the machine reset without a
  word. `-march=x86-64` says which machine he is for, and a gcc whose
  default is already that builds him to the same bytes as 1.0.0.

  the early struct's check, the plan's 1.0.1, is 1.0.2 now.

- **1.0.0**: philemon on his own. the loader is the one velvet 0.4.3
  booted with, and the two halves build to the same bytes they did there.
  what moved is where it lives: `src/` and `include/` instead of `boot/`
  and `include/velvet/`, with the paths in the image writers and the
  assembly's include changed to match. the handoff is revision 1, the
  table on the disk is the one images have carried since 0.3.26, and
  the magic is still `PHLMN0`.

  the image writer's checks came with him. velvet ran them inside its own
  tool check, on its kernel and its ramdisk; `tools/mkbootcheck.py` runs
  them here on pieces of its own, since the writer only places bytes and
  never reads them. it asks one thing velvet's never did: that an image
  written without a source archive says so, with zeroes in the table,
  because velvet's own images stop carrying one.

  a lint, the ci and a pre-commit hook, with the naming table in
  `NAMING_STYLE.md`. the code that came with him predates the table, so
  the lint warns about the names it breaks rather than failing on them.

  still open, and carried as it was: the assembly writes `struct
  ph_early` field by field and stores `boot_drive` at 108 where the C
  struct puts it at 112, and the agreement check only covers the boot
  table. the FIXME in `tools/mkboot.py` says what a real check would
  compare.
