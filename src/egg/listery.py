import egg.globerr

def get_flag_value(lst, flag):
    if flag not in lst:
        return None
    idx = lst.index(flag)
    if idx + 1 >= len(lst):
        _instance = egg.globerr.AGC_GLOBAL()
        _instance.err(f"Flag '{flag}' requires a value.")
        return None
    return lst[idx + 1]

def clear_empty_gap(lst:list):
    return [x for x in lst if x]

def cmpList(lst1:list, lst2:list):
    if not lst1 or not lst2: return True # since None == None
    if len(lst1) != len(lst2): return False
    return True

def cmpLLen(lst1:list, lst2:list):
    if len(lst1) != len(lst2):return False
    return True

def ulen(lst:list):
    fullIndex = 0
    for i, each in enumerate(lst):
        if isinstance(each, list):
            fullIndex += ulen(each)
        fullIndex += 1
    
    return fullIndex