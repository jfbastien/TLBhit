---
episode: 4
title: "t-r-a-c-/e̅‾\\-o-m-p-i-l-e"
guid: "27fba042-5bc0-44d7-b3a9-4af5bf9d42f2"
pubDate: "Fri, 06 May 2022 12:00:05 +0000"
duration: "00:37:48"
audio: "tlbhit4.mp3"
description: "Monitor. Compile. Bail. Repeat!"
explicit: false
---
# Episode 4: `t-r-a-c-/e̅‾\-o-m-p-i-l-e`


## Prologue [00:00]

* Haven't done an episode in a while, what's up with that
* We now call it season 2... to make it sound totally intentional... which it was...
* JF coming to us from Land of the Rising Sun
* Chris still can't pronounce words in foreign languages, that has not changed
* Standard disclaimer!
  * Only know so much...
  * We *try* not to say things that are wrong!
  * Follow up with errata / corrections / clarifications in the show notes.
  * We do the "lifelong learners" thing -- always trying to push the boundaries of things we know about and have conversations about what's interesting to develop & hone our understanding.
* Today we're talking about trace compilers and trace compilation
* Many folks we talk to understand static compilation pretty well but [dynamic compilation can be a bit of a mystery](https://www.youtube.com/watch?v=tWvaSkgVPpA)
* Thought we'd dive into one approach for dynamic compilation called trace compilation, understand what that means

## Tracing a Brief History of Tracing [01:10]

* Long & amazing background in trace compilation
* Joseph Fischer and VLIW machines (Very Long Instruction Word)
* Idea: take a big control flow graph of operations, figure out how to schedule stuff within that horizontally, as big parallel words (full of instructions) that all execute at the same time
  * [Ed: answering the question: what "trace" or "traces" through the control flow graph should we schedule into those big parallel instruction words?]
* Question was: how do you do that, and why do you approach it one particular way? What of this big control flow graph to you pick out to schedule horizontally, to happen at the same time?
* Idea was to take operations that would be sequentially but present them to the machine hardware at the same time so we could get parallelism, because we thought a lot of the performance we could obtain would come from Instruction Level Parallelism (especially at the time)
* Early academic systems started doing VLIW, e.g. the ELI-512 machine at Yale, famous thesis (at least "famous in compiler world") called the Bulldog Compiler thesis that had a lot of the ideas required for effective VLIW compilation in it
* Led to some commercial computers as well, Trace computer at a company called Multiflow, and there's actually a book on that, and it's a pretty decent book -- always cool to have accounts of real-world-built computer systems
* Optimality of scheduling operations in the control flow graph had relation to optimality as in "Operations Research" optimality and things like job shop scheduling
* Brings up classic topic of: how do we do optimal scheduling, optimal register allocation, what's the right phase order to pick to do them in, or the holy grail of "can we do both of those simultaneously" which has been a source of an unbounded number of PhD theses over time
* Talking about job shop scheduling, even the concept of Just-In-Time was a concept made in manufacturing by Toyota, borrowed by the compiler space -- small world phenomenon as JF works at Toyota!

## Dynamic Binary Translators and Binary Instrumentation [03:10]

* We're talking about early history of trace compilation there, but eventually lots of concepts were shared between something called Dynamic Binary Translation (DBT) and trace compilation
* DBT was affected through things like Dynamo (2000) / DynamoRio (2002)
* Trace compilation also later used more for dynamic language virtual machines (VMs)
  * Franz/Gal tracing used in TraceMonkey JavaScript VM in early Firefox
  * LuaJIT another popularly used trace JIT today
  * PyPy tracing the metal level, lots of interesting things there
* Can compare and contrast to static instrumentation, Pin for x86 and ATOM for Alpha (1994), perhaps the OG binary instrumentation
  * Worked on by Alan Eustace, worked at Google, jumped from space (2014)
  * Ergo, you work on compilers maybe you can jump from space after 20 years
* Also ties back to something we had touched on previously, caching of micro-operation tracelets in the Pentium 4 microarchitecture

## Dynamic Compilation vs Static Approach [04:25]

* Dynamic compared to static: want to try to discover information
* "How do you find things out about a program" we've talked about in previous episodes
* In static compilation you look at the code and say, "well, X is probably
  generally true, so I'm going to favor it", but there's a fallback path (to
  handle ~X)
* It's pretty rare in static compilation to do speculative optimizations at a large scale
* You have code that's always "correct" / ready to handle all the possible
  cases, never have to "undo" any mistakes you made
* You only really speculate on a few instructions [ed: that won't cause
  exceptions!] and then use something like a conditional move
* With more dynamic approaches -- like "trace monitoring" -- it's a way to dynamically figure out what the real code is doing while executing
* Instead of looking statically and saying "I *think* the code is going to do
  X, but this integer could hold a ton of different values", you can look at
  the values that are actually held and figure out "this is what the code is
  doing when it's really executing"

## Workloads and Phasic Behavior [05:20]

* What's interesting is when you do that dynamically is it's very workload
  dependent -- dynamically you only measure what you
  actually see -- that can lead to sub-optimal choices if you make them
  "forever" -- record once, take it to the bank and lock in your observations
  "forever"
* If your program has phases, where it does some kind of behavior for a
  while, and then shifts to another behavior afterwards, then that workload
  that you originally measured isn't representative anymore!
* We can do a comparison of this kind of dynamic tracing / recording of information to Profile Guided Optimization (PGO) that folks use in static compilation approaches.
* When you do PGO you're supposed to do it on the entire program and it's supposed to be representative, whereas when you're tracing you're doing that live! So how do you know when you're tracing that *what you've recorded* is representative?

## Quick vs Confident [06:15]

* Inherent trade-off beneath the surface:
  * You can trace a JIT compile very quickly [without observing as much] and then correct yourself later,
  * Or you can wait longer to get more perfect information / more confidence in the information you've seen by observing the program for a longer period of time
  * Have to trade these two things off
* Interesting pipeline-like nature to tracing and JIT compilation
* If you can be super low overhead then you can compile very quickly on things like mobile devices
* Could make a "no stage compiler" where *as* the bytecodes are executing they are being "splatted out" as native machine code -- cool trade-off point in the space

## Pop-Up Ideas In Specialization/Speculation [07:00]

* Pop-up ideas:
  * How hard are we going to try to specialize for things that we saw
  * What do we choose to bet on "continuing to be true over time"
  * What does it cost for us to fall back and try something different when our speculation is off
  * Again, we're tuning that "speculation knob", how *aggressively* we're going to try to speculate, and *what* we choose to speculate on
* Concept here is "act on information you saw"
* You can do specialization and you can guard
* In a linear trace the number of assumptions you're making accumulates as you execute [towards the end of the trace you have the most assumptions built up]
* If you have an always-taken control flow, e.g. some virtual function call that's always calling the same actual function, a tracing compiler will treat all back-to-back branches as one set of straightline code
* Always-taken or always jumping to the same function, it's *like* straightline code when you execute it dynamically!
* What it's going to do dynamically is check *on* the trace whether that was a bad assumption
* It'll say: "Hey: I'm going to execute this all back to back, *and*, whenever convenient, I'm going to check whether any of those assumptions were wrong"
* On the "cold path" -- again, when it's convenient -- it'll undo all the inapplicable things if it turns out the branches weren't true
* Called a "bailout" ["bailing out" of the trace]
* What's interesting with a bailout is you're being surprised with "new information that you didnt expect"; e.g. something you didn't observe when you were tracing
* You trust that everything you've trace is going to happen, it's all going to well, and you're going to be able to optimize for it
* But then at runtime, when convenient, you're going to *check*, and then bail if you were wrong, and have the rollback on the cold path
* So the hot path, the one you're *pretty sure* is going to execute, is quite optimal
* That really captures the essence of what trace compilers are usually trying to go for!

## Implementation Angles [08:50]

* Interesting *implementation* angles to it as well
* One of the chool things about trace compilation: you can "bolt" a tracer into an existing interpreter!
* In a lot of language environments you'll *have* an interpreter that's executing "op at a time"
* You can then hook in a tracer which observes what the interpreter is doing and "make some machine code on the side" based on how the interpreter ran
* Also cool: you can implement just a *subset* of the operations [ed: you might call this property "compiler completeness" for your op set]
* Let's say you have some very common bytecode operations inside of your environment and some uncommon ones
* You could implement *only* the common ones and simply end your trace when you hit one that was not implemented, because it was uncommon
* You can build up this trace JIT-ing capability over time, because the system is built with this assumption you can bail out of the trace for whatever reason and go back to "interpreter land"
* Could imagine making a JIT that just:
  * Covered `MUL`s and `ADD`s and could make fused/composite `MUL/ADD` bytecode combos
  * Specialize that for one common type; e.g. if you have many types in your
    language, could support that just for integer types, or just for FP ops
    e.g. if it were numerical code, and then just bail if any other types showed up
    at runtime; i.e. if you're in a dynamic programming language
* To do this need in order to do this a way to record "what you assumed" and then your trace can say "oh no, I saw something I didn't assume", and then call back to the runtime for help, or go into interpreter mode
* What *trace invariants* do, is they say, when traces call to other traces; e.g. I recorded some set of ops A, and some set of other ops B, and I'm jumping from A to B, I need to make sure that the assumptions between those two things are lining up -- called trace fusion or building *bridges* between traces
  * Can do this if you know the *invariants* (i.e. "what must be true") on the exit from A and the entry to B are lining up / compatible with each other
* Important to know because traces can represent the state of the program very differently; e.g. if you had different optimization levels, say, may be holding things in different register/stack locations; maybe A is putting everything on the stack and B assumes things come in register form and eliding stack slots, then transitioning from A to B requires mapping A's stacky view of the program into B's register view
* Can also do thing like burn-in global properties; e.g. things that were static values / global state, can burn those into the trace, but then also need to mark the trace as invalid if those global values were changed at some point
  * Need to be able to say "I'm freezing this trace on the assumption global value `global_x` being equal to 42. Oh, somebody changed it to 43? Ok let me go note that trace is no longer valid."

## Tracing Through Some Terms [11:40]

* Lots of terms in dynamic compilation people might not be as familiar with
* Go through a collection of concepts in the space to try to give a picture of the whole elephant

## Concept: Method Inlining [11:55]

* Concept of "method inlining"
* In trace compiler you just execute *through* methods [to form a linear of trace of operations, e.g. back to a loop header]
* Go through operations... don't really care you've traversed to run within a new function/method or not
* Inlining kind of the natural path of compilation when doing trace compilation -- just linear execution where the jumps/calls/returns simply disappear
* This is one interest aspect of trace compilation, we do method inlining effectively "by construction"!

## Concept: Tail Duplication [11:55]

* Concept of "tail duplication"
* As you run through different execution paths, the longer that path is, the more potential avenues that you're forming
* Like a road, and all these avenues you take down that road as you dynamically execute things
* What you end up doing as you do that dynamic execution is you duplicate what's called "the tail";  i.e. the "end path" of each trace
* Imagine you're tracing through code, different traces will duplicate that tail, you'll have multiple copies of it between all these linear traces
* One clear example is if you have a conditional, and then a common return path, you would form one trace for one side and another trace for the other side of that condition, but they share the return path, so it's duplicated in both, and that's called tail duplication

  ```
  for (...) {
    if (OP_EQ(x, 42)) {
      OP_GETATTR $f00;
    } else {
      OP_GETATTR $bar;
    }
    OP_T;
    OP_A;
    OP_I;
    OP_L;
  }
  ```
  
  ```
  trace 0: OP_EQ; guard--true: OP_GETATTR $f00;  OP_T; OP_A; OP_I; OP_L
  trace 1:            \-false:  OP_GETATTR $bar; OP_T; OP_A; OP_I; OP_L
                                                 ^--------------------^--- tail duplicated ops
  ```

* **13:00** What's interesting with tail duplication is it can be *good*, includes the "provenance" as a source of optimization; e.g. common path may execute differently based on where you came from
* But at the same time, what it does, is you are *duplicating* the code, potentially exponentially when you do that
* Can cause an exponential explosion in trace compilation: conditions can stack up causing a quick $2^N$ stacking, which is kind of a problem, so you have to find a balance

[ed: Perhaps in summary, you can think about tail deuplication as de-aliasing control possibilities (via duplication) so you could potentially specialize for their differences aggressively along a particular linear path]

## Region Formation / Spectrum of "Avoiding Strict Linearity" [13:30]

* A lot of what we're discussing here is what happens when you strictly linearly follow where the interpreter goes
* Interpreter executes at a Program Counter (PC), then it executes at the next PC, when you do a call you're kind of changing from one function's PC to the next function's PC
* This is within a spectrum of techniques we think of as "region forming"
* A linear region is one particular region you can form where it marches through the program order with one sequence of executed program counter values
* So that's trace formation: linear marching through the program
* More *generally* we refer to "region formation": can say, "hey I see a conditional in the source, I could go down both sides of the conditional abstractly... can I compile for both possibilities at once?"
* Then there's *method JIT-ing*: you take a whole method/function and say "there's a bunch of different paths I can go down in this method, can I compile for this whole method at the same time?"
* So really in a sense you chop out pieces of a method to get a region, and chop down to one sequence of operations to get a linear trace
* You can see how this is a spectrum of chopping things out from the original source programming in a sense
* Or maybe "inlining *plus* chopping things out", because tracing e.g. can jump between different functions and inline them all into one trace
* **14:45** So if two traces can join back together, say one trace can jump into [the middle of] another done in its linear sequence, that would form a region instead of a linear trace
* A trace is straightline, if they join together at some point, we'd consider that to be the more general "region formation" instead

  Using the above example -- note the join point in both tracelet 1 and tracelet
  2 jumping to "tracelet 3". [Note: a linear trace monitoring would never
  construct this, we'd need to monitor multiple control flow executions and
  decide to compile them together, or have static analysis that detected the
  condition was present then create facilities that can compile with a known
  join.]
  
  ```
  region:
   tracelet 0: OP_EQ; JMPIF trace1 or trace2
   tracelet 1:                               OP_GETATTR $f00; jump tracelet3
   tracelet 2:                               OP_GETATTR $f00; jump tracelet3
   tracelet 3:                                                               OP_T; OP_A; OP_I; OP_L
  ```

* **15:00** If you JIT'd only at method boundaries, you'd have a "method JIT"
* That's term of art what we'd call something that takes a method, maybe the
  methods it calls to / inlines them, but that "whole method" is a trivially
  (maximal) defined kind of region
* For the *hybrid* approach you could imagine forming a trace, observing what
  the interpreter did, forming a little line, and then trying to form the
  various lines of execution you observed together (e.g. with "join points"),
  and chopping out the paths we didn't actually take from the method
* So a conditional that was never executed one way after N times we had observed it, we can treat the other side of the conditional as dead code
* This is the way to think about the spectrum of "region formation"
* **15:40** Also a notion of packing as much known-hot code together, which can be more challenging when discovering things on the fly
* Like mentioned with tail duplication, generating potentially lots of new code with tail duplication
* We may have touched on systems like BOLT in the past, that are trying to pack together code into the closest regions they can for locality in instruction memory and having them be prefetchable so you get instruction cache TLB hits (!)
* But at the end of the day if we have to spread all this code out because we're discovering it on the fly, it can be a penalty for our instruction cache locality
* [Ed: but also note if you have hot trace bridges you can re-form the frequently
  taken trace paths into a new macro-trace that has locality, it just takes
  sophistication to recognize that and effectively trigger recompilation at an
  effective time vs eagerly bridging pieces of trace together as they're
  discovered.]
* **16:15** Idea of tracing through something like a switch statement, taking only 1/N of the paths in that switch, can become pretty rough when you have a pretty large N
* E.g. if you had a big switch like an interpreter itself, interpreter switch tends to have a lot of opcodes, can be rough to trace through 1/N

## When Do We Trigger Compilation? [16:35]

* Important concept related to trace formation is *when* do you trigger compilation?
* Talking about "JIT quickly" vs "record for a long time and then JIT" -- when to trigger is really important
* Different papers have policies on what they found to make a lot of sense
* Honestly ends up very workload dependent when you should actually compile
* If doing DBT machines a la Transmeta finding a universal solution is not obvious
* But might be a different solution from a JIT for a very specific workload and can find optimal parameters for your workload
* Imagine you have a *generic* machine that does trace compilation -- supposed to run *everything*!
  * So really comes down to what the "everything" is -- what does the user actually do with the machine
* Touched on it in the past: dynamic binary translation is a very difficult
  problem because you're pretending to be a particular architecture or kind of
  machine, and have to generate new assembly, and need to do that very quickly
  if you want kind of "machine level" repsonsiveness; maybe where it gets most
  tricky vs something like Java virtual machine or language-level virtual
  machine where there's some assumption latency might be incurred for JIT
  facilities
* Story from ex-Transmeta people: "when" trigger had to be pretty early for
  them because they didn't know for example when they were JIT'ing the mouse
  driver code, and if they didn't JIT it fast enough then the mouse wasn't
  responsive on the screen, could be kind of janky -- so had to JIT pretty
  quickly, and meant they couldn't optimize all that much [ed: at least in the
  "quick" tiers"]

## How Do We Gather Information/Observations? [18:35]

* How do we gather type and control information?
* Some system: instead of compiled code JIT'd directly [a la splat / baseline
  JIT], and re-JIT it over time, might start with something like an interpreter
* If you're not sure -- you want to start executing but don't want to JIT
  everything, you can interpret values coming in and then start tracing through
  that
* Can imagine e.g. if your operations are super generic -- getting a property in Python for example, can visit a ton of different objects and do a ton of different things, so in order to specialize it you probably want to see what it does the first time, and once you have confidence then you might JIT for it
* This is a concept called monitoring -- we "look at" what happens when we're in interpreter mode
* So we go into "monitoring mode" where we start recording things that happened into a side buffer
* Or you *can* JIT on the fly... but if you want to make sure that when you JIT compile something into native code that you did something that will be reusable over time [ed: "amortizes"] you would wait longer as we've been discussing
* Monitoring mode slows you down a lot because you're recording stuff into a side buffer
* But recording this info so you can make better choices and get return on your investment of writing this stuff down
* Also the idea of type-based stubs, so e.g. in dynamic language you don't know necessarily what the types of object are, so stubs are things that can record the type that was seen; e.g. inline inside the bytecode or "on the side" [ed: inline cache] as part of the baseline JIT compiled code
* Nothing stops you from having on-disk info about what happened in previous executions that you could mix with your new runtime observations, but often in practice we just expect the JIT will discover that stuff over time -- we just kind of toss it all away, load the program back up and have the interpreter re-derive it from scratch

[Ed: we didn't talk about a) monomorphism which is a nice property that types
observed one time in dynamic language code are often the one type you'll ever
observe, or b) the related idea of "free" monitoring mode side buffer
capabilities that come e.g.  with last branch record tables and similar in CPU
architectures.]

## Call Threaded Interpreters [20:30]

* Also concept of choosing how aggressively to specialize traces for the *values* we observed
* What we could do is just make little blobs of assembly
* Then we could spit out function pointers [in an array] that call to these blobs of assembly all in a row
* This is called a "call threaded interpreter"
* You build up these "ops" as function pointers, and they have some convention for passing stuff to each other in registers, and then you call them in a big sequence
* What's neat is you don't necessarily even need to generate native code at all, you could just put a bunch of function pointers into a big array and then call them in sequence so that they can communicate to each other
* But then you need to form the calling convention for how these pass data to each other
* Can form the "op set I'd like to have" offline based on how you see things being used [e.g. if you see a lot of MUL-then-ADD you could make a composite MUL-ADD op as a function call and make that into a single function call in the call-threaded bytecode sequence, this composite opcode creation is also known as macro-op fusion]

  ```c++
  void OpDup(Value* stack, uint32_t* stack_size, Value* retval);
  void OpPop(Value* stack, uint32_t* stack_size, Value* retval);
  void OpMulAdd(Value* stack, uint32_t stack_size, Value* retval);  // op we "macro op fused"
  void OpReturn(Value* stack, uint32_t* stack_size, Value* retval);
  
  using CallThreadedOp = void(*)(Value*, uint32_t*, Value*);
  
  CallThreadedOp kMyProgram[4] = {&OpDup, &OpMulAdd, &OpPop, &OpReturn};
  
  Value Interp(CallThreadedOp[] ops, size_t n) {
    Value stack[128];
    Value retval;
    uint32_t stack_size;
    for (size_t pc = 0; pc < n; ++i) {
      ops[i](&stack, &stack_size, &retval);
    }
    return retval;
  }
  ```

## How Aggressively To Specialize Traces For Observations [21:15]

* Other fundamental questions like: "hey I saw the integer 4 when I was monitoring, I saw it maybe 3 times now... do I want to assume that that value is always gonna be 4, or is it just an integer that *happened* to be the number 4 these past three times"
* Kind of simple to think about if it's a parameter -- you can think about, "do I want to specialize for this particular value for the function parameter I saw" or how many times does it need to be before I'm convinced that the parameter is actually effectively a constant
* Can seem like a far-fetched thing -- why would I want to assume that an integer that can hold 32 bits of value would always be 4?!
* Imagine you're tracing an interpreter -- that's the running program (being traced) -- kind of inception here...
* Some dynamic language like Python that you're running inside of trace compilation [e.g. CPython running on a DBT machine]
* You might notice 4 is a really important bytecode number
* That happens pretty often when you look at actual programs, where sure the integers can span any value, but many of them are just used to determine control or avenues that code is going to take
* So again: how many times do you want to see 4 before you believe that it's always going to be 4, what do you do there

## Splat JIT'ing [22:50]

* More interesting terminology you often hear is the term "splat JIT'ing", goes to what we were talking about earlier
* Bit like what QEMU does, QEMU being the "virtual machine emulator thing"
* Does JIT'ing basic block by basic block, i.e. no direct jumps taken in between
* Generates those block dynamically but kind of "splats" them out flat one after another
* As opposed to something that works harder to optimize bigger regions before code generation; e.g. trying to join multiple basic blocks together

## Tiers and JIT speed [23:20]

* Especially in JIT compiler environment where you have different "tiers" [levels of time spent JIT compiling aggressively]
* In splat JIT level you might measure "how many cycles does it take me to compile this many ops"
* Really want it to be as fast as possible so you're just blitting stuff into a buffer that you can use as your JIT compiled program
* This is avoiding the interpreter dispatch overhead
* If you have a big switch before every op you run and indirect branch overhead that's very unpredictable, that's going to cost you something
* Managing the protocol for passing things between these different bytecode operations
* These are the things that usually cost you that you want to avoid as early as possible because they'll definitely slow you down [ed: "standard interpreter overheads"]

### Chopping Traces [24:00]

* Another things you can do [re: compile time trade-offs] is chop bigger linear traces into smaller trace*lets*; e.g. tracing "just basic blocks" (which QEMU does)
* Means that you can revisit your assumptions made for the basic block and potentially pay a less-large cost because you are revising/recompiling a smaller amount of stuff
  * Only have a small handful of instructions I'm doing my compilation for, not that expensive to redo compilation for a handful of instructions
  * Going to chop my traces into smaller pieces so I can revisit my assumptions more quickly and easily

## Some Spooky Concepts [24:40]

* Trace compilers are very cool but also have some difficulties in their implementation
* Concept of re-entering the virtual machine when you're in a trace
* So you're executing your assembly code that's trace compiled
* But then you need to call to the runtime for help
* But *then* the runtime *itself* needs to compile some trace-compiled code
* Now have nesting/recursion between code that you compiled and then runtime to then code you compiled ad nauseum
* Then something goes wrong down way at the bottom -- in TraceMonkey I think they called these "deep bailouts"
* You have to figure out how to unwind through all those various layers and get back to a safe point where you know "this is the set of assumptions that's ok to pass back to the interpreter at this time" even though you went through different native code and runtime a bunch of times over [each of which could have changed things in difficult-to-generally-reason-about ways]
* Some of this is definitely some element of this which is complexity that's also present in method JITs, but I think tracers are even more interesting because they naturally may inline more method calls and burn in more assumptions over time, and so some of that is exposed to you in higher volume when you're building a trace compilation system
* Another spooky thing I remember is if you conceptually trace compiled tail-looking calls to loops w/ bailouts -- might need to create 1,000 stack frames if something went wrong in the 1,001th iteration, so reifying all those stack frames can be scary
* Also the fundamental aspect of, [if you use backedge targets as trace anchors,] when you start trace recording, you're assuming your trace will probably go back to a loop header [to complete it], and if it never does then you just get trace divergence where you run in monitoring mode for a really long time and never got return on investment of of the trace / recording that you made

## Those Who Do Not Remember History Are Doomed To... Uh... Something [26:50]

* When you record a bunch of decisions and they're invalidated -- so you don't overfit for those decisions again, you "learn a mistake"
  * You traced and either it never happened, or it keeps changing / has multiple modes
* You've learned something you don't want to do... but how long do you keep track of these mistakes, these things you "don't want to do", and how precise do you want to be as well?
* Tricky: if you have lots of possible mistakes you can make, you don't want to use lots of memory to keep track of them
* How long you keep track of them and how much memory you use to remember your mistakes are tricky aspects there [ed: and what mistakes you can / cannot even describe!]
* On e.g. DBT machine can use a single word to represent this information: "in this region of code these are the types of problems that occur"
  * e.g. lot of concurrency happening or a type of floating point math that's tricky to optimize; each bit represents a type of mistake / speculation to not make in that code generally
* Blow away the list of mistakes from time to time, because some programs have phases -- if you're tracing a whole guest machine of instructions, maybe the program is doing something completely different
* Just kind of periodically blow the information away
* Have to feel like you're going to be re-deriving it quickly enough that the mistakes are not going to be biting you if you actually throw that information away

## Long Tail Corpus / Flat Profiles [28:10]

* Relates to: some scariness in having long tail of workloads, e.g. corpus of the whole web for TraceMonkey as an example
* Kind of an assumption in trace compilers that maybe most of the time is spent in (relatively) inner loops
* Run into the tyrrany of flat profiles -- if things actually have flat profiles may not actually get to focus on key inner loops that have most of the time spent running in the program
* Have this question of: I start tracing after I see this loop do N backedges, i.e. N returns back to the top of the loop, what do you set that N value to be for the general world
* Lots of fun related to TraceMonkey and JaegerMonkey around what to set these kinds of heuristic values to for the broader web and for benchmark sets
* Also ties into things like inlining heuristics and things like this -- in compiler land we have some basic premises and some benchmarketing we have to do to make things look good on benchmarks, but hard to come up with a truly perfect set of numbers for things like inlining heuristics
* Dovetails with things like user expectations for performance properties -- if I'm a user I want to be able to understand what this compiler system did for me and why -- been my experience people find it's harder to debug, hard to have a mental model for what the underlying system will do and why, versus method JIT'ing where methods are maybe more-clearly outlined -- could be one of the biggest downsides relative to more traditional method JIT'ing approach
* In classic fashion when trace compilation works well it's like *magic*: it's specializing perfectly for your key inner loop and speeding up most of the program with minimal effort and minimal compilation time, kind of amazing

## Popping Back to Episode 0: On Stacks [30:00]

* Gotta revisit stacks just a little bit here
* Native stack running e.g. my C code
* Virtual machines will often keep a managed stack [i.e. the bytecodes push/pop from]
* Sometimes can smash the two together -- can keep track of your {Java,JavaScript,Python} machine stack values by keeping them on the native stack unifying the two [i.e. with frame links that are not pointing at heap objects, or eliding frames / reifying them lazily]

* Speaking of stacks, another aspect we can talk about called On Stack Replacement (OSR) -- likely a whole episode on its own, but idea of jumping into newly JIT'd code at a loop entry point *when an existing frame is already running* (i.e. "on the stack")
* Tracers are kind of saying "at this particular bytecode I'm going to start doing my bytecode execution which this chunk of code I made for the loop body", so with tracers OSR is less challenging than it is with method JIT compilation because tracers naturally have this OSR entry point formulation
* But then there's still also On Stack Invalidation (OSI) -- when you're down in a lower level frame and some JIT code just became invalid, e.g. because I made some assumption invalid like "it assumed the static value is 42 and it became 43", but then two stack frames above the newest stack frame I have some JIT code that assumes it's always 42 -- that remains difficult in trace compilation mode, even when tracing into inline calls, you have to create multiple stack frames and invalidate everything appropriately

## Notion of "Bolting the Tracer On" [31:42]

* We talked about the fact you can "bolt a tracer in" to an interpreter [ed: which is both a superpower but also can yield complexities in what it does to the modularity of your interpreter and monitoring]
* Can grab information from the guts of the interpreter that's not easy to re-derive statically, e.g. related to heap state queries at a particular bytecode execution time
* To support the various ways we wanted to instrument the interpreter we had ifdefs in the JS interpreter C++ translation unit, and IIRC it was used in three different ways, could be a bit hairy

## High Level Trade-offs Involved in Trace Compilation [32:15]

* Always wondering:
  * What's going to get compiled
  * What's causes JIT compilation to start monitoring / continue monitoring / finish
  * When do you trigger monitoring / compilation of bytecode execution -- after gathering a bunch of data but how much / how long
  * What do you retain long term if there's phasic program behaviors
  * What code / trace / information about mistakes you made do you retain across say a global garbage collection phase
  * How do you decide when compilation is going to pay off or be interest or be stable -- what's the backedge trip count
    * "I went back to this bytecode as part of this loop, how many times do I need to do that before I make a decision" and how that shows up in benchmarks
* Cross cutting: performance vs user expectations, we're always trying to balance those
* One thing we didn't mention at all in this whole dicussion is security and maintainability, which are huge issues when you talk about these types of programs -- want them to be very secure in most cases, and maintainability can be pretty tricky as you add new heuristics and learn new things about how you should optimize, it can get hard to maintain things if you're not careful
* [Ed: the vast scope of runtime statefulness of the system can be challenging for e.g. understanding the heap state that led to a JIT code formation / crash where you just have a stack dump from long after the heap state that formed the JIT code seen on the stack]
* Touched on the fact there's the spectrum from method JIT'ing with chopped out portions of the control graph to region formation to linear traces that go through multiple methods -- touched on each point in that spectrum
* Essential difference vs method JIT'ing: method focus vs straight line code focus, chopping unused paths to maximize early assumptions
* Resulting fact that, if things are stable and friendly to initial assumptions made then you can save a bunch of useless work / recompilation work, one of the classic tradeoffs in aggressive speculation

## Sample Tracing JITs [34:15]

* LuaJIT is really interesting, with a [great talk by Slava](https://www.youtube.com/watch?v=EaLboOUG9VQ) -- notion of code bases that are super small, really compact and elegant in a way -- but can be really difficult to ramp up, kind of have to be a super genius with a lot of hours to ramp on it because it doesn't have the traditional modularity you'd expect out of more enterprise scale codebases
  * We know cleverness can be a double edged sword but if you love to nerd out it's also hyper impressive and the resulting performance is often really nice as well
  * Remember some cool things like a custom ABI between the interpreter ops that minimzed the amount of register shuffling around required
  * Fun to note that interpreter loops are one of the examples where writing in hand crafted assembly can make sense because traditional register allocation can have a harder time ascribing meaning to registers when there's this giant soup of code and operations in a giant interpreter-loop switch
  * So there *are* cases where register allocation, despite being a modern marvel, there are places where we can still sometimes do better by hand
* Another cool thing to look into is PyPy and it's approach on "tracing the meta level"
  * Have an interpreter implementation language and it can be fairly directly lowered to lower-level primitives
  * But what's cool is being able to grab the representation of the program to form fragments of a broader trace
  * Can annotate in the implementation language what values indicate that backedges are being formed
* Holy grail in a sense -- objects you use to *build* your interpreter and the "guest" objects hosted *inside* your interpreter can be unified in their representation -- any implementation level objects are sharing unified GC infrastructure with the language implementation
* Always an underlying implementation question of "how do we get reuse between these different execution modes" -- e.g. between interpreter, maybe baseline JIT, maybe opt JIT -- conceptually all have similar semantics and a shared runtime model
* There's this notion you could have like a "copy paster" that took e.g. your C++ interpreter code and just turned it into a splatted-JIT mechanism [i.e. just cloning your C++ switch cases together in a sequence]
* In practice we use self-hosted builtins; e.g. for native primitives like `Array.indexOf` we might define in JavaScript even though by the spec it's a "native" primitive

## Meta-Circular Interpreters & Cool Trace JITs [36:50]

* Gets towards the concept of meta-circular interpreters -- cool systems I got to play with like Narcissus at Mozilla (JS implemented in JS), and cool things heard about like Maxene JVM (Java virtual machine implemented in Java)

* Hip Hop Virtual Machine tracelet based JIT machine doing aggressive specialization for things they really cared about in their PHP serving workload
* Goes back to discussion on basic block vs region formation vs method JIT'ing possibility
* Very rich and cool space out there!

## Epilogue [37:20]

* Glad we got to do another podcast again
* Hoping we don't take too long to record another one again
* Hopefully everybody likes this discussion on basics of trace compilation and tradeoffs involved there
* Would be interested to hear questions/comments/errata on Twitter, @TLBHit
