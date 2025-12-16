---
episode: 1
title: "*(char*)0 = 0"
guid: "d5f882cd-bac2-4ede-a51a-daab8e61e51d"
pubDate: "Mon, 23 Nov 2020 06:09:40 +0000"
duration: "00:43:52"
audio: "tlbhit1.mp3"
description: "The adventure of storing NUL to NULL!"
explicit: false
---
# Episode 1: `*(char*)0 = 0`!


## Intro [00:00]

* Talked about TLBs last time, but didn't define what the acronym meant!
* Rectify that by talking about them way too much this time
* Episode title: `*(char*)0 = 0`!
* Standard disclaimer: only know so much, will try not to say things that are
  wrong, feel free to give us feedback
* Extensive show notes on the website (you're reading them right now!)

## First Errata! [00:37]

* The Go Programming Language [no longer uses segmented
  stacks](https://golang.org/doc/go1.3#stacks), does stack
  copying now
* Mistakes: how you learn! [Thanks to Graydon for pointing it
  out!](https://twitter.com/graydon_pub/status/1323503245717692417)

## The Program [01:15]

* How are we going to talk about TLB hits today?
* Figure out how a program gets to a TLB hit, to help us define what "TLB" is,
  and what hitting in it means
* Propose analyzing a C program:
  ```c
  int main() {
    *(char *)0 = 0;
  }
  ```
* For people who don't have a teletypewriter inside of their head:
  * main entry point
  * taking zero, turning it into a char star
  * deref-assigning it 0
* In a nutshell: storing zero to address 0 (as a `char*`)
* How can you not love this program?

## What about its C++y cousin? [02:10]

```c++
int main() {
  *reinterpret_cast<char*>(nullptr) = 0;
}
```

* Use `nullptr` value and `reinterpret_cast` it
* Can't `reinterpret_cast` nullptr, so won't compile -- #JustC++Things
* As of C++20 can use `std::bit_cast`: just takes a value and moves the bits
* Not guaranteed what you get when you bitcast/memcpy the nullptr!
* Since `nullptr` is monostate [i.e. existential] its contents are generally
  irrelevant and thus not defined what its bit contents are
* Old ways a bit more clear here

## Why do we have both `bit_cast` and `reinterpret_cast`? [03:10]

* `bit_cast` takes the object representation's literal bits (as-if by memcpy)
* Requires that the types (source and destination) have same size
* `bit_cast` returns a completely new object, whereas `reinterpret_cast`
  returns a reference (or pointer)
* Key here is that `std::nullptr_t` doesn't really have a value anyways
* Tricky stuff around here like whether value types exist in the from-type or
  to-type (but do any of us really exist?!)
* Interesting to learn about the language lawyer-y aspects of C++ so we know
  what we're typing in!

## Getting back to the program! [04:55]

* Dereferencing `NULL` and assigning it zero, and it's a `char*`
* What's cool talking about this program is everybody will look at it in a
  different way from their perspective: language, compiler, OS/hypervisor,
  instructions, hardware -- open, and a lot to talk about!
* Dig into the basics!
* Trying to reinterpret the value zero as a pointer, store another value, zero,
  inside that memory location
* Abstract translation from C to pseudo-assembly -- always a good exercise!

  ```
  r0 <- 0
  [r0] = st r0
  ```
* Even without a particular CPU in mind, the translation from C to abstract
  assembly is useful to know how to do

## Does the compiler even let you compile this program? [06:45]

* Writing something into null -- does the compiler "let you" turn it into
  assembly or does it give you an error at compile time?
* If it does give you an error at compile time, why?
* Some people will run a static analyzer on their code to catch
  definitely-null-deref errors like this, that can be determined statically
* Probably won't come out of the box as part of normal C compiler
* Stock gcc or clang will happily turn this into assembly instructions for me
* Clang static analyzer will flag it -- tries to detect "may-be-null
  dereferences" -- legitimate source of bugs in real code
* People will often run static analyzers as part of presubmits or nightlies
* "If you take this path, you'll be dereferencing null" analysis results
* Other static analyzers like Coverity also do things like this
* So at least the compiler will let us turn this into some binary (some set of
  assembly instructions)
* But now, we should note this is undefined behavior in both C and C++...

## What does undefined behavior mean?

* Generally means "it can be exploited by the compiler that `$X` is not the
  case"
* `$X` in this case is "I will not write to address 0 dynamically" -- because
  you're only allowed to write to actually existing objects
* Compiler can use the fact it must be an existing object to do optimizations
* If you actually do this at runtime then all bets are off for what the program
  behavior actually is
* Important thing: all a dynamic property -- if you have UB in part of your
  code that never runs then it's not UB because it never executes! [For runtime
  UB]
* In this case if you actually execute that code it is UB
* In C++ [and C] it likes to think about objects, everything is an object, and
  if there is no object there you're not allowed to write to it, no lifetime
  that has begun for that object
* At a high level UB is not the compiler trying to be a jerk to the programmer
* Allows compiler to assume that something isn't possible -- on the premise, if
  it were to happen, it's a bug in your program
* Ends up having kind of a ripple effect in code optimization -- each
  individual optimization step makes sense but final result is often surprising
  to people

## Memory mapped register pattern [09:55]

* Could make well defined by using `volatile` and using a non-zero value like
  `1` 
* Follows pattern of taking some number and casting to volatile `char*` or
  `int*`
* See this often with hardware-defined (memory mapped, e.g. from a peripheral)
  registers
* Hardware vendor will say "this address is a magical value, e.g. defined in
  the spec, manual, or header file, and if you write to it [or read from it]
  this is the behavior that you get out of the hardware" -- it can do something
  special!
* So could use volatile address of `1`, and value could still be 0 we're
  writing, it would still be well defined in that case.

## Zero is usually not mapped in [10:35]

* Zero is not mapped in to the address space is most modern userspace environments
* In kernel mode or more niche architectures this could actually do something
  -- could have peripheral with registers mapped in on address 0, or not fault
  on writes to address 0 running some kind of embedded system -- on x86 in
  physical memory the interrupt vector table resides at address 0

## What does the assembly really look like? [11:15]

* We talked about what the assembly would look like
* Good to try it out in reality and see if you were wrong
* Compiler explorer -- godbolt.org! gcc or llvm in different modes (x86, ARM)
* Funny: without volatile, [Clang on x86 just makes
  `ud2`](https://godbolt.org/z/zxn88r) (which just traps! [but also gives a
  nice warning])
* Similarly makes `brk` on ARM64 which does similar
* Code after optimization: enter main, then crash! (If you don't use volatile)
* GCC a little "nicer" -- instead of just emitting `ud2` or `brk` it'll store
  to `NULL` and *then* emit `ud2` or `brk` -- so it's "doing what you asked it
  to do" and then crashes afterwards
* But if you add volatile in there so you do:
  ```c
  int main() { *(volatile char*)0 = 0; }
  ```
* On x86 you'll get a `mov`, on [ARM a `strb`](https://godbolt.org/z/Gc3erb)
  (byte store).
* What's extra funny is GCC stil emits `ud2` after the null dereference even if
  it's volatile. [GCC even *ignores* the value being
  written!](https://godbolt.org/z/3PMWsE) Changing to:

  ```c
  int main() { *(volatile char*)0 = 42; }
  ```

  Still tries to store value 0!
* A bit unintuitive and annoyed kernel folks in the past, but can tell GCC to
  stop this with `-fno-delete-null-pointer-checks` -- unintuitive/frustrating
to people around `volatile`, but!
* If we step back a bit, zero is a special value, but let's deref one instead,
  gets rid of the silly `ud2`
  ```c
  int main() { *(volatile char*)1 = 42; }
  ```

  Now everything is like we expect.
* Address zero really is treated specially by both clang and gcc
* In this case volatile really tells the compiler when it sees address 1, that
  there are some effects that it can't reason about might be happening --
  "something special, don't try to be too smart"
* This pattern if you have memory mapped hardware registers is legitimate to
  access special memory and happens frequently!

## Traps and faults and aborts, oh my! [14:30]

* Back to focusing on user mode -- how does this instruction cause a trap, or
  should we call it a fault?
* Good question, maybe first can talk about exceptional things that happen in
  the processor in general when running a program
* Taxonomy of weird stuff that happens independent of normal flow of
  instructions through the processor
* Sometimes people break into categories of: traps, faults, and aborts
* Trap: ask operating system for assist or to inspect what happened
* Faults: something actually went wrong, and maybe can be corrected
* Aborts: program basically has to terminate
* For exceptions inside of the CPU, questions come up: do I need to show the
  exact architectural state where this thing happened [what if I'm reordering
  instructions under the hood?]
* Differences between things like divide by zero [maybe I just need to know the
  offending program counter?] and a system call, where your program is
  "cooperatively" asking the operating system for something, and interrupts
  that might come asynchronously to the program stream from a peripheral device
  telling you it has a packet available or similar to be serviced
* Relates questions like: can the hardware effectively reorder things assuming
  that an address is non-null [or valid in general]: gets back to "precise
  exceptions"
* If a segfault happens, you want to be able to analyze the [exact] cause of
  the segfault you got, instead of just "skidding to a stop" however it kept on
  going in the program [for other instructions that were in flight]
* Things inside of CPU like Reorder Buffers and the Point of No Return [and
  retirement] -- at what point can you start clobbering your architectural
  state with subsequent things that happen?
* Popping back up to the compiler level there's a similar question: can the
  *compiler* reorder things assuming a load is non-zero?
* Even though the abstract machine in the language standard has no notion of
  what a program looks like when something gets loaded from zero, compilers
  bridge the "practicality gap" between abstract machine concept and what
  people really expect their program to do when running against the hardware
* Again goes back to the notion of implementation- or un-defined behavior

## Even *more* bespoke circumstances! [16:45]

* Traps or faults can happen *within* instructions
* If you have repeated instructions like `rep movsb` (memcpy instruction),
  canonical exmaple of composite CISC-y instruction
* Or multi stack-push ARM instruction we talked about last episode
* Also devices that send asynchronous interrupt the CPU potentially in the
  middle of a long-running CISC-y instruction, how do we preempt that
  instruction
* Two traps racing: uniprocessor and an NMI comes in when exception is being
  raised from somewhere else

## Back to userspace virtual memory [17:45]

* Memory accesses in user mode all dealing with virtual addresses, which we
  talked a bit about last time
* Virtual addresses != physical addresses, the latter are morally linear "DRAM
  locations" all lined up in physical memory
* Each process in each guest VM has its own view of memory (virtual memory)
  distinct from how others see it, all done through virtual memory address
  layer
* Two worlds of virtual and physical stuff, pretty complicated how one maps to
  another

## Lots of memory access instructions! [18:25]

* If you look at assembly, probably a third of instruction are memory accesses,
  that's a lot! Lots of complication and a third of instructions have to deal
  with it!
* Guessing at reasoning for 1/3: conventional wisdom five instruction basic
  block, one load and one store; therefore 2/5?
* Technical term is a "NPOOA" -- order of magnitude, *lots* of instructions
  needing to go through this process!
* In computer systems always talking about "fast path" or "common case" because
  if we can speed that up it might be large percentage of the workload, and
  speeding up most important things [c.g. Amdahl's law]
* In the common case when you've addressed the memory location recently you
  want accesses to it to be fast, and caches are how this is made fast (we
  talked a bit about this last time)

## Virtual vs physical addresses as cache keys [19:45]

* Some caches can be addressed virtually using the virtual addresses to lookup
* Some can be address physically using the physical address you resolved from
  the virtual address
* Virtual address can be used for a "virtually addressed cache", of course also
  using the process context as an [effective, if not materialized] additional
  key, since it has its own view of memory
* As soon as you address physically (and most caches are address physically),
  need to somehow translate the virtual address to a physical one, and OS keeps
  the mapping in a (hierarchical) table called the page table
* Page table maps virtual address and process context/VM ID, mapping to
  physical address and properties of memory location, like RWX permissions
* At a high level organized as a tree, each level of tree is keyed off of bits
  of the virtual address, because going to be pretty sparse, flattening would
  make it huge, so needs a sparse (tree) layout
* On x86 we have hardware page table walkers and there's a control register
  called CR3 that describes where the base of the page table structure lives
* What's cool is the kernel puts stuff in memory and tells the hardware that
  location is special, and the hardware can start walking that autonomously
* As a userspace programmer you're not used to the hardware having a contract
  with your data structures, can be kind of mind boggling!
* Granularity of the mapping we're talking about depends on memory pages, size
  has to be dictated by hardware
* Often the smallest page size will be something like 4KiB
* Larger granularity called "hugepages" or "superpages"
* Finding base of a page, just lop off the bottom bits to get the base of your
  page

## Zoom back out to the big picture [22:50]

* Page table structure, lives in memory
* Specialized piece of hardware that knows how all the structs look inside of
  that page table structure
* Contract between hardware and the operating system
* Hardware capable of doing lookups to determine the virtual-to-physical
  mapping
* Slicing bits off the virtual address (from MSb to LSb) and walking
  through the levels of the tree structure [each level has 1024 entries then it
  slices 10 bits each time]
* Potentially goes through four page table levels, four data dependent accesses
* Ton of load instructions, four data dependent accesses would be quite
  expensive
* Sounds slow -- classic solution: add a cache!
* Every memory access looks up in the TLB.
* If the translation is found, TLB hit!
* Otherwise, not found, TLB miss, makes us sad :-(
* Every memory access, every instruction that does a memory access will look at
  the TLB and see if it's a hit or miss, really interesting, making it so you
  don't need to do the page table walk every memory access, makes a lot of
  sense!
* Important also that it only finds mapping for the current process/virtual
  machine -- finding other process' translations would be a Bad Thing
* TLB could be indexed using process context ID, but others are just flushed on
  every context switch -- every time kernel touches CR3 flushes the TLB, can be
  done on context switch
* Also why it's more uncommon to see fully virtual caches, don't want two
  process' views of memories confused, use a more physical notion instead of
  needing to flush entries anytime a process switch occurs

## How many entries? [25:50]

* Can't be that many since it uses hardware implementing an associative array
* Big parallel comparison on keys to figure out which value should be selected
* Generally at most one should ever match
* Gets into more detailed notion of how many cycles does it take to hit in the
  L1 cache and what are those cycles of latency doing?
* Usually ~3 cycles [correction: usually 4] on a super tight timing path --
  look up entry in TLB and that tells us what the tag is that we compare
  against for that address, and we look up the index in the cache (groups
  addresses together), and then we resolve the index against the tag
* Could be spelled out in more detail, but this couple-of-step process

## Page Table Walkers As Little Accelerators [27:00]

* TLB is software managed, when OS changes page table it flushes out the
  entries from the TLB
* Not totally sure, but think TLBs are pretty complete, aside from
  invalidation, page table walkers can operate entirely autonomous from the OS
  (don't require assistance)
* Sometimes little fast accelerators can only handle common cases, but because
  walking page table is a fairly straightforward process, can be pretty
  complete and don't need to ask for help

## Once physical translation is resolved [27:45]

* On TLB hit then the hardware queries the cache and accesses the line if it's
  present; if not, cache protocol kicks in asking the next level
* Should do an episode on how the caches line up and talk to each other
* If not in any level will go fetch the line from DRAM
* We should do a followup on DRAM row buffering and cache line replacement
  policy and things like this involved in the memory subsystem

## What about on TLB miss? [28:25]

* If the TLB misses then a page table walk occurs -- either that'll find an
  entry or it won't find the entry (if there's no entry there)
* So if the entry is found it'll be inserted into the TLB (want to find it next
  time)
* Some TLBs are managed by hardware and some by software -- who adds it to the
  TLB depends on what the hardware platform dictates
* Don't need to have hardware page table walkers -- could ask the OS when you
  page fault "can you walk this for me and put it into the TLB", then resume
  the userspace program
* Of course also have to check access permissions for the page; if you don't
  have a "W" bit and you're doing a store, then a fault still needs to be
  raised in that case

## Code and data [29:30]

* Complication of separate data and instruction caches
* Code itself lives in memory!
* Code is effectively data, even though it may be cached differently [when it's
  being pulled into the instruction dispatch path]
* Executing an arithmetic instruction like an `add` might cause a memory
  access, because that actual instruction needs to be fetched!
* Roughly a third of instructions cause memory access when they execute, but
  *any* instruction could cause a memory access to be fetched
* And that fetch is from virtual memory so can cause a page table walk, and
  result in several memory accesses
* In addition to instruction and data caches, modern systems have both
  instruction and data TLBs
* Different TLBs for instruction and data memory fetch paths, makes you wonder
  what instruction can cause the most memory accesses on its own?!
* [Folks on the internet showed MMUs are Turing
  complete](https://github.com/jbangert/trapcc), which ruins the fun
  question -- if you stopped at "simple" instructions, then how could we
  generate the most loads and stores from a single instruction
* Say a scatter or gather instruction in the vector unit -- if that misses in
  the iTLB (say 4-5 accesses) and then the gather itself touches 8 or 16
  locations, and each could miss in the dTLB/cache
* Maybe folks on the intertubes have ideas of what the maximum number of memory
  accesses you could do in an instruction?!
* The AVX gather instruction has an astounding amount of memory level
  parallelism -- cool to see as new instructions are introduced what it does in
  terms of questioning the assumptions of what we usually do with scalar code
* Mind boggling to think about stores on the data path can be storing into
  memory locations that are cached inside of the instruction cache [perhaps uop
  translated or in-flight!] -- if need to be kept coherent then immediately the
  store needs to be observable by the instruction side of the machine
* On other [i.e. non x86] machines you need to explicitly flush the instruction
  cache to perform a (non-coherent) writes into your instruction memory

## IOMMUs: virtualized memory for devices [32:25]
 
* Devices can also get a view of memory that's virtualized that can help
  prevent e.g. evil PCIe devices, like if I made a malicious FPGA card that
  wanted to grab things out of physical memory
* Notion of IOMMUs, I/O Memory Management Units, can maintain a virtual memory
  view for these peripheral devices
* How you keep them consistent and such probably too much for this episode!

## Back to initial example [33:00]

* Virtual address was zero!
* Some operating systems map zero page without any permissions so it'll always
  cause a fault for every process
* Global bit you can set on these entries to say it pertains to everybody
* We don't want to map anything there to catch bugs
* When you do mmap and you try to map something at 0 it doesn't have to handle
  it specially because the entry is already there
* But ends up acting similarly to if we load from an address that wasn't mapped
  at all, then the page table walk would fail saying "I don't see an entry for
  this" and causing a segmentation fault

## So what is a segmentation fault? [33:45]

* Hardware does the walk, and then tells the OS "hey I couldn't find anything
  (valid)"
* What the hardware ends up doing is using an ABI (Application Binary
  Interface) between the hardware and the OS where the hardware then knows to
  "start executing $here"
* ABI defines what values will be in what registers, and from the kernel's
  perspective, looks similar to a function call with a calling convention when
  that interrupt handler is invoked
* Can look like a regular (C) functional call when you look at it
* Perhaps you get an enum that tells you what kind of trap/fault, say page
  fault, and the address at which it occurred, and some notion of process
  context identification
* You'd find that in the architecture handbook/manual of how to program this
  kind of machine -- what exactly happens when a CPU exception happens?
* OS figures out which process it corresponds to and then decides what to do
* If OS itself created an unexpected page fault maybe it panics!
* If OS itself running in hypervisor, hyerpvisor might get first dibs on
  handling hardware exception, pass it to guest OS
* Guest OS might say "that wasn't my problem", pass it on to the userspace
  program in the form of a signal
* Most userspace programs people don't really handle signals
* Default signal handler gets triggered, and default handler might just say
  "thanks for playing!" (e.g. "segfault happened at $location") and then stop
  the program; i.e. call abort

## Running in debuggers [36:38]

* If running program under a debugger will have installed signal handlers [for
  its inferior] and report the issue
* After reporting the issue to the developer will go back to the debugger
  prompt
* gdb and lldb are programs, running with a thin "emulation" layer [ed: maybe
  more like "supervisor"?]
* They talk to the kernel and they let the program pretend everything is
  executing regularly when really they're "inside"/"under" the debugger
* Other programs that do this kind of thing for a variety of reasons

## JS engines / WebAssembly [37:35]

* JS engines in browsers optimize things like WebAssembly by installing signal
  handlers to capture invalid memory accesses
* Dive into that, sounds a bit odd
* Managed virtual machine running untrusted code from the internet, but
  execution has to be secure
* JS is a dynamic language that has semantics should prevent faulting from
  happening
* WebAssembly wants to provide a VM for something that looks like low level
  static code (C++/Rust)
* Associated with WebAssembly "instance" w/continuous 4GiB-limited slab of
  memory -- currently 32-bit process model
* On startup will map 4GiB of *virtual* memory with a redzone after, but it's
  not physically backed -- allocating page table entries
* Everything can be done as `base+offset` memory accesses using that virtual
  base
* Instead of checking "have I mapped this" every time, everything mapped
  `-RWX` (from the start), unless user code has asked to map them
* Hardware is telling you if it hasn't been mapped!
* Ride on the existing fast paths -- way most VMs implement WebAssembly these
  days is by having the hardware letting it know if something isn't mapped,
  since hardware is good at that
* Have to be sure access doesn't go past the 4GiB, 128MiB (say) of redzone
* If the JIT can prove may go past that it will explicitly do an OOB check, but
  anything inside it will just let trap
* Can prove most memory accesses are within that bound in practice, rare to
  have really large (known) offsets on loads and stores
* If wasm access faults, browser signal handler checks whether it was a wasm
  program -- signal handlers are process wide, so browser needs to figure out
  if it's a wasm memory access, if so, unwind wasm stack (as in last episode)
  and throw JavaScript exception (from the wasm access that faulted in
  hardware)
* If indexing relative to a null object address, and you know the offset would
  still be within the null page, can just catch the faulty access (via fault
  handler) and resume by throwing a Java `NullPointerException` after that
  handler had run [Advanced note: also requires on-stack-invalidation to happen
  in the handler]
* Common technique for (Language) Virtual Machines in general!

## Rough "Numbers to Know" [42:30]

* We *did* cover what a TLB hit is, yay!
* A lot of the numbers mostly similar to how they were when this talk was given
* Talked about L1 cache hit could be order 3 cycles [edit: really 4 in modern
  Intel machines]
* Branch mispredicts: have to flush pipeline which is O(a dozen) pipe stages,
  something like 16 cycles \approx 5ns.
* L2 cache references, farther away, maybe 10 clocks; L3 cache references,
  farther away still [and may have to cross slices], maybe 30 clocks
* Main memory references can be O(100ns)
* PCIe [RTT/2] traversal maybe 500ns away
* These are various times "local to the machine" that could be interesting;
  then other things like flash/spinning disk or communicating packets over the
  network
* Can imagine walking page table and doing bunch of main memory references,
  four back to back main memory references potentially
* Loads can vary from fraction of a nanosecond to hundreds of nanoseconds!
* Really interesting because loads are a) at the heart of computing and b) have
  such varied performance characteristics in the von Neumann machine model
* Can go all the way to packets across the world and satellites and such!
* Everybody likes good performance numbers!

## Until Next Time [45:00]

* A lot for now! Until next time...

## Things we didn't get to!

* `perf stat` [shows iTLB and dTLB
  events](https://perf.wiki.kernel.org/index.php/Tutorial#Events), but you do
  always have to be careful looking up what the counters mean for your
  particular architecture
* One of the cool things about open cores like BOOM is you can just link to the
  [implementation of a TLB implemented in
Chisel](https://github.com/riscv-boom/riscv-boom/blob/1cb1596224c5681b839b8b115c1fbf6d802cc512/src/main/scala/lsu/tlb.scala)
  and [a page table
walker](https://github.com/chipsalliance/rocket-chip/blob/407496940311a0f0e8ec24627d93a7b839692ac6/src/main/scala/rocket/PTW.scala#L156)!
