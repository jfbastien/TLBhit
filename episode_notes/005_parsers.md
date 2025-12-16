---
episode: 5
title: "parsers"
guid: "dbdfca99-ba05-4735-b8a4-6cb63faf3b8c"
pubDate: "Thu, 23 Feb 2023 11:24:00 +0000"
duration: "00:41:40"
audio: "tlbhit5.mp3"
description: "Parsers?"
explicit: false
---
# Parsers Podcast Notes

## [00:00] Horrible Winter Holiday / Valentine's Day Cold Intro

* Warm and fuzzy... and **parse-y**... time of year
* Today just going to talk about parsers not fuzzers, but JF likes parse-ley and other assorted rabbit foods

## [00:13] Disclaimer

## [00:35] On Parsers

* Talking mostly about our practical experience with parsers
* Addressing parsing field as a whole is difficult because it's both theoretically nuanced and large (c.f. a whole Theory of Computation class in school)
* One of the criticisms you often hear about original edition of The Dragon Book is that it was frontloaded with a lot of theoretical parser content which tripped many folks up in "intro to compilers" class
* A lot of that book was on syntax directed code generation as a backend flow [whereby you parse into an AST, and then largely just walk that AST to generate code directly corresponding to the AST structure as you're walking it, i.e. parse-then-emit-pass-style]
	* Understandable that it did a lot on parsing
	* But also not always what people were looking to understand in compilers class... [vs perhaps: what do the guts of an optimizing compiler look like, how do program transforms typically work, what can I expect a compiler to do / not do, etc]

## [01:20] Embracing Recursive Descent Parsers

* A bit heretical, but part of what we're going to claim today is that parsers, in a practical sense, you can view as a stylized pattern of coding
* With recursive descents parsers as a solution, you can easily create your own parsing scenarios & solutions and reuse that understanding [e.g. even across languages, environments]

## [1:40] Parsers Show Up All Over!

* Parsers, when you get into them, show up **all over the place**
* People will say "you can't just point at anything and call it a parser," but when you start loving parsers, you kind of do!
* An example is CPU front-ends, the ones that decode the instructions
* Really they are very compact, on-the-fly parser/generators for microcode
* If you look at ARM64: it's 4-byte words that you parse one at a time, CPU parses it as any disassembler would do it, sometimes does it more than one word at a time, but basically a fancy parser
* [And parsers that can vectorize with respect to input/output symbols are a whole other area of interest; e.g. in this example can you, in the average case, consume two 4B words and produce >= 2 micro-ops in a given clock?]
* x86 is a bit trickier as a front-end because the instruction size [input symbols] are variable length, variable-width encoding but still a kind of a parser
* This is a type of parser that needs to have **context** to decode the instructions properly, e.g. starting at the right place [and in the right mode] to decode the right instructions
* In fact, if you're mis-aligned, you could decode totally different instructions
* Still effectively a very fancy parser!
* In the realm of security, this is one of the fun things that **shell code** [attacker-controlled code buffer payload] will try to do to take advantage of this: place a bunch of constants into the code and jump to a weird offset, so the move-constant-to-reg instructions will be decoded differently via the immediates that are not at the intended "start" of the instruction

## [2:50] Some Naive Background on the Parsing Process

* As humans we often write text down using alphabets that we use to make composite words
* We have "parts of speech" that put words in relation to one another to make sentences that have semantic meaning
* Parsing for computer programs is analogous/similar in a lot of ways
* We have scanned characters, like code points in unicode, which make up our alphabet
* We use those to make up "tokens", which are kind of like words
* We put those tokens into a "parse tree", that often relate values, which are like nouns, and verbs, which are like operators together
* We can then define **new composite things** by putting all these primitive pieces together!
* In this vein, if you've never watched [Guy Steele's "Growing a Language" talk](https://www.youtube.com/watch?v=lw6TaiXzHAE) [OOPSLA'98], you probably want to push pause right now and go watch that, it's really good! [Apologies to listeners for the binary sex distinction made at the start, but it explained later in the talk how/why it is used as a rhetorical device.]
* **Using Declarative Languages:** often we use declarative languages to describe "how to read in" computer languages
	* We use **regular expressions**, for example, to say how to scan tokens out of a character stream
	* We use little languages like **BNF** (Backus-Naur Form) that describe grammars of languages, the kind of "recursive definition"
	* e.g. an *arithmetic expression* can be made of "weak arithmetic with additions/subtractions, which can have "strong arithmetic" expressions inside of it with multiplications/divisions; i.e.:
	  ```
	  ARITH_EXPR ::= WEAK_ARITH_EXPR
	  WEAK_ARITH_EXPR ::= STRONG_ARITH_EXPR ["+" STRONG_ARITH_EXPR]
	  STRONG_ARITH_EXPR ::= TERM_EXPR ["*" TERM_EXPR]
	  TERM_EXPR ::= Number
	  ```
  * BNF restructured as these recursive rules for how to turn tokens into a tree, and that's the parse tree that we get out of the parsing process

## [4:25] Unicode-qua Parser

* Example of "pointing at a thing and calling it a parser"
* Unicode itself, need a form of parser for
* Self-restarting parser: not that context-ful
* Way [variable-length] unicode is encoded every UTF start, in UTF-8 for example, tells you where the start of the code point is
* So if you miss one code point, the next one you won't be able to miss, because of the way is encoded
* Very simple parser, but still something you would "parse out" of a byte stream
* Parsers are everywhere!

## [5:05] Questioning Conventional Wisdom? Trade-offs in Parser-Generation

* Conventional wisdom out there is to ever write a parser by hand, but to always use a parser-generator
* JF & Chris generally think the conventional wisdom here is wrong
* We would [for mission-mode projects] prefer to write a parser by hand: start with a recursive descent parser, and if that form causes issues, use more of a state-machine style form that tracks context/state when necessary
* [Or sometimes over-recursion errors that come from an deep recursive structure can be transformed to be more iterative formulation, like [precedence climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing)]
* Recursive form is easy to write, and translating to more of a "state machine" form is not that bad
* JF started his first parsers a long time ago with the conventional wisdom: tried a bunch of things
* Tried ANTLR, tried lex/yacc & flex/bison
* Ended up with Boost Spirit -- in retrospect felt it was a bad idea: hard to write, hard to debug, not really flexible, gave terrible error messages, *but as a trade-off* gave terrible compile times too!
* Silver lining of working in Boost Spirit all that time ago is JF gets to make fun of [Bryce Lelbach](https://twitter.com/blelbach) -- friend of the show & [ADSP podcast](https://adspthepodcast.com/) host, worked on Spirit and JF always makes of him for that, silver lining in learning to disregard the conventional wisdom
* Boost Spirit is kind of an EBNF Domain Specific Language (DSL) written in C++ Template Metaprogramming (TMP)
	* If you look at EBNF it has special operators; some of these exist in C++'s overloadable operator set
	* Somebody went and made a clever C++ optimizer in template metaprogramming for a DSL language using templates and operator overloading, to made somewhat of an EBNF parser; very cute but kind of a silly idea honestly, would rather write all of that stuff by hand
* Think we, in industry, had a rude awakening [with Yacc] to see `.y` files trying to interleave various things into the parsing process; unclear lifetimes in the `.y` files, memory errors that would result -- part of what made JF love recursive descent parsing by contrast was that kind of stuff
	* When I make fun of Boost Spirit I wouldn't say .y files are better than what you end up with there; really think recursive descent parsers are the right way to go: more malleable, nicer to write, easier to debug, & etc
* For folks who haven't used Yacc before, `.y` files are stylized C templates that the Yacc parser can call into when events occur in the formation of the parse tree
	* You create this "hybridized, C-looking file", but where things are happening that are driven by the Yacc parser [as the main loop]
	* JF is personally a big fan of code generation: custom DSL that you (yourself) parse -- and generate C/C++ code to do things -- that your codebase uses; just seems like Yacc files are not the best compositional way do code generation
	* Increasing people are trying to create and use simple versions that operate more like that; in Yacc the inner loop driven by the theoretical LALR grammar composition -- i.e. there's something you don't understand that you'll get your shift reduce conflicts from in your inner loop, but that triggers events in this other file
	* Things like PEG grammars that people are trying to use more of now can end up spitting out a C file that *is* a recursive descent parser, but we'll talk about some of the trade-offs there as well
	* Even though things like PEG grammars are are a more modern technique that are spitting out recursive descent parser *implementations*, here we're mostly going to talk about the hand-rolled recursive descent parsers
	* Trade-off for hand-rolled ones is that they work well and are understandable when you structure them as code yourself, and really it just comes down to a stylized way of structuring your code to make a useful and easily-recognized data structure, which is the parse tree that comes out, or a nice error message that can use the context from where the error message occurred
	* Very good article that gives a counterpoint to our view that this is our preferred way to do it: [Why We Need to Know LR and Recursive Descent Parsing Techniques](https://tratt.net/laurie/blog/2023/why_we_need_to_know_lr_and_recursive_descent_parsing_techniques.html)
		* [A key observation from this article is that we should all internalize: recursive descent parsers being "just stylized code" is both a blessing and a curse: you can write an ambiguity in your grammar like "if it's Tuesday parse it this way" and not skip a beat. Understanding how to make languages regular in form, even when they are implemented as hand-rolled recursive descent, is key. In a hand-rolled recursive descent parser, striving to write LL(1), for example, where you can disambiguate what direction the grammar is going with a single token of a lookahead, is a good thing.]
	* Parsing historically was one of these great crossovers between fundamental CS and practical applications
	* You learn about it in a Theory of Computation class:
	* A regular expression has a certain level of power
	* Push-down automata are the next level of power that enable you to do things like match parentheses; e.g. when you have open a close parentheses
		* You can't write an HTML parser, for example, using just regular expressions!
	* So parsers are strictly more powerful than what you can do with regular expressions!
		* People, as a result of the important theoretical basis, can feel that the underlying theory is important, which makes sense -- to the extent you can find yourself learning about Chompsky's theories and Cantor diagnalization proofs and things like this -- which are all important and great, knowing CS fundamentals is great!
		* Similarly, from a practitioner perspective, there's an aspect which says: if you just write code in a particular stylized way, you can accomplish your particular task, you can get done the job you want to get done; and, if you find the theory daunting, you may be able to skip over some of those fundamentals, and just learn to write this stylized form of code
	* JF worked with someone 10 years ago or so who did their PhD on parsing -- perhaps today we think parsing is a well known field -- doing a PhD on that he significantly advanced the state of the art in CS in the 70s -- really tells you that computer science itself is a fairly novel field, lots of things were figured out fairly recently
		* Interesting that we're in this field where things are so novel that it's possible to know folks who invented key things

## [11:40] Recap basic flow of parsing

* "Tokenize" the characters: linear stream of characters transforms into linear stream of tokens
* Make a tree out of those tokens
* Scanning and tokenization are synonyms
* But even that fact is interesting: brings up questions like: 
	* "is tokenization context-sensitive?" and
	* "how parallelizable is it with respect to the character stream?"
* Sometimes want to split parsing and scanning [e.g. for nice separation of concerns], sometimes you want to join them
* Scanning tends to have *very little* ‌context -- usually only understands basic delimiters in the text itself
* Whereas parsing tends to understand the context and the structure of the grammar that you're dealing with
* The parser itself has a state, to understand where you are -- i.e. in a state machine, to decode the grammar that you're parsing
* The parser generates an output: depends on what you're doing, could be an abstract syntax tree you generate from your parser
* i.e. could generate code directly if you're a small/efficient [i.e. "one pass"] compiler
* In a recursive descent parser, that state is partly encoded in the control flow itself: the function calls, what's on the stack, and so on, encodes some of the state
* When we were discussing converting a recursive descent parser into more of a state machine, what you end up doing is looking at that state you had via recursion, and having your own stack  to encode that state as a side data structure
* And this is a generally interesting thing in the way that we write sequential programs: the program counter is effectively a state that marches forward and takes jumps and things like this
	* Recursive functions is one particular way to structure your state with data on the stack and the marching forward of the program counter in various ways

* [13:30] Like we were talking about, the tokens get formed from the character stream
* Lookahead ahead at what token you see is part of what determine the grammar production (grammar rule) to apply
* If I'm looking at the character stream and I'm holding something in my hand, and looking ahead I see the plus sign, I 
* Lookahead ahead at what token you see is part of what ultimately can determine the grammar rule to apply: if I'm looking ahead and I see a plus sign, I know this is probably a binary plus operator (in many common languages) that wants to take the thing I just saw on the left hand side and add it to a thing (I still have to determine) on the right hand side
* And so what happens with these rules, is they nest: I'll take the plus operator and say "ok I must be currently doing a weak arithmetic expression" -- because times binds more tightly than plus, plus is "weaker"
* So then I would look at the right hand side and ask "can I parse what I see after the `+` as a *strong* arithmetic operation? Like a `*` maybe? One that *binds more tightly* than the plus I'm currently looking at as an operator?"
	* This binding or precedence level determines whether you nest the next expression at the same level or an increased level, like a tighter binding; i.e. the `*` would be more tightly binding than the `+` operator
	* So you set up your grammar rules so that things that *nest more tightly* become more interior nodes inside the tree
	* You do this using self-contained rules; e.g. `WEAK_ARITH_EXPR` above that has `STRONG_ARITH_EXPR` on the left hand side and right hand side
	* You stylize your grammar recursive functions / BNF grammar to make this association clear

## [15:10] JavaScript Fanciness: Outlining Functions

* In JavaScript land, beyond these basic flows of how grammars work, there are some cool and fancy things
* Imagine there are hundreds of functions in the file, peek at where the beginning/end of the functions are so I can lazily load in the tree that describes the syntax (i.e. lazily parse it)
* Imagine I never end up calling a particular function, do I really want to spend cycles parsing and analyzing it if I never call it?
* But can also be interesting challenges: tokenization, for example! If you're in a regular expression you might switch your scanner from regular expression mode to normal JavaScript code mode
* Or if you find yourself in the middle of a multi-line comment there could be arbitrary stuff in there that doesn't do anything at all!
* Challenges in doing advanced/fast/concurrent scanning or tokenization
* When you try to parallelize things you need to have enough work in each parallel worker to do something useful: classic parallelism/concurrency tradeoff -- do you go off and optimize  all the functions at this point?
	* You have a quick parallelel parser that figures out where the start/ends are -- do you fork off work to N threads to quickly optimize all of them, or maybe do some extra amount of parsing, or do you just keep that information around and do that lazily with an interpreter when you end up executing it? And then Just-in-Time compile it? *And then* do you Just-In-Time with a foreground thread or a background threads, part of the trade-off
	* Parallelization is a good way to use multiple cores, but for lower latency page load maybe you want to block and compile right there/then on the foreground thread and do the work as it comes in
	* Always an interesting trade-off to see if you tie in parsing with optimization or other kinds of context generation

## [17:15] Backtracking

* To pull back a bit from the advanced techniques we're talking about and go back to fundamentals of parsing
* One of very important aspects of parsing is this concept of backtracking
* Just like you speculatively might parallelize for parsing javascript on a page or something like this
* In the parsing process itself when there's something ambiguous to do: you see a `<` operator -- you're not sure if that's starting a template instantiation in C++ or doing a less-than operation -- when you see that `<` in C++ it could mean one of two things, so you have this ambiguous choice
* Backtracking basically means capturing your current point in the process of parsing, and being able to revisit that choice and make a different choice
* So you might speculate that this `<` operator is going to be an actual less-than operator, and you might go try to parse as-if that's the case, and if you find that was an error, you may go back, restore your original context, and go down the opposite path [of a template instantiation]
* Some languages can be more regular and require less-backtracking or no-backtracking, and there's a whole description of what languages can have this property in the theory -- it's an important concept that gets introduced when you grammar isn't fully determined by look-ahead tokens, so this is a property than many real-world languages do have that we use in computers
* [18:55] Rust relatedly has this "turbo fish" operator that helps resolve the ambiguity mentioned in C++ -- instead of seeing the `<` symbol and thinking "maybe that's a template instantiation" there's an explicit operator which is `::<` that says to the parser "the thing on the left hand side of this operator is a type name being instantiated, I'm telling you that it is!" Interesting solution for making things less ambiguous as the cost of thing having more punctuation in the lines
* Haskell relatedly has the ability for users to create whole new infix operators, so you can extend the grammar e.g. with the Kirby operator `<(o.o)>` (or maybe not quite that far) -- but almost arbitrary punctuation can become new infix operators
* Things like [CamlP4](https://en.wikipedia.org/wiki/Camlp4) [ed: my bad I misremembered and said Caml4P] were in the history/insiration of the Rust macro creation, where things are extensible in user space so the syntax can be extended so you can build new parse trees and constructs
* [20:00] For backtracking in general but also in parsing you have these decision points where you make have to throw away work done in some subtree and then go on to make a different choice until you figure out what the actual subtree was
* Similar to all transactional things: make continuation point you may choose to revisit, until you decide that, "ok I actually finished and I never need to revisit", and then you actually commit that and pass your "Point of No Return"
* [20:28] Backtracking also reminds us: designing a parser is something you want to do ideally while you design the grammar you want to parse itself
* A lot of grammars are designed in a way that ought to be easy to parse, some of the thinking is: it's not only easy for a programmer to write a parser, it's also easy for a human to understand what's written
* In C++ we were talking about the `<` operator; those familiar with C++ in a template context, you end up having to specify typename and template
* `typename` and `template` keywords have a few different meanings -- in a template context it disambiguates certain things; when C++ was designed its grammar was realized to be quite complex and those keywords are there to help disambiguate some of the things, not only for parsers, but for humans as well
* When they were creating Go this was a big focus -- they wanted to have a grammar that was not just for humans, but *also* easy to parse, and so they ended up having some things like types following identifiers

## [21:30] How doth a tree grow?

* [21:30] Basic thing we're burying in talking about recursive descent parsers primarily is whether parse trees should grow from the leaves to the root, or visa versa
* If you look at a graph: from the bottom of the graph or the root at the top?
* Joke here: *real* trees probably have a strong preference in which direction things grow! But in CS trees you get to choose how trees grow
* In LL and recursive descent, that's usually top-down, start at the root; LALR / bottom up parsing starts at the leaves / terminals of the grammar
* Trade-offs in choosing each of these based on what it is you're parsing: what is the language/grammar you're looking at
* Sometimes recursing "from the left" / "from the right" may have more backtracking and therefore be less efficient
* Again, designing your grammar with the parser makes trade-offs in how things are efficient and how you implement the parsing
* Ultimately comes down to how ambiguities are resolved and when they're detected during the parsing process
* Shift-reduce conflicts are notorious here and come from ambiguities in the bottom-up merging process
* What's neat about recursive descent parsers is you're really just writing code, resolving conflicts with the code that you write -- one of the things that can be nice, if you're not careful you don't even notice you're doing it -- what's bad is the same thing that's good, you're just writing code, sometimes it's nice, sometimes it's a great way to make a mess
* Very powerful tool, with great power comes great responsibility
* Can easily say "the grammar parses this way when it's a Wednesday after 4pm", but that would be a terrible parser to write, even thought it's possible in a recursive descent parser
* What the structure of these declarative things is forcing you to do is say: "it follows this regular structure, and it has ways of resolving ambiguities that I placed in my specification up front"

## [23:53] To hand-roll or to generate: *that* is the question!

* [23:53] Back to what we were talking about at the beginning on the trade-off between parser-generators and hand-rolled recursive descent parsers: no way to avoid the language of trade-offs
* Some things might consider are: performance; when you parser-generator gives you something that gives a certain performance in parsing, what are your tools/techniques for getting more performance out of the system, e.g. parsing more megabytes of text per second into your data structure
* With code in your hand in a recursive descent parser, we can use a lot of our conventional techniques for optimization, whereas with a parser-generator restructuring the grammar or perhaps providing hints to the parser-generator are ways you might do it in a generated scenario
* When you're writing code you have more control over memory usage and how things gets structured; e.g. if there are peak memory limits you want to stay within, or if you have some kind of divide-and-conquer you may be able to do
* When you have the code in your hand you have all the control and the power, but at the cost of some additional code writing and extra work for you
* Error mesages are a pretty important point we have to talk about more:
* Things like **inline diagnostics**: say you get part of the way through parsing your program, but then you find that there's some problem, diagnostics on the partially-completed parse process are very important to be able to feed back to the user
	* "I got to this point but then I saw that `$THIS_THING`, in particular, went wrong"
* Tracking state for diagnostics like this in a "sidecar" for diagnostic purposes as you parse is a really powerful tool in recursive descent parsers
* If you look at Clang -- the C++ front-end -- it always tracks potential errors / diagnostics in a side-state while it's parsing -- it's always keeping track of a bunch of things
	* If it encounters a problem it will print it out of the diagnostic, if it is is enabled, otherwise it will just kind of "keep going"
	* This also allows it to print out diagnostic context more easily, because it keeps track of context while it's doing the parsing
	* Diagnostic information itself can lead to better error *correction* as well -- to keep making progress, you may want to keep parsing instead of just giving up on the first encountered error
	* Some languages want to give more useful errors, not just the first one in the compiler invocation
	* Particularly if the compile time is slow! Want to have a handful of errors you can address, not just the first one, before recompilation
	* Kind of similar to "lax mode" in HTML "quirks" parsing
	* If you know the history of HTML, there's been these back-and-forths with XHTML and HTML5 and the previous versions
	* There were people who were very religious about "HTML has to parse exactly correct and any small error you should not render a webpage" vs "HTML should be parseable... kinda... whatever!" [c.f. [Postel's Law](https://en.wikipedia.org/wiki/Robustness_principle)]
	* If you look at HTML parsers nowadays in browsers they do very interesting things to be able to form slightly misformed HTML that "happens to work"
	* Ability to handle error messages and error cases very well using partially constructed information does end up hurting the ability to modularize [the parsing process] a bit -- you end up wanting to reach in to the "surrounding" "what didn't finish yet?" "how much of it did get done?"
		* Can often prevent you from creating little very easily pluggable modules, we'll talk a little bit more about that
* [27:30] Have seen arguments against recursive descent parsers in the sense of: "what if the grammar is changing a lot?" In the case could make you do significant changes to the recursive descent parser code that you wrote [vs more simply changing BNF]
	* In personal experience, things evolve structure over time in a way that can compose function-wise; these functions are defined in productions / helpers inside of your grammar
	* Usually productions don't disappear entirely or get 100% re-worked in the language, vs getting tweaked and/or refactored
	* So declarative specifications like BNF are good but there's also some trade-offs around driving everything off of them
	* If you wanted to have multiple versions of your language, for example, say you wanted to be able to ingest version 1, make some internal AST changes, and then format out version 2 via some formatting methodology like clang-format or something similar
	* Nice to be able to have simultaneous parsers/formatters there with common sub-routines between them even though they are differing sub-versions of the language which may have differing BNF
	* On the point of modularity: there are also parser "combinators" which are really cool -- functions that have the same API for doing things -- general idea of combinators are lego bricks you can plug together because they have a uniform interface
	* Challenge with those is, because they have a uniform interface, they can't pass side-band information between each other easily, because they all take a stream of tokens in, say, and produce some sub-fragment of the AST out
	* So handling that global context/state of error messages and things can be more difficult: how does that side-band information come in to play?
	* Although combinators can be difficult for getting the best error message experience in my experience, they're really nice when the UX is less important, because you can make them very quickly in the same sense as parser-generators
	* One cool case study: because formatting is the inverse function of parsing, you can make one combinator that both parses and formats out its input, and we did that for example for TPU assembly, for example
	* Can create a little environment of data that came from parsing the assembly, and use that *same* environment for formatting the assembly out with the same combinator
	* Nice that these functions can be easily inverted when you plug them together in this combinator sort of way

## [30:15] Engineer / Pig-Mud Equilibrium

* We're both engineers and we like to get our hands dirty, way JF likes to describe it is as the saying goes, "It's like wrestling in the mud with a pig, at some point you realize that the pig likes it"
* We like to get our hands dirty with code
* Few times we got our hands dirty with parsers
* We worked on an array database query language that had operators that associated right-to-left
	* You make a right leaning tree instead of a left-leaning one, meaning the outer-most expression is on the right hand side of the screen, interesting code base!
	* First time seeing idea that operators would apply right-to-left, made for an interesting parser
* Features that were somewhat notorious we got exposed to in JavaScript that had funny grammatical properties, like its Automatic Semicolon Insertion (ASI)
	* Normal BNF grammars don't have a notion of a "negative lookahead"; like "there can not be this terminal here", but that's how ASI was described in the JavaScript spec
	* In Firefox SpiderMonkey [JS engine] we had a recursive descent parser, so it was very clear how that kind of "production rule extension" could be handled, but believe [OS X Safari] JavaScriptScore had a lex/yacc based parser -- not exactly sure how it handled things like this negative token lookahead, but would be interesting to go back and find out; how did it deal with this extension to the BNF grammar that was present in the JavaScript spec
	* ASI one of the strange quirks of JavaScript people ideally do not rely on, but makes it an interesting language to parse; interesting accident
	* "If there would be an error, but putting a semicolon there would make it not-an-error, then you should put a semicolon there" is perhaps the rule
	* [32:30] When JF worked on Chrome's Native Client security sandbox, the parsing had to be correct, or it was a potential security vulnerability
	* Idea of Native Client back when it started in 2009 -- [really great paper describing it](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/34913.pdf) -- let's try to run native code run on the web
	* At the time had written V8 and realized there's a wall you hit with JavaScript regardless of how much your compiler can optimize things for JavaScript and kind of want to run more powerful things on the web
	* Native Client isn't what ended up being standardized, Web Assembly was
	* But core idea of running native code on the web was really interesting, and there were different experiments: NaCl, PNaCL, and at Mozilla there was asm.js which ended up with us creating Web Assembly together
	* In all those contexts the parser is really really critical to get right, if you don't get it right there's a vulnerability
	* When JF worked on Native Client the input was x86-32 x86-64 and ARM, so there's really tricky things and parsing those ISAs correctly is important to security
		* The CPU is just going to execute it, so if you haven't validated the executable correctly, something else is going to be executed which may be a vulnerability
		* One fun bug the team had to resolve early way before launch was dealing with `pushf` / `popf` instructions in x86
		* Those tend to just push the flags, overflow flag and such
		* But because of the way x86 is made, it has interesting flags nobody really uses; e.g. direction flag you can save and restore, which sets the direction of the `REP` prefix instructions
		* `REP` is the "repeat" prefix which ends up being used in things like memcpy [which can be implemented via `REP MOVSB`] -- when you change the `REP` prefix you can change the direction flag to make that memcpy go backwards
		* Interesting but a great way to write vulnerabilities; if you're trying to bounds check things, you see a `REP` instruction, you "know" it's going to go in increasing addresses, but if you set the flags differently it goes backwards! This lets you go out of bounds and create an exploit chain
		* Interesting part of parsing we had to get right was in ARMV7, some interesting features, can change from one endianness to another (and sub- instruction set, e.g. Thumb) *during* execution -- if you see those instructions that change endianness or instruction set one thing you can do is just disallow them; if you try to handle them can be tricky to do very well, giant context change for a parser, not something wanted to allow so just disallowed it in the parser; other interesting pieces like Jazelle in ARM too
		* Other cool stuff that came out of the NaCl team: at some point the team wrote an auto-generated x86 parser; had a description of the x86 they wanted to handle, auto-generated the parser from that description
		* Code generated was so big was the biggest set of functions inside of Chrome, blew up Visual Studio really badly, had some behavior where it gave up and generated very terrible code, until they figured out how to tune the code generator to split up what it generated so Visual Studio wouldn't choke on it 
		* Also one of the things to bring up as one of the potential pitfalls for Recursive Descent Parsing; you have these production rules -- your functions represent grammar production rules -- they're all co-recursive, they're all calling in to each other -- some of them will be hotter than others, some will be smaller handling code thats inlined into outer sites that try to implement parts of the grammar, so sometimes can get giant mega-frames, end up with tons and tons of stack data when you call a particular functions
		* Can end up with giant frames leaping over guard pages or terrible things that end up with the OS not paging in the next stack page appropriately -- something to watch out for, these giant stack frames / stack overflows that cause segmentation faults
		* JF worked on another cool parser, good chunk of parser for WebAssembly inside of WebKit, and testing and things, wrote the core of it and folks wrote the rest of the parsing, that is also security sensitive, WebAssembly kind of a stack machine little language, but all byte oriented when you parse it, and has to be secure: if you don't parse it properly you wind up having vulnerabilities, but also in those cases want to have good error messages, because it's a bunch of bytes you push in, so a developer being able to look at the error messages with WebAssembly is very important
		* Something JF liked doing to solve the parsing of WebAssembly in WebKit was using a recursive descent parser, but used the C++ `std::expected<T, E>` type to return a result or an error
		* What was nice in a recursive descent parser where you have an `expected` is it's basically impossible to ignore the errors when you do this -- if you set it in a mode where any access of the wrong thing is going to fail, and where you cannot disregard the return value of something, makes it *almost* correct by construction when you write the parser
		* Or not necessarily correct by construction, because you still need to treat the information correctly, but makes it much easier to do the right thing and harder to do the wrong thing
		* If you compose it well, it's hard to get things like integer overflows, or out of bounds accesses, or things like that, when you're doing the parsing, because you're building it out of basic parts that you put together
		* Ends up being interesting to write a security-sensitive parser with modern tools like that
		* Nice example story -- `std::expected` is easy to like, Chris hopes there's a `?` [operator for it like in Rust one day](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#a-shortcut-for-propagating-errors-the--operator), so if there's C++ committee people listening...
		* JF says there's not for now but there's the monadic operators for C++23 the same way they're added for `std::optional`
			* Not quite the same power as the `?` operator or something like it, but somewhat novel... JF not sure it'll make it to C++26
			* JF says what's nice is you can write the scope in the if declaration position as a neat syntactic thing in C++:
				```c++
				if (auto something = make_my_expected_thing()) {
				  // happy case using "something"
				} else {
				  // sad case using "something"
				}
				```
			* [Chris quietly thinks this is a sad consolation prize]
		* One other story: Chris works on a team that parses SystemVerilog using ANTLRv4 that may be the largest ANTLR grammar
			* We've been talking a bit about the trade-offs we see there
			* Performance optimization work sometimes means re-structuring the grammar so that the generator can do better with it
			* Same interesting questions come up around memory usage and you get a lot of power from the grammar-generating that would be a lot of work to write in a recursive-descent parser form, especially as the grammar gets large
			* But there's clearly a trade-off space there, been fun to re-live this understanding of the tradeoffs
* One last thing we wanted to touch back on: difference between parse trees and Abstract Syntax Trees (ASTs)
	* We threw the terms around a bit here
	* Think it's not *formally* defined
	* But notion that a parse tree is literally the fully tree that comes straight out of the grammar's structure
	* Whereas AST will be "more reduced form" -- e.g. if I have a bunch of `+` operators strung together at the same precedence level, if I make an n-ary node that has all the operands to the strung together `+`s, that's not *strictly* what the grammar specified [it would have been deeply nested] but it's equivalent in representation, if simplied
	* So how people tend to talk about AST vs parse trees
* Good amount of knowledge talked about parsers today
* Adjourn and meet soon for another deep dive into interesting geeky topic
