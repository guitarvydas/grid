"""
Test execution functionality for GridLang compiler.
Handles running and validating compiler tests.
"""
import math
from pathlib import Path

class GridLangTestRunner:
    """Handles test execution and validation."""

    def __init__(self, compiler=None):
        self.compiler = compiler

    def run_tests_independent(self, tests):
        tyresize_code = """Input make as text
Input model as text



[A1]: Width as number
[B1]: Ratio as number
[C1]: Diameter as number

if make = "TOYO" then
  if model = "YARI" then
    let width = 195
    let ratio = 55
    let diameter = 16
  elseif model = "AURI" then
    let width = 205
    let ratio = 55
    let diameter = 16
  elseif model = "CH-R" then
    let width = 215
    let ratio = 60
    let diameter = 17
  end
end
if make = "MERC" then
  if model = "A205" then
    let width = 205
    let ratio = 55
    let diameter = 17
  elseif model = "C200" then
    let width = 225
    let ratio = 45
    let diameter = 18
  end
end

if len(make) = 4 """

        tests_data = [
            ("Test 1: Basic calculation", "[A1] : a = 51", {'A1': 51}),
            ("Test 2: Arithmetic with reference",
             "[A1] := 51\n[A2] := ([A1] + 15) / 1.2e3\n[A3] := sum[A1:A2]", {'A1': 51, 'A2': 0.055, 'A3': 51.055}),
            ("Test 3: Variable in cell definition",
             "[A1] : a = 51\n[A2] : b = (a + 15) / 1.2e3\n[A3] : c = sum([A1:A2])", {'A1': 51, 'A2': 0.055, 'A3': 51.055}),
            ("Test 4: Global variables and sum{}",
             ": a = 51\n: b = (a + 15) / 1.2e3\n: c = sum{a, b}\n[A1] := a\n[A2] := b\n[A3] := c", {'A1': 51, 'A2': 0.055, 'A3': 51.055}),
            ("Test 5: Inline comment parsing",
             "[AB2] := 33 '28th column", {'AB2': 33}),
            ("Test 6: Horizontal array assignment from inline var",
             "[A1] : a = 51\n[^B2] := {12, (15 + a) / 1.2e3, 1+[A1], 8}", {'A1': 51, 'B2': 12, 'C2': 0.055, 'D2': 52, 'E2': 8}),
            ("Test 7: Horizontal array from variable", "[A1] : a = 51\n: b = {12, (15 + a) / 1.2e3, 1+[A1], 8}\n[^B2] := b", {
             'A1': 51, 'B2': 12, 'C2': 0.055, 'D2': 52, 'E2': 8}),
            ("Test 8: Math function - SQRT",
             "[A1] := 2*( SQRT(100) - 7 )", {'A1': 6.0}),
            ("Test 9: Interpolation with cell reference",
             ": n = 2\n[A{ n }] := 33\n[A{n + 1}] := -4.9", {'A2': 33, 'A3': -4.9}),
            ("Test 10: 2D range assign and slice", "[A1:C2] := {1, 2, 3; 10, 11, 12}\n[^A3] := [A1:C1]", {
             'A1': 1, 'A2': 10, 'A3': 1, 'B1': 2, 'B2': 11, 'B3': 2, 'C1': 3, 'C2': 12, 'C3': 3}),
            ("Test 11: Range read and vertical assignment",
             "[^A1] := {1; 2; 3}\n[B1:B2] := [A2:A3]", {'A1': 1, 'A2': 2, 'A3': 3, 'B1': 2, 'B2': 3}),
            ("Test 12: Text type assignment",
             ": t as text = \"Hello\"\n[A1] := t", {'A1': 'Hello'}),
            ("Test 13: Cell var definition", "[A1] : e = 3", {'A1': 3}),
            ("Test 14: Number type declaration",
             ": x as number = 42\n[A1] := x", {'A1': 42}),
            ("Test 15: Number declaration with scientific notation",
             ": num as number = 12.34e-5\n[A1] := num", {'A1': 0.0001234}),
            ("Test 16: Number sequence with custom step",
             ": seq = 1 to 6 step 1.5\n[^B1] := seq", {'B1': 1.0, 'C1': 2.5, 'D1': 4.0, 'E1': 5.5}),
            ("Test 17: Interpolated text", ": name as text = \"world\"\n[A1] := $\"Hello, {name}!\"", {
             'A1': "Hello, world!"}),
            ("Test 18: Self-referential assignment (should fail)", ": x = x", None),
            ("Test 19: Variable before definition",
             ": y = x + 1\n: x as number = 5\n[A1] := y", {'A1': 6}),
            ("Test 20: Integer division", "[A1] := 10 \\ 3", {'A1': 3}),
            ("Test 21: Exponentiation", "[A1] := 2 ^ 3", {'A1': 8}),
            ("Test 22: Modulus", "[A1] := 10 mod 3", {'A1': 1}),
            ("Test 23: Special value #INF",
             "[A1] := #INF", {'A1': float('inf')}),
            ("Test 24: Special value -#INF",
             "[A1] := -#INF", {'A1': float('-inf')}),
            ("Test 25: Special value #N/A",
             "[A1] := #N/A", {'A1': float('nan')}),
            ("Test 26: Text concatenation", ": t1 as text = \"Hello\"\n: t2 as text = \"world\"\n[A1] := t1 & \", \" & t2", {
             'A1': "Hello, world"}),
            ("Test 27: Quote escaping", ": q as text = \"I say \"\"Hello\"\"\"\n[A1] := q", {
             'A1': "I say \"Hello\""}),
            ("Test 28: Padding right", ": num = 42\n[A1] := $\"Number: {num, 5}\"", {
             'A1': "Number:    42"}),
            ("Test 29: Padding left",
             ": num = 42\n[A1] := $\"Number: {num, -5}\"", {'A1': "Number: 42   "}),
            ("Test 30: Multi-line interpolation",
             ": name = \"world\"\n[A1] := $\"{*Loudly} I say:  \n\t\t\"\"Hello\"\", {name}!\"", {'A1': "{Loudly} I say:\n\"Hello\", world!"}),
            ("Test 31: Empty braces",
             "[A1] := $\"Empty: {}\"", {'A1': "Empty: {}"}),
            ("Test 32: Escaped brace",
             "[A1] := $\"Escaped: {{{*star\"", {'A1': "Escaped: {{{star"}),
            ("Test 33: Escaped brace with closing brace",
             "[A1] := $\"Escaped: {{{*star}\"", {'A1': "Escaped: {{{star}"}),
            ("Test 34: Number sequence default step", ": dice = 1 to 6\n[^A1] := dice", {
             'A1': 1, 'B1': 2, 'C1': 3, 'D1': 4, 'E1': 5, 'F1': 6}),
            ("Test 35: Point type spilling on grid",
             "Define Point as Type\n: x as number\n: y as number\nEnd Point\n: p = new Point(-4.3, 2.1)\n[^A3] := p", {'A3': -4.3, 'B3': 2.1}),
            ("Test 36: Array of Points spilling on grid",
             "Define Dot as Type\n: x as number\n: y as number\nEnd Dot\n: p1 = new Dot(1, 2)\n: p2 = new Dot(3, 4)\n[^C3] := {p1, p2}", {'C3': 1, 'C4': 3, 'D3': 2, 'D4': 4}),
            ("Test 37: Nested Rectangle type spilling on grid",
             "Define Point as Type\n: x as number\n: y as number\nEnd Point\nDefine Rectangle as Type\n: top as Point\n: bottom as Point\nEnd Rectangle\n[^A1] := new Rectangle(new Point(0, 10), new Point(5, 3))", {'A1': 0, 'B1': 10, 'C1': 5, 'D1': 3}),
            ("Test 38: Point type assigned to single cell",
             "Define Point as Type\n\t: x as number\n\t: y as number\nEnd Point\n: p = new Point(-4.3, 2.1)\n[A1] := p", {'A1': {'x': -4.3, 'y': 2.1}}),
            ("Test 39: Access field of point type",
             "Define Point as Type\n: x as number\n: y as number\nEnd Point\n: p = new Point(-4.3, 2.1)\n[A3] := p.y", {'A3': 2.1}),
            ("Test 40: Concatenation with interpolation",
             ": m = \"hello\"\n[A1] := \"I say-\" & $\" {m} world!\"", {'A1': "I say- hello world!"}),
            ("Test 41: Nested {* interpolation",
             "[A1] := $\"{{*\"", {'A1': "{{"}),
            ("Test 42: Dimension constraint",
             ": Weights as number dim {0 to 10, 0 to 10} = 0\n[A1] := Weights{0, 0}", {'A1': 0}),
            ("Test 43: Multi-dimensional addition",
             "[A1] := {0, 3; 10, 11} + {1, 2; 3, 4}", {'A1': [[1.0, 5.0], [13.0, 15.0]]}),
            ("Test 44: Multi-dimensional subtraction",
             "[A1] := {0, 3; 10, 11} - {1, 2; 3, 4}", {'A1': [[-1.0, 1.0], [7.0, 7.0]]}),
            ("Test 45: Multi-dimensional multiplication",
             "[A1] := {0, 3; 10, 11} * {1, 2; 3, 4}", {'A1': [[0.0, 6.0], [30.0, 44.0]]}),
            ("Test 46: Multi-dimensional division", "[A1] := {0, 3; 10, 11} / {1, 2; 3, 4}", {
             'A1': [[0.0, 1.5], [3.3333333333333335, 2.75]]}),
            ("Test 47: Multi-dimensional exponentiation",
             "[A1] := {0, 3; 10, 11} ^ {1, 2; 3, 4}", {'A1': [[0.0, 9.0], [1000.0, 14641.0]]}),
            ("Test 48: Multi-dimensional modulo",
             "[A1] := {0, 3; 10, 11} mod {1, 2; 3, 4}", {'A1': [[0.0, 1.0], [1.0, 3.0]]}),
            ("Test 49: Multi-dimensional integer division",
             "[A1] := {0, 3; 10, 11} \\ {1, 2; 3, 4}", {'A1': [[0.0, 1.0], [3.0, 2.0]]}),
            ("Test 50: Pipe operator", "[^A1] := {1, 2} | {3, 4} | {-5, -6}", {
             'A1': 1.0, 'B1': 2.0, 'A2': 3.0, 'B2': 4.0, 'A3': -5.0, 'B3': -6.0}),
            ("Test 51: Dim reshape",
             "[A1] := {10, 11} dim {*, 1}", {'A1': [[10], [11]]}),
            ("Test 52: Range with 1D vertical",
             "[B2:B4] := {9, 8, 7}", {'B2': 9, 'B3': 8, 'B4': 7}),
            ("Test 53: Range with 1D repeated", "[A2:B4] := {1, 2}", {
             'A2': 1, 'A3': 1, 'A4': 1, 'B2': 2, 'B3': 2, 'B4': 2}),
            ("Test 54: Named dimensions",
             ": Results as number dim {Dept: *, Quarter: 4} = {9, 4, 5, 1}\nResults!Quarter.Label{\"Q1\", \"Q2\", \"Q3\", \"Q4\"}\n[A1] := Results!Quarter(\"Q2\")", {'A1': 4}),
            ("Test 55: Assign and access dimensioned array",
             "[A1:D1] := {10, 20, 30, 40}\n: Results as number dim {Dept: *, Quarter: 4} = [A1:D1]\nResults!Quarter.Label{\"Q1\", \"Q2\", \"Q3\", \"Q4\"}\n[B2] := Results!Quarter(\"Q2\")", {'A1': 10, 'B1': 20, 'B2': 20, 'C1': 30, 'D1': 40}),
            ("Test 56: Multi-dimensional addressing", "[A2:D2] := {10, 20, 30, 40}\n: Results as number dim {Dept: *, Quarter: 4} = [A2:D2]\n[A1] := Results[B1]", {
             'A1': 20, 'A2': 10, 'B2': 20, 'C2': 30, 'D2': 40}),
            ("Test 57: FOR with already defined variable",
             ": x = 34\nFOR x AS NUMBER", None),
            ("Test 58: FOR with LET defining local variable",
             "For x = 34\nlet x as number\n[A1] := x", {'A1': 34}),
            ("Test 59: FOR block with LET defining local variable",
             "For x = 34 DO\n    Let x as number Then\n        [A1] := x\n    end\nEnd", {'A1': 34}),
            ("Test 60: LET block with FOR using already declared variable",
             "Let x as number Then\n    For x = 34 DO\n        [A1] := x\n    end\nEnd", None),
            ("Test 61: LET followed by FOR with local variable",
             "Let x as number\n[A1] := x\nFor x = 34", {'A1': 34}),
            ("Test 62: LET followed by global variable declaration",
             "Let x as number\n[A1] := x\n: x = 34", {'A1': 34}),
            ("Test 63: LET with constraint x > 10",
             ": x = 34\nLet x > 10 then\n    [A1] := x\nEnd", {'A1': 34}),
            ("Test 64: LET with constraint x < 10",
             ": x = 34\nLet x < 10 then\n    [A1] := x\nEnd", {}),
            ("Test 65: LET with constraint x < 10 halting execution",
             ": x = 34\nLet x < 10\n[A1] := x", {}),
            ("Test 66: LET chain with dependencies X -> Y -> Z",
             "Let X = 2 and Y = X * 5 and Z = Y - X\n[A1] := Z", {'A1': 8}),
            ("Test 67: LET chain with wrong order (Y uses X before defined)",
             "Let Y = X * 5 and X = 2\n[A1] := Y", None),
            ("Test 68: LET with array and named dimension", "For names dim 0 to 4\nLet names = {\"Alice\", \"Bob\", \"Carla\", \"Dylan\", \"Edith\"}\n[^A1] := names", {
             'A1': 'Alice', 'B1': 'Bob', 'C1': 'Carla', 'D1': 'Dylan', 'E1': 'Edith'}),
            ("Test 69: Global assignment used in FOR",
             ": n = (m + 10) / 10\n[A1] := n\nFor m = 32", {'A1': 4.2}),
            ("Test 70: LET with array access (index and label)",
             "For names dim 0 to 4\nLet names = {\"Alice\", \"Bob\", \"Carla\", \"Dylan\", \"Edith\"}\n[A1] := names(0)\n[B1] := names[3]", {'A1': 'Alice', 'B1': 'Carla'}),
            ("Test 71: Define custom type and array of objects",
             "define Tensor as type\n    : name as text\nEnd Tensor\n\nFor V as tensor with (name = \"V\", grid DIM {4, 4, 2} = 1.0) \n[A1] := V.grid{4, 4, 1}\n[B1] := V.name", {'A1': 1.0, 'B1': 'V'}),
            ("Test 72: Define custom type and array with no constraint for {4, 4, 2}",
             "define Tensor as type\n    : name as text\nEnd Tensor\n\nFor V as tensor with (name = \"V\", grid DIM {4, 4, 2} = {1,1,1,1;2,2,2,2;3,3,3,3;4,4,4,4} | {1,2,3,4;2,3,4,5;3,4,5,6;4,5,6,7})\n[A1] := V.grid{4, 4, 1}\n[B1] := V.grid{4, 4, 2}\n[C1] := V.name", {'A1': 4.0, 'B1': 7.0, 'C1': 'V'}),
            ("Test 73: Define custom type and array with variable assignment for {4, 4, 3}",
             "define Tensor as type\n    : name as text\nEnd Tensor\n\nFor var = {1,1,1,1;2,2,2,2;3,3,3,3;4,4,4,4} | {1,2,3,4;2,3,4,5;3,4,5,6;4,5,6,7} | {11,2,3,4;2,3,4,5;3,4,5,6;4,5,6,7}\nFor V as tensor with (name = \"V\", grid DIM {4, 4, 3} = var)\n[A1] := V.grid{3, 1, 2}\n[B1] := V.grid{4, 4, 2}\n[C1] := V.name\n[D1] := V.grid{1, 1, 3}", {'A1': 3.0, 'B1': 7.0, 'C1': 'V', 'D1': 11.0}),

            # Milestone 5 Tests - IF Statements and FOR Loops
            ("Test 74: If condition is false, whole block",
             "Let V = 33\n[A1] := \"single digit\"\nif V < 10", {}),
            ("Test 75: If condition is true, whole block",
             "Let V = 1\n[A1] := \"single digit\"\nif V < 10", {'A1': 'single digit'}),
            ("Test 76: If condition is true, whole block with division",
             "For a = 20 and b = 4\n[A1] := a / b\nIf b not = 5", {'A1': 5.0}),
            ("Test 77: If then block with else",
             ": name = \"Jane\"\nFor Friend as number\nIf name in {\"Oscar\", \"Jane\"} then\n\tLet Friend = 1\nElse\n\tLet Friend = 99\nEnd\n[A1] := Friend", {'A1': 1}),
            ("Test 78: Single line if then else",
             ": name = \"Liz\"\nFor Friend as number\nIf name in {\"Oscar\", \"Jane\"} then let Friend = 1 else let Friend = 99\n[A1] := Friend", {'A1': 99}),
            ("Test 79: Elseif statement",
             ": name = \"Jane\"\nFor Friend as Number\nIf name = \"Oscar\" Then\n  Let Friend = 1\nelseIf name = \"Jane\" Then\n  Let Friend = 2\nElse\n  Let friend = 99\nEnd\n[A1] := Friend", {'A1': 2}),
            ("Test 80: Undefined variable, condition is false",
             "If V > 10 then\n  [A1] := \"big\"\nelse\n  [A1] := \"small\"\nEnd", {'A1': 'small'}),
            ("Test 81: Multiple conditions",
             "For a = 3 and b = 7\nif b > a and a <= 3 and b not = 16 then\n  [A1] := \"true\"\nEnd\nIf b = 5 OR a = 3 then\n  [B1] := \"true\"\nEnd", {'A1': 'true', 'B1': 'true'}),
            ("Test 82: If constraint on Expression",
             "If 1 + 1 = 2 then\n  [A1] := \"true\"\nEnd", {'A1': 'true'}),
            ("Test 83: If constraint on Expression with variable",
             "For a = 3\nIf a * 3 = 9 then [A1] := \"true\"", {'A1': 'true'}),
            ("Test 84: If constraint on Expression with comparison",
             "For a = 3\nIf 10 > a * 3 then [A1] := \"true\"", {'A1': 'true'}),

            # Milestone 5 Tests - FOR Loops
            ("Test 85: For loop with range",
             "For i in 1 to 3\n[A{i}] := \"hello\"", {'A1': 'hello', 'A2': 'hello', 'A3': 'hello'}),
            ("Test 86: Combining loops",
             "For a in 1 to 1000\nFor b in 8 to 9\npush [A{a}] = b", {'A1': 8, 'A2': 9}),
            ("Test 87: Combining loops with different ranges",
             "For a in 1 to 2\nFor b in 8 to 90\npush [A{a}] = b", {'A1': 8, 'A2': 9}),
            ("Test 88: For loop block",
             "For i in 1 to 3 do\n\t[A{i}] := i + 3\nEnd", {'A1': 4, 'A2': 5, 'A3': 6}),
            ("Test 89: For loop block with set",
             "For I in {1, 2, 3} do\n\t[A{I}] := I + 3\nEnd", {'A1': 4, 'A2': 5, 'A3': 6}),
            ("Test 90: Nested loop with AND",
             "For a in {1, 2} AND b in {9, 10} do\n  [A{2 * a + b - 10}] := a * b\nEnd", {'A1': 9, 'A2': 10, 'A3': 18, 'A4': 20}),
            ("Test 91: Loop with index",
             "For b in {9, 10} index i do\n\t[A{i}] := b\nEnd", {'A1': 9, 'A2': 10}),
            ("Test 92: Loop with step and index",
             "For b in 9 to 15 Step 3 index i do\n\t[A{i}] := b\nEnd", {'A1': 9, 'A2': 12, 'A3': 15}),
            ("Test 93: Nested loop with step and index",
             "For a in {1, 2} Index I AND b in 9 to 15 step 3 Index J do\n  [A{3 * I + J}] := a * b\nEnd", {'A4': 9, 'A5': 12, 'A6': 15, 'A7': 18, 'A8': 24, 'A9': 30}),

            # Milestone 5 Tests - IF with Dimension Constraints
            ("Test 94: If condition Dimension constraint - single element",
             "for x = {3}\nif x dim 1 then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),
            ("Test 95: If condition Dimension constraint - array",
             "for x = {3, 8}\nif x dim 1 then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'false'}),
            ("Test 96: If condition Dimension constraint - 2D",
             "for x = {3, 8}\nif x dim 2 then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),
            ("Test 97: Dimension condition two-dim",
             "for x = {3, 8; 1, 0}\nif x dim {2, 2} then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),
            ("Test 98: Dimension condition zero-dim",
             "for x = 3\nif x dim 1 then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'false'}),
            ("Test 99: Dimension condition zero-dim with *",
             "for x = 3\nif x dim * then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'false'}),
            ("Test 100: Dimension condition zero-dim with {}",
             "for x = 3\nif x dim {} then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),

            # Milestone 5 Tests - IF with Type Constraints
            ("Test 101: If condition Type constraint - uninitialized",
             "For z as text\nIf z as text then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),
            ("Test 102: If condition Type constraint - string value",
             "For z = \"Grid\"\nIf z as text then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),
            ("Test 103: If condition Type constraint - number value",
             "For z = 99\nIf z as text then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'false'}),
            ("Test 104: If condition Type and Dimension constraint",
             "For z = \"Grid\"\nIf z as text dim {} then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),
            ("Test 105: If condition Type and Dimension constraint - array",
             "For z = {\"Grid\", \"lang\"}\nIf z as text dim * then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),
            ("Test 106: If condition Type and Dimension constraint - scalar",
             "For z = \"Grid\"\nIf z as text dim * then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'false'}),

            # Milestone 5 Tests - IF with Value Constraints
            ("Test 107: If condition Possible Values constraint - in set",
             "For Z = \"Grid\"\nIf z in {\"Grid\", \"lang\", \"2025\"} then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),
            ("Test 108: If condition Possible Values constraint - not in set",
             "For z = \"hello\"\nIf z in {\"Grid\", \"lang\", \"2025\"} then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'false'}),
            ("Test 109: If condition Possible Values constraint - in range",
             "For z = 99\nIf z in 50 to 100 then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),

            # Milestone 5 Tests - IF with Unit Constraints
            ("Test 110: If condition Unit constraint - with value",
             "For z of dollar = 4\nIf z of dollar then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),
            ("Test 111: If condition Unit constraint - without value",
             "For z of dollar\nIf z of Dollar then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'true'}),
            ("Test 112: If condition Unit constraint - different unit",
             "For z of peso\nIf z of dollar then\n  [A1] := \"true\"\nelse\n  [A1] := \"false\"\nEnd", {'A1': 'false'}),
            ("Test 113: Full Fibonacci Sequence (30 elements)",
             "For D as number dim {30, 2}\nLet D[A1] = 1\nLet D[B1] = 1\nFor i in 1 to 29 do\n  Let D{i+1, 1} = D{i, 2}\n  Let D{i+1, 2} = D{i, 1} + D{i, 2}\nend\n[^A1] := D",
             {'A1': 1, 'B1': 1, 'A2': 1, 'B2': 2, 'A3': 2, 'B3': 3, 'A4': 3, 'B4': 5, 'A5': 5, 'B5': 8,
              'A6': 8, 'B6': 13, 'A7': 13, 'B7': 21, 'A8': 21, 'B8': 34, 'A9': 34, 'B9': 55, 'A10': 55, 'B10': 89,
              'A11': 89, 'B11': 144, 'A12': 144, 'B12': 233, 'A13': 233, 'B13': 377, 'A14': 377, 'B14': 610,

              'A15': 610, 'B15': 987, 'A16': 987, 'B16': 1597, 'A17': 1597, 'B17': 2584, 'A18': 2584, 'B18': 4181,
              'A19': 4181, 'B19': 6765, 'A20': 6765, 'B20': 10946, 'A21': 10946, 'B21': 17711, 'A22': 17711, 'B22': 28657,
              'A23': 28657, 'B23': 46368, 'A24': 46368, 'B24': 75025, 'A25': 75025, 'B25': 121393, 'A26': 121393, 'B26': 196418,
              'A27': 196418, 'B27': 317811, 'A28': 317811, 'B28': 514229, 'A29': 514229, 'B29': 832040, 'A30': 832040, 'B30': 1346269}),
            ("Test 114: Pascal Triangle Sequence",
             "For D as number dim {15, 1}\nLet D[A1] = 1\nFor I in 3 to 30 step 2 index k do\n   Let D{k+1, 1} = D{k, 1} + i\nend\n[^A1] := D",
             {'A1': 1, 'A2': 4, 'A3': 9, 'A4': 16, 'A5': 25, 'A6': 36, 'A7': 49, 'A8': 64, 'A9': 81, 'A10': 100,
              'A11': 121, 'A12': 144, 'A13': 169, 'A14': 196, 'A15': 225}),
            ("Test 115: Fibonacci Sequence with Cell References",
             "[A1:B1] := 1\nFor I in 1 to 29 do\n  [a{I+1}] := [B{i}]\n  [b{I+1}] := [a{i}] + [B{I}]\nend",
             {'A1': 1, 'B1': 1, 'A2': 1, 'B2': 2, 'A3': 2, 'B3': 3, 'A4': 3, 'B4': 5, 'A5': 5, 'B5': 8,
              'A6': 8, 'B6': 13, 'A7': 13, 'B7': 21, 'A8': 21, 'B8': 34, 'A9': 34, 'B9': 55, 'A10': 55, 'B10': 89,
              'A11': 89, 'B11': 144, 'A12': 144, 'B12': 233, 'A13': 233, 'B13': 377, 'A14': 377, 'B14': 610,
              'A15': 610, 'B15': 987, 'A16': 987, 'B16': 1597, 'A17': 1597, 'B17': 2584, 'A18': 2584, 'B18': 4181,
              'A19': 4181, 'B19': 6765, 'A20': 6765, 'B20': 10946, 'A21': 10946, 'B21': 17711, 'A22': 17711, 'B22': 28657,
              'A23': 28657, 'B23': 46368, 'A24': 46368, 'B24': 75025, 'A25': 75025, 'B25': 121393, 'A26': 121393, 'B26': 196418,
              'A27': 196418, 'B27': 317811, 'A28': 317811, 'B28': 514229, 'A29': 514229, 'B29': 832040, 'A30': 832040, 'B30': 1346269}),
            ("Test 116: Array with step and index in FOR loop",
             "For D as number dim 15\nLet D[1] = 1\nFor i in 3 to 30 step 2 index k do\nLet D(k+1) = D(k) + i\nend\n[^A1] := D",
             {'A1': 1.0, 'B1': 4.0, 'C1': 9.0, 'D1': 16.0, 'E1': 25.0, 'F1': 36.0, 'G1': 49.0, 'H1': 64.0, 'I1': 81.0, 'J1': 100.0,
              'K1': 121.0, 'L1': 144.0, 'M1': 169.0, 'N1': 196.0, 'O1': 225.0}),
            ("Test 117: Nested FOR loop with dynamic range building grid pattern",
             "For D as number dim {10, 12}\n\nLet D[B1] = 1\nFor a in 2 to 10 AND b in 1 to a do\n  Let D{a, b+1} = d{a-1, b} + d{a-1, b+1}\nEnd\n\n[^A1] := D",
             {'A1': 0.0, 'B1': 1.0, 'C1': 0.0, 'D1': 0.0, 'E1': 0.0, 'F1': 0.0, 'G1': 0.0, 'H1': 0.0, 'I1': 0.0, 'J1': 0.0, 'K1': 0.0, 'L1': 0.0, 'A2': 0.0, 'B2': 1.0, 'C2': 1.0, 'D2': 0.0, 'E2': 0.0, 'F2': 0.0, 'G2': 0.0, 'H2': 0.0, 'I2': 0.0, 'J2': 0.0, 'K2': 0.0, 'L2': 0.0, 'A3': 0.0, 'B3': 1.0, 'C3': 2.0, 'D3': 1.0, 'E3': 0.0, 'F3': 0.0, 'G3': 0.0, 'H3': 0.0, 'I3': 0.0, 'J3': 0.0, 'K3': 0.0, 'L3': 0.0, 'A4': 0.0, 'B4': 1.0, 'C4': 3.0, 'D4': 3.0, 'E4': 1.0, 'F4': 0.0, 'G4': 0.0, 'H4': 0.0, 'I4': 0.0, 'J4': 0.0, 'K4': 0.0, 'L4': 0.0, 'A5': 0.0, 'B5': 1.0, 'C5': 4.0, 'D5': 6.0, 'E5': 4.0, 'F5': 1.0, 'G5': 0.0, 'H5': 0.0, 'I5': 0.0, 'J5': 0.0, 'K5': 0.0, 'L5': 0.0, 'A6': 0.0, 'B6': 1.0, 'C6': 5.0, 'D6': 10.0, 'E6': 10.0, 'F6': 5.0, 'G6': 1.0, 'H6': 0.0, 'I6': 0.0, 'J6': 0.0, 'K6': 0.0, 'L6': 0.0, 'A7': 0.0, 'B7': 1.0, 'C7': 6.0, 'D7': 15.0, 'E7': 20.0, 'F7': 15.0, 'G7': 6.0, 'H7': 1.0, 'I7': 0.0, 'J7': 0.0, 'K7': 0.0, 'L7': 0.0, 'A8': 0.0, 'B8': 1.0, 'C8': 7.0, 'D8': 21.0, 'E8': 35.0, 'F8': 35.0, 'G8': 21.0, 'H8': 7.0, 'I8': 1.0, 'J8': 0.0, 'K8': 0.0, 'L8': 0.0, 'A9': 0.0, 'B9': 1.0, 'C9': 8.0, 'D9': 28.0, 'E9': 56.0, 'F9': 70.0, 'G9': 56.0, 'H9': 28.0, 'I9': 8.0, 'J9': 1.0, 'K9': 0.0, 'L9': 0.0, 'A10': 0.0, 'B10': 1.0, 'C10': 9.0, 'D10': 36.0, 'E10': 84.0, 'F10': 126.0, 'G10': 126.0, 'H10': 84.0, 'I10': 36.0, 'J10': 9.0, 'K10': 1.0, 'L10': 0.0}),
            ("Test 118: Complex nested FOR loops with IF conditions and set iteration",
             "For D as number dim 65\nLet D(2) = 1\nFor I in 1 to 9 do\n  For a = (i + 3) * i \\ 2 + 1\n  For b = (I + 1) * i \\ 2\n  For J in 1 to I+1 do\n    Let D(a+j) = D(b+j-1) + D(B+J)\n  end\nend\n[^A1] := D",
             {'A1': 0.0, 'B1': 1.0, 'C1': 0.0, 'D1': 1.0, 'E1': 1.0, 'F1': 0.0, 'G1': 1.0, 'H1': 2.0, 'I1': 1.0, 'J1': 0.0, 'K1': 1.0, 'L1': 3.0, 'M1': 3.0, 'N1': 1.0, 'O1': 0.0, 'P1': 1.0, 'Q1': 4.0, 'R1': 6.0, 'S1': 4.0, 'T1': 1.0, 'U1': 0.0, 'V1': 1.0, 'W1': 5.0, 'X1': 10.0, 'Y1': 10.0, 'Z1': 5.0, 'AA1': 1.0, 'AB1': 0.0, 'AC1': 1.0, 'AD1': 6.0, 'AE1': 15.0, 'AF1': 20.0, 'AG1': 15.0, 'AH1': 6.0, 'AI1': 1.0, 'AJ1': 0.0, 'AK1': 1.0, 'AL1': 7.0, 'AM1': 21.0, 'AN1': 35.0, 'AO1': 35.0, 'AP1': 21.0, 'AQ1': 7.0, 'AR1': 1.0, 'AS1': 0.0, 'AT1': 1.0, 'AU1': 8.0, 'AV1': 28.0, 'AW1': 56.0, 'AX1': 70.0, 'AY1': 56.0, 'AZ1': 28.0, 'BA1': 8.0, 'BB1': 1.0, 'BC1': 0.0, 'BD1': 1.0, 'BE1': 9.0, 'BF1': 36.0, 'BG1': 84.0, 'BH1': 126.0, 'BI1': 126.0, 'BJ1': 84.0, 'BK1': 36.0, 'BL1': 9.0, 'BM1': 1.0}),
            ("Test 119: Binomial coefficient calculation with nested loops",
             "For D as number dim 15\nLet D(2) = 1\nFor I in 1 to 3 do\n  let a = (i + 3) * i \\ 2 + 1\n  let b = (I + 1) * i \\ 2\n  For J in {1, 2, 3, 4} do\n    if j <= I+1 then\n      Let D(a+j) = D(b+j-1) + D(B+J)\n    end\n  end\nend\n[^A1] := D",
             {'A1': 0.0, 'B1': 1.0, 'C1': 0.0, 'D1': 1.0, 'E1': 1.0, 'F1': 0.0, 'G1': 1.0, 'H1': 2.0, 'I1': 1.0, 'J1': 0.0, 'K1': 1.0, 'L1': 3.0, 'M1': 3.0, 'N1': 1.0, 'O1': 0.0}),
            ("Test 120: Binomial type with grid spilling (Pascal's Triangle)",
             "define binomial as type\n  [B1] := 1\n  For a in 2 to 10 AND b in 2 to a+1 do\n    Let grid{a, b} = grid{a-1, b-1} + grid{a-1, b}\n  End\nend binomial\n\n: Bin = new Binomial()\n[^A1] := Bin.grid",
             {'A1': 0, 'B1': 1, 'B2': 1, 'C2': 1, 'B3': 1, 'C3': 2, 'D3': 1, 'B4': 1, 'C4': 3, 'D4': 3, 'E4': 1, 'B5': 1, 'C5': 4, 'D5': 6, 'E5': 4, 'F5': 1, 'B6': 1, 'C6': 5, 'D6': 10, 'E6': 10, 'F6': 5, 'G6': 1, 'B7': 1, 'C7': 6, 'D7': 15, 'E7': 20, 'F7': 15, 'G7': 6, 'H7': 1, 'B8': 1, 'C8': 7, 'D8': 21, 'E8': 35, 'F8': 35, 'G8': 21, 'H8': 7, 'I8': 1, 'B9': 1, 'C9': 8, 'D9': 28, 'E9': 56, 'F9': 70, 'G9': 56, 'H9': 28, 'I9': 8, 'J9': 1, 'B10': 1, 'C10': 9, 'D10': 36, 'E10': 84, 'F10': 126, 'G10': 126, 'H10': 84, 'I10': 36, 'J10': 9, 'K10': 1}),
            ("Test 121: Guard prevents earlier statements",
             "[A1] := 9\nIf 2 < 1\n[A2] := 7", {}),
            ("Test 122: Guard allows execution when true",
             ": needle = 5\n[A1] := needle\nIf needle < 10\n[A2] := needle + 1", {'A1': 5, 'A2': 6}),
            ("Test 123: Guard blocks when condition false with definition",
             ": limit = 25\n[A1] := 42\nIf limit < 10\n[A2] := limit", {}),
            ("Test 124: Assignment waits for future FOR variable",
             "[A1] := total + 1\nFor total as number = 10", {'A1': 11}),
            ("Test 125: LET waits for future definition",
             "Let result = base + 5\nFor base as number = 7\n[A1] := result", {'A1': 12}),
            ("Test 126: IF THEN ELSE simple",
             ": V = 1\n[A1] := \"single\"\nIf V < 10 then [B1] := \"ok\"", {'A1': 'single', 'B1': 'ok'}),
            ("Test 127: FOR range block assignment",
             "For i in 1 to 3 do\n  [A{i}] := i\nEnd", {'A1': 1, 'A2': 2, 'A3': 3}),
            ("Test 128: Guard prevents runtime errors in body",
             "If 1 = 0\n[A1] := 1 / 0", {}),
            ("Test 129: Global FOR declaration executes before main",
             "For length as number = 6\n[A1] := length", {'A1': 6}),
            ("Test 130: Doc LET chain dependencies",
             "Let X = 2 and Y = X * 5 and Z = Y - X\n[A1] := Z", {'A1': 8.0}),
            ("Test 131: Doc LET with late declaration",
             "Let x = y \\ 2\nFor x as number\nFor y as number = 13\n[A1] := x", {'A1': 6.0}),
            ("Test 132: Doc guard sum condition",
             "[B1] := 400\n[B2] := 500\n[A1] := 9\nIf sum[B1:B2] < 1000", {'B1': 400, 'B2': 500, 'A1': 9}),
            ("Test 133: Doc guard with input allows execution",
             "Input x as number\n[A1] := 9\nIf x < 1000", {'A1': 9}, ['500']),
            ("Test 134: Guard allows execution when true with input",
             "input needle as number\n[A1] := needle\nIf needle < 10\n[A2] := needle + 1", {'A1': 5.0, 'A2': 6.0}, ['5']),
            ("Test 135: Guard blocks when condition false with input",
             "input limit as number\n[A1] := 42\nIf limit < 10\n[A2] := limit", {}, ['25']),
            ("Test 136: Doc global FOR sequence",
             "For n in 2 to 4 do\n  [A{n}] := n\nEnd", {'A2': 2, 'A3': 3, 'A4': 4}),
            ("Test 137: Tyre size lookup TOYO YARI",
             tyresize_code, {'A1': 195, 'B1': 55, 'C1': 16}, ['TOYO', 'YARI']),
            ("Test 138: Tyre size lookup MERC C200",
             tyresize_code, {'A1': 225, 'B1': 45, 'C1': 18}, ['MERC', 'C200']),
            ("Test 139: Default input value",
             "Input x as number or = 5\n[A1] := x",
             {'A1': 5.0}),
            ("Test 140: INIT allows later updates",
             ": x as number init 3\n[A1] := x\npush x = 7\n[A2] := x",
             {'A1': 7, 'A2': 7}),
            ("Test 141: Function reverse example",
             "define Reverse as Function\n Input word as Text\n For rev as Text init \"\"\n For i in 1 to Len(word) do\n  Let c = Mid(word, i, 1)\n  push rev = c & rev\n End\n return rev\nend Reverse\n[A1] := Reverse(\"SINED\")",
             {'A1': 'DENIS'}),
            ("Test 142: Function square with output",
             "Define SQUARE as Function\n Input n as number\n Output sq as number\n push Sq = n ^ 2\nEnd SQUARE\n[A1] := square(5)",
             {'A1': 25.0}),
            ("Test 143: Function spellreverse multi-output",
             "define SpellReverse as function\n Input word as Text\n For i in Len(word) to 1 step -1 do\n  return Mid(word, i, 1)\n End\nend SpellReverse\nreturn SpellReverse(\"DIRG\")",
             {}),
            ("Test 144: Subprocess pushes to caller binding",
             "define DoublePush as subprocess\n Input n as number\n Output res as number\n push res = n\n push res = n * 2\nend DoublePush\n\nDoublePush(3, [^A1])",
             {'A1': 6}),
            ("Test 145: Subprocess grid spill through result",
             "define SpellReverseSub as subprocess\n Input word as Text\n [^A1] := {Mid(word, Len(word), 1), Mid(word, Len(word)-1, 1), Mid(word, Len(word)-2, 1), Mid(word, Len(word)-3, 1)}\nend SpellReverseSub\n\n[^C1] := SpellReverseSub(\"DIRG\").grid",
             {'C1': 'G', 'D1': 'R', 'E1': 'I', 'F1': 'D'}),
            ("Test 146: Subprocess split name push to binding",
             "Define SplitName as Subprocess\n Input Name as text\n Output Result as text\n For Parts as text = TextSplit(Name, \" \")\n  push Result = Parts\n End SplitName\n\n[A1] := \"Jane Doe\"\nSplitName([A1], [^B1])",
             {'A1': 'Jane Doe', 'B1': 'Jane', 'C1': 'Doe'}),
            ("Test 147: Subprocess grid builder reverse word",
             "define SpellReverseSub as subprocess\n Input word as Text\n For i in Len(word) to 1 step -1 index c do\n  Let grid{1, c} = Mid(word, i, 1)\n End\nend SpellReverseSub\nFor myword = SpellReverseSub(\"DIRG\")\n[^A1] := myword.grid",
             {'A1': 'G', 'B1': 'R', 'C1': 'I', 'D1': 'D'}),
            ("Test 148: Type constructor with inputs and mutable peer",
             "Define Point1 as Type\n Input in_x as number\n Input in_y as number\n : x = in_x\n : y = in_y\nEnd Point1\nDefine Point2 as Type\n : x as number\n : y as number\nEnd Point2\n\n: P1 = new Point1(3.0, -2.0)\n: P2 = new Point2(1.2, 0.7)\npush P2.Y = 1001.0\n[^A1] := P1\n[^A3] := P2",
             {'A1': 3.0, 'B1': -2.0, 'A3': 1.2, 'B3': 1001.0}),
            ("Test 149: Type constructor immutability conflict",
             "Define Point1 as Type\n Input in_x as number\n Input in_y as number\n : x = in_x\n : y = in_y\nEnd Point1\n: P1 = new Point1(3.0, -2.0)\npush P1.Y = 1001.0\n[A1] := P1.y",
             None),
            ("Test 150: Member function DistanceToOrigin",
             "Define Point1 as Type\n: x as number\n: y as number\nEnd Point1\nDefine Point1.DistanceToOrigin as Function\nInput p as Point1\nreturn SQRT(p.x ^ 2 + p.y ^ 2)\nend Point1.DistanceToOrigin\n: P1 = new Point1(3, 4)\n[A1] := P1.DistanceToOrigin",
             {'A1': 5.0}),
            ("Test 151: INIT copies object, equality shares reference",
             "Define Point as Type\n: x as number\n: y as number\nEnd Point\n: f = new Point(-1.0, 0.0)\n: p init f\npush f.y = 2.0\n[^A1] := f\n[^A3] := p",
             {'A1': -1.0, 'B1': 2.0, 'A3': -1.0, 'B3': 0.0}),
            ("Test 152: Equality constraint tracks updates",
             "Define Point as Type\n: x as number\n: y as number\nEnd Point\n: f = new Point(-1.0, 0.0)\n: p = f\npush f.y = 2.0\n[^A1] := p",
             {'A1': -1.0, 'B1': 2.0}),
            ("Test 153: Input default via equality constraint",
             "Define square as function\n Input x as number or = 5\n return x ^ 2\nEnd\n: y = square()\n: z = square(\"circle\")\n[^A1] := y",
             {'A1': 25.0}),
            ("Test 154: Output INIT vs equality on output",
             "Define square_init as function\n Input x as number\n Output r as number Init x ^ 2\nEnd\nDefine square_eq_c as function\n Input x as number\n Output r as number = x ^ 2\nEnd\n[A1] := square_init(3)\n[A2] := square_eq_c(4)",
             {'A1': 9.0, 'A2': 16.0}),
            ("Test 155: FOR INIT generator without IN",
             "define SpellReverse as function\n Input word as Text\n For i in Len(word) to 1 step -1 do\n  return Mid(word, i, 1)\n End\nend SpellReverse\n: acc as text init \"\"\nFor letter as text init SpellReverse(\"DIRG\") do\n push acc = acc & letter\nend\n[^A1] := acc\n\nFor letter2 as text init SpellReverse(\"DIRG\")\n[A2] := letter2\n\nFor letter3 as text\n push letter3 = SpellReverse(\"DIRG\")\n[A3] := letter3",
             {'A1': 'GRID', 'A2': 'D', 'A3': 'D'}),
            ("Test 156: Subprocess INIT materializes grid result",
             "define SpellReverseSub as subprocess\n Input word as Text\n For i in Len(word) to 1 step -1 index c do\n  Let grid{1, c} = Mid(word, i, 1)\n End\nend SpellReverseSub\nFor myword init SpellReverseSub(\"DIRG\")\n[^A1] := myword.grid",
             {'A1': 'G', 'B1': 'R', 'C1': 'I', 'D1': 'D'}),
            ("Test 157: Friendly member function call via For assignment",
             "Define Point1 as Type\n Input in_x as number\n Input in_y as number\n : x = in_x\n : y = in_y\nEnd Point1\n\nFor P1 = new Point1(3.0, -2.0)\n\nDefine Point1.DistanceToOrigin as Function\n Input p as Point1\n return SQRT(p.x ^ 2 + p.y ^ 2)\nend Point1.DistanceToOrigin\n\nFor d = P1.DistanceToOrigin()\n[^A1] := d",
             {'A1': 3.605551275463989}),
            ("Test 158: Nested generator zipping in Push",
             "define SpellReverse as function\n Input word as Text\n For i in Len(word) to 1 step -1 do\n  return Mid(word, i, 1)\n End\nend SpellReverse\n\ndefine combine as function\n Input a, b as text\n return a & \"-\" & b\nend combine\n\nreturn combine(SpellReverse(\"DIRG\"), SpellReverse(\"ecin\"))",
             {}),
            ("Test 159: FOR text without dim allows any size",
             "For a as text = {\"hello\", \"world\", \"!\"}", {}),
            ("Test 160: FOR text with dim size mismatch",
             "For a as text dim 2 = {\"hello\", \"world\", \"!\"}", None),
            ("Test 161: FOR nested init with push and cell write",
             "for acc as text init \"\" do\n  for letter as text init \"o\" do\n    push acc = letter & \"x\"\n    [A1] := acc\n  end\nend",
             {'A1': 'ox'}),
            ("Test 162: Milestone 4 constraints",
             "For vmax = 5\nFor v <= vmax\nLet v = 3\nFor names dim 0 to 4\nLet names = {\"Alice\", \"Bob\", \"Carla\", \"Dylan\", \"Edith\"}\n[A1] := v\n[^A2] := names",
             {'A1': 3, 'A2': 'Alice', 'B2': 'Bob', 'C2': 'Carla', 'D2': 'Dylan', 'E2': 'Edith'}),
            ("Test 163: Combined constraints literal values",
             ": choice as number in {1, 2, 3} = 2\n: span as number in 1 to 10 = 7\n: words as text dim 2 = {\"hi\", \"yo\"}\n\n[A2] := choice\n[A3] := span\n[^A4] := words",
             {'A2': 2, 'A3': 7, 'A4': 'hi', 'B4': 'yo'}),
            ("Test 164: Subprocess writes into dimmed parts",
             ": parts as text dim 2\n\nDefine SplitName as Subprocess\n Input Name as text\n push Parts = TextSplit(Name, \" \")\nEnd SplitName\n\n[A1] := \"Jane Doe\"\n[^B1] := parts\nSplitName([A1])\n[^B1] := parts",
             {'A1': 'Jane Doe', 'B1': 'Jane', 'C1': 'Doe'}),
            ("Test 165: Column interpolation",
             ": i = 4\n[{i :A}5] := 11\n: j = 4\n[{j :CB}5] := 22", {'D5': 11, 'CE5': 22}),
            ("Test 166: Hidden field skipped on spill",
             "Define SecretPoint as Type\n: x as number\n: $secret as number init 99\nEnd SecretPoint\n: p = new SecretPoint with (x = 7)\n[^A1] := p",
             {'A1': 7.0}),
            ("Test 167: Hidden field access outside type errors",
             "Define SecretPoint as Type\n: x as number\n: $secret as number init 99\nEnd SecretPoint\n: p = new SecretPoint with (x = 7)\n[A1] := p.secret",
             None),
            ("Test 168: Private helper in constructor",
             "Define Point as Type\nInput in_x, in_y as number\n: x as number init in_x\n: y as number init in_y\nShiftRight(2.0)\nEnd Point\nDefine Point.ShiftRight as PrivateHelper\nInput dx as number\nPush x = x + dx\nEnd Point.ShiftRight\n: p = new Point(1.0, 2.0)\n[^A1] := p",
             {'A1': 3.0, 'B1': 2.0}),
            ("Test 169: Private helper called from member function",
             "Define Point as Type\nInput in_x, in_y as number\n: x as number init in_x\n: y as number init in_y\nEnd Point\nDefine Point.ShiftRight as PrivateHelper\nInput dx as number\nPush x = x + dx\nEnd Point.ShiftRight\nDefine Point.GoSlightlyRight as Function\nInput P as Point\nOutput Shifted as Point\nPush Shifted = P.ShiftRight(0.5)\nEnd Point.GoSlightlyRight\n: p = new Point(1.0, 2.0)\nFor s as Point\nPush s = Point.GoSlightlyRight(p)\n[^A1] := s",
             {'A1': 1.5, 'B1': 2.0}),
            ("Test 170: Hidden member function call outside type errors",
             "Define Point as Type\n: x as number\n: y as number\nEnd Point\nDefine $Point.OnTheRight as Function\nInput P1, P2 as Point\nReturn P1.x > P2.x?\nEnd $Point.OnTheRight\n: p1 = new Point(1.0, 0.0)\n: p2 = new Point(2.0, 0.0)\n[A1] := p1.OnTheRight(p2)",
             None),
            ("Test 171: Type instantiation from array without constructor inputs",
             "Define Simple as Type\n: x as number\n: y as number\nEnd Simple\nFor P as Simple = {1.0, -5.0}\n[^A1] := P",
             {'A1': 1.0, 'B1': -5.0}),
            ("Test 172: New with WITH and shorthand variables",
             "Define Point as Type\n: x as number\n: y as number\nEnd Point\n: x = 1.0\n: y = -5.0\n: P = new Point with (x, y)\n[^A1] := P",
             {'A1': 1.0, 'B1': -5.0}),
            ("Test 173: Type extension with Super and new field",
             "Define Point as Type\nInput in_x, in_y as number or = 0.0\n: x as number init in_x\n: y as number init in_y\nEnd Point\nDefine RoundDot as Type(Point)\nInput in_x, in_y as number or = 0.0\nSuper(in_x, in_y)\n: radius as number or = 0.1\nEnd RoundDot\n: R = new RoundDot(2.0, 3.0) with (radius = 0.5)\n[^A1] := R",
             {'A1': 2.0, 'B1': 3.0, 'C1': 0.5}),
            ("Test 174: Type constraints on numeric subtype",
             "Define RateValue as Type(Number) >= 0.0 <= 1.0\nEnd RateValue\nFor r as RateValue = 0.25\n[A1] := r",
             {'A1': 0.25}),
            ("Test 175: Type constraint violation errors",
             "Define RateValue as Type(Number) >= 0.0 <= 1.0\nEnd RateValue\nFor r as RateValue = 1.5\n[A1] := r",
             None),
            ("Test 176: Member function override polymorphism",
             "Define Point as Type\n: x as number\n: y as number\nEnd Point\nDefine Point.OnTheLeft as Function\nInput P1, P2 as Point\nReturn P1.x < P2.x?\nEnd Point.OnTheLeft\nDefine RoundDot as Type(Point)\nInput in_x, in_y as number or = 0.0\nSuper(in_x, in_y)\n: radius as number or = 0.1\nEnd RoundDot\nDefine RoundDot.OnTheLeft as Function\nInput D1, D2 as RoundDot\nReturn D1.x + D1.radius + D2.radius < D2.x?\nEnd RoundDot.OnTheLeft\n: R = new RoundDot(9.0, 0.0) with (radius = 0.5)\n: S = new RoundDot(9.5, 4.0) with (radius = 0.5)\n[A1] := R.OnTheLeft(S)",
             {'A1': 0}),
            ("Test 177: Member function override uses RoundDot",
             "Define Point as Type\nInput in_x, in_y as number or = 0.0\n: x as number init in_x\n: y as number init in_y\nEnd Point\nDefine Point.OnTheLeft as Function\nInput P1, P2 as Point\nReturn P1.x < P2.x?\nEnd Point.OnTheLeft\nDefine RoundDot as Type(Point)\nInput in_x, in_y as number or = 0.0\nSuper(in_x, in_y)\n: radius as number or = 0.1\nEnd RoundDot\nDefine RoundDot.OnTheLeft as Function\nInput D1, D2 as RoundDot\nReturn D1.x + D1.radius + D2.radius < D2.x?\nEnd RoundDot.OnTheLeft\n: R = new RoundDot(9.0, 0.0) with (radius = 0.5)\n: P = new RoundDot(900.0, 0.0) with (radius = 0.5)\n[A1] := R.OnTheLeft(P)",
             {'A1': 1}),
            ("Test 178: Array init fixed dim via LET",
             "For A as Number dim 3\nlet A(1) = 12\nlet A(2) = 5\nlet A(3) = 0.3\n[^A1] := A",
             {'A1': 12, 'B1': 5, 'C1': 0.3}),
            ("Test 179: Array dim * requires PUSH",
             "For B as Number dim *\nlet B(1) = 12",
             None),
            ("Test 180: Array dim * grows with PUSH",
             "For C as Number dim *\npush C(1) = 12\npush C(2) = 5\npush C(3) = 0.3\n[^A1] := C",
             {'A1': 12, 'B1': 5, 'C1': 0.3}),
            ("Test 181: Push without dim errors",
             "For D as Number\npush D(1) = 12",
             None)
        ]

        doc_tests = [
            ("Doc: helloworld_basic", "Documentation_Tests/helloworld_basic.grid", ...),
            ("Doc: helloworld_calc", "Documentation_Tests/helloworld_calc.grid", ...),
            ("Doc: helloworld_input",
             "Documentation_Tests/helloworld_input.grid", ..., ['World']),
            ("Doc: helloworld_inputs",
             "Documentation_Tests/helloworld_inputs.grid", ..., ['3', '2']),
            ("Doc: helloworld_input_default",
             "Documentation_Tests/helloworld_input_default.grid", ...),
            ("Doc: helloworld_input_typed",
             "Documentation_Tests/helloworld_input_typed.grid", ..., ['World']),
            ("Doc: helloworld",
             "Documentation_Tests/helloworld.grid", ..., ['3', '2']),
            ("Doc: scratch_basic", "Documentation_Tests/scratch_basic.grid", ...),
            ("Doc: scratch_avg", "Documentation_Tests/scratch_avg.grid", ...),
            ("Doc: scratch_arrays", "Documentation_Tests/scratch_arrays.grid", ...),
            ("Doc: scratch_arrays_2d",
             "Documentation_Tests/scratch_arrays_2d.grid", ...),
            ("Doc: scratch", "Documentation_Tests/scratch.grid", ...),
            ("Doc: scratch_custom_type",
             "Documentation_Tests/scratch_custom_type.grid", ...),
            ("Doc: scratch_constraints",
             "Documentation_Tests/scratch_constraints.grid", ...),
            ("Doc: credit_type", "Documentation_Tests/credit_type.grid", ...),
            ("Doc: credit_usage", "Documentation_Tests/credit_usage.grid", ...),
            ("Doc: variables", "Documentation_Tests/variables.grid", ...),
            ("Doc: variables_push", "Documentation_Tests/variables_push.grid", ...),
            ("Doc: variables_push_multireturn",
             "Documentation_Tests/variables_push_multireturn.grid", ...)
        ]

        base_dir = Path(__file__).resolve().parent
        #for entry in doc_tests:
        #    name, rel_path, expected, *rest = entry
        #    code = (base_dir / rel_path).read_text(encoding='utf-8')
        #    tests_data.append((name, code, expected, *rest))

        passed = 0
        failed = 0
        total = 0
        failed_tests = []

        print("DEBUG: Starting test suite")
        for entry in tests_data:
            if len(entry) == 3:
                name, code, expected = entry
                test_args = None
            elif len(entry) == 4:
                name, code, expected, test_args = entry
            else:
                raise ValueError(f"Invalid test specification: {entry}")
            if not tests or name.split(":")[0][5:] in tests:
                print(f"DEBUG: Test code for {name}:\n{code}")
                if test_args is not None:
                    print(f"DEBUG: Test arguments for {name} = {test_args}")
                print(f"DEBUG: Expected output for {name} = {expected}")
                total += 1
                print(f"\nDEBUG: Running {name}")
                try:
                    if test_args is not None:
                        result = self.compiler.run(code, test_args)
                    else:
                        result = self.compiler.run(code)
                    sorted_res = dict(sorted(result.items()))
                    print(
                        f"DEBUG: Test output: {self.compiler.truncate_output(sorted_res)}")
                    # f"DEBUG: Test output: {sorted_res}")
                    if expected is ...:
                        print("DEBUG: Documentation test executed")
                        passed += 1
                    elif expected is None:
                        print("DEBUG: Expected error but got success")
                        failed += 1
                        failed_tests.append(name)
                    else:
                        sorted_exp = dict(sorted(expected.items()))
                        match = True

                        # Case-insensitive key comparison
                        res_keys_lower = {
                            k.lower(): k for k in sorted_res.keys()}
                        exp_keys_lower = {
                            k.lower(): k for k in sorted_exp.keys()}

                        if set(res_keys_lower.keys()) != set(exp_keys_lower.keys()):
                            match = False
                        else:
                            for exp_key in sorted_exp:
                                exp_key_lower = exp_key.lower()
                                # Find the actual result key (case-insensitive)
                                actual_res_key = res_keys_lower.get(
                                    exp_key_lower)
                                if actual_res_key is None:
                                    match = False
                                    break

                                a_val = sorted_res[actual_res_key]
                                e_val = sorted_exp[exp_key]
                                if isinstance(e_val, float) and math.isnan(e_val):
                                    if not (isinstance(a_val, float) and math.isnan(a_val)):
                                        match = False
                                elif isinstance(e_val, float) and isinstance(a_val, float):
                                    if not math.isclose(a_val, e_val, rel_tol=1e-9):
                                        match = False
                                elif isinstance(e_val, int) and isinstance(a_val, float) and a_val.is_integer():
                                    a_val = int(a_val)
                                    if a_val != e_val:
                                        match = False
                                elif isinstance(e_val, list) and isinstance(a_val, list):
                                    # Support both nested lists and flat lists
                                    if all(isinstance(a, list) for a in a_val) and all(isinstance(e, list) for e in e_val):
                                        if not all(isinstance(a, list) and isinstance(e, list) and all(math.isclose(av, ev, rel_tol=1e-9) if isinstance(ev, float) else av == ev for av, ev in zip(a, e)) for a, e in zip(a_val, e_val)):
                                            match = False
                                    else:
                                        if len(a_val) != len(e_val) or not all(
                                                math.isclose(av, ev, rel_tol=1e-9) if isinstance(
                                                    ev, float) and isinstance(av, (int, float)) else av == ev
                                                for av, ev in zip(a_val, e_val)):
                                            match = False
                                elif isinstance(e_val, dict) and isinstance(a_val, dict):
                                    if not all(a_val.get(kk) == vv for kk, vv in e_val.items()):
                                        match = False
                                elif a_val != e_val:
                                    match = False
                        if match:
                            print("DEBUG: Test passed")
                            passed += 1
                        else:
                            print(
                                # f"DEBUG: Test failed. Expected: {self.truncate_output(sorted_exp)}")
                                f"DEBUG: Test failed. Expected: {sorted_exp}")
                            failed += 1
                            failed_tests.append(name)
                except Exception as e:
                    print(f"DEBUG: Test error: {type(e).__name__}: {e}")
                    if expected is ...:
                        print("DEBUG: Documentation test failed")
                        failed += 1
                        failed_tests.append(name)
                    elif expected is None:
                        print("DEBUG: Test passed (expected error)")
                        passed += 1
                    else:
                        print(
                            # f"DEBUG: Test failed. Expected: {self.truncate_output(expected)}")
                            f"DEBUG: Test failed. Expected: {expected}")
                        failed += 1
                        failed_tests.append(name)
        print(
            f"DEBUG: Test summary - Total: {total}, Passed: {passed}, Failed: {failed}")
        if failed_tests:
            print("DEBUG: Failed tests:")
            for test_name in failed_tests:
                print(f"  - {test_name}")

import sys
from compiler import GridLangCompiler
GridLangTestRunner(GridLangCompiler()).run_tests_independent(sys.argv[1:])
