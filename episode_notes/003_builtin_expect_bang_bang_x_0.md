# Episode 3: `__builtin_expect(!!(x), 0)`

<audio id="audioplayer" src="https://traffic.libsyn.com/secure/tlbhit/tlbhit3.mp3" controls="controls" class="podcast-audio" preload="auto"></audio><div class="playback-rate-controls"><ul><li><a href="#" onclick="setPlaybackSpeed(0.5)">0.5⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1)">1⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.25)">1.25⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.5)">1.5⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.75)">1.75⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(2)">2⨉</a></li></ul></div>

## Intro [00:00]

* Been a while!
* Let's talk about `__builtin_expected(!!x, 0)`.
* Standard disclaimer!
	* Only know so much...
	* We *try* not to say things that are wrong!
	* Follow up with errata / corrections / clarifications in the show notes.
	* We do the "lifelong learners" thing -- always trying to push the boundaries of things we know about and have conversations about what's interesting to develop & hone our understanding.

## Programmers and Programs: What Do They Know? Do They Know Things? Let's Find Out! [00:30]

* *Broad theme*: first episode in a really broad series?!
* What is it we know statically?
* What's effectively discoverable only at runtime?
* How do we tell "the machine" (compiler and/or hardware):
	* Things we *know* to be true...
	* Things we *expect* to be true...
	* Things we *expect* to be true but *want to do something about* when it's not...
	* Things we have no idea about!
* How do we collect that information that we have no idea about?
* What happens if we're wrong? What if the workload is inherently irregular?
* In the limit, random noise could drive our control decisions!
* We talked a bit about precise vs imprecise exceptions before and automatic reordering, and we've mentioned vector machines and auto-vectorization.
	* All falls into the broader theme here, but we're always questioning what we can actually cover in an hour...
	* We'll try to give it a go for a subset of these things!
	* Time is often the limiting factor.

## Episode Title [01:30]

* The episode title is the thing that we often macro define as `#define UNLIKELY`
* In C/C++ code you might say "this control condition is unlikely", and say `if (UNLIKELY(condition))`
* In C++20 there was added these `[[likely]]` and `[[unlikely]]` annotations that do the same thing, but with more square brackets, so clearly better!

## What are annotations and where do they go? [02:00]

* Idea behind this is that we want to annotate our code and say what's likely and unlikely to happen [ed: in terms of control]
* But what does it even make sense to annotate?
* Syntactically in C++ with these new annotations *can* apply them in a few places -- but really we're trying to affect the assembly we get out of the compiler.
* But we probably want to bias things like the `test` instructions, or the conditional instructions, or something like that. But at the C++ code level you code doesn't look like those instructions you have in assembly.
* It's not really what your compiler IR looks like either [ed: it probably looks like a control flow graph of basic blocks with branches as the edges causing control transfer].
* Would it make sense to apply these annotations to `if`/`else`-`if`/`else` statements only, or would `switch` statements make sense too? [ed: you might think anything a branch profile that can be provided to the compiler might effect?]
* What if we were saving into an explicit bool variable, could we say "this is likely to be true"?
* Or maybe even temporary booleans, e.g. on expressions being passed to functions without saving it into an explicit variable.
* And really, what does it even mean in parallel execution -- say it's a SIMD boolean value (with multiple lanes worth of boolean data)? If you say it's likely, does it mean all of them are likely? Dunno!
* What C++ decided is the attributes can be applied to any non-declaration statement as well as labels.
* Interesting we go through this mental model exercise of translating C++ into C as if were the classic cfront compiler, or C into assembly, as if we were a naive/straightforward C compiler. What would these annotations turn into in the resulting assembly is what it comes back to.
* If you were writing assembly by hand, you might say "this is my common case condition how do I make that as fast as possible".
* Somehow trying to hint that attribute to the compiler as "hey this is what I'm going for, compiler".

## Probability Distribution [04:00]

* Really looking at what the likelihood is of something happening, and how often do we expect something to be true?
* Documentation if you look the `__builtin_expect` documentation in GCC it says the compiler is going to assume it's going to be like 90% accurate. Where did 90% come from? No idea, somebody pulled it out of... somewhere, and decided 90% is what it means.
* That means, in a loop, it'll affect the unrolling of the loop. Loop will assume say, one time out of 10, the loop will exit.
* But if you want to have more fine grained control, better granularity, can use some other intrinsic, such as `__builtin_expect_with_probability` -- takes the same parameters as `__builtin_expect` but also takes a double value in the range `[0.0,1.0]`. Finer grained control over how often something is true!
* Played with it in GCC, lets you pass in `-0.0` as well as `NaN` and other things, whereas Clang is really strict, kind of disappointing, maybe Clang doesn't like fun.
* At the end of the day the sanitation is trying to let you put a probability on the control transfer that wasn't available in the language syntax.

## Annotations and Semantics, Principle of Least Astonishment [05:00]

* Ties back into a broader question of, what do annotations even mean?
* Big question I always have about annotations is: what does it mean for your program *semantically*?
* If it's kind of "hints that the compiler is free to do something or not do anything about, it's free to discard them" that's how you end up with a `register` or `inline` keyword that in the modern era does basically nothing.
* Really trying to provide value to the user, but also trying to not violate the ["principle of least astonishment"](https://en.wikipedia.org/wiki/Principle_of_least_astonishment), which is always walking a bit of a tightrope.
* When the person upgrades their compiler and it doesn't consider something the same way it used to, maybe your annotations are discarded and you're hitting this performance cliff for upgrading your compiler. That violates the Principle of Least Astonishment we usually think about.
* To be robust in the face of what the annotations are telling you, you want to provide some way of reasoning about what must/should be the case when you put an annotation, and that goes back to semantics.
* At the end of the day goes back to "what mental framework can I use to reason about this annotation I'm putting" and that's how you can help solve for the Principle of Least Astonishment. If that framework exists, the programmer or user has a chance of thinking about it properly [ed: and robustly!].

## Performance Cliffs, Performance Portability [06:15]

* That mentions a bit the notion of performance cliffs.
* With scalar compilers (compilers for scalar C code like we're traditionally used to) the performance cliffs tend to be a little lower than if you had maybe an accelerator program.
* There's always this interesting question [ed: in compiler construction]. For the ML compiler I worked on where slowdowns could cost you several "x" in your computation, like 2x, 3x, or even more, you don't want to expose the *internals* too much because it slows down the progress/evolution of your compiler, but you also don't want to astonish the user by changing the way you think about these things in a way that would effectively discard their annotations.
* Lot of ways that annotations are used in compilers, things like auto-vectorization annotations that don't necessarily port equivalently between environments, or pragmas.
* Even cool compiler projects that have taken new approaches, like Halide made the physical-incarnation-of-the-functional-code a first class citizen called the schedule.
* Databases classically have these query planners which can talk about the mapping of their logical form into their physical form in terms of how they execute.
* Halide is a cool paper *and* it got productized, both Google and Adobe using a derivative of that, cool project used in a bunch of different things all over the place.
* Really great kernel generator for making these high performance kernels, trading off parallelization vs rematerialization there's always this tradeoff, [jrk has a really good presentation about the three-space of things it's trading off](https://www.youtube.com/watch?v=dnFccCGvT90#t=8m26s) that everybody should go watch.

## Is this AoP?! [08:00]

* In a way what we're tackling is kind of Aspect Oriented Programming (AoP), if folks have heard of that before. Challenge is "how do I refer to a piece of a program and describe its attributes in a way that composes, but also stays relevant in the face of refactoring". And that's super hard!
* The compiler is effectively a tool that's automatically refactoring and reworking things for you under the hood, but if I change my program, how do I know what has remained stable even if the face of refactoring and changes in my program.

## Data flow vs control flow, conditional move [08:30]

* So why do we even branch?
* Programs often have branches around stuff that "doesn't make sense to do" either because we're trying to be efficient, or the compute could cause an exception.
* Could imagine a world where no value computation causes exceptions.
* Sometimes you might want to compute two possible values eagerly and just select one of them, and that might be more effective than just branching around the ones you do want to pick.
* If you think about the assembly level, pretty much all ISAs have the idea of conditional selection. Instead of having branches in assembly you can have a "conditional select" instruction, x86 has `cmov`, ARMV8 has `csel`, and before that ARM could conditionalize pretty much every instruction that it had. Even in THUMB it had IT blocks where you could conditionalize up to four subsequent instructions after the IT block.
* Kind of an interesting way to, instead of having just branches, just saying "do this thing conditionally" or "select this thing" and move the results there.
* RISC-V doesn't have `cmov` so you have to branch around things, it creates small sequences of instructions where you have to branch around stuff all the time, interesting tradeoff there.
* They've worked on things like instruction fusion, so on the frontend you'll detect little sequences -- not sure the extent to which it'll detect things that are cmov looking sequences, would have to go back and look, but also an interesting question of "what peepholes can you do in the frontend that'll reconstruct these cmovs".

## Flags registers [10:10]

* Speaking of predication and conditional moves and stuff, flags registers are often used as funny ways to communicate properties from the data stream (the data operations that are going on) to the control side of the machine.
* You can compare the flags registers approach -- e.g. if you do a subtraction and the result is zero, then the zero flag will be set -- that's effectively a predicate within this bigger flags register you have access to -- vs actually having explicit predicate registers in your ISA, so that's an interesting contrast you see in computer architecture.
* Flags registers notoriously can create these weird dependencies because they alias together a bunch of properties, and they create this [implicit] sideband context that, as instructions execute in a thread, these flags are going in and out of individual instructions and they may or may not be used.
* At some point we'll need to do a "Fun with EFLAGS" episode just about all the fun and interesting things to do with flags registers.
* We can probably spend more than an hour talking about flags in general...

## Control on von Neumann style machines [11:10]

* Ties back to general theme of control on von Neumann style machines.
* You can imagine different machines to the ones we have today. Maybe you could make a pure dataflow machine.
* Not super familiar with the LISP machines people had created but they may be less von Neumann style?
* Von Neumann is characterized by the big backing store we're putting data back against (with frequent load/store instructions).
* As with everything there's this explore/expoit tradeoff and what we found over time as an industry discovered over time is that we could tune the heck out of imperative instructions executing little compute instructions against a register set, and doing loads/stores out of a (virtually) large backing store in a von Neumann style.
* Sometimes people talk about the idea of ["non Von" for non Von Neumann machines](https://scholar.google.com/scholar?cluster=865646003534538949&hl=en&as_sdt=0,5).
* But the kinds of machines we have you control what instruction stream feeds the processor by redirecting it around to start fetching from other places using these branching or jumping instructions.
* With an unconditional branch you say exactly where you go start fetching from.
* With a conditional branch you say "start fetching from this other place, but only if this thing is true".
* With indirect branch you say "fetch from this data dependent location that I placed in a register" -- this is very closely tying a full data value from the data stream into the control side of the machine.
* [ed: note the relation to Control Flow Integrity]
* In some ways the conditional and indirect branches are both cases of the data side of the computation feeding the control side.
* But important to note the machine has more knowledge of the possibilities when it has conditional branches, since there's only two possibilities of where it might go.
* Usually the jump amount in a conditional mount is relative to the current program counter, and the program counter is known to the machine so it's really just selecting between those two places for a conditional branch.

## To loops... to loops... to loops... [13:35]

* Takes us to loops -- classic notion is that most of your program's execution time is probably spent in loops somewhere; otherwise, what would your program really do?
* Back of the envelope wise: in 1ms can run a million instructions, ~4MiB binary. [ed: Straightline instructions run really quickly, must be looping if your binary is not gigantic.]
* Pays to think about what a loop actually is.
* Loops usually branch backwards.
* When you branch forwards you're usually doing that for conditional things.
* Branching backwards is probably what's called a "loop backedge". Negative delta so goes backwards in program memory when you do that.
* Loops have a "trip count" -- evaluating whether it extinguishes goes into the flags, e.g. comparing whether we counted down to zero.
* Imagine processing RGBA value in a loop, can predict taken for the backedge always, but if you do that, you'll mispredict 25% of the time, which is pretty bad!

## What's the point of the annotations? [15:00]

* Why would you go with likely/unlikely? What's the point of the annotations at all?
* Trying to bias the likely code so it's straightline and the branches are never taken.
* Reason is not to help the branch predictor at all -- some ISA had branch hints inside of the instructions themselves, like Itanium, but doesn't really matter so much these days.
* What we're really trying to do is tell the compiler to generate code that improves the execution; i.e. lay out the code so every instruction fetch will fetch cache lines that will be fully executed.
* So as you have branches, the likely-taken branches all follow each other in the straightline code, and you never take any of the unlikely [ed: "bailout"] branches. So when you fetch cache lines one after another you just "fall through" to the remainder of the code to execute.
* Other thing you may want to do is think about cold-code paths and out-of-line code.
* With likely/unlikely annotations is telling compiler "this [side of the branch] is unlikely to happen, so don't make it bigger, don't make it faster, just make it small, and if it happens, then I'll take the hit on the extra instructions/cycles that are required."
* You don't want the compiler to hoist a bunch of unlikely computation into likely code because that would increase the number of instructions you execute without actually increasing the useful work that's being performed by the CPU.

## Work efficiency [16:30]

* That feeds into the general notion of work efficiency.
* Even in CPU speculation, what we're trying to do is fill functional units with speculative instructions, but it also burns power to run them.
* Compiler is also reasoning about what to put on the "hot path", but it's just reasoning about it statically ahead of this execution time whereas the CPU is doing it at runtime.
* It could be useful, it could end up burning power and taking up lots of uarch slots in the datapath that could be used for useful computation.
* If you had an oracle it would tell you "you can speculate on this and it will definitely help you make forward progress", but we don't have oracles, those are the idealizations.
* What if I wanted to increase my Instructions Per Clock *without* getting more useful work done?
* Fun to figure out how to write "power viruses" for an ISA -- how do you max out the power consumption. To do something like that really have to write assembly to precisely control the machine.
* **Ultimately**, want to optimize code size differently for a real program if something is very unlikely. Imagine you were writing the assembly, again, you would put it on a cold path, you'd generate smaller code, you'd force extra spills to happen when you entered that path.
	* Keep the registers in place for the common case, and if the unlikely thing actually happened, spill a bunch of stuff to the stack and patch it up and make it look the way I want it to.
	* Let the straightline code in the common case have all the registers.
* Tradeoff here: "we're going to be grossing up code [with these annotations] and it could be wrong!"
* Sometimes you might hear in code review, if you were trying to write general purpose code that had a lot of these likely/unlikely annotations, that it might be premature optimization and you could actually be wrong about your annotation.
* Counterbalance is that you're grossing up code with things you *suspect* to be the case, but we all have limited insight/foresight. 
* *Ideally* we wouldn't need to say *anything* that would turn out to be wrong and we could just key off evidence we actually observe, instead of using our intuition.
* When you are wrong, you have to clean up the speculative things that you did; say, if you changed the state that wasn't committed to a register (at the CPU level more than at the compiler level).
* Say we were logging things as "verbose logging", and that only got activated when "verbose logging" mode was on. We could put into our standard logging functions/macros the likely/unlikely annotations.
	* In this case, it's unlikely I'm doing verbose logging in production.
* This helps the compiler know what slow paths are unlikely to be executed throughout the code base, and push those into cold code. 

## Profile Guided Optimizations [19:15]

* Trying to figure out, "hey I put these annotations, are they generally true or not"?
* At some point you think, shouldn't Profile Guided Optimizations (PGO) take care of all of this? Is it a magic wand that will solve for this?
* In theory yes, it can totally solve this issue, we wouldn't need to annotate anything [if we were always using PGO builds].
* Realistically, very few projects turn on PGO "correctly". Some might collect data *once* or *every few months*, and then use those data they've collected for years down the line.
* Just update it "every so often", use whatever previous data they had while the code changes and evolves. In this situation the data aren't really connected with what the new program does anymore.
* Others will collect PGO data on all the unit tests. The thing with unit tests is that they ought to test the odd / corner cases more than the common ones. So your unit tests might run faster, but you've conceptually optimized for the "wrong thing" -- most of your users aren't running your unit tests, they're not running into all the corner cases all the time.
* With *actually good* profiles, you wouldn't need these likely/unlikely annotations, would have to set up a really good pipeline to run representative samples of what it is that your program does to run PGO correctly.
* At the same time, you look at this and in programs where performance is a feature (not just something you sprinkle on at the end), it's actually good documentation to say "this is likely, this is not likely".
* But documentation is only *good* when you get it *right*.
* If you get it wrong it's not very good documentation.
* It'd be cool to have PGO tell us when our annotations were wrong.
* If we have these annotations inside of our code and really good PGO instrumentation, PGO could come in and tell us "here's what I figured out about your program and by the way, you were completely wrong over there", or "by the way, I never executed this branch you told me would be likely/unlikely".
* That's interesting because it can tell you that you don't have good PGO coverage.
* Not just "you're wrong with the coverage you provided me", but "you didn't even try to cover this".
* Cross checks what the programmer thinks is important and gets a reality check on it in the PGO suite for insight into the code.

## Cover Points [21:50]

* One really neat thing they do in hardware design is they have a notion of "cover points".
* Ahead of time you think of what scenarios are important to cover in terms of verification of the piece of hardware you're making.
* But also can have *performance oriented* cover points, where you describe conditions [e.g. as a boolean assertion-looking thing] that you definitely want to be collecting profiles for.
* Because you think they're important scenarios to see in your benchmarks and you think they really should happen when running your program.

## PGO Examples [22:20]

* Also remember Firefox got some good mileage out of its Profile Guided Optimization builds [in terms of benchmark performance].
* Another cool system called GWP (Google Wide Profiling) -- has a system called AutoFDO, with a really neat paper.
* Keeps a continuous pipeline going collecting information from applications that are running throughout Google and actually describes in the paper how performance drops off as a function of time using stale data.
* If you capture data for the symbols in a binary on a given day and you wait a couple of weeks later, the code is constantly changing and evolving, so the effectiveness of the data you collected drops off over time.
* Actually shows how effective it remains as a function of time.
* Extra neat because it's running on a live system and collecting data on a system that's being continuously changed as well. 

## "Exceptional Systems" [23:20]

* Another fun example is folks who say "I have to totally lie to the compiler when I use these annotations, because I have an 'exceptional system', I want to optimize for the *unlikely* thing, because that's the one that matters!"
* So they tell the compiler "this is likely" when actually that's the completely unlikely thing that never happens, but if it happens, they want the compiler to make it extremely fast. Things like High Frequency Trading or safety systems. Emergency brakes or firing missiles (after taking a nap).
* Interesting mind-bend in the way people approach stuff, the code that ought to never execute, if it does execute, it better execute really fast -- when it (unfortunately) has to execute.
* Interesting to think back to PGO, if we use PGO and we have tests that bias towards the unlikely thing that we want to make fast, maybe PGO would be a better *option* there.
* Speaking of HFT, it's only natural to talk about our options. [sensible chuckle]

## Simplest Possible Solutions [24:50]

* Also interesting to go back to the theme of: "what are the simplest possible solutions in the space here".
* Episode title is the "unlikely" annotation. Relatively simple solution compared to something involved like setting up an FDO pipeline or something like this.
* FDO is Feedback Directed Optimization.
* There's a spectrum of FDO, which goes from offline collection of profiles to Just-In-Time observation of your code.
* All lives in this "feedback directed" spectrum.
* Something on the spectrum which is "programmer has something in their head, so they type it into the program because they think it's the case".
* That's somewhere on there, it's the programmer's thinking/intent.
* We go back to, what if you have no branch predictor at all in your hardware, and you've got a conditional branch in your CPU frontend, what are the simplest things you can do?
* One thing is to foist it onto the C programmer.
* At the end of the day it's all about balance of probabilities.
* You could do simple things like "predict randomly which way the branch will go", and if you had a uniform distribution in the source program you'd have a 50% chance of getting it right, nice mental baseline for comparison.
* But pretty clear you can do even better than that.

## Hardware Isn't Instantaneous [26:20]

* What we're trying to get to when we talk about branches is that hardware isn't instantaneous. Instructions take a little while to execute.
* We have a branch and we don't know which way to go. CPU sees a branch and ask "where should I go now". This is why these annotations are useful, because it tries to help you figure out which way it might go and bias the generated code / CPU.
* If you go back to the MIPS days, they added delay slots. Branches have what's called delay slots -- while you figure out which way the branch is going to go, maybe I can give you a few more (unconditional) instructions for you to munch on.
* Delay slots are a way to hide the latency to send the conditional predicate to the instruction fetch unit. Some instruction(s) that I execute unconditionally associated with every conditional branch.
* Acknowledging that if I don't do that, I'll have dead space, baking it into the ISA. "I need some slots of work to do after you tell me that you're going to do a branch".
* Looks weird to see instructions in a program under the branch [that are part of the basic block] but conceptually you can think of them as paired up *with* the branch. "Branch and also do these other things before branching".

## Heisen-fetch! [28:10]

* Just as a reminder, if we're taking our conditional branch we're going to the target.
* Instruction fetcher has to conceptually heisen-fetch from these two possible locations. One is "branch is not taken" so just fall through to next instruction or we have to redirect where we're fetching from to the other location.
* Or we have to redirect where we're fetching from to the other location.
* There's a little memory in your system it's trying to read the next instruction from. In the simplest possible case, it just has one port for you to fetch an instruction out.
* So you have to figure out the address and then fetch that address from this little memory.
* CPUs have this fundamental problem (when they're trying to be as simple as possible) that they live in this heisen-state where you're fetching from either the next instruction or the thing arbirarily far away.
* Or misaligned, or switching processor modes, or various forms of things that can happen when you jump...
* But when you collapse this wavefunction, it's only going to do one of those.

## Modern CPUs vs max simplicity [28:50]

* But here's the problem for modern CPUs, contrast to "max simplicity".
* In a modern CPU the branches *could* conceptually make you seize up and make you wait until you're sure, in a look-before-you-leap kind of style, and then you'd look for something like delay slots.
* But alternatively we could do the easier-to-ask-for-forgiveness-than-permission thing, and then we keep running from there to wherever we "think" we're going to branch to, and we use special "retirement hardware" to prevent those results from landing into *committed architectural state* -- the kind of thing you would see in a debugger if you stopped it on a given program counter or if you were stepping instructions, that's your architecturally visible and committed state.
* Effectively there's a little bit of micro-transactionality happening inside, where you have these faculties inside of the CPU pipeline that say "alright, I did this, but I'm not sure it's definitely what has to happen, I did it because I think it probably has to happen, but I'm not sure." Those have to be retired via the retirement hardware.
* We get tons of performance out of the instruction stream on modern CPUs by speculating past branches that would otherwise paralyze us in place. We run the stuff we *expect* we're going to have to run.
* Classic notion of ILP mining. ILP stands for Instruction Level Parallelism.
* Churning through the instruction stream and finding things we can run concurrently on our execution paths, along branches we expect we're going to take, in order to reduce the overall execution time witnessed by the user for running the overall program.
* Classic conundrum is, as your CPU pipeline gets really deep, this becomes "very difficult" or "doesn't work" at some point.
* Pipeline depth means we potentially have a bunch of branches in flight simultaneously.
* Arbitrary numbers purposes: pipeline depth 40, basic block size 5, 8 branches in flight at any given time, so even predicting a given branch with 90% accuracy, now I have `.9^8=.43` (43%) chance of predicting them all properly. So I'll have a bunch of wasted work, going back to the notion of work efficiency / wasted work we talked about earlier.
* Some number of branches you can do before you're back at 50/50 probability of some misprediction.

## Retirement Hardware [31:15]

* What is it even? Is it where compiler engineers go when they're done doing compilers?
* Not really! [gasp]
* Basically have a bunch of extra registers and caches and such inside of the hardware, and they're not supposed to be visible from the ISA.
* Say you're on ARMv8, you have 32ish registers, the other ones in the actual hardware are not visible, you may have twice as many or more.
* They're not supposed to be visible. We've learned in the past 3-4 years that they are visible via timing, but you know what we mean, let's ignore that timing is a thing.
* The hardware keeps track of all these extra registers and cache state to remember which are speculative. Which ones hold values they haven't fully committed to, and which hold (committed) architectural state.
* It's going to throw away missed speculation and [conceptually] "roll back" to a known good state.
* Same thing with caches, extra level of caching can allow you to have speculation.
* Basically retirement just tracks what is it that's the "Point of No Return" in the reorderable instruction sequence.
* We're over simplifying, another one we could probably do a slew of new episodes on the topic.
* But interesting to think about this when we talk about how from a programming language perspective you're trying to bias what the compiler is going to do to generate specific assembly instructions to *then* have the hardware run them and speculate on the things that are going to happen.
* Layers of speculations and layers of abstraction in there, even in assembly there's so much abstraction in it.
* Amazing that assembly is really like a little interpreted language that gets unrolled into these micro instructions under the hood. Always a fascinating thing.
* Point of no Return is interesting because it shows the transactionality we were talking about earlier: says "an exception cannot happen beyond this point", as in "this point has all been committed to architectural state, I know the machine definitely got here". The "commit point" that's running ahead through the program.
* Also a bunch of different kinds of machines cited through the literature. Notion of brawny vs wimpy cores, with things like Branch Delay Slots and trying to keep hardware as simple as possible, versus big reordering hardware with speculation and prediction and things.
* Even in the modern era for embedded systems or systems that have less heavyweight hardware per thread, having the knowledge that programmers know in their head, or that profiling determined can be very helpful.
* GPUs for example, amortize their control hardware over some number of threads that they hope will be running in tandem. Trying to get as much information about whether the threads will run in unison as possible.
* In order to be Turing Complete, which is the baseline level of expressiveness we expect out of machines today, you need data to be able to influence control somehow: need to be able to do while loops, or if, or similar [ed: ifs can be implemented with while loops].
* Most systems will have to consider how the data is going to interact with the control side of the machine at some level.
* To go back to the brawny vs wimpy core thing, some amazing hardware that's been landed, or at least proposed, for beefy machines. One example was the notion of perceptrons, which was the early use of neural networks for branch prediction.
* Ultimately "just" have to predict one bit given a history of what branches have done. Have a little neural network doing matrix multiply that has to determine all this. Notions that come in of the size, and how power hungry it is, and the importance of latency.
* Need the answer quickly to "which way is this branch going to go" so we know where to start fetching from.
* Can't take too long, or we start needing to hide the latency of the thing that determines how to hide the latency.
* Conversation points towards "what are state of the art branch predictors?" which we'll have to talk about in some future episode.
* Effective forming things that, to me, look like VLIW (Very Long Instruction Word) bundles.
* Take code that's in a big sequence, figure out which ones are really going to run, turn them horizontal to run [concurrently] as micro-operations against all these datapaths that you have, and you do this on the fly using the natural size of basic blocks that exist and the reservation station scoreboarding algorithms that exist inside of the machine.
* There's also interesting things like, how do you form *regions* out of these little traces of code that get executed, in the literature.
* Ties into things like the Reorder Buffer size: CPUs have this big set of instructions that they can reorder to execute, reorder buffering and region formation are related concepts.
* Challenges of dispatching out of a really big reorder buffer. Things like the Apple M1 silicon have been pushing the limits here.
* Going back to historical papers, cool things like the trace cache in the Pentium 4 that shows the spectrum between approaches. It was a hardware structure that was storing uop-decoded tracelets that it strung together using all hardware primitives.

## So Much Left To Discuss... [37:00]

* Many more topics related to all this: vector predicated masks, SIMT, vector-threading, Cray-style scalar runahead, branch target prediction for indirect branches.
* How do branch predictors take address bits and use those to track the history? What's the aliasing in the subset of bits you use to track branches? How do you do use global/local history data in branch prediction schemes?
* Hybrid global/local branch predictor mixes.
* "Virtuals as ultimate control structure", relying on devirtualization: how would you bias a virtual dispatch if you were using it in lieu of a switch?

## When you assume... [37:45]

* Been talking about `__builtin_expect`.
* Haven't really talked about `__builtin_assume`
* Builtin expect is saying "expect this thing, but this other thing might happen as well".
* Builtin assume is saying "assume this is going to happen, and if it doesn't happen, then all bets are off, just do whatever you want with my program, I don't really care". It's totally undefined behavior if that happens.
* `__builtin_assume` is another interesting possible thing to use. There are certain programs where people have "assert" in one compilation mode and "assume" in the other one.
* Extreme wars about whether that's a valid thing to do or not depending on what the background of the programmer is.
* Interesting tradeoff there, expect and assume are hotbutton topics for different people.
* Interesting to be able to say "hey compiler, you can really take this as a given", and then of course things can be wrong, and the question is always "how wrong do things go when one of your axioms are untrue", it's a funny idea.

## Crude Mechanisms: Expect the Unexpected! [38:50]

* At the end of the day, to summarize a lot of this, scalar code really wants to have this notion of control inside, where it's moving around the instruction that's being executed, changing the program counter to point at different places inside of your program.
* We really only have these fairly crude ways of asking for things to happen.
* Usually we hope the compiler will have some way of doing the right thing, but often it has no way of knowing what the right thing is at compile time, given just the information presented to it in the program at large.
* So I guess the compiler just has to expect the unexpected.
* Like if somebody was trying to predict how often our podcasts come out, that's basically impossible.
* Unless they have a side channel, could be a good source of entropy for RNGs.
* Won't make predictions, but expect we'll do another episode in the near future.
