inc = """
"""

def cInc(name):
    if name:
        global inc
        inc += f"#include <{name}>"