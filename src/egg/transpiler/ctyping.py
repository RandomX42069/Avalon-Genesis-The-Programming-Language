import egg.parser as grammar
import egg.transpiler.cdepency as cdep
import egg.transpiler.ctypesDSL as cdsl
import egg.transpiler.cglob as cglob

def ctypeFromValue(string):
    string = string.strip()
    if grammar.isString(string):return ["char", cdep.cDepency(None), cdsl.ctypeDSL({"list": False})]
    elif grammar.isInteger(string):return ["int", cdep.cDepency(None), cdsl.ctypeDSL({"list": False})]
    elif grammar.isBool(string):return ["bool", cdep.cDepency("stdbool.h"), cdsl.ctypeDSL({"list": False})]
    elif grammar.isFloat(string):return ["double", cdep.cDepency(None), cdsl.ctypeDSL({"list": False})]

def ctypeFromArray(string):
    elements = grammar.split_arg(string)
    if not elements: return
    fullReturn = ctypeFromValue(elements[0])
    baseType = fullReturn[0]
    for i, v in enumerate(elements):
        if ctypeFromValue(v)[0] != baseType: return [baseType, cdsl.cWarn("Mixed types"), fullReturn, True]
    
    return [baseType, cdsl.cWarn(None), fullReturn, True]

def ctypeFromValueEx(string):
    """
    this version come with a more full type
    """
    string = string.strip()
    if grammar.isString(string):return ["char", cdep.cDepency(None), cdsl.ctypeDSL({"list": False})]
    elif grammar.isInteger(string):return ["int", cdep.cDepency(None), cdsl.ctypeDSL({"list": False})]
    elif grammar.isBool(string):return ["bool", cdep.cDepency("stdbool.h"), cdsl.ctypeDSL({"list": False})]
    elif grammar.isFloat(string):return ["double", cdep.cDepency(None), cdsl.ctypeDSL({"list": False})]
    elif grammar.isArray(string):return [ctypeFromArray(string), cdep.cDepency(None), cdsl.ctypeDSL({"list": True})]
