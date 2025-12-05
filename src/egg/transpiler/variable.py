import re
import egg.transpiler.ctyping as ctyper
import egg.transpiler.cglob as cglob

variableRegex = re.compile(r'(.+)\s*\=\s*(.+)')
variable2Regex = re.compile(r'(.+)\:\s*(.+)\s*\=\s*(.+)')

def processToC(string):
    match1 = variableRegex.match(string)
    match2 = variable2Regex.match(string)

    cA = ""

    if match1:
        varName = match1.group(1)
        varRawValue = match1.group(2)
        varValue = ctyper.ctypeFromValueEx(varRawValue)
        
        if isinstance(varValue[0], str):
            if varValue[1]: cglob.cInc(varValue[1])
            cA += varValue[0] + " " + varName + " = " + varRawValue + ";"
        elif isinstance(varValue[0], list):
            if varValue[0][2][1]: cglob.cInc(varValue[0][2][1])
            cA += varValue[0][0] + " " + varName + "[]" + " = " + varRawValue + ";"

    elif match2:
        varName = match2.group(1)
        varType = match2.group(2)
        varRawValue = match2.group(3)
        