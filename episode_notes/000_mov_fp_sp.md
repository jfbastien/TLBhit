---
episode: 0
title: "mov fp, sp"
guid: "c685f738-397d-4b7b-9dc6-171eaf2b07de"
pubDate: "Mon, 02 Nov 2020 01:21:16 +0000"
duration: "01:04:28"
audio: "tlbhit0.mp3"
description: "The stack, and how it relates to TLB Hits."
explicit: false
---
# Episode 0: `mov fp, sp`


## 00:00:00 Intro

* Website: [tlbh.it](https://tlbh.it/)
* Twitter: [@tlbhit](https://twitter.com/tlbhit)
* [This episode on Apple podcast](https://podcasts.apple.com/us/podcast/mov-fp-sp/id1538369465?i=1000496866078)
* The stack pretty much always TLB hits!

## 00:00:59 Disclaimer

* We're lifelong learners, only know so much!
* Will put errata up on [the TLB Hit website](https://tlbh.it/)
* ["Sidechannels"](https://en.wikipedia.org/wiki/Covert_channel) via Twitter

## 00:01:42 What's the stack?

* Episode is named `mov fp sp`
* `mov fp sp` in the prologue of functions
* Epilogue has "reverse" `mov sp fp`
* Instructions that manipulate *the stack*!
* Compiler spills values that registers can't hold onto the stack
* Functions do it a lot -- have their own [local] state, call functions that
  have their own state
* Because subroutines can recurse without bounds would need unbounded number of
  registers
* Often different kinds of registers: arithmetic value registers, floating
  point registers
* Registers contain fairly arbitrary "stuff": pointers to data, pointers to
  code, return addresses, etc.
* Stack is *usually* contiguous and allocated on a per-thread basis
* Idea of "GPRs": general purpose registers, though some machines have
  dedicated registers for floating point values as well, or SIMD for really
  wide
* Prologue moves stack pointer to base pointer, epilogue moves base pointer
  back to stack pointer, "undoing", locally manipulating the stack pointer then
  rolling things back to where they previously were

## 00:03:50 Mechanisms in the processor

* Frame pointer/base pointer (bp/fp), stack pointer (sp)
* Usual convention is that the frame pointer doesn't change during the course
  of the function's execution
* Generated code addresses "slots" relative (at offsets from) the frame
  pointer; e.g. `+4`, `+8`, etc.
* Stack is kind of like a linked list! Pointer of the stack that says "this is
  where the frame pointer *used to be* before we came into this routine".

## 00:05:10 Comparison to an abstract stack machine

* In CS class you may learn about machines where you push two operands onto a
  stack then do an add operation that consumes the top two things on the stack
* Compare to traditional processor we use today: expanding the stack as a
  single operation that makes a bunch of slots at once
* The slots don't need to be consumed in a strictly stack-order fashion
* Distinction of "stack machine" vs scratchpad-area style frame areas
  that happen in stack-like fashion for subroutine calls

## 00:06:05 Some instruction set considerations

* Considerations on modern machines for frequency of these operations and how
  they fit in our instruction cache; e.g. on x86 `push`/`pop` are single byte
  opcodes
* On ARM we may have a "push multiple values" instruction; little CISC-y but you
  do so commonly it may make some sense
* ARMv7 had instruction allowed to push 16 registers (all GPRs) and increment
  stack pointer. Yay RISC!

## 00:07:09 Compiler optimizations and stackiness

* By moving things onto the stack -- code is constantly working with the things
  in its stack frame
* Locality, but also avoiding memory allocation subroutines (100s or 1000s of
  cycle depending)
* In scratchpad area values are tracked precisely in dataflow sort of style
* Bring them "in" to the compiler, values becomes more trackable
* SSA values vs arbitrary memory references
* When structs are brought onto the stack the individual fields inside can be
  broken apart and the component fields can be tracked as individual values
* Often called "scalar replacement of aggregates" (e.g. in LLVM)
* When we home them on the stack we can do our common optimizations, CSE, DCE;
  if on the heap, may be a lot harder to to do
* In managed languages (e.g. JavaScript, Java) would do escape analysis to show
  it doesn't escape via heap to an unknown subroutine -- once placed on the
  stack you can eliminate whole objects and just track sub-fields inside of it
* Allows you to just "explode" the object itself and think about its component
  fields individually and get rid of whatever doesn't matter in there

## 00:09:17 Eliding heap allocations in C++

* Some compilers can also sometimes optimize local heap allocations, turn them
  into stacky allocation
* C++ explicitly allows you to do that as of a few years ago, Clang does that
* If you new an object no guarantee that you're actually going to put it on the
  heap / call the underlying allocator
* Can be surprising to people -- can do SRoA, other stuff, might get rid of the
  entire computation
* Neat, unless it's not what you're trying to do
* But seems like a key optimization to do
* If you're thinking about things as objects instead of raw bytes having higher
  level understanding you can optimize based off of is pretty key it seems?

## 00:10:18 Frame pointer omission

* When JF started programming there was "frame pointer omission" (FPO) which
  was cool because optmizers weren't as good as they are now
* Back when you only had 8 registers for x86 the extra register could go a long
  way potentially -- stack is hot in cache but doing stores and loads to memory
  locations
* Was known to some as "that flag that makes the debugger way worse" -- debug
  information has to be a lot more prescriptive when you can't simply describe
  where things are as an offset from a canonical (assumed unchanging) register
* Modern CPUs doing register renaming under the hood against a much bigger
  micro-architectural register set -- not as worried about saving that one
  register as much of the time -- although in hot code you still might

## 00:11:49 "Leaf" functions

* When you inline things you make bigger regions for analysis, ideally make big
  fat leaf functions
* How much of program time is generally spent in leaf functions over some set
  of applications?
* Function at the end of the call tree
* If your subroutine doesn't call any other subroutines that's a nice property,
  because now you know that everything at the end of the stack belongs to you,
  you're just doing your work and popping back up to whoever called you
* Inlining really unlocks power of leaf -- inlining into non-leaf-functions can
  *make* them become the leaf
* So long as you don't over-inline and the working set doesn't become too big
  -- the compiler can know everything it does and have a good amount of work to
  do
* Small region in which you can analyze *everything*, like tiny little whole
  program analysis

## 00:13:10 Why do we have a stack again?

* Why can't we inline everything?
* Two main issues: 1) don't necessarily know call graph for the whole program
  2) recursion
* If you knew where all the calls went (virtual/indirect/etc in your
  translation unit and other ones in your program), and without recursion, you
  wouldn't need a stack, you know a perfect call graph
* For some of these you could avoid having a stack -- virtual functions but
  only a few actually implementations of it, could change to test-and-branch
* If you have a fully analyzable virtual dispatch it effectively just becomes a
  switch, can potentially inline what the targets are
* Control flow analysis takes indirect branch that can go anywhere and
  enumerate the real set of possibilities (devirtualization within a
  translation unit)
* Fully analyzeable call graph is an interesting computer history topic:
  FORTRAN77 classically able to do this (programs were restricted enough you
  could analyze it)
* XLA ML/array programming machine learning compiler has the same property
  where the whole call graph is analyzeable so you can create a slab that's the
  giant frame for the whole program you're optimizing and all allocations are
  known-fixed size
* Whole program call graph analyzeability lives on in these niche use cases!
* In stark contrast, sometimes we need multiple different kinds of stacks at
  the same time!
* The JS engine would sometimes recur from JS calls through the VM runtime to
  other JS code, and that would need to potentially create a sub-stack (!) --
  multi stack problems exist beyond even just needing to analyze/manage a
  single stack
* Programming in FORTRAN is cool, for scientific code often trying to
  solve a specific physics problem don't *usually* need those tools like
  recursion or virtual functions
* When everything is "monomorphized" -- you have big arrays of
  fixed-value-types you can know everything about the world and really optimize
  everything based off of it -- fun mode to be in for scientific computing code

## 00:16:34 Considerations beyond recursion and indirect calls?

* Some languages use the stack for fast thread switching? Things like full
  stackful coroutines?
* Stacks in Go for example are not contiguous: more like C++ deque: linked list
  of lists instead of one contiguous stack -- clever x86 code sequence that
  makes it fast to find previous and next frame
* Allows Go stacks to be distinct allocations -- each page-wise is one frame
  and the next function has another frame -- can put multiple functions in one
  allocation
* Used to have really bad perf if you were in a hot loop and happened to
  straddle that boundary
* Coroutines in some languages ended up having some "stackless" stuff like
  this, where the closure is heap allocated instead
* C++ coroutines try to do away with all the heap allocations, but depends on
  optimization level whether it can do that or not
* Kind of similar for Objective-C blocks -- until recently always heap
  allocated, started being stack allocated in last few years where they could
* Language doesn't say whether stuff lives on the heap or not
* Because stack is less constrained can live in different places, e.g. in Go
* In some cases you remove the allocation entirely

## 00:18:25 Scaling to millions of threads?

* If you want to be able to scale your concurrency assumptions to millions of
  threads, you don't want to have huge stacks
* Each thread has a stack, and if you have millions of threads you don't want
  to be allocating too much
* And need to be able to switch between those threads quickly
* So raises the question: how do you usually size those stacks in the
  per-thread context you have?
* If you're doing tiny little operations; e.g. if every operation in your
  program was conceptually a thread, you wouldn't want to allocate 512KiB every
  time you did a tiny atomic operation

## 00:19:10 Managed languages putting frames on the heap

* On the term "stackless": one of the [Python
  "greenlet"](https://greenlet.readthedocs.io/en/latest/) ("lightweight thread"
  terminology) attempts was called [Stackless
  Python](https://github.com/stackless-dev/stackless/wiki)
* In managed languages like Python the frames can be allocated on the heap;
  e.g. in CPython the frames are allocated on the heap
* But you still have a native stack for your native program that's doing the
  managed VM execution! (e.g. the interpreter code written in C)
* Something that JITs can do is unify the stacks; so that the "interpreted"
  code uses the same stack space as the virtual machine -- single native thread
  of stack space
* [ed: on *deoptimization* the JIT code can be reified into a
  managed stack frame on the heap through a process called "On Stack
  Invalidation"]
* Frame is really just some space, spaces get linked together in the abstract
  concept of a stack, both of those things can also happen on the heap -- no
  reason this one virtual memory region that we call the stack is the place where
  that *has* to happen

## 00:20:20 Stack sizes in practice

* GPUs have thousands and thousands of threads (organized in warps), you end up
  wanting to not want huge stacks
* But typically on CPU between 512KiB and 2MiB in common environments (MacOS,
  Linux, Windows)
* Allocated at thread startup
* Most platforms have API to change the size -- some can only do at runtime,
  some can only do at startup
* Being able to change the stack size is this "uneven" thing across platforms
* That's common "userspace": if you look at kernel threads or embedded systems
  it may be way smaller, XNU: 16KiB
* Blowing the stack can be easy in these cases when you're handling interrupts
  -- can end up blowing stack pretty easily so have to be careful

## 00:21:27 What are the biggest stack programs?

* The reverse of "tiny stacks" environments is interesting -- what are the
  biggest stack programs that exist? Who does that?
* In some environments that set stack limit quite low, when you compile in
  debug mode, you'll be spilling a bunch of things, and then you'll get a
  random segfault because the frame got bigger than the initial stack
  allocation was assuming or you hopped into the guard pages

## 00:22:08 Allocating default start size

* Conceptually, doesn't all have to be allocated at the start do you?
* Could grow on the fly as you determine that you need more space
* Interesting mechanisms to do that at OS level and for managed languages you
  could even locate where your stack segment is
* Just allocate a page and virtually map the other ones (no physical backing),
  fault when they get accessed, then map them in as needed
* In managed languages when you know where all the pointers are you can
  relocate all the pointers that had anything to do with the stack locations

## 00:22:58 Stacks working nicely with LRU caches

* Younger frames are recently touched
* Spatial and temporal locality are two things that caches exploit
* Spatial: when I touch a piece of data might touch something right next to it
* Temporal: when I touch a piece of data might touch it again quickly (close in
  number of cycles / time)
* Last-In-First-Out (LIFO) nature of stack and the predictable access pattern
  -- we go down in addresses and pop back up -- lines up with CPU features like
  LRU caches and address predictors trying to prefetch things you're going to
  be pulling in
* Function's frame is usually in the cache in memory as "recently used"

## 00:23:54 Broader question: how does memory in a modern computer work at all?

* Talking to stick of DRAM there are values going over the wires, those are the
  physical addresses
* What the computer program sees is the notion of virtual addresses
* Virtual memory introduced originally so we could share the physical memory on
  a system more easily in shared environments
* Also offer facilities like protection, etc.
* Virtual memory really means "I have some address" -- modern system
  [userspace] has effectively 47 bit addresses -- that value is really an
  "alias" -- it that turns into a real physical location
* The alias is potentially unique to each program -- two different programs
  hypothetically could have different 47-bit values that the mapping could turn
  into the same physical location [ed: this property is the bane of virtually
  tagged caches]
* Each one of these memory access instructions like a load or store needs to
  translate 47 bit virtual address into a corresponding physical address
* You very likely have less than 47 bits of memory in your system (128PiB!) --
  maybe you only have 4GiB (32b) of physical memory
* Can pretend the physical space is larger and do tricks like page things out
  to disk, take things that would be backed by physical memory and store them
  on disk: magic possibilities of the virtual memory subsystem!

## 00:25:55 TLB Hit!

* Each one of these accesses where I take a virtual address and turn it into a
  physical address 
* Can be expensive because OS has to maintain/walk a big table of how that
  translation happens
* But there's a translation cache in the hardware called a TLB (Translation
  Lookaside Buffer)
* Because the stack is accessed so frequently and is small in terms of number
  of pages, and pages are frequently used -- each stack access will usually hit
  inside of this translation cache
* TLB hit! As opposed to a miss
* Caches are smort
* Should do an episode that talks about virtual memory subsystems in more
  detail!
* Stack is LRU-cache amenable structure, and other benefits to it as well
* Long winded way of describing how we ultimately arrive at TLB hits

## 00:27:00 Store-to-load forwarding of stack values

* Other advantages to stack too -- registers are really fast, caches are fast,
  and go to main memory tier at some point
* Modern CPUs have store-to-load forwarding -- "cache" that forwards values
  from recent stores to loads without having to ask the cache
* Store to load forwarding effectively an "L0" cache -- stack can often hit in
  there -- many stack accesses can hit in this, acting as an L0 cache
* [ed: alignment is another important property for being able to hit in the
  store to load forwarding pipeline!]

## 00:27:57 Multiprocessing teaser!

* Let's say I'm a CPU in a multi-core die and I do a store, and I do
  store-to-load forwarding, but some other processor stored to the same
  location -- shouldn't I have seen the store that the other processor did?
* "Stuck" in "L0 cache" -- hasn't been written to cache yet -- will it snoop?
  Coherency is working at the cache level.
* How does it work, how can you think about it. Memory models! Once you're in
  multiprocessing world store-to-load forwarding can be even more interesting
  than a common optimization.
* What properties do you want from your system? Are these single thread
  improvements "great until they're not?!"

## 00:29:00 Sparsity of stack slot usage

* Each stage is contiguous
* How a function uses the stack can be super sparse!
* Compiler allocates a slot for each named value in your program
* "Coloring" problem -- some parts of the function might have disjoint use of
  slots
* Similar to register allocation -- set of resources is stack memory
* Figures out which ones are mutually exclusion like register allocation
* In if/else blocks there's mutual exclusion -- even if you reuse slots in that
  way you end up with parts of the stack that are unused
* You could split paths? But probably a lot more overhead for the compiler to
  track the paths / stack implications and know how to roll them back
* Do compilers ever split to optimize stack behavior? 
* Compiler will do partial outlining to make cold code less intrusive, force
  any required spilling on that cold path -- maybe that reduces required stack
  space to some degree?
* Probably they need to unify their understanding of the stack at any given
  program point

## 00:31:50 Where does the stack go?

* Do addresses grow up or grow down?
* If A calls B is A's frame addresses bigger than B's frame addresses?
* These days it's usually down: earlier in the call stack has higher address
  for its frame than its callees
* Architecture like ARM is both bi-endian and bi-directional in its stack
  growth
* Nothing to do with the abstract notion of push/pop.
* Direction is interesting in general -- x86 has a direction register bit!
* Changes the direction the addresses iterate for REP (repeat) instructions.
* There are these various convention(s) we adhere to based on ABI.
* Different implementations do different things when they implement the ABI.

## 00:33:07 Seemingly arbitrary choices in computer systems

* Always fun to see these -- little vs big endian, address map with 0 at top or
  bottom?
* Endianness from Gulliver's Travels: Lilliputians crack and egg on one side or
  the other (big or little side) that led to holy war.
* We have a "war" over whether the low bytes of a multi byte word go at the low
  memory or high memory [byte] address, we similarly fight these wars over
  interesting small issues [ed: tabs vs spaces, anybody?].
* If you only had the ability to access a word, you wouldn't know what the
  endianness of a machine is! If you can't observe the byte storage. Would need
  to fix alignment as well -- or only have word addresses. Word.

## 00:35:05 Unwinding

* Let's say you want to grab a backtrace from your program because it crashed
  or there's a bug or want to know where it is for diagnostic purposes, or in
  C++ you throw an exception and need to unwind it, any exception guards to
  trigger? etc
* Even just programming normal C you might want to capture a backtrace to emit
  a good message on segfault or something, send crash diagnostics back to home
  base in the case of browsers or something
* [ed: or sampling profiling!]
* Conceptually just want to walk the linked-list-like structure described earlier
* Frame pointer to find older frame, look next to it to find the return address
* Linkage between frames and code that caused the frame to be on the stack (via
  return address)
* Lots of cool libraries people have developed to do this: libunwind,
  libunwind-llvm, libunwind-gcc, crash reporting libraries that wrap up
  unwinding facilities e.g. breakpad -- what code was executing when something
  bad like a crash happened?
* Ability to walk stack structure and ask questions about it is key!

## 00:36:40 Walking with frame pointer omission?

* If you think about a basic unwinder, all you have to do is walk the stack
  itself -- tiptoe through the linked list.
* But what if you elided frame pointers.
* Side data structure that tells you how to determine the frame size for each
  function.
* Compiler knows what it is, so can emit "side data" in the program.
* Unwinder needs to look at current program counter -- for callers that gets
  pushed onto the stack (for the call), callee pops it into the program counter
  to go back to where it was
* Program counter can be used to look up the frame size data
* Read only information that the compiler generates keyed off of program counter
* Less info to carry on the stack, and only need to look up those side data
  structures if you're trying to do unwinding
* Goes into binary section like DWARF info if you're using ELF binaries, or
  PCOFF or what have you on Windows
* If you're doing unwinding have to call RAII destructors or finally blocks in
  languages like Java
* In other cases may want to do setjmp/longjmp with landing pads -- Win32 did
  that on x86 to implement exception handling
* As you unwind the stack you somehow have to figure out where your landing
  pads are because those have the code that do the cleanup
* For exceptions you have to run code: destructors, catch blocks, etc
* Unwind one, look up landing pad, do some work, look up the next landing pad
* If you have an exception that happens during the "work", have to deal with
  that
* On Windows it mixes Structured Exception Handling (SEH) with C++
* If you have faults or divide by zero floating point you can handle it with
  SEH
* In Windows C++ code you can catch unrelated exceptions from SEH which can be
  surprising
* So with SEH you can write a trap handler in a C program -- might use signals
  for in other environments like POSIX

## 00:40:35 What are setjmp/longjmp?

* Way to save the current state of registers and where you are on the stack and
  such
* setjmp buffer -- saves it, longjmp you give the buffer and it puts the state
  back the way it was before
* setjmp is a function that can return "twice" (a la `clone()`) -- first time
  it saves the state, when you longjmp back it tells you that the state has
  been restored -- a function that can return twice!
* Local state inside of the CPU, sometimes called a microcontext? Registers in
  it and such to restore to make the local processor state look the way it was
* Heap can't go back, but local processor state can go back to where it was
* Similar to what we do when we enter kernel space in a way, stash a bunch of
  state away so the kernel can start doing its thing, then you can resume
* Abstract notion of continuations we may have to talk about at some future point

## 00:41:53 Variable sized stack entities!

* We've been talking about frames being of a set size, but there are these
  functions in C and (kind of) C++, called `alloca`, and you also have variable
  length arrays (VLAs)
* N bytes is the size, and declare it goes on the stack
* Interesting topics: how are they optimized, what's their behavior when it's
  dynamic, and such!
* If you look at standard C++ there's no variable length arrays, common
  extension to support C VLAs in C++ but not officially a thing that exists
* Neat to be able to change the size of the stack frame at runtime
* Small stack buffer optimizations using alloca; e.g. "only up to 256 bytes of
  stuff, otherwise I'll heap allocate"
* alloca is kind of an extension to the language in a way
* alloca/malloc and then corresponding nothing/free before it exits the scope
* alloca(0) technically undefined behavior, as is VLAs of 0
* Can try to optimized based off of that undefined behavior, but it breaks
  things!
* What about VLA of negative value? Can't un-grow the stack!
* Alloca/VLAs don't fail!
* Is it pronounced alloca or "alloh-ka"? We're not sure, but we do know JF is
  French-Canadian. Alloc, eh?
* Returns a pointer to the stack location, can it return null? Would have to be
  slower if it nominally could fail.
* Part of language or OpenGroup POSIX standard? C Programming Language? We're
  not sure, maybe part of POSIX.
* Within LLVM everything is represented as alloca and creates stack out of
  consolidated allocas, and put things into registers that it can.

## 00:45:31 Stack buffer overruns

* We put lots of things on the stack, we see some are variable sized
* Sometimes we put fixed size array on the stack and *think* we're writing into
  the right way
* But O.G. buffer overrun exploit was to overrun an array that somebody put on
  a stack, then attacker gets you to clobber the return address -- write an
  address into there, and maybe jump to the data I had written if the stack
  were executable. Nowadays the stack is never executable.
* Pages in virtual memory have an "execute" bit on them that says whether you
  can fetch instructions into the CPU out of that virtual memory location.
* Fairly new? CPUs 20 years ago couldn't do that
* Fascinating all the security/mitigations added recently in computer history.
* Originally learned about the buffer overrun exploit in school, and nominally
  not possible to happen anymore, especially because compilers had facilities
  for inserting protector guards and things
* Exploit shows how everything mixes together in the stack: instruction
  pointers, data you want to home there.
* In a memory unsafe environment an attacker can potentially take advantage of
  the fact that these all mix together, things like virtual table pointers and
  such may be in there.
* Lots of extra technologies came in later not just from CPU side but from
  compiler trying to protect stuff.
* Stack protector: when you create a large frame (say 8KiB stack array) --
  statically (when frame is constructed) or dynamically (as the code executes)
  will touch all the pages that the code might access. If you went to go access
  the end right away, might run afoul of the guard page (e.g. if it's a 4KiB
  single guard page).

## 00:48:56 What are guard pages?

* When the OS creates a thread it'll map a certain amount of stack
* It could do that lazily or eagerly
* Imagine it eagerly allocates 16KiB, can put a 4KiB "guard page" at the end,
  marked as not readable or writable
* Intent is as you naturally run out of stack you'll fault, more will be
  provided with physical backing, and execution will be resumed
* Have been exploits in the past where programs just "jump over" accessing the
  guard page and the exploit uses those accesses to do malicious things -- past
  that guard page is other memory, either another stack, or a heap, etc.
* Stack is just another part of the memory space!
* Struct offset can be any value -- can have 4GiB of data in an inline array!
* In the conventional sense where stack grows down and heap grows up, at some
  point they might meet! Could jump from one into the other... it's all just
  locations in memory.
* Or if you have multiple stacks maybe stack can collide with another stack.
* At the end of the day we have this big flat address space in an abstract
  sense on modern machines so jumping around inside you have to know the
  extents.
* Brings up topics like how segment registers have evolved on x86: future
  episode!

## 00:51:20 The Red Zone

* Speaking of x86 evolution! Sounds cool... *Red Zone*.
* Idea you can guarantee some space underneath your frame; e.g. 128B on x86-64,
* As leaf function, you know there's extra space that's guaranteed to be there,
  avoid accounting and clobber stuff relative to frame pointer without having
  to do accounting.
* Part of ABI that that extra space exists there.

## 00:52:00 Alignment!

* Usually you always try to have an aligned stack. Byte aligned stack is weird
  when most of the point is to spill registers and registers are 4B or 8B.
* When ARMv8 was being designed all stack specific instructions (manipulating,
  aligning) had to fault if the stack itself wasn't aligned properly
* Expected any stack manipulation spills at least *two* 64-bit registers --
  invariant: aligned to 16B all the time!
* Instructions not just specialized to the stack, also trying to find incorrect
  usage.
* More you know about how your system *should* be working, the easier it would
  be to detect if something is trying to be exploited or going off the rails
  potentially.
* Invariants about how system should be operating get stronger.
* Prevents people from doing
* super-creative-if-somewhat-dangerous-in-the-general-case stuff like "futurist
  programming" idea: self modifying code tight inner loops to get all the
  efficiency of a modern machine.
* Just to say: some things can become more difficult as we start make this
  general process around how things are supposed to work.

## 00:53:45 Processes vs performance

* Establishing processes and conventions for "how a machine is used" vs
  performance
* Classic considerations around what registers are saved by caller vs those
  saved by the callee, can have a big impact on performance
* On architectures that by convention had purposes on different machines could
  make these considerations even more interesting; mul using ecx, rep using edi
* Questions of "what do we save away when switching from userspace to
  kernelspace" -- some set of resources that's not too small but also not
  overly large
* Kernel threads having full separate stack once they leave interrupts to go to
  full kernel thread
* Big space of conventions around performance and the stack that's always
  fascinating

## 00:55:45 Managed Virtual Machines: WebAssembly

* In WebAssembly all the code is totally separate from the data
* WebAssembly meant to be secure VM that can run inside of the browser
* Most C/C++ programs use von Neumann machine model where data and code are
  mixed together
* WebAssembly follows Harvard architecture (code and data are kept separate)
* Writing C/C++/Rust program in WebAssembly you don't know where any of the
  code is in an absolute sense
* WebAssembly really has two stacks!
* Call stack with internal state having function pointers etc.
* Whatever state needs to be reified in your web assembly program; e.g. taking
  address of variable, needs to see the values
* Separate stack in the WebAssembly memory space separate from the call stack
* If WebAssembly is running in a web browser it's interleaved with JS
* Within WebAssembly memory there's a separate stack for your program's
  execution -- part of the ABI
* Extra neat: if you look at the virtual ISA it doesn't have a finite set of
  registers!
* Functions can have infinite registers, can return infinite set of values
* "Virtual register" and "variadic return value arity"
* Functions have fixed number of inputs
* How does it do `printf`/`va_lists`?
* Compiler creates a stack in user accessible memory (the WebAssembly stack)
  you spill to
* `printf` routine can access those stack spills into WebAssembly memory

## 00:58:48 Whole stack'o browser stacks

* In full browser, there's native stack, JavaScript stack which JIT can unify
  with the native stack, also WebAssembly stack -- WebAssembly is also being
  JIT compiled and potentially pushing things onto the native stack again!
* Whole ecosystem of things all have interesting and potential unifying
  treatment of the general notion of stacks
* Like the glue that binds program execution together, in a way!
* Super integral to how we think about how machines are going to work today

## 00:59:30 Managed VM's rich stack choices

* In managed VMs you can potentially put more invariants on the program being
  executed (you are managing what the language is doing)
* CLR/.NET you have a typed stack [every slot has a known fixed type]
* Projects like Pydgin mapped Python onto the typed stack, but CPython
  has both data and control stack per frame, so figuring out how to mux Python
  execution onto the CLR notion of stackiness in this managed world creates all
  these interesting ideas/interactions
* Around what a stack should be, how it should operate, what invariants we know
  about it; e.g. whether the type of a given slot is always the same, or is it
  a big bag of bytes
* With typed arrays; are the typed arrays words or are they bytes, etc. Lots of
  variations on how we might think about them.

## 01:00:40 What happens at the end of the stack?

* In C++ when you stack overflow it's not defined where stack end is or what
  happens when you run out of stack
* Realistically what happens is you'll trap because of guard page in most
  implementations
* In JavaScript not defined *when* you stack overflow
* Defined that *if* you stack overflow it a JavaScript exception is thrown, and
  you can catch it!
* Neat as a programmer, though it is kind of hard to handle
* As a VM implementer it's kind of painful -- when you JIT code you're careful
  about the JIT-ed code not running out of stack similar to stack protector
* But runtime functions that are supposed to *support* the JIT use stack space,
  and could violate the stack extent!
* Now need to throw into the JavaScript code from a out-of-stack condition
  inside native code
* Can be a source of bugs in JS VMs -- JS fuzzers can do a cute "recurse, call
  helper, unrecurse, call helper" to mess with VM to fuzz those runtime
  functions interacting with stack overflow
* Working on JS engine in FireFox you turn on the fuzzer when some feature is
  ready and you get the deluge of interesting things that are corner cases in
  the universe
* Really good fuzzers out there for JavaScript: resulting code is evil, but
  great stuff, that's what you want
* Reducers are also the stars of the show -- getting the crisp short program
  that shows some key problem is always amazing to see

## 01:03:48 Stack limit!

* More things we haven't talked about: rotating register windows, return
  predictors
* [ed: ROP gadgets!]
* Infinite stuff to talk about: unlike the stack!
* Write to us on Twitter for feedback!

## Terminology Glossary

* VM / Virtual Machine: an overloaded term; however, most of the time that we
  use it in the podcast we're referring to the notion that a managed language
  implementation runs on an abstract machine that be thought of as designed for
  that language in particular -- e.g. Python has a set of stack-based bytecodes
  and associated runtime support that conceptually implements the abstract Python
  virtual machine; similarly for the Java Virtual Machine and so on.
* JIT: Just-in-Time compiler -- these are often used for speeding up managed
  language environments by compiling managed programs to native code at runtime
* "Stackless": "Stackless Python, or Stackless, is a Python programming
  language interpreter, so named because it avoids depending on the C call
  stack for its own stack." -- [https://en.wikipedia.org/wiki/Stackless_Python]
* reify: to "make real", i.e. materialize somehow in the computer or program;
  antonym: erasure: erasing information from being present in the program that
  had been determined in some prior phase like compilation
* [translation
  unit](<https://en.wikipedia.org/wiki/Translation_unit_(programming)>): the
  input that is processed by a single compiler invocation (akin to a "module"
  concept in languages with modules), serves as a natural scope for compiler
  optimizations
