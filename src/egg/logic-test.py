import egg.logic as logic

def sayhello():
    print("hello")

new = logic.pAst_if("1 == 1")
logic.doFuncWhenIfMatch([sayhello], [new])