VERSION = 1
PATCHLEVEL = 0
SUBLEVEL = 0
PHILEMONRELEASE = $(VERSION).$(PATCHLEVEL).$(SUBLEVEL)

# philemon build. needs gcc, nasm, binutils, make and python3.
#
# targets:
#   make          -> the loader, bin/philemon.bin and bin/philemon64.bin,
#                    and the image writer in C, bin/mkboot
#   make test     -> the host suite and the image writer's checks
#   make lint     -> the style lint (whole tree, or FILES=src/philemon.c)
#   make release  -> print the version
#   make clean
#
# building from somewhere else. a tree that boots with philemon builds it
# out of this one and says where the outputs go, so nothing lands here:
#
#   make -C philemon BINDIR=... OBJROOT=...
#
# and writes its image with tools/mkboot.py from this tree, which checks
# that this tree's assembly and C agree before it writes anything.

BINDIR  ?= bin
OBJROOT ?= obj
T := $(BINDIR)/tests

NASM    := nasm
CC      := gcc
LD      := ld
OBJCOPY := objcopy

# the 64-bit half runs before anything has set up the fpu or a stack
# with a red zone anybody would honour, and at the address the linker
# script gives it rather than wherever a loader would like
CFLAGS := -std=gnu11 -ffreestanding -fno-pic -fno-stack-protector \
          -mno-red-zone -mno-sse -mno-mmx -mno-80387 -mcmodel=small \
          -Wall -Wextra -O2 -Iinclude

HOSTFLAGS := -std=gnu11 -Wall -Wextra -g -Iinclude

LOADER := $(BINDIR)/philemon.bin $(BINDIR)/philemon64.bin

.PHONY: all test lint release clean

# the `@:` keeps a build that includes this one quiet when there is
# nothing to do, since it asks every time
all: $(LOADER) $(BINDIR)/mkboot
	@:

$(BINDIR)/philemon.bin: src/philemon.asm include/philemon.inc
	@mkdir -p $(@D)
	$(NASM) -f bin -I include/ $< -o $@

$(BINDIR)/philemon64.bin: src/philemon.c include/philemon.h src/philemon.ld
	@mkdir -p $(@D) $(OBJROOT)
	$(CC) $(CFLAGS) -c src/philemon.c -o $(OBJROOT)/philemon.o
	$(LD) -T src/philemon.ld -nostdlib -static --no-warn-rwx-segments \
		$(OBJROOT)/philemon.o -o $(OBJROOT)/philemon.elf
	$(OBJCOPY) -O binary $(OBJROOT)/philemon.elf $@

$(BINDIR)/mkboot: tools/mkboot.c
	@mkdir -p $(@D)
	$(CC) $(HOSTFLAGS) $< -o $@

# the 64-bit half compiled for the host, so the suite can fabricate a
# machine and hand it to the parts that are easy to get wrong
$(T)/philemon: tests/test_philemon.c src/philemon.c include/philemon.h
	@mkdir -p $(@D)
	$(CC) $(HOSTFLAGS) tests/test_philemon.c src/philemon.c -o $@

test: $(T)/philemon $(LOADER) $(BINDIR)/mkboot
	@fail=0; \
	printf '  %-10s ' philemon; \
	if out=$$(./$(T)/philemon 2>&1); then \
		echo 'ok'; \
	else \
		echo 'FAILED'; echo "$$out" | sed 's/^/    /'; fail=1; \
	fi; \
	printf '  %-10s ' mkboot; \
	if out=$$(python3 tools/mkbootcheck.py $(BINDIR) 2>&1); then \
		echo 'ok'; \
	else \
		echo 'FAILED'; echo "$$out" | sed 's/^/    /'; fail=1; \
	fi; \
	exit $$fail

lint:
	@python3 tools/lint.py $(FILES)

release:
	@echo $(PHILEMONRELEASE)

clean:
	rm -rf $(BINDIR) $(OBJROOT)
