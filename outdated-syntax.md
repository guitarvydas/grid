Note about the PDF: [@B1] is old syntax for [^B1]

: p = new Point(-4.3, 2.1) when x and y are public fields, is no longer valid. Use: : p = new Point with (x=-4.3, y=2.1) or : p as Point = {-4.3, 2.1}

Super(in_x, in_y) assumes that x and y are inputs, not public fields. Otherwise use: Let x = in_x and y = in_y

Guard example is broken.

For i in 1 to 3 without a block or an assignment is not really a loop. It pushes the values from the sequence to variable « i » one by one, which can have the same effect as a loop if the instruction depends on « i ». That is a nuance to know. If there is a block (do) then the whole block repeats, so it is a loop.

You can have the same effect as For i in 1 to 3 with a function that returns multiple times, for example:

Define Three as Function
  return 1
  return 2
  return 3
End Three
For i = Three()
