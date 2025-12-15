---
episode: 6
title: "ƑẍɄʑʑ҉⟆Ƒu𝔷𝔷⧫ᶳΩ𝓕𝕦𝘇𝘇֍⧩"
guid: "964fa473-82c2-4c59-bd04-fd8aaf3fd0cd"
pubDate: "Sun, 15 Dec 2024 01:10:00 +0000"
duration: "00:28:11"
audio: "tlbhit6.mp3"
description: "Code coverage and fuzzing exploration, including MC/DC testing and AFL."
explicit: false
---
# Episode 6: ƑẍɄʑʑ҉⟆Ƒu𝔷𝔷⧫ᶳΩ𝓕𝕦𝘇𝘇֍⧩ Podcast Notes

<audio id="audioplayer" src="https://tlbh.it/episodes/tlbhit6.mp3" controls="controls" class="podcast-audio" preload="auto"></audio><div class="playback-rate-controls"><ul><li><a href="#" onclick="setPlaybackSpeed(0.5)">0.5⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1)">1⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.25)">1.25⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.5)">1.5⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.75)">1.75⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(2)">2⨉</a></li></ul></div>


**Chris** Welcome to our weekly episode of TLB Hit\! Wait, is that right?

**JF** Start with some levity:  

* A software tester walks into a bar and orders a beer.  
* Then orders `0` beers.  
* Then orders `2,147,483,647` beers.  
* Then orders a lizard.  
* Then orders `-1` beers.  
* Then orders `"qwertyuiop"` beers.  
* Finally, the first real customer walks in and asks where the bathroom is. The bar bursts into flames. 🔥

What’s this got to do with anything? We want to talk about code coverage and fuzzing\!

This joke is great because it illustrates what happens when you, presumably a human, test what you think needs to be tested. The problem we thinking meat-creatures have is that we don’t always know where failure might be. That’s where metrics like coverage are useful: as a human we might think that testing beer orders is where a bar might fubar. But as the saying goes, it’s hard to make things fool-proof because fools are so ingenious, or in this case the loo is where failure was.  

Anyhow, I hear that needing to explain jokes is what makes them good.

**Chris** Let’s talk about coverage\!

**What kind of coverage is there?** We think about the program under test and ask: “did this thing run?”

* Line: was a particular line of code executed.  
* Branch: was this “if” statement observed as taken, and not taken? Was this loop executed at least once? Similar to basic block execution counts.  
* Function: was the function called? (Did we get to the function entry? Can be more interesting for inlined functions.)  
* Path: what was the path taken through basic blocks — the sequence of program counters we jumped to  
* State Space: for some piece of state, what values did we observe it take on? Similar for value coverage; what of all concrete values did we observe for some abstract value?  
* MC/DC: Modified Condition/Decision Coverage — not to be confused with the iconic rock group AC/DC  
* Human injected conditions of interest: coverpoints — also can explicitly help guide what we’re trying to hit or look for

**JF** Why is coverage desirable?

Ultimately this is all about quality assurance — is the thing we’re making good, does it do what we think it does?  
I don’t know about you, but I don’t like it when software doesn’t work.

Though that sounds easy and makes sense, the details can be tricky. What it actually means to cover code, e.g. with template instances, is one instance enough? For type traits, does it even make sense to have coverage since it’s kind of “meta-code”? With constexpr, if it all executes at compile time can you say it’s been covered?

**Chris** Thinking about the theoretical

“what are we computing and how” aspect. Aspect of pure functions vs functions that execute with some state in the background. And for partial evaluation at various runtimes for the program.

Constexpr case is more similar to pure functions, limited side effects possible and state is available in constexpr evaluation. In C++ constexpr used to be totally pure but now there’s transient allocations so slightly more interesting.

The full space of all possibilities is **combinatorial** for general programs. Just for perspective, even exhaustively verifying a function with 64-bit input space by executing it is fairly intractable\! 32-bits you can do in a few minutes, but 64-bits now you’re in trouble. Some programs, like safety related ones may try to have less branchiness by construction. But sometimes it is hard to have less branchiness by construction, sometimes the business logic just is what it is.

**JF** What’s MC/DC? (Modified Condition/Decision Coverage)

It’s a type of coverage that’s often used in functional safety software, for example in aviation under DO-178, or automotive under ISO26262. The quick-and-dirty explanation is that you make sure all independent boolean combinations for each function have been executed.

We talked about combinatorial conditions earlier, doesn’t MC/DC run into this? Basically yes, and the argument is that for functional safety programs you shouldn't have combinatorial space because that’s difficult to ensure the safety of.

**Chris** **How is coverage implemented?**

You can do static instrumentation of the program that you then execute dynamically, and gather the statistics. Or you can do dynamic sampling, where you run the program and interrupt it every so often, recording where it was when you interrupted.

**JF** **How to reach coverage goals.**

Can you even do 100%? Do you want to do it with unit tests? Should you just do coverage in systems tests?

SQLite has things to say on coverage: [https://www.sqlite.org/testing.html](https://www.sqlite.org/testing.html)

See “**Tension Between Fuzz Testing And 100% MC/DC Testing**” where they basically say that they started with 100% MC/DC coverage to ensure robustness, but found that doing so discouraged defensive programming and having unreachable code. They’d been doing MC/DC for a while, but then when they started fuzzing they found vulnerabilities. How come? Their discovery is that MC/DC and fuzzing are at odds with each other, they’re a balance between ensuring robustness in normal code versus resiliency against attackers. But they’re also complementary, because having high MC/DC helps ensure that when a bugfix comes in due to a fuzzing report, that bugfix doesn’t itself add another bug.

**Chris** Segue into fuzzing

Fuzzing is like a million mecha monkeys trying all inputs they can to get good coverage.

**Two different kinds of fuzzing that are commonly used:** generative vs mutation-based coverage guided fuzzing

Generative is like describing a parse grammar but running it in reverse — nodes expand in tree form until you hit leaves (also known as terminals). Generative is like Haskell quickcheck or Python hypothesis.

**Mutation-based coverage** guided is through libraries and tool suites like AFL and libfuzzer, keeps a corpus of stimulus it maintains and mutates it randomly to try to get fitness on a coverage metric, and prunes out redundant entries in the corpus. What it’s really doing is tapping into the coverage instrumentation we mentioned earlier to help drive your program down paths where we may be able to find problems. Works in a very scalable manner since it’s random and embarrassingly parallel, just need to exchange coverage findings periodically to avoid too much redundant work.

**JF** **libFuzzer has an interesting mode tuned for people using protobuf.**

It takes an arbitrary proto with fields, and can do some generative expansion — defining an action space for the mutation.

Protobuf contents are the things that get fuzzed based on the proto schema. It’s nice because then you don’t have to teach the fuzzer about your APIs, because some companies have protobuf as their API for everything.

Google has cluster level fuzzing, e.g. for OSS projects, there’s interesting talks on youtube about OSS-Fuzz which we’ll link in the show notes: [https://www.youtube.com/watch?v=SmH3Ys\_k8vA](https://www.youtube.com/watch?v=SmH3Ys_k8vA) 

It’s fascinating that you can take this interface — “give me stuff” and coverage guided fuzzers can find the interesting things from nothing — traps and signals and address sanitizer violations.

**Chris** And how they do that:

**AFL and libfuzzer get information from the instrumentation** — i.e. branches that are taken — and use that to poke the inputs to the program, trying to figure out which inputs will get these branches to go in another direction.

**What does fuzzing even look for?** They turn on the sanitizers and can look for UB, use-after-free, crashes, terminations, etc. Fuzzing goes great with sanitizers because it increases the set of things you’ll find.

Sometimes they also find things you don’t care about so much, like your stack growing overly large in recursive programs, or integers overflowing innocuously.

Helpfully they also provide tools like minimizers that, given a stimulus that finds a failure, tries to prune down the input and take a similar path to a similar failure. Similar to “delta debugging”.

**JF** **Some fuzzers can be pretty dumb**

In how they mutate inputs, versus some that can be smart.

You can go all generational genetic algorithms on them, with a bunch of inputs saved and mixed. But really fuzzers mostly mutate previous inputs, based on branch coverage information, to try to explore new branches. They’re surprisingly good at this, exploring branches and switches even for things like image format which have structured formats with headers and then more data. So in a way they’re smart, and in a way they’re not.

In fact, take a look at AFL’s logo, we’ll put a link in the show notes. [https://en.m.wikipedia.org/wiki/File:AFL\_Fuzz\_Logo.gif](https://en.m.wikipedia.org/wiki/File:AFL_Fuzz_Logo.gif)   
It’s originally a JPEG from Alice in Wonderland, which Michal turned into a gif showing each step of the fuzzer changing the image, one change per frame. The fuzzer can, through its branch coverage, understand the structure of the image format and perform mutations based on this structure.  
It’s oddly relaxing to watch that logo.

**Chris** **Fuzzers do particularly well when you feed them a corpus of information that they can mutate.**

For example you might take all your unit tests that caused errors in the past or came from resolved issues. That helps them figure out how to reach different branches easily, it’s a map of where to start. They can also cross over the interesting parts of examples with each other, similar to how genetic algorithms do crossover and mutation.

Separately, you can also provide suggestions on which mutators to use which help fuzzers figure out what to change in an input.

The problem with corpus is you have to remember how to pluralize it. Corpie, Corpora, corpoxen?

**JF** **We talked about using sanitizers to find UB. Why are we looking for UB?**

Oftentimes, UB is where unexpected things live. Not all UB is really bad, but if you’re trying to fix potential issues then removing all UB is valuable. That doesn’t help find problems in your program’s higher level behavior. The programmer knows what their requirements are, and what is invalid state. That’s where defensive programming is useful, where the programmer adds checks for state that is invalid in their program, and aborts when such state is reached. This type of check is useful because the programmers tell the fuzzer what to look for.

**Chris** There’s really **two styles of fuzzing**:

binary mode where you don’t have sources and rewrite or observe the binary, versus instrumentation mode, where you have the sources and emit extra code into the output artifact.

In a way, binary mode ties into tools like valgrind and dynamic binary instrumentation, whereas static and code-available instrumentation is how the sanitizers work.

Fuzzing uses randomness to explore a format and branches, but there’s diminishing returns at some point. How can we maximize exploration of the program’s state while minimizing the types of inputs that have the same outcome?

On fuzzing binaries, it’s kind of fuzzing with an implementation that you can’t see: ISA fuzzing finds unpublished instructions, there’s a cool BlackHat talk titled “Breaking the x86 Instruction Set” in this dimension [https://www.youtube.com/watch?v=KrksBdWcZgQ](https://www.youtube.com/watch?v=KrksBdWcZgQ)

**JF**

We’re scratching the history of fuzzing a bit, on that topic Thomas Dulien has a keynote on fuzzing’s success, we’ll put a link in the show notes: [https://www.youtube.com/watch?v=Jd1hItbf52k](https://www.youtube.com/watch?v=Jd1hItbf52k)

Let’s change topics a bit and **segue to hardware**.

There are strong ties between fuzzing software and hardware design verification. You don’t want to have bugs in hardware, because that’ll cost you millions of dollars to fix. You’d better make sure it’s correct before going to a fab and making a chip.

And the problem with hardware is that you have deep and giant state spaces with all the flip flops and stateful elements on a chip.

What’s been done for a long time in hardware is therefore to use formal methods and tools like SAT solvers to mathematically prove properties of the hardware.

In those circumstances, where you can prove correctness of some properties, you don’t need fuzzing because you have a proof of the entire state space. Fuzzing is basically trying to get a dynamic execution to do something unexpected, whereas formal methods are trying to mathematically prove a property for all possible inputs.

So what’s been done with hardware for a long time can also apply to software: if you can use formal methods, even on a subset of your program, then fuzzing isn’t needed for that subset.  

You can use SAT or SMT solvers, proving whether conditions are reachable at all.

Fully inductive proofs are quite difficult to close, I don’t know enough about how inductive proofs to really understand when they don’t work, it would be fun to learn more.

One fun thing is that you can **turn subsets of a compiler’s IR into SMT input**. You can’t do it *easily* for all programs and all programming languages, often things are left explicitly undefined. This is also a problem when you try to create hardware from a language that has undefined behavior, which many/most of them do\! Imagine a shift operation that’s undefined when overshifting — what gates come out and what gate patterns are acceptable if you end up statically or dynamically overshifting? Clearly you care about this\!

**Chris** Formal Methods

Formal methods also make proving properties of very large spaces more tractable; e.g. the 64-bit input space is intractable to validate exhaustively, but we can prove properties of the computation symbolically using the properties inside the computation.

Also relates to TLA+ which is a formal modeling language and runtime that people use for proving properties of important algorithms, including distributed and consensus type algorithms like Paxos — often times people will translate Finite State Machines into a TLA+ model and prove properties on it in that abstract form. Link to Hillel Wayne’s talk on getting started with TLA+ which helped me get started writing models.

**JF** Let’s jump into quickfire topics on fuzzing\!

**Chris** Fuzzing By Proxy:

My mind was slightly blown by the idea of fuzzing by proxy from the SiliFuzz paper: the idea we can fuzz something like QEMU and use the complexity and coverage in the simulator implementation as a proxy for complexity and coverage in a silicon implementation even if it’s implemented totally differently.

**JF** Compiler instrumentation:

Part of how coverage guided fuzzing works as well as it does is that the compiler and native code generation are in on the game.

Instrumentation makes callbacks to the fuzzing runtime that tracks it in a data structure — doing this in-process allows the fuzzing process to run a lot faster than if it was out of process.  
Maximizing the frequency with which you run the fuzzed program is also a big part of the game, being able to iterate linearly.

Basically coverage recording flags can control where and how to add pseudo-branches.

Consider if you’re branching on an arithmetic expression `x > 32`, maybe you still want to know what bits are set in x beyond the 5th bit and include those in the things you try to cover.

**Chris** **Fault injection:**

Sometimes to hit rare cases you have to do fault injection to get you down some path you don’t expect to happen in practice.

In a way, it goes back to our “[not taken branches](https://tlbh.it/003_builtin_expect_bang_bang_x_0.html)” podcast from a few weeks ago, forcing our way to exceptional circumstances being handled in the code.  

You need enough seams to enable fault injection testing, sometimes people will do it with mocks or fakes.

Have to design the software so you can easily reach in and cause something atypical to happen — Michael Feathers has a great book on testing patterns that really hammered home the word “seams” for me — really liked his book “Working Effectively with Legacy Code”

**JF**

I have to chime in and mention my coworker [Robert Searcord](https://en.wikipedia.org/wiki/Robert_C._Seacord)’s book “[Modernizing Legacy Systems](https://www.amazon.com/Modernizing-Legacy-Systems-Technologies-Engineering/dp/0321118847/)”. It’s from 2003 and I haven’t read it, but Robert will be happy I mentioned his book.

**Chris** Oh thanks\! I won’t read it either\!

**JF** Another quickfire topic: Classic software question around assertions and check-failures.  

**Is it better to crash or keep on trucking?**

It typically depends on how unrecoverable and impactful your invariant failure is, and what the potential impact of crashing vs trucking on in an inconsistent state may be. What we’ve seen is that different teams and different industries define different value functions around this.

You don’t want someone to be able to send you a “packets of doom”.

Even with a supervisor process, it’s possible to crash loop.

In functional safety, Hazard Analysis and Risk Assessment, used to see what program failures could be and how to react to failure. Often end up with a supervisor which handles failure, and forces the design to handle these problems.

**Chris** Concolic is another fun one:

It’s a mix of concrete and symbolic, a term often used in the hardware testing space and the subject of a bunch of good papers and research.

Find a condition that never triggers, ask yourself, “can it ever trigger and I’m just not finding the right stimulus?” So then you go and try to back-solve symbolically to find if that condition is ever possible to reach. If it is, you found a great thing to add to your corpus. If not, you know that condition is effectively dead and you can flag that.

**JF** This “can I ever see this condition” testing is also related to **bounded model checking**

Imagine your program had a top level loop, like a `while(1)` — you can ask successively, can the bad thing happen if I run the loop just one time? No? Ok, what about if I run it exactly two times? No, ok… As you brute force unroll and try-to-prove you gain more confidence in whether the condition seems reachable with a reasonable amount of stimulus and time steps. You just hardcode a limit on unrolling, and give up once you reach the limit.

Also if you have a symbolic representation of the valid state of your program, you can try to “fast forward” to some reachable state by changing the value, and then walk forward time steps from there.

**Chris**

Joe Armstrong of Erlang fame (inventor of Erlang, may he rest in peace) has a great talk called [the mess we’re in](https://www.youtube.com/watch?v=lKXe3HUG2l4) — it talks about how QA being so difficult relates to the huge state space we have in modern systems, and that they’re often not well defined, and that we try to rev designs with lots of features.

It indeed does look like a mess in many ways, but it is *our* mess. And with fuzzing we solve our “carefully constructed mess” *using* focused beams of random mess\! Beautiful in its own way as we strive to find ways to do things better.

**JF** on that note, I’m glad we got to record this episode, and I hope folks enjoyed it. Please join us next week for our next podcast episode\!

We’d like to thank our sponsors, but we don’t have any.

Don’t forget to like and subscribe, tell your friends, and go fuzz something.

**Chris** Are you telling people to go fuzz themselves?

**JF** I guess I did.  
