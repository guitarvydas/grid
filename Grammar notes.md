Let me read the OhmJS skill first, then work through the grammar systematically.No OhmJS skill, so working from knowledge. Let me build this carefully.Now let me review it critically for consistency and fix issues before presenting:Several OhmJS-specific issues to fix — separator rules must be arity-1, inconsistent arity in alternations, missing `ArgList`. Let me fix them all:The issue is that `eol` (a blank-line handler) makes `Statement` nullable. The fix: remove `eol` from Statement and handle blank lines at the Program level with a dedicated `BlankLine` rule.Clean. Now let's do a quick smoke test against a handful of the actual code snippets:26/28 already. Two failures to diagnose:Two clear fixes: `GlobalVarDecl` simple branch needs to allow `RangeExpr` as a value, and `ColName` should allow lowercase letters (the tests use `[a{i}]`):28/28. Let's add more tests from the harder cases:15/19, four targeted fixes needed:Now I have all four root causes clearly. Let me apply all fixes at once:47/47. Let's copy to outputs and present:610 lines, **243 rules**, **47/47 smoke tests passing** against actual snippets from the test suite. Here's a summary of the key decisions made:

**Structural choices:**

- `eol` (not `end`, which is OhmJS built-in) terminates every statement — newlines are significant
- `spaces` overridden to horizontal-only (`" " | "\t"`) so newlines stay visible for statement termination
- `BlankLine` at the `Program` level absorbs empty lines without making `Statement` nullable

**Tricky resolutions:**

- **`For` overloading** — split into 7 variants ordered most-specific first: `ForLoopInitBlock`, `ForLoopIterBlock`, `ForTypedWith`, `ForTypeInit`, `ForConstraint`, `ForDecl` (with sub-cases)
- **`RangeExpr` on RHS** — `GlobalVarDecl` and `ForDecl` use `RangeOrExpr` (tries `RangeExpr` first) so `: seq = 1 to 6 step 1.5` works
- **`dim` in expression position** — `PostfixExpr` has a `-- dim` alternative so `{10, 11} dim {*, 1}` parses as a postfix operation
- **Interpolation args** — `{num, 5}` uses `InterpContent = Expr ("," Expr)?` to capture the padding format directive
- **`new id(args) with (fields)`** — added as the highest-priority `NewExpr` variant
- **Column names are `letter+`** (not `upper+`) to allow lowercase like `[a{i}]`
- **`VarInitClause`** covers `= expr`, `init expr`, and `or = expr` for typed global var declarations

**Known open items** (from previous analysis): the `!` dimension accessor in expressions, the `{*...}` star-escape semantics in interpolated strings, and subprocess `.grid` result access are lightly covered and may need refinement as the compiler evolves.

# GridLang OhmJS Grammar

```
GridLang {

  //----------------------------------------------------------------
  // Top-level
  //----------------------------------------------------------------

  Program = (Statement | BlankLine)*

  BlankLine = comment? ("\r\n" | "\n") spaces

  Statement
    = TypeDef
    | NumericSubtypeDef
    | FuncDef
    | SubprocessDef
    | PrivateHelperDef
    | InputDecl
    | OutputDecl
    | ForStmt
    | LetStmt
    | IfStmt
    | PushStmt
    | ReturnStmt
    | SubprocessCall
    | CellAssign
    | GlobalVarDecl
    | DimLabel


  //----------------------------------------------------------------
  // Type definitions
  //----------------------------------------------------------------

  TypeDef
    = caseInsensitive<"Define"> spaces identifier spaces caseInsensitive<"as"> spaces caseInsensitive<"Type"> TypeParent? eol
      TypeMember*
      caseInsensitive<"End"> spaces identifier eol

  TypeParent = "(" identifier ")"

  TypeMember
    = FuncDef
    | SubprocessDef
    | PrivateHelperDef
    | InputDecl
    | OutputDecl
    | CellAssign
    | ForStmt
    | LetStmt
    | PushStmt
    | SuperCall
    | GlobalVarDecl


  SuperCall = caseInsensitive<"Super"> "(" ArgList ")" eol

  ArgList = ListOf<Expr, listSep>

  //----------------------------------------------------------------
  // Numeric subtype  e.g. Define RateValue as Type(Number) >= 0.0 <= 1.0
  //----------------------------------------------------------------

  NumericSubtypeDef
    = caseInsensitive<"Define"> spaces identifier spaces caseInsensitive<"as"> spaces
      caseInsensitive<"Type"> "(" identifier ")" NumericConstraint* eol
      caseInsensitive<"End"> spaces identifier eol

  NumericConstraint = spaces compOp spaces Expr

  //----------------------------------------------------------------
  // Function / Subprocess / PrivateHelper definitions
  //----------------------------------------------------------------

  FuncDef
    = caseInsensitive<"Define"> spaces QualifiedName spaces caseInsensitive<"as"> spaces caseInsensitive<"Function"> eol
      FuncMember*
      caseInsensitive<"End"> spaces QualifiedName eol

  SubprocessDef
    = caseInsensitive<"Define"> spaces QualifiedName spaces caseInsensitive<"as"> spaces caseInsensitive<"Subprocess"> eol
      FuncMember*
      caseInsensitive<"End"> spaces QualifiedName eol

  PrivateHelperDef
    = caseInsensitive<"Define"> spaces "$"? QualifiedName spaces caseInsensitive<"as"> spaces caseInsensitive<"PrivateHelper"> eol
      FuncMember*
      caseInsensitive<"End"> spaces "$"? QualifiedName eol

  FuncMember
    = InputDecl
    | OutputDecl
    | ForStmt
    | LetStmt
    | IfStmt
    | PushStmt
    | ReturnStmt
    | SubprocessCall
    | CellAssign
    | GlobalVarDecl


  QualifiedName = identifier ("." identifier)*

  //----------------------------------------------------------------
  // Input / Output declarations
  //----------------------------------------------------------------

  InputDecl  = caseInsensitive<"Input"> spaces InputVarList eol
  OutputDecl = caseInsensitive<"Output"> spaces identifier spaces caseInsensitive<"as"> spaces TypeExpr InitOrEqClause? eol

  InputVarList = NonemptyListOf<InputVar, listSep>

  InputVar
    = identifier spaces caseInsensitive<"as"> spaces TypeExpr DefaultClause?  -- typed
    | identifier DefaultClause?                                                -- plain

  DefaultClause = spaces caseInsensitive<"or"> spaces "=" spaces Expr

  InitOrEqClause
    = spaces caseInsensitive<"init"> spaces Expr  -- init
    | spaces "=" spaces Expr                       -- eq

  //----------------------------------------------------------------
  // FOR statement  (ordered most-specific first)
  //----------------------------------------------------------------

  ForStmt
    = ForLoopBlock
    | ForLoopInline
    | ForTypedWith
    | ForTypeInit
    | ForConstraint
    | ForDecl

  // For i in 1 to 3 do ... End
  // Also: For letter as text init expr do ... End
  ForLoopBlock
    = ForLoopInitBlock
    | ForLoopIterBlock

  ForLoopInitBlock
    = caseInsensitive<"For"> spaces identifier spaces caseInsensitive<"as"> spaces TypeExpr spaces ForTypeInitOp spaces Expr spaces caseInsensitive<"do"> eol
      Statement*
      caseInsensitive<"End"> eol

  ForLoopIterBlock
    = caseInsensitive<"For"> spaces ForLoopBindings spaces caseInsensitive<"do"> eol
      Statement*
      caseInsensitive<"End"> eol

  // For i in 1 to 3   (standalone / guard-style)
  ForLoopInline
    = caseInsensitive<"For"> spaces ForLoopBindings eol

  ForLoopBindings = NonemptyListOf<ForLoopBinding, andSep>

  ForLoopBinding
    = identifier spaces caseInsensitive<"in"> spaces RangeOrSet spaces caseInsensitive<"step"> spaces Expr spaces caseInsensitive<"index"> spaces identifier  -- withStepIndex
    | identifier spaces caseInsensitive<"in"> spaces RangeOrSet spaces caseInsensitive<"index"> spaces identifier  -- withIndex
    | identifier spaces caseInsensitive<"in"> spaces RangeOrSet spaces caseInsensitive<"step"> spaces Expr         -- withStep
    | identifier spaces caseInsensitive<"in"> spaces RangeOrSet                                                    -- plain

  RangeOrSet
    = ArrayLit    -- set
    | RangeExpr   -- range

  // For V as tensor with (name = "V", grid DIM {4,4,2} = expr)
  ForTypedWith
    = caseInsensitive<"For"> spaces identifier spaces caseInsensitive<"as"> spaces identifier spaces
      caseInsensitive<"with"> spaces "(" ForFieldList ")" eol

  ForFieldList = NonemptyListOf<ForField, listSep>

  ForField
    = identifier spaces caseInsensitive<"dim"> spaces DimSpec spaces "=" spaces Expr  -- dimField
    | identifier spaces "=" spaces Expr                                                -- eqField
    | identifier                                                                        -- bare

  // For acc as text init ""
  ForTypeInit
    = caseInsensitive<"For"> spaces identifier spaces caseInsensitive<"as"> spaces TypeExpr spaces
      DimClause? spaces ForTypeInitOp spaces Expr eol

  ForTypeInitOp = caseInsensitive<"init"> | "="

  // For v <= vmax  (constraint only)
  ForConstraint
    = caseInsensitive<"For"> spaces identifier spaces compOp spaces Expr eol

  // For x as number = 42  /  For x as number  /  For x = expr  /  For a = e1 AND b = e2
  ForDecl
    = caseInsensitive<"For"> spaces ForDeclBody eol

  ForDeclBody
    = identifier spaces caseInsensitive<"as"> spaces TypeExpr spaces DimClause? spaces caseInsensitive<"of"> spaces identifier spaces "=" spaces Expr  -- typedUnitInit
    | identifier spaces caseInsensitive<"as"> spaces TypeExpr spaces DimClause? spaces ForTypeInitOp spaces Expr  -- typedInit
    | identifier spaces caseInsensitive<"as"> spaces TypeExpr spaces DimClause?                                    -- typedOnly
    | identifier spaces caseInsensitive<"of"> spaces identifier spaces "=" spaces Expr                            -- unitInit
    | identifier spaces caseInsensitive<"of"> spaces identifier                                                    -- unitOnly
    | NonemptyListOf<ForSingleEq, andSep>                                                                          -- multiEq

  ForSingleEq = identifier spaces "=" spaces Expr

  //----------------------------------------------------------------
  // DIM clause
  //----------------------------------------------------------------

  DimClause = spaces caseInsensitive<"dim"> spaces DimSpec

  DimSpec
    = "{" NonemptyListOf<DimDim, listSep> "}"  -- structured
    | "{" "}"                                   -- empty
    | "*"                                       -- star
    | Expr                                      -- scalar

  DimDim
    = identifier ":" DimSize  -- named
    | DimSize                 -- anon

  DimSize
    = "*"       -- star
    | RangeExpr -- range
    | Expr      -- expr

  //----------------------------------------------------------------
  // LET statement
  //----------------------------------------------------------------

  LetStmt
    = LetBlock
    | LetInline

  LetBlock
    = caseInsensitive<"Let"> spaces LetBindings spaces caseInsensitive<"Then"> eol
      Statement*
      caseInsensitive<"End"> eol

  LetInline
    = caseInsensitive<"Let"> spaces LetBindings eol

  LetBindings = NonemptyListOf<LetBinding, andSep>

  LetBinding
    = identifier spaces caseInsensitive<"as"> spaces TypeExpr spaces DimClause?  -- typedDecl
    | ArrayIndexExpr spaces "=" spaces Expr                                        -- arrayIndex
    | identifier spaces compOp spaces Expr                                         -- constrained
    | identifier spaces "=" spaces Expr                                            -- eq

  //----------------------------------------------------------------
  // IF statement
  //----------------------------------------------------------------

  IfStmt
    = IfBlock
    | IfInline
    | IfGuard

  IfBlock
    = caseInsensitive<"If"> spaces CondExpr spaces caseInsensitive<"Then"> eol
      Statement*
      ElseIfClause*
      ElseClause?
      caseInsensitive<"End"> eol

  ElseIfClause
    = caseInsensitive<"ElseIf"> spaces CondExpr spaces caseInsensitive<"Then"> eol
      Statement*

  ElseClause
    = caseInsensitive<"Else"> eol
      Statement*

  // single-line: If cond then stmt [else stmt]
  IfInline
    = caseInsensitive<"If"> spaces CondExpr spaces caseInsensitive<"then"> spaces Statement
      (spaces caseInsensitive<"else"> spaces Statement)?

  // guard: If cond   (controls the block above it)
  IfGuard = caseInsensitive<"If"> spaces CondExpr eol

  //----------------------------------------------------------------
  // PUSH statement
  //----------------------------------------------------------------

  PushStmt = caseInsensitive<"Push"> spaces LValue spaces "=" spaces Expr eol

  LValue
    = CellRef                       -- cell
    | identifier ArrayIndexSuffix+  -- indexed
    | QualifiedName                 -- var

  ArrayIndexSuffix
    = "{" NonemptyListOf<Expr, listSep> "}"  -- curly
    | "(" NonemptyListOf<Expr, listSep> ")"  -- paren
    | "[" NonemptyListOf<Expr, listSep> "]"  -- square

  //----------------------------------------------------------------
  // RETURN statement
  //----------------------------------------------------------------

  ReturnStmt = caseInsensitive<"Return"> spaces Expr eol

  //----------------------------------------------------------------
  // Subprocess call (standalone)
  //   SplitName([A1], [^B1])
  //----------------------------------------------------------------

  SubprocessCall = QualifiedName "(" SubprocessArgList ")" eol

  SubprocessArgList = ListOf<SubprocessArg, listSep>

  SubprocessArg
    = CellRef  -- cell
    | Expr     -- expr

  //----------------------------------------------------------------
  // Cell assignment
  //----------------------------------------------------------------

  CellAssign
    = CellRef spaces ":" spaces identifier spaces caseInsensitive<"as"> spaces TypeExpr eol  -- typedDecl
    | CellRef spaces ":" spaces identifier spaces "=" spaces Expr eol                        -- varAssign
    | CellRef spaces ":=" spaces Expr eol                                                    -- directAssign

  //----------------------------------------------------------------
  // Global variable declaration
  //----------------------------------------------------------------

  GlobalVarDecl
    = ":" spaces "$"? identifier spaces caseInsensitive<"as"> spaces TypeExpr
      DimClause? spaces InConstraint? spaces VarInitClause? eol  -- typed
    | ":" spaces identifier spaces "=" spaces RangeOrExpr eol    -- simple
    | ":" spaces identifier eol                                    -- bareDecl

  RangeOrExpr = RangeExpr | Expr

  InitOrEqClauseRange
    = spaces caseInsensitive<"init"> spaces RangeOrExpr  -- init
    | spaces "=" spaces RangeOrExpr                      -- eq

  // Accepts "= expr", "init expr", or "or = expr"
  VarInitClause
    = spaces caseInsensitive<"or"> spaces "=" spaces RangeOrExpr  -- orEq
    | spaces caseInsensitive<"init"> spaces RangeOrExpr           -- init
    | spaces "=" spaces RangeOrExpr                               -- eq

  InConstraint
    = caseInsensitive<"in"> spaces "{" NonemptyListOf<Expr, listSep> "}"  -- set
    | caseInsensitive<"in"> spaces RangeExpr                               -- range

  //----------------------------------------------------------------
  // Named dimension label assignment
  //   Results!Quarter.Label{"Q1", "Q2", "Q3", "Q4"}
  //----------------------------------------------------------------

  DimLabel
    = identifier "!" identifier "." caseInsensitive<"Label">
      "{" NonemptyListOf<Expr, listSep> "}" eol

  //----------------------------------------------------------------
  // Condition expressions
  //----------------------------------------------------------------

  CondExpr
    = CondExpr spaces caseInsensitive<"AND"> spaces CondTerm  -- and
    | CondExpr spaces caseInsensitive<"OR">  spaces CondTerm  -- or
    | CondTerm

  CondTerm
    = Expr spaces caseInsensitive<"not"> spaces "=" spaces Expr              -- notEq
    | Expr spaces caseInsensitive<"in"> spaces InRHS                         -- in
    | Expr spaces caseInsensitive<"as"> spaces TypeExpr DimClause?           -- typeCheck
    | Expr spaces caseInsensitive<"of"> spaces identifier                    -- unitCheck
    | Expr spaces caseInsensitive<"dim"> spaces DimSpec                      -- dimCheck
    | Expr spaces compOp spaces Expr                                          -- compare
    | Expr                                                                    -- expr

  InRHS
    = "{" NonemptyListOf<Expr, listSep> "}"  -- set
    | RangeExpr                               -- range

  //----------------------------------------------------------------
  // Expressions
  //----------------------------------------------------------------

  Expr = ConcatExpr

  ConcatExpr
    = ConcatExpr spaces "&" spaces AddExpr  -- concat
    | AddExpr

  AddExpr
    = AddExpr spaces "+" spaces MulExpr  -- add
    | AddExpr spaces "-" spaces MulExpr  -- sub
    | MulExpr

  MulExpr
    = MulExpr spaces "*"   spaces ExpExpr                          -- mul
    | MulExpr spaces "/"   spaces ExpExpr                          -- div
    | MulExpr spaces "\\"  spaces ExpExpr                          -- intDiv
    | MulExpr spaces caseInsensitive<"mod"> spaces ExpExpr         -- mod
    | ExpExpr

  ExpExpr
    = UnaryExpr spaces "^" spaces ExpExpr  -- exp
    | UnaryExpr

  UnaryExpr
    = "-" UnaryExpr  -- neg
    | "+" UnaryExpr  -- pos
    | PipeExpr

  PipeExpr
    = PipeExpr spaces "|" spaces PostfixExpr  -- pipe
    | PostfixExpr

  PostfixExpr
    = PostfixExpr "." identifier                                   -- member
    | PostfixExpr "!" identifier "(" Expr ")"                     -- dimAccess
    | PostfixExpr "{" NonemptyListOf<Expr, listSep> "}"           -- curlyIndex
    | PostfixExpr "(" ListOf<Expr, listSep> ")"                   -- call
    | PostfixExpr "[" NonemptyListOf<Expr, listSep> "]"           -- squareIndex
    | PostfixExpr spaces caseInsensitive<"dim"> spaces DimSpec     -- dim
    | PrimaryExpr

  PrimaryExpr
    = SpecialValue       -- special
    | InterpolatedString -- interp
    | PlainString        -- string
    | number             -- number
    | ArrayLit           -- array
    | NewExpr            -- new
    | CellRef            -- cell
    | FuncCallExpr       -- func
    | identifier         -- ident
    | "(" Expr ")"       -- paren

  // new Point(1.0, 2.0)  /  new Point with (x, y)  /  new Point(args) with (fields)
  NewExpr
    = caseInsensitive<"new"> spaces identifier "(" ListOf<Expr, listSep> ")" spaces caseInsensitive<"with"> spaces "(" NewWithList ")"  -- withArgsAndFields
    | caseInsensitive<"new"> spaces identifier spaces caseInsensitive<"with"> spaces "(" NewWithList ")"  -- withFields
    | caseInsensitive<"new"> spaces identifier "(" ListOf<Expr, listSep> ")"                              -- withArgs
    | caseInsensitive<"new"> spaces identifier                                                             -- bare

  NewWithList = NonemptyListOf<NewWithField, listSep>

  NewWithField
    = identifier spaces "=" spaces Expr  -- namedField
    | identifier                         -- shorthand

  // Function calls as expressions:  SQRT(100)  /  sum{a, b}  /  sum[A1:A2]
  FuncCallExpr
    = identifier "{" NonemptyListOf<Expr, listSep> "}"  -- curlyArgs
    | identifier "[" CellRef "]"                         -- rangeArg
    | identifier "(" ListOf<Expr, listSep> ")"           -- parenArgs

  //----------------------------------------------------------------
  // Range expression   1 to 6 step 1.5
  //----------------------------------------------------------------

  RangeExpr
    = Expr spaces caseInsensitive<"to"> spaces Expr spaces caseInsensitive<"step"> spaces Expr  -- withStep
    | Expr spaces caseInsensitive<"to"> spaces Expr                                              -- plain

  //----------------------------------------------------------------
  // Array literal  {1, 2, 3}  /  {1, 2; 3, 4}
  //----------------------------------------------------------------

  ArrayLit = "{" NonemptyListOf<ArrayRow, rowSep> "}"

  ArrayRow = NonemptyListOf<Expr, listSep>

  //----------------------------------------------------------------
  // Cell references
  //
  //   [A1]   [^B2]   [A{i}]   [A1:C2]   [{i :A}5]
  //----------------------------------------------------------------

  CellRef
    = "[" "^"? CellRange "]"  -- range
    | "[" "^"? CellAddr "]"   -- single

  CellRange = CellAddr ":" CellAddr

  CellAddr
    = InterpColExpr InterpRowExpr  -- bothInterp
    | ColName InterpRowExpr        -- interpRow
    | InterpColExpr RowNum         -- interpCol
    | ColName RowNum               -- plain

  // {i :A}  — offset from base column A
  InterpColExpr = "{" Expr spaces ":" ColName "}"

  // {n}  /  {n + 1}
  InterpRowExpr = "{" Expr "}"

  ColName = letter+

  RowNum = digit+

  //----------------------------------------------------------------
  // Array index expression used in LetBinding LHS
  //   D{i+1, 1}  /  D(k)  /  D[A1]
  //----------------------------------------------------------------

  ArrayIndexExpr
    = identifier "{" NonemptyListOf<Expr, listSep> "}"  -- curly
    | identifier "(" NonemptyListOf<Expr, listSep> ")"  -- paren
    | identifier "[" CellAddr "]"                        -- cell

  //----------------------------------------------------------------
  // Type expressions
  //----------------------------------------------------------------

  TypeExpr
    = caseInsensitive<"number">  -- number
    | caseInsensitive<"text">    -- text
    | identifier                 -- userDefined

  //----------------------------------------------------------------
  // Special values
  //----------------------------------------------------------------

  SpecialValue
    = "-" "#INF"  -- negInf
    | "#INF"      -- inf
    | "#N/A"      -- na

  //----------------------------------------------------------------
  // String literals
  //----------------------------------------------------------------

  // "hello"  /  "I say ""Hello"""
  PlainString = "\"" PlainStringChar* "\""

  PlainStringChar
    = "\"\""     -- escapedQuote
    | ~"\"" any  -- other

  // $"Hello, {name}!"
  InterpolatedString = "$\"" InterpSegment* "\""

  InterpSegment
    = "{{{" ~"*"            -- tripleEscape
    | "{{" ~"*"             -- doubleEscape
    | "{*" (~"}" any)* "}"  -- starEscape
    | "{}"                  -- emptyBraces
    | "{" InterpContent "}" -- interpolate
    | ~("\"" | "{") any     -- literal

  InterpContent = Expr (spaces "," spaces Expr)?  // {var} or {var, width}

  //----------------------------------------------------------------
  // Numbers
  //----------------------------------------------------------------

  number = digit+ ("." digit+)? (("e" | "E") ("+" | "-")? digit+)?

  //----------------------------------------------------------------
  // Comparison operators
  //----------------------------------------------------------------

  compOp
    = "<="  -- lte
    | ">="  -- gte
    | "<"   -- lt
    | ">"   -- gt
    | "="   -- eq

  //----------------------------------------------------------------
  // Separators (arity-1 rules for use as NonemptyListOf separators)
  //----------------------------------------------------------------

  listSep = spaces "," spaces

  rowSep = spaces ";" spaces

  andSep = spaces caseInsensitive<"AND"> spaces

  //----------------------------------------------------------------
  // Identifiers  (keywords are still valid identifiers in context)
  //----------------------------------------------------------------

  identifier = (letter | "_") (alnum | "_")*

  //----------------------------------------------------------------
  // Inline comment
  //----------------------------------------------------------------

  comment = spaces "'" (~"\n" any)*

  //----------------------------------------------------------------
  // End-of-line  (newlines are significant — statements end here)
  // Horizontal whitespace only in "spaces"; newlines stay visible.
  //----------------------------------------------------------------

  eol
    = comment? "\r\n" spaces  -- crlf
    | comment? "\n" spaces    -- lf
    | spaces &eof             -- atEof

  eof = ~any

  //----------------------------------------------------------------
  // Override default "spaces" to horizontal whitespace only
  //----------------------------------------------------------------

  spaces := (" " | "\t")*

}
```
