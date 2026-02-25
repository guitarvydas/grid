I've just begun to wrap my head around what you've sent me. (Sorry for the delay).

At first, in general, I just want an eagle's eye overview. I just want to "get a feel" for what code in the language looks like. I would have manually chopped and reformatted test_runner.py, but, it dawned on me to get Claude to do.

This note captures some of the intermediate work...

I'm going to pause here just in case I'm in the weeds. Tell me what you think.

![Note 2026-02-25](Note%202026-02-25.md)

---

let's begin by writing only the grammar in OhmJS as best as we can

---

![Grammar notes](Grammar%20notes.md)

---

I created `grid.ohm` and stuck it into [ohm-editor](ohmjs.org).

It seems to "compile clean", i.e. the grammar seems OK, such as it is.

I stuck the "tyre" example into the examples window (bottom left) and it seems to parse ok.

![](Parse%20light%20test%20Screenshot%202026-02-25%20at%208.15.41%20AM.png)

I'm going to pause here just in case I'm in the weeds. Tell me what you think.

My gut says, the next steps would be
- continue with the grammar so that it handles ~90% of the language (the last bit is the hardest and we can kick that can down the road)
- maybe write some more test cases to test the edge cases of the grammar
- once the grammar is in place, there are a number of options
	- transmogrify `grid` code to Python
	- or, write a full-blown compiler
- I would begin with an attempt at transmogrifying to Python
	- this forces us to think about the "semantics" of what the language needs to do (by "us" I probably mean "me", you probably already have a strong understanding)
	- we can abort and switch to building a full-blown compiler at any time we feel comfortable
	- frankly, I don't see any reason to bother building a compiler, since that's a lot of work and already existing tools like Python, LLVM, *any other language* already do all of this work
- Here's how I (currently) think about transmogrifying `grid` code examples to Python
	- write `grid.rwr` to do an identity transform (this would do "nothing", but test that the mechanics are in place)
	- a rewrite file `grid.rwr` acts as the back end to an OhmJS grammar
		- stock OhmJS wants you to write the back end in Javascript
		- I've discovered that - for transmogrifying to another language, like Python - you don't need all of Javascript, so I invented a DSL `.rwr` that contains only the operations I need for doing transmogrification (something like 6 operations (don't quote me), all concerning string manipulation) - the result is a way to write a "compiler" in a very concise manner in weeks instead of years
	- hack on `grid.rwr` to begin mapping a simple example of `grid` code to working Python
- Yes, the semantics of `grid` probably don't easily flow into the semantics of Python, or assembler, but, that's a menial issue - compiler writers are used to the idea of writing routines to enact certain semantics and to "call" the routines from compiled code (e.g. like C does for startup using crt0.c). It's just the accepted way of writing a compiler. You can probably imagine the semantics of `grid` written out in Python. In general, I tend to choose a *very* low-level language as the target, e.g. assembler, or lisp, or Javascript, or WASM, or..., because sometimes higher level languages make it harder to do certain things and cause a lot of hand-wringing and workarounds. In the end it boils down to machine code, no matter what intermediate language you use.
- The stuff I'm doing (PBP) is concerned with low-level message passing, and concurrency without using thread libraries or processes (i.e. thread-like behaviour in pure Javascript, Python, etc.). If you already have constraints working in `grid` then you've probably already solved a lot of the problems. I can kibitz on  nuances and how to do "layering" cheaply, when the time comes, but it's probably too early in the process for that ("layering" is not very common, so don't worry if you don't understand what I just said :-)