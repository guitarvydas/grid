

import rtlib
subject = rtlib.fresh ()
#  ---- Test 142: Function square with output | expected: {'A1': 25.0} #1

def square (self): #2

    rtlib.input (subject, "n",  "number") #3
    rtlib.output (subject, "sq",  "number") #4
    rtlib.push (subject, "sq", n^2) #5
    
    #end square
#6


rtlib.cellAssign (subject, "a", 1, square(5))
#7



