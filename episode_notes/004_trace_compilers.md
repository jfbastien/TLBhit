# Episode 4: `t-r-a-c-/e̅ ̅\-o-m-p-i-l-e-r-s`

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
