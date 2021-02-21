# Episode 2: `https://tlbh.it^M`

<audio id="audioplayer" src="https://traffic.libsyn.com/secure/tlbhit/tlbhit2.mp3" controls="controls" class="podcast-audio" preload="auto"></audio><div class="playback-rate-controls"><ul><li><a href="#" onclick="setPlaybackSpeed(0.5)">0.5⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1)">1⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.25)">1.25⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.5)">1.5⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(1.75)">1.75⨉</a></li><li><a href="#" onclick="setPlaybackSpeed(2)">2⨉</a></li></ul></div>

### Artisinal hand-crafted intro [00:00]

* Our friends are all starting podcasts and they're better than us at getting episodes out quickly :-)
* It's been a while... let's say we're going for more the artisinal hand-crafted thing
* Only choice at this point is to claim we're going for quality over quantity... or something...
* You can see [the bubbles](https://en.wikipedia.org/wiki/Pipeline_stall) in our hand-crafted episode designs so you can tell they're made with love

### Standard disclaimer [00:30]

* Standard disclaimer: here to share our love of random systems and systems-programming topics
* But we only know so much! Will try not to say things that are wrong
* Will followup with "errata" (corrections/clarifications) as we find out about them and put them up on (this) website
* We do the "lifelong learners" thing, always trying to push the boundaries of things we know about and have conversations about what's interesting to develop and hone our understanding

### The "silly" interview question [00:55]

* Bunch of ideas for things to talk about
* Today we're going to go kind of a "silly" interview question
* We've heard people do ask this question!
* Walk into the interview, interviewer says "tell me what happens when you put
  an address into the URL bar and hit enter **in as much detail as humanly
  possible**?!"
* Probably not going to cover a lot of things, we're shooting for ~1 hour,
  everybody listening will know a bunch more than we do about these things, so
  tweet [@TLBHit](https://twitter.com/tlbhit) with more juicy details we can
  note in the show notes or in a future episode
* Not going to start from Maxwell's equations / SPICE simulations of
  transistors, gonna start a *little* higher than that

### Timeless questions [02:00]

* Related story: when working on chipsets knew person who would slam
  motherboard down on the table, point at it, and ask the candidate to describe
  how some aspect of it worked
* Not recommended, but fun concept, in the sense it's easy to lose yourself in all the wonderful details of a modern machine
* Lots of complexity comes together to make these things happen (and some complexity we got via the evolutionary process!)
* What's great about modern computers is how much of it is actually possible to
  understand and possibly even do yourself
* Projects doing PicoSoCs
* [Open source software projects like QEMU](https://en.wikipedia.org/wiki/QEMU) where you can create a
  software emulation layer for an entire machine from scratch
* Things like
  asm.js or [WebAssembly where you can create a familiar machine and operating
  system experience in a
  browser](https://github.com/WebAssembly/tool-conventions/issues/27), etc.
* All the visibility of modern computing systems and the fact you *can* understand everything down to nearly the transistors is in a way what's beautiful about working in computers.
* But *just* as importantly you don't *need* to know it all to use them well --
  we have these nice abstraction layers and you can keep diving down into the
  layer that interests you and snowball-up more knowledge and capabilities as
  you go.
* This is really the power of abstraction.
* So this interview question is well trodden in a sense and can apply to many
  different fields, adapted to different areas.
* Everybody has to deal in abstraction, one of the few fundamental human
  faculties.
* [Hume had described a few different fundamental ways](https://iep.utm.edu/hume-ima/#SH3b) that humans come up with things like imagination, abstraction, and such.
* Related: [powers of ten video from 1977](https://www.youtube.com/watch?v=0fKBhvDjuy0): shows expanding scale from a cell on somebody's hand up to the highest abstractions in the universe and down the smallest ones all in one dialog/visualization. Fun and enlightening!
* Both abstraction and decomposing things into the smallest pieces you can both fun ways to learn.

### What was the question again? [04:15]

* Back to the fun question for today!
* What happens when you go to the browser's address bar, type "https://tlbh.it" and then hit enter.
* Have to start with the keypress, you pressed enter!
* Out in physical world before physical I/O becomes digital I/O.
* Some of us are familiar with this basic concepts from Tron (or Tron: Legacy, or its Draft Punk soundtrack), all of which will be helpful.

### Starting in physical IO space [04:50]

* Keyboards! Fundamental component of computer I/O design e.g. for input of text (still more popular than footpedals)
* All also (conceptually) based on switches! Just like internals of computer are based on switches -- took the idea and put them both inside the computer but also underneath your fingertips.
* Going to go with mechanical keyboards because they're enjoyable, make a beautiful clacky noise.
* Very classic keyboard was the IBM Model M keyboard (@cdleary had one of those!), had a "buckling spring" design -- buckling caused switch to close.
* Modern keyboards instead have a little plastic "leaf" that prevents electrical connectivity, when you move it out of the way with your finger press electrical connectivity is established. Switch action: on/off, controlled by your finger.
* Keyboard has a little microcontroller inside of it, it's looking for things that get pressed, usually done through a "general purpose input/output pin" (GPIO).
* Microcontrollers can look at voltages / whether things are connected to it in order to ask "is this a zero or a one right now" via these GPIO pins. Some of them are configured to read (to look for a 0 or 1 voltage level and say which one is currently observed when it's sampled by the microcontroller).
* Microcontroller reads these lines, then figures out what key (or set of keys) are pressed based on the 1s and 0s lines for the GPIO input lines that are 1s going to the microcontroller.
* So in our case, it sees the row/column activated means that the "enter" key is pressed (because that's what the row and column I see "map to" in its firmware running on the microcontroller).

### How can we relate this back to Tron though? [06:40]

* This is the grid from Tron presumably? And the lightcycles will need to come in to take us to the computer proper.
* Gotta send stuff over to the computer!
* In modern era USB devices talk this standard USB Human Interface Device (HID) protocol that's layered on top of USB transactions.
* What you do is send packets to a *standard driver* inside of your computer that knows how to talk to these human interface devices.
* Good we've standardized on at least how keyboards and mice tend to work at this point in computer history. (Joysticks: let's not go there.)

### Brief intro to USB [07:15]

* USB is a neat, modern, minimal-number-of-wires protocol for peripherals talking to computers.
* What you do is wiggle these differential transmission lines -- in order to get good signal integrity there's common ways to do these protocols for things talking over wires to computers (differential transmission, NRZI & long-term-balanced balanced codings, etc).
* You're able to wiggle these transmission lines at pretty high speeds these days -- lots of work has gone into figuring out how to make the minimal number of wires to go quickly when toggling between zeros and ones.
* @cdleary only knows about low(/full/high) speed USB from a random project I had worked on in the past, USB 3 may be interestingly different to achieve such high speeds.
* Serial engine that turns signals into packets and packets turn into transactions, OSI-style model of different layers of the communication protocol pieces.
* Few different types of transfers in USB: keyboard firmware going to shove scan code into interrupt transfer that goes to the host, and that goes out to the host, on the wire (via the lightcycle :-)

### Enter vs return? [08:30]

* Is there a difference between enter and return? `^M` vs `^V` say? [ed: are "return" and "enter" keys meaningfully different?!]
* Remapped keyboard for caps lock to be "return" (whereas my normal key is "enter") and it seemed to do the same thing, so not sure where it makes a difference.
* @jfbastien remaps caps lock to be escape, traditional vi vs emacs difference?
* @cdleary couldn't figure out how to undo the mapping.
* Classic interview question where answer is ":q".

### Into the chipset [09:05]

* Now we're getting to the motherboard "chipset": it's called a chipset because it's literally a set of chips, the little rectangles with the black epoxy and logos on top
* There's a thing inside of your "motherboard" (big green Printed Circuit Board with all the chips on it inside of your computer)
* Called the "southbridge": talks to computer peripherals, things you're going to plug into your computer to interact with the CPU / core complex
* You can see the term "bridge" here, it's "bridging" or turning other ways of communicating *into* something the CPU core complex understands more natively like PCIe reads and writes
* One of the things that usually lives in the southbridge is a USB "host controller"
* USB host controller is going to help talk to all the USB devices that you might plug into your computer
* The USB host controller talks to the USB devices over the wires that are plugged in from USB on one "side", and talks PCIe to the CPU on the other "side", over memory writes/reads to addresses that get configured on boot: this is the part that interfaces with the CPU / core complex
* The writes that get routed from the USB host controller towards the core complex may have to go through a device MMU, or IOMMU, which can prevent wild writes from devices to arbitrary physical memory locations -- notably this IOMMU can have a TLB for fast caching of address translation -- for places we write to frequently we'll likely get TLB hits! 
* Things like DMA (Direct Memory Access) can happen through the PCIe-side connections [where peripherals can dump things directly into the same address space observed by the CPU]
* USB host controller is going to need to inform the CPU about the interrupt (with the keypress payload) that came in from the keyboard peripheral so it can handle it appropriately
* Standard PCIe interrupts (e.g. MSI-X) are just little write packets that happen over an address space to a memory location
* Those get serialized over the PCIe wires
* Those get serviced in a (coalesced) interrupt handler inside of the CPU
  * So I'll say "hey CPU I have something that I need to tell you about / need you to do, I'm a peripheral"
  * Then the kernel will come pick up that note (which has been written to a memory location) inside of the "bottom half" interrupt handler
  * Kernel breaks interrupt handling into two pieces: bottom half and top half
  * Bottom half just quickly tries to handle "oh there's something here, let me make a note of that"
  * Top half comes along and tries to actually do the work when there's time
  * Instead of keeping interrupts masked for a really long time will punt things to happen in the top half in a kernel process, so that's just a software architecture / terminology thing
* Ultimately events are pushed through file descriptors (in our particular case), as a record that indicates "hey there's an event that happened on this input device of this type with this code and it had some value associated with it" -- usually this data record is a "triple" for the input device drivers

### Why are input events exposed through file descriptors? [12:00]

* Why are events pushed as file descriptors?
* A bit odd that when you put a key on the keyboard there's files involved *with your keyboard*
* Is it because everything in UNIX style is a file descriptor?
* Guess it makes it easy to handle these types of functions like select/poll/epoll to have files, but why is it fundamentally?
* Right, kernel is trying to expose everything in a uniform way
* Could have just arbitrary memory locations that are changing that are accessible to programs in userspace
* OR could use this already existing abstraction of a file to talk about things that have happened and then people can look at files
* In Linux kernel example is something like SysFS are ways to askthe kernel about arbitrary properties like "what is the connectivity of my devices"
* Lots of things riding on this filesystem abstraction concept

[Note: for low latency communication between peripherals and userspace folks often do map registers from the device's PCIe memory space directly into userspace (as uncacheable memory) and have a protocol for interacting with the device so that you don't need to go through filesystem syscall overheads, folks are continuing to try to build reusable abstractions for this like `io_uring`.]

### Through the window manager to the browser-UI-owning process ~12:15

* In our particular case we'll notice the interrupt came from the keyboard device
* We'll serve it up to the driver which will push that event over that file descriptor
* Kernel produces a keycode
* If you're running X11 / Xorg based window manager the X server is going to translate the keycode into a symbol (which is basically just a fancy keycode but at the X11 abstraction layer)
* The X server will do a file descriptor event loop to look for these keycodes that are happening and push them to various windows which might be looking for what's happening with the keyboard
* Thread that spins and waits for these notifications and then decides what to do when events come in
* Like JF said, something like a select or an epoll would happen where you get woken up when a file descriptor it's watching gets updated
* You see the input you notify the X client which is a window of some kind (in this case the browser window), it'll be informed that an enter has been pressed
* So now that event that has been pushed to the browser window has to be handled by the browser process (which is the window-manager-connected application)
* Browser has a "thing" (i.e. client handle) that connects to the window manager and it gets the event
* Browser notices that the URL bar widget inside of the "browser chrome" -- which is the part of the browser that's not the content being displayed by a web page but that part that's wrapped around the content displayed by a web page -- is the thing that has focus
* Fun fact! In Firefox the widgets were even implemented with a web-like technology called XUL that uses XML based widget descriptions and JavaScript event handlers
* So `onKeyPress` event you'd use in a web page  is also generated for the URL bar widget
* Reuse across content and chrome inside of the Firefox browser architecture
* Similar things happen for native widget toolkits as well
* This "chrome" is part of the root window for the process
* But modern browsers have processes that manage groups of tabs for isolation so things like crashes are not effecting all web pages running inside of the project, that's been done through various initiatives like electrolysis in Firefox

### Which parts of the browser might share a process? [~15:15]

* Interesting: what parts of the browser are sharing across processes?
* Chris Palmer presentation at Enigma talking about how sandboxing works for Chrome
* One process for browser root, one for GPU process, bunch of separate renderer, networking, storage processes
* Evolved over time which parts have their own process or not
* Sometimes will put things in the same process to save resources
* ... thousands of tabs maybe, but don't want thousands of processes!
* Interesting tradeoff that they do

### Inter-Process Communication patterns [16:20]

* Classic question of how do you when you split things into processes, how do you not pay the penalty; e.g. retain fast communication even though we separated them into process isolated bits
* Interesting part of the design of a browser (or a general multi-process application architecture!)
* When you can have asynchrony you can have but but when you want fast communication between processes how do you avoid getting slammed by context switch overheads
* Funny that Chrome is named after the part that's been minimized / that you're not supposed to see!
* Depending on how keypress notification is handled, may have one process sending to another process, e.g. one displaying currently displayed tab
* Tell it to "please navigate to the target URL because enter was pressed"
* Cross process messaging, can be done in a bunch of ways
* Can use something like pipes, but in a lot of cases you want to use something like shared memory
* Shared memory itself is really neat, and not just because it involves TLB hits!
* Also shared memory is an interesting way that two processes can share physical pages at (potentially) different virtual addresses
* Interesting: shared memory is not something that C/C++ acknowledge really exist in the machine model
* Same way in C/C++ before C++11, threads didn't exist in the abstract machine model described by the language
* In *reality* they exist of course, but question of what's directly addressed by language semantics / model
* The way it's modeled right now is it's basically addressed like external modifications, so really ought to use volatile to do shared memory accesses
* Probably need a separate synchronization primitive, at least hypothetically, to do cross-process locking say -- because needs different guarantees from ones you get from threads which *do* live inside of the abstract machine model

### Tabs and back/forward cache [19:20]

* One thing about tabs, they have a navigation cache for going backwards and forwards
* When we're updating the location -- say we're starting on a blank tab, which are their own entity in the browser universe, they may take you to a special display page or similar
* Then when you navigate it away to a particular website (like tlbh.it) then if you hit the back button it may take you back to the blank tab page or where you were before the navigation happened
* What's funny is apparently one of the most complicated pages in the whole browser is about:blank -- weirdly complicated for some reason!

### Working at places and not knowing everything [22:40]

* Funny to work for a browser company (Mozilla in @cdleary's case) but mostly because of working on the JS engine learn things as they pertain to that one part that @cdleary had worked on
* Learn maybe about some of the interfacing parts, like how DOM nodes get reflected into JS objects or how interop with the browser-level cycle collector is supposed to happen


* Notion that Isaac Newton was perhaps the last person to know all of human knowledge at one time
* Who was the last person to know all of CS?
* Kind of winging it, not sure how interviewer would feel about our answer
* We'll just assume we're doing well on the interview and keep going on
* Benefit of doing our own podcast is we pretty much have to be here no matter how badly we do on the interview question

### Domain name to IP resolution [24:40]

* Now that we've parsed the URL we have the TLD, the domain, the subdomains (none)
* Going to ignore the rest of the request for now, how do we talk to that server?
* Have to figure out how to talk to the server that name corresponds to?
* Resolve via DNS (Domain Name Service) resolution
* `.it` is the top level domain, do we have to go to Italy? Not quite how it works...
* There's DNS servers that just map all of the domains to IP address and such
* They do more than IP addresses but by and large this is what we care about here
* What's interesting: DNS resolution is notoriously totally insecure! Done in the clear, uses UDP packets
* Going to need to craft and send out a packet here (haven't talked about packets yet)
* Bunch of things on top of this basic concept: recently Firefox rolled out DNS resolution over https, used CloudFlare to do resolution

### Stacks of trust and probabilistic data structures [26:15]

* All stacks of trust right? Between "trust no one ideal" where you would only have to trust yourself how do you stack things on top and keep everything copacetic
* Not just roots of trust all the way down also caches all the way down (as we know cache invalidation is hard!)
* First thing browser does before it reaches out, asks whether it had looked up the domain name before
* When it hasn't looked up the domain name before asks "is this URL a known malicious website?"
* Has a list of websites you just don't want to go to, will suggest that it looks malicious
* Something called Google Safe Browsing inside of Chrome that's also used by other browsers
* There's a *lot* of websites and the list changes pretty frequently
* Instead of local browser having full list of all malicious sites...
* Google fun interview tip is to know about bloom filters ;-)
* Originally implementation of safe browsing used bloom filters:
  * You ask whether domain is safe, it will either say "yes" or "I'm not sure"
  * When "not sure" asks a separate server with the full list (Google central server) whether it is or in
* When your browser already has it cached doesn't have to do that extra round trip
* WebKit noted they were going to start proxying safe-browsing requests through separate server led to a lot of discussion

### Protocol changes/upgrade [28:45]

* We were talking about how to parse a given protocol

### Surprisingly nuanced: unicode domains [~32:30]

* Unicode and domain names
* Cyrillic characters might look exactly like what you would expect from roman alphabet

### Signoff [56:10]

* Took a while to record this "episode 2", hope we take less time to record the next one
* If people have questions/answers/comments / things they want us to talk about / errata to suggest hit us up on twitter @TLBHit
* We don't know how email works
* Whole nother episode, how does email work
* Every program has to grow until it does email
