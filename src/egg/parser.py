import re

def checkInstance(string, unallowedChars:list|str=None):
    """return true if there are unallowed chars else false"""
    if not unallowedChars: unallowedChars = "`~!@#$%^&*()-=_+}{[]:;'\"\\|<>?/.,"
    if unallowedChars in string: return True
    return False

def isInteger(inputI: str):
    try:
        int(inputI)
        return True
    except ValueError:
        return False

def isFloat(inputF: str):
    try:
        float(inputF)
        return not isInteger(inputF)
    except ValueError:
        return False
    
def isString(s):
    return (
        isinstance(s, str)
        and (
            (s.startswith('"') and s.endswith('"'))
            or
            (s.startswith("'") and s.endswith("'"))
        )
    )
    
def isChar(inputC):
    if isString(inputC) and len(inputC) == 1:
        return True
    return False

def isBool(inputB):
    if inputB.strip() in ["false", "true", "True", "False"]:
        return True
    return False

def isArray(inputl):
    try:
        list(inputl)
        return True
    except ValueError:
        return False
    
def split_arg(string):
    pattern = r'''((?:[^,"'()\[\]]+|"[^"]*"|'[^']*'|\([^\(\)]*\)|\[[^\[\]]*\])+)'''
    return [a.strip() for a in re.findall(pattern, string.strip(), re.VERBOSE)]