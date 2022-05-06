# Episode 4: `t-r-a-c-/e̅‾\-o-m-p-i-l-e`

<audio id="audioplayer" src="https://traffic.libsyn.com/secure/tlbhit/tlbhit4.mp3" controls="controls" class="podcast-audio" preload="auto"></audio><div class="playback-rate-controls"><ul><li><a href="#" onclick="setPlaybackSpeed(0.5)">0.5⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1)">1⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.25)">1.25⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.5)">1.5⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.75)">1.75⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(2)">2⨉</a></li></ul></div>

## Intro [00:00]

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
* Many folks we talk to understand static compilation pretty well but dynamic compilation can be a bit of a mystery
* Thought we'd dive into one approach for dynamic compilation called trace compilation, understand what that means

## Tracing a Brief History of Tracing [01:10]

* Long & amazing background in trace compilation
* Joseph Fischer and VLIW machines (Very Long Instruction Word)
* Idea: take a big control flow graph of operations, figure out how to schedule stuff within that horizontally, as big parallel words (full of instructions) that all execute at the same time
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

* Inherent tradeoff beneath the surface:
  * You can trace a JIT compile very quickly [without observing as much] and then correct yourself later,
  * Or you can wait longer to get more perfect information / more confidence in the information you've seen by observing the program for a longer period of time
  * Have to trade these two things off
* Interesting pipeline-like nature to tracing and JIT compilation
* If you can be super low overhead then you can compile very quickly on things like mobile devices
* Could make a "no stage compiler" where *as* the bytecodes are executing they are being "splatted out" as native machine code -- cool tradeoff point in the space
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

11:14

* Can also do thing like burn-in global properties; e.g. things that were static values / global state, can burn those into the trace, but then also need to mark the trace as invalid if those global values were changed at some point
  * Need to be able to say "I'm freezing this trace on the assumption global value `global_x` being equal to 42. Oh, somebody changed it to 43? Ok let me go note that trace is no longer valid."

11:40

* Lots of terms in dynamic compilation people might not be as familiar with
