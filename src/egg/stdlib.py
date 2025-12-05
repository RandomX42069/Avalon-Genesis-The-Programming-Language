bit8IntLimit = 255
bit16UsignedIntLimit = 32767
bit16SignedIntLimit = 65535
bit32IntLimit = 2147483647
bit64IntLimit = 9223372036854775807

import datetime
import os
import sys
import pathlib

class clock:
    def __init__(self, stamp=None):
        self.stamp = stamp
        self.logRate = {
            "newborn": 86400,
            "normal": 360000,
            "ancient": 13234342342
        }
        self._egg_global = AGC_GLOBAL()
        self._fs = filesystem()

    def integerDate(self):
        return int(datetime.datetime.now().timestamp())

    def _isFar(self, t, override=None):
        threshold = self.stamp if override is None else override
        return (self.integerDate() - t) > threshold

    def _filetime(self, fn):
        if not self._fs.isExistAndFile(fn):
            self._egg_global.err(f"File doesn't exist: {fn}")
            sys.exit(0)
        return int(os.path.getmtime(fn))

    def _ancient_log(self, fn, suffixes, threshold=None):
        if not self._fs.isExistAndFile(fn):
            self._egg_global.err(f"File doesn't exist: {fn}")
            sys.exit(0)

        p = pathlib.Path(fn)
        if p.suffix not in suffixes:
            return False
        return self._isFar(self._filetime(str(p)), override=threshold)

    def clean_directory(self, directory, suffixes, rate="normal"):
        if rate not in self.logRate:
            self._egg_global.err(f"Invalid rate '{rate}', must be one of: {list(self.logRate.keys())}")
            sys.exit(1)

        age_limit = self.logRate[rate]
        if not self._fs.isExistAndDir(directory):
            self._egg_global.err(f"Directory doesn't exist: {directory}")
            sys.exit(0)

        dirpath = pathlib.Path(directory)
        deleted = 0
        scanned = 0

        for file in dirpath.iterdir():
            if not file.is_file():
                continue
            scanned += 1
            abs_path = str(file)
            if self._ancient_log(abs_path, suffixes, threshold=age_limit):
                try:
                    os.remove(abs_path)
                    deleted += 1
                    self._egg_global.ok(f"Deleted old log: {abs_path}")
                except Exception as e:
                    self._egg_global.err(f"Error deleting {abs_path}: {e}")

        return {"scanned": scanned, "deleted": deleted}


import colorama

FBLACK, FRED, FGREEN, FYELLOW, FBLUE, FMAGENTA, FCYAN, FWHITE, FRESET = (
    colorama.Fore.BLACK, colorama.Fore.RED, colorama.Fore.GREEN,
    colorama.Fore.YELLOW, colorama.Fore.BLUE, colorama.Fore.MAGENTA,
    colorama.Fore.CYAN, colorama.Fore.WHITE, colorama.Fore.RESET
)

FBRIGHTBLACK, FBRIGHTRED, FBRIGHTGREEN, FBRIGHTYELLOW, FBRIGHTBLUE, FBRIGHTMAGENTA, FBRIGHTCYAN, FBRIGHTWHITE = (
    colorama.Fore.LIGHTBLACK_EX, colorama.Fore.LIGHTRED_EX, colorama.Fore.LIGHTGREEN_EX,
    colorama.Fore.LIGHTYELLOW_EX, colorama.Fore.LIGHTBLUE_EX, colorama.Fore.LIGHTMAGENTA_EX,
    colorama.Fore.LIGHTCYAN_EX, colorama.Fore.LIGHTWHITE_EX
)

BBLACK, BRED, BGREEN, BYELLOW, BBLUE, BMAGENTA, BCYAN, BWHITE, BRESET = (
    colorama.Back.BLACK, colorama.Back.RED, colorama.Back.GREEN,
    colorama.Back.YELLOW, colorama.Back.BLUE, colorama.Back.MAGENTA,
    colorama.Back.CYAN, colorama.Back.WHITE, colorama.Back.RESET
)

BBRIGHTBLACK, BBRIGHTRED, BBRIGHTGREEN, BBRIGHTYELLOW, BBRIGHTBLUE, BBRIGHTMAGENTA, BBRIGHTCYAN, BBRIGHTWHITE = (
    colorama.Back.LIGHTBLACK_EX, colorama.Back.LIGHTRED_EX, colorama.Back.LIGHTGREEN_EX,
    colorama.Back.LIGHTYELLOW_EX, colorama.Back.LIGHTBLUE_EX, colorama.Back.LIGHTMAGENTA_EX,
    colorama.Back.LIGHTCYAN_EX, colorama.Back.LIGHTWHITE_EX
)

STYLEBRIGHT = colorama.Style.BRIGHT
STYLEDIM = colorama.Style.DIM
STYLERESET = colorama.Style.RESET_ALL

def encodeChar(char):
    return ord(char)

def encodeStr(string):
    string = string.strip()
    final = 0
    for char in string:
        final += encodeChar(char)
    return final

def encodeStrReversible(s):
    return s.encode("utf-8")

def decodeStrReversible(b):
    return b.decode("utf-8")

def encodeStrToInt(s):
    result = 0
    for c in s:
        result = (result << 16) | ord(c)
    return result

def decodeIntToStr(n):
    chars = []
    while n > 0:
        chars.append(chr(n & 0xFFFF))
        n >>= 16
    return "".join(reversed(chars))

def encodeFixed8(s: str) -> int:
    b = s.encode("utf-8")[:8].ljust(8, b"\x00")
    return int.from_bytes(b, "little")

def decodeFixed8(n: int) -> str:
    b = n.to_bytes(8, "little")
    return b.rstrip(b"\x00").decode("utf-8")

import shutil

class filesystem:
    def __init__(self):
        self.recursiveSteps = 0
        self._glob = AGC_GLOBAL()

    def isExistAndFile(self, path): return pathlib.Path(os.path.abspath(path)).is_file()
    def isExistAndDir(self, path): return pathlib.Path(os.path.abspath(path)).is_dir()

    def createFile(self, filename):
        with open(filename, "w") as f:
            f.write("")

    def writeToFile(self, filename, content):
        if not self.isExistAndFile(filename):
            self._glob.err(f"File doesn't exists: {filename}")
        if not isinstance(content, bytes):
            content = content.encode("utf-8")
        with open(filename, "wb") as f:
            f.write(content)

    def readFromFile(self, filename):
        if not self.isExistAndFile(filename):
            self._glob.err(f"File doesn't exists: {filename}")
        with open(filename, "rb") as f:
            return f.read()

    def appendToFile(self, filename, content):
        if not self.isExistAndFile(filename):
            self._glob.err(f"File doesn't exists: {filename}")
        if not isinstance(content, bytes):
            content = content.encode("utf-8")
        with open(filename, "ab") as f:
            f.write(content)

    def rmdir(self, directory):
        shutil.rmtree(directory, True)

class AGC_GLOBAL:
    def __init__(self):
        pass

    def err(self, msg, raiseException=True):
        if not raiseException:
            print(f"{colorama.Fore.RED}[ FATAL ]: [ GLOBAL ]: {msg}{colorama.Fore.RESET}")
            sys.exit(1)
        raise RuntimeError(f"{colorama.Fore.RED}[ FATAL ]: [ GLOBAL ]: {msg}{colorama.Fore.RESET}")

    def ok(self, msg):
        print(f"{colorama.Fore.GREEN}[ OK ]: {msg}{colorama.Fore.RESET}")

_fs = filesystem()

def __glue__(filenames: list[str]) -> str:
    parts = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for fp in filenames:
        abs_fp = os.path.join(script_dir, fp)
        if _fs.isExistAndFile(abs_fp):
            content = _fs.readFromFile(abs_fp).decode("utf-8", errors="replace")
            parts.append(f"# src file: {abs_fp}\n{content}")
    return "\n\n".join(parts)

def __glue__package__(filenames, output="bundled.py"):
    _fs.createFile(output)
    data = __glue__(filenames)
    out_dir = os.path.dirname(os.path.abspath(output))
    if out_dir and not _fs.isExistAndDir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    _fs.writeToFile(output, data.encode("utf-8"))

class IndexableTool:
    def __init__(self):
        pass

    def get_last_occurrence(self, obj: list | str, occurrence):
        try:
            return obj.rindex(occurrence)
        except ValueError:
            return None

def get_flag_value(lst, flag):
    if flag not in lst:
        return None
    idx = lst.index(flag)
    if idx + 1 >= len(lst):
        _instance = AGC_GLOBAL()
        _instance.err(f"Flag '{flag}' requires a value.")
        return None
    return lst[idx + 1]

def clear_empty_gap(lst: list):
    return [x for x in lst if x]

def cmpList(lst1: list, lst2: list):
    if not lst1 or not lst2: return True
    if len(lst1) != len(lst2): return False
    return True

def cmpLLen(lst1: list, lst2: list):
    return len(lst1) == len(lst2)

def ulen(lst: list):
    fullIndex = 0
    for each in lst:
        if isinstance(each, list):
            fullIndex += ulen(each)
        fullIndex += 1
    return fullIndex

class pAst_if:
    def __init__(self, con):
        self.context = con

def bind2func(func, func2):
    func()
    func2()

def doFuncWhenIfMatch(functions: list, statements: list[pAst_if]):
    agc_init = AGC_GLOBAL()
    if not cmpList(functions, statements):
        agc_init.err(f"Functions and statement cmp list return false")
    for i, each in enumerate(functions):
        if bool(eval(statements[i].context)):
            each()

import re

def checkInstance(string, unallowedChars: list | str = None):
    if not unallowedChars:
        unallowedChars = "`~!@#$%^&*()-=_+}{[]:;'\"\\|<>?/.,"
    if unallowedChars in string:
        return True
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
    return isinstance(s, str) and ((s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")))

def isChar(inputC):
    return isString(inputC) and len(inputC) == 1

def isBool(inputB):
    return inputB.strip().lower() in ("true", "false")

def isArray(inputl):
    try:
        list(inputl)
        return True
    except ValueError:
        return False

def split_arg(string):
    pattern = r'''((?:[^,"'()\[\]]+|"[^"]*"|'[^']*'|\([^\(\)]*\)|\[[^\[\]]*\])+)'''
    return [a.strip() for a in re.findall(pattern, string.strip(), re.VERBOSE)]

class StringTool:
    def __init__(self, string: str):
        self.string = string

    def _asm_define_from_string(self):
        match self._asm_strType():
            case "str": return "db"
            case "int": return "dd"
            case "bool": return "db"
            case "float": return "dq"

    def _asm_strType(self):
        if self._is_pure_string():
            return "str"
        elif self._is_int():
            return "int"
        elif self._is_float():
            return "float"
        elif self._is_bool():
            return "bool"
        return "Unknown"

    def _asm_def(self, name):
        raw = self.string.replace("\"", "\\\"")
        db_parts = []
        i = 0
        s = raw
        while i < len(s):
            if s.startswith("\\n", i):
                db_parts.append("0x0A")
                i += 2
                continue
            if s.startswith("\\r", i):
                db_parts.append("0x0D")
                i += 2
                continue
            db_parts.append(f"'{s[i]}'")
            i += 1
        db_parts.append('0')
        return f"{name} db " + ", ".join(db_parts)

    def _string_split(self, splits, t=1):
        if t == 1:
            return [self.string.split(each) for each in splits]
        elif t == 2:
            return {each: self.string.split(each) for each in splits}

    def _is_bool(self):
        return self.string.lower() in ("true", "false")

    def _is_int(self):
        try:
            int(self.string)
            return True
        except Exception:
            return False

    def _is_float(self):
        return not self._is_int() and self._string_can_float()

    def _string_can_float(self):
        try:
            float(self.string)
            return True
        except ValueError:
            return False

    def _is_pure_string(self):
        return (self.string.startswith('"') and self.string.endswith('"')) or (self.string.startswith("'") and self.string.endswith("'"))

    def _retend(self, endstring=""):
        return self.string + endstring

    def _truncate(self, length, trailings="..."):
        return self.string[:length] + trailings if len(self.string) > length else self.string

    def _language_safe(self):
        return self.string.replace("\"", "\\\"").replace("\'", "\\'")

