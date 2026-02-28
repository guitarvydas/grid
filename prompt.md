grid lang is a new language under development. I've attached test_runner.py. show me the "grid" code snippets with newlines expanded so that I can get a "feel" for what the language is.

---

ForDeclBody is a Syntactic rule (OhmJS semantics). Why does this rule contain "spaces"?

---

You've caught a real OhmJS design issue.

In OhmJS, **Syntactic rules** (names starting with an uppercase letter) automatically skip whitespace between every term. **Lexical rules** (lowercase names) do not. `ForDeclBody` starts with an uppercase letter, so it's syntactic — and that means all those explicit `spaces` calls are redundant at best, and potentially cause subtle parse failures at worst, because OhmJS inserts its own whitespace-skipping *between* the automatic skips and the explicit `spaces` matches.

The fix is consistent: **remove all `spaces` from every syntactic rule**. They should only appear in lexical rules (like `eol`, `comment`, `listSep`, etc.) where whitespace is *not* automatically consumed.

So `ForDeclBody` should read:

```
ForDeclBody
  = identifier caseInsensitive<"as"> TypeExpr DimClause? caseInsensitive<"of"> identifier "=" Expr  -- typedUnitInit
  | identifier caseInsensitive<"as"> TypeExpr DimClause? ForTypeInitOp Expr  -- typedInit
  | identifier caseInsensitive<"as"> TypeExpr DimClause?                     -- typedOnly
  | identifier caseInsensitive<"of"> identifier "=" Expr                     -- unitInit
  | identifier caseInsensitive<"of"> identifier                               -- unitOnly
  | NonemptyListOf<ForSingleEq, andSep>                                       -- multiEq
```

And the same treatment applies throughout — `ForLoopBinding`, `LetBinding`, `CondTerm`, `NewExpr`, `PostfixExpr`, all of them. The grammar as written has `spaces` sprinkled everywhere in uppercase rules, which is the wrong idiom.

There's a secondary consequence: `andSep`, `listSep`, `rowSep` are lexical rules (lowercase) used as separators inside syntactic rules. Since the syntactic rule already skips whitespace around each separator application, the `spaces` inside those separator rules is also redundant when called from a syntactic context — though harmless rather than harmful.

The deeper fix would be to audit every uppercase rule and strip the `spaces` calls, relying on OhmJS's automatic skipping. The lexical rules (`eol`, `comment`, `number`, `identifier`, `ColName`, etc.) stay exactly as they are.

---

please audit every uppercase rules and strip `spaces` where possible.

---

I would like to remove all of the `caseInensitive<...>` calls. Can we write a simple pre-pass in Python that would remove the need for all of this noise?

---

[aborted]

---

explain why newlines are significant

---

In GridLang, newlines are the statement terminator — the language has no semicolons or other explicit end-of-statement markers. Every statement ends when the line ends.

This creates a specific problem with OhmJS's two-tier rule system:

**Syntactic rules** (uppercase names) automatically skip *all* whitespace — spaces, tabs, **and newlines** — between every term. This is OhmJS's convenience feature for languages where layout doesn't matter.

**Lexical rules** (lowercase names) skip nothing. Every character must be matched explicitly.

GridLang needs newlines to be *visible* so that `eol` can match them and terminate statements. But if the rules that contain `eol` are syntactic, OhmJS will silently consume the newline *before* `eol` ever gets a chance to match it. The statement terminator disappears.

Concretely:

```
ForLoopInline = kw<"for"> ForLoopBindings eol
```

OhmJS parses this as: skip whitespace, match `kw<"for">`, **skip whitespace including `\n`**, match `ForLoopBindings`, **skip whitespace including `\n`**, match `eol`. By the time `eol` is attempted, the newline is already gone.

This is why the grammar had to override `spaces` to horizontal-only — that suppresses newline-skipping *within* the spaces rule. But syntactic rules don't use the `spaces` rule for their automatic inter-term skipping; they have their own built-in whitespace consumer that ignores the override and always skips all whitespace including newlines.

The implication is that **any rule containing `eol` must be a lexical rule** — lowercase name — or the `eol` will never be reachable. The current grammar has all those rules as uppercase (syntactic), which is the root of the problem. The original grammar worked because `caseInsensitive<"For">` is itself a lexical-context match and the whole design stayed just barely on the right side of the line — but it was fragile. The pre-pass work has exposed the underlying tension.

The proper fix is to rename every statement-level rule to lowercase, making them lexical so newlines are preserved. That's a significant structural change to the grammar.

--- 

A partial solution to the newline problem would be to create a Python pre-pass that converts every newline (\r\n, \n) into a visible item like "⎩NN⎭" where NN is the line number in the original source. Correct?

---

Yes, exactly right.

If the pre-pass converts:

```
For i in 1 to 3
[A{i}] := "hello"
```

into something like:

```
For i in 1 to 3 ⎩1⎭ [A{i}] := "hello" ⎩2⎭
```

then the entire source becomes a single flat stream of tokens with no newlines. OhmJS's syntactic whitespace-skipping becomes harmless — it skips spaces and tabs between tokens, but the `⎩1⎭` sentinel is visible and matchable as a literal string. The `eol` rule becomes simply:

```
eol = "⎩" digit+ "⎭"
```

And you get the line number for free in every `eol` match, which is useful for error reporting.

A few things to be careful about:

**Strings and comments.** The pre-pass must not replace newlines *inside* string literals or after a comment marker `'`. A newline inside a string is part of the string value (test 30 has `\n` inside an interpolated string). A newline after `'` ends the comment but should still emit a sentinel so statement counting stays correct.

**The sentinel characters.** `⎩⎭` are arbitrary — anything works as long as the characters can't appear in legitimate GridLang source. You could equally use `§`, `↵`, or even a simple token like `__NL_1__`. The bracket form is nice because it's visually obvious and self-delimiting.

**The grammar's `spaces` override becomes unnecessary.** Once newlines are replaced by visible tokens, you no longer need `spaces := (" " | "\t")*` — the default OhmJS whitespace skipping is fine, because there are no newlines left to accidentally consume.

**`BlankLine` also simplifies.** A blank line just becomes a bare `⎩N⎭` with nothing before it, which the grammar already handles naturally.

So yes — it's a clean solution and probably cleaner than the lexical/syntactic split approach.

---

what is test 30? explain what it means

---

From the test file:

```python
("Test 30: Multi-line interpolation",
 ": name = \"world\"\n[A1] := $\"{*Loudly} I say:  \n\t\t\"\"Hello\"\", {name}!\"",
 {'A1': "{Loudly} I say:\n\"Hello\", world!"})
```

Expanding the escaped Python string, the GridLang source is:

```
: name = "world"
[A1] := $"{*Loudly} I say:  
		""Hello"", {name}!"
```

And the expected cell value is:
```
{Loudly} I say:
"Hello", world!
```

So this test is demonstrating that an interpolated string `$"..."` can **span multiple lines** — the literal newline inside the string is part of the string value, not a statement terminator. The `\n\t\t` in the middle of the string is content, not syntax.

It also shows two other interpolation features at work simultaneously:

- `{*Loudly}` — the `{*` form suppresses interpolation and emits the braces literally, so `{*Loudly}` becomes `{Loudly}` in the output
- `{name}` — normal interpolation, substituting `"world"`
- `""Hello""` — the double-quote escape inside a string, producing a literal `"Hello"`

This is the one case where a naïve newline-replacement pre-pass would break things — if you blindly replace the `\n` inside the string with `⎩2⎭`, the string value would contain the sentinel rather than a real newline.

The pre-pass needs to track whether it is currently inside an open `$"..."` string and leave those newlines alone.

---

would a post-pass that replaced all newline sentinels with simple newlines help simplify the problem?

---

Yes, and it closes the loop cleanly.

The full pipeline becomes:

```
original source
     │
     ▼ pre-pass 1: keyword lowercasing
     │
     ▼ pre-pass 2: newline → ⎩N⎭  (skipping inside strings)
     │
     ▼ OhmJS grammar (all syntactic rules, no eol complexity)
     │
     ▼ CST / semantic actions
     │
     ▼ post-pass: ⎩N⎭ → \n in any string values
     │
     ▼ final output
```

The grammar simplifies substantially:

- `eol` becomes a plain terminal: `eol = "⎩" digit+ "⎭"`
- `BlankLine` becomes `eol` directly
- `spaces` override is no longer needed — default OhmJS whitespace skipping is fine
- Every statement rule stays syntactic (uppercase) without any tension

The post-pass is trivial — it only needs to touch **string literal values** that the semantic actions have already extracted. At that point you're working with plain Python strings, so it's just `value.replace("⎩N⎭", "\n")` — or more precisely, a regex replace of `⎩\d+⎭` → `\n`.

The only subtlety worth noting: by the time the post-pass runs, the sentinel carries the original line number. If you want to preserve that for error messages or debugging you'd extract it before replacing. Otherwise just strip it.

So yes — pre-pass handles the input, post-pass handles the output, and the grammar itself becomes clean and straightforward in between.

---

Let's say that the post-pass replaces all newline sentinels with a Python comment `⎩NN⎭ --> #NN\n` except inside strings where `⎩NN⎭ --> \n`. Is this simple to write in python?

---

Yes, very simple. The post-pass only ever sees two contexts — inside a string value or outside one — and by the time it runs, the semantic actions have already done the parsing, so you're just iterating over the output values, not re-parsing anything.

Something like:

```python
import re

_SENTINEL = re.compile(r'⎩(\d+)⎭')

def postpass_value(value, in_string=False):
    """Replace sentinels in a single extracted value."""
    if in_string:
        return _SENTINEL.sub(lambda m: '\n', value)
    else:
        return _SENTINEL.sub(lambda m: f'# {m.group(1)}\n', value)

def postpass_program(lines):
    """Replace sentinels in generated code (list of output lines)."""
    return _SENTINEL.sub(lambda m: f'# {m.group(1)}\n', lines)
```

The reason it's simple is that the hard work — distinguishing "is this sentinel inside a string or not?" — was already done by the OhmJS grammar. The grammar knows which sentinels are inside `PlainString` or `InterpolatedString` nodes and which are statement terminators. Your semantic actions just call the right variant when extracting values:

- String node → `postpass_value(s, in_string=True)` → sentinel becomes `\n`
- Everything else → `postpass_value(s, in_string=False)` → sentinel becomes `# NN\n`

You never need to re-scan or re-tokenise. The context is already resolved by the parse tree.

---

List the keywords of this language.

---

From the test suite and grammar, here are the keywords grouped by role:

**Declaration / definition**
`define`, `end`, `type`, `function`, `subprocess`, `privatehelper`

**Variable binding**
`for`, `let`, `input`, `output`, `push`, `return`, `init`, `new`, `with`, `super`

**Control flow**
`if`, `then`, `else`, `elseif`, `do`

**Type system**
`as`, `number`, `text`, `dim`, `of`, `in`

**Operators**
`mod`, `not`, `and`, `or`

**Sequence / range**
`to`, `step`, `index`

**Other**
`label`— used only in `Results!Quarter.Label{...}` dimension labelling

That's **35** keywords total, which matches what's currently in the pre-pass `KEYWORDS` set — with one caveat worth flagging: `index` is missing from the pre-pass. It appears in loop bindings like `For b in 9 to 15 step 3 index i` and would need to be added.

---

explain the syntax of strings in grid

---

From the test suite, GridLang has two string forms.

---

**Plain strings** `"..."`

Delimited by double quotes. The only escape mechanism is doubling the quote character — `""` inside a string produces a literal `"`. There is no backslash escaping.

```
: t = "Hello"
: q = "I say ""Hello"""    →  I say "Hello"
```

---

**Interpolated strings** `$"..."`

Prefixed with `$`. Inside the string, `{expr}` interpolates the value of an expression. Everything else is literal text.

Several special forms exist inside `$"..."`:

- `{expr}` — interpolates the expression value
- `{expr, N}` — interpolates with padding; positive N pads right (right-aligns), negative N pads left
- `{}` — literal empty braces, no interpolation
- `{{` — literal `{` (escaped open brace)
- `{*text}` — suppresses interpolation; emits `{text}` literally into the output (the `*` is stripped, the braces are kept)
- `{{{*text}` — produces `{{{text}` literally

```
: name = "world"
[A1] := $"Hello, {name}!"          →  Hello, world!
[A1] := $"Number: {num, 5}"        →  Number:    42   (right-padded to width 5)
[A1] := $"Number: {num, -5}"       →  Number: 42      (left-padded)
[A1] := $"Empty: {}"               →  Empty: {}
[A1] := $"Escaped: {{{*star"       →  Escaped: {{{star
[A1] := $"{*Loudly} I say: {name}" →  {Loudly} I say: world
```

Interpolated strings can also **span multiple lines** — a literal newline inside `$"..."` is part of the string value, not a statement terminator (Test 30).

---

**Common to both forms**

- `""` is the empty string
- Quote escaping with `""` applies in both plain and interpolated strings
- There is no string type coercion — `text` variables hold strings, `number` variables hold numbers, and mixing them requires explicit interpolation or concatenation with `&`

---

concatenate all test cases into one long test case in markdown that I can copy
