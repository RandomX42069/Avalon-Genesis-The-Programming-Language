import egg.listery as lstool
import egg.globerr as alert

class pAst_if:
    def __init__(self, con):
        self.context = con

def bind2func(func, func2):
    func()
    func2()

def doFuncWhenIfMatch(functions:list, statements:list[pAst_if]):
    agc_init = alert.AGC_GLOBAL()
    if not lstool.cmpList(functions, statements): agc_init.err(f"Functions and statement cmp list return false")
    for i, each in enumerate(functions):
        if bool(eval(statements[i].context)):
            each()