Just quick feedback on:

**What's ambiguous or underspecified:**

- **`[B1]` vs `[A1]` inside type bodies** — the binomial type uses `[B1] := 1` inside a type definition. Is that always valid? Are cell refs relative or absolute inside types?

Type and subprocess define their own local grid. Functions use the global grid.

- **`Let D[A1] = 1`** — here `[A1]` is used as an _index_ into a dimensioned array, not a cell assignment. The grammar needs to distinguish these two uses of `[...]`.

Note that D[A1] is a shortcut for D([A1]) (syntactic sugar). There is also D{1, 1} equivalent to D({1, 1}). If D is a variable then the parameter is an address (you can’t have a function variable).

Also, I wish to make « Let » optional if the grammar allows it.

- **`push` semantics** — sometimes `push var = expr`, sometimes `push X(i) = expr`, sometimes `push obj.field = expr`. The LHS forms need to be fully enumerated.

LHS needs to be a variable or a cell/array item(s)

- **`For` overloading** — `For` does at least 5 different things: iteration, variable declaration, constraint declaration, type-constrained declaration, and loop-with-block. Disambiguating these in a PEG grammar requires careful ordering.

I need to write more about the « iteration » bit. The various declarations are also for « Let », « Input », « Output » and « : ».

You can do For declaration with block too (although I recommend « Let » for that use.)

- **`Results!Quarter("Q2")`** — the `!` dimension accessor syntax only appears once. Its full form isn't clear.

The name of the dimension must be declared with « Dim ». I will share a write-up about that.

- **`{i :A}` column interpolation** — appears in Test 165 but the rule isn't obvious from examples alone.

That means [A] if i is 1, [B] if i is 2, etc. You could also use [{i :C}] for [C] if i is 1, ...

- **`$secret` / `$Point.OnTheRight`** — `$` prefix for privacy/hidden, but only 2-3 examples.

It is hidden yes

- **Subprocess call syntax** — `SplitName([A1], [^B1])` vs `DoublePush(3, [^A1])` — output binding via `[^...]` as an argument is unusual.

Used for output binding yes

- **`tyresize_code` fragment** — ends mid-sentence (`if len(make) = 4` ), so that's intentionally incomplete.

That is a guard. The rest of the code will only execute if the condition is true (except for dependencies, in this example make declaration comes first).

![outdated-syntax](outdated-syntax.md)

---

Actually I now see that won’t work. How do we know if D([A1]) means « take the value of cell A1 and use it as index in D » or means « the cell of D with the address A1 »? I think Excel uses the syntax D!A1 but I don’t like it (I mean, no harm adding support to D![A1] but I don’t want it to be the standard).

My original idea was that an input can be of type « cell address », in which case the value of a cell is not used but the address (A1) is passed to the function instead. Then D([A1]) uses that concept to reference to the cell in D. But that’s too much overload and will confuse developers.

I think I need to be pragmatic and use different semantics when D is a variable not a function, even if the syntax is the same.

D[A1] = the cell of D with the address A1
D([A1]) = take the value of cell A1 and use it as index in D

While I am at it, we can allow round brackets with multiple indexes:

D(1, 3, 1)

Which will be same as:

D{1, 3, 1}

and same as:

For indexes = {1, 3, 1}   ’indexes can be a calculated value
D(indexes)

Sorry if I am sharing too much of my internal process, it helps to put it in writing.