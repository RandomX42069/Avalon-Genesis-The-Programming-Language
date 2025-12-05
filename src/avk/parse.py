import re, colorama, json, subprocess, sys, os, egg.fs, egg.globerr, avk.make
from egg.colorful import *

jsonMatch = re.compile(r'\s*@json\s*(.+)\s+(.+)')
functionCall = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*\)\s*$')
functionStart = re.compile(r'@function\s+(.+)')
functionEnd = re.compile(r'@end')

# arguement ARE SPECIFICALLY NOT ALLOWED IN MAKEFILE COMMAND LINES
# so that why I ignore them

class MakefileParser:
    def __init__(self, code:str|list, workingdir):
        self.code = code.strip()
        self.in_ml_comment = False
        self.pos = 0
        self.funcPos = 0
        self._func_parser_pos = 0
        self.working = workingdir
        self.signed = True
        self.debug = False
        self.jsonmake = {}
        self.func = {}
        self.name = "[ AGK ] "
        self._fs = egg.fs.filesystem()
        self._globerr = egg.globerr.AGC_GLOBAL()

    def dprint(self, msg):
        if self.debug:
            print(f"{self.name} Debug: {msg}")

    def checkIllegalName(self, name):
        name = name.strip()
        if not name:
            return

        unallowed = "`~!@#$%^&*()_+-=}{[]:;\"'|\\<>?/., "

        for index, char in enumerate(name):
            if char in unallowed:
                self.err(f"Syntax Error: Name has illegal characters: {name}, Index: {index}/{char}")

        if name[0].isdigit():
            self.err(f"Syntax Error: Name starts with a number: {name}")

    def ostream(self, msg):
        print(f"{FBLUE}{self.name}{FRESET}{msg}")

    def strip_signleline_comment(self, line: str) -> str:
        markers = ["//", "#", ";"]
        for marker in markers:
            if marker in line:
                line = line.split(marker, 1)[0]
        return line.strip()
    
    def strip_multiline_comment(self, line:str) -> str:
        result = ""
        i = 0
        n = len(line)
        while i < n:
            if self.in_ml_comment:
                end = line.find("*/", i)
                if end == -1:
                    return ""
                else:
                    self.in_ml_comment = False
                    i = end + 2
                    continue

            start = line.find("/*", i)
            if start == -1:
                result += line[i:]
                break
            else:
                result += line[i:start]

                end = line.find("*/", start + 2)
                if end == -1:
                    self.in_ml_comment = True
                    break
                else:
                    i = end + 2
                    continue

        return result.strip()

    def strip_comments(self, line:str) -> str:
        line = self.strip_multiline_comment(line)
        line = self.strip_signleline_comment(line)
        return line
    
    def processStringBloat(self, string:str) -> str:
        string = string.strip()
        if string and string[-1] in "\"'":
            string = string[:-1]
        if string and string[0] in "\"'":
            string = string[1:]
        return string

    def err(self, msg):
        self.signed = False
        self.red(f"[ ERROR ] {self.name}: {msg}")
    
    def red(self, msg):
        print(f"{colorama.Fore.RED}{msg}{colorama.Fore.RESET}")

    def _parse(self):
        if not self.signed:
            self.red("Makefile locked: Signed: False")

        if not isinstance(self.code, list):
            self.code = self.code.splitlines()
        while self.pos < len(self.code):
            line = self.strip_comments(self.code[self.pos])
            self.dprint(f"Parser position: Index: {self.pos}, Context: {self.code[self.pos]}")

            if not line:
                self.pos += 1
                continue
            
            jsInclude = jsonMatch.match(line)
            funcCall = functionCall.match(line)
            functionMatch = functionStart.match(line)
            if jsInclude:
                self.processJsonInclude(jsInclude.group(1), jsInclude.group(2))
                self.pos += 1
                self.dprint(f"Regex Matched: jsInclude")
                continue
            elif funcCall:
                self.process(funcCall.group(1).strip())
                self.pos += 1
                self.dprint(f"Regex Matched: funcCall")
                continue
            elif functionMatch:
                self.processFunction(functionMatch.group(1))
                continue
            self.pos += 1
            
    def process(self, functionName):
        functionName = functionName.strip().replace("\ufeff", "")
        if functionName == "jsonStart":
            self.processStartJson()
        elif functionName in self.func:
            self.processFunctionCall(functionName)

    def processFunction(self, functionname):
        self.checkIllegalName(functionname)
        content = []
        self.pos += 1
        while self.pos < len(self.code):
            line = self.code[self.pos]
            if functionEnd.match(line):
                self.pos += 1
                break
            content.append(line)
            self.pos += 1
        self.func[functionname] = "\n".join(content)
        self.dprint(f"function define: \n{self.func[functionname]}")

    def processFunctionCall(self, functionName):
        lines = self.func[functionName].strip().splitlines()
        if functionName in ("--verbose", "--debug"):
            self.debug = True
        self.dprint(f"Function call: \n{lines}")
        self.dprint(f"")
        self.funcPos = 0
        while self.funcPos < len(lines):
            line = lines[self.funcPos]
            if not line:
                self.funcPos += 1
                continue
            try:
                result = subprocess.run(line, capture_output=True, text=True, shell=True)
                if result.stdout:
                    print(f"[ SUBPROCESS ] IO: STDOUT:\n{result.stdout}")
                if result.stderr:
                    print(f"[ SUBPROCESS ] IO: STDERR:\n{result.stderr}")
            except Exception as e:
                print(f"Error running line: {line}\n{e}")
            finally:
                self.funcPos += 1
        self.funcPos = 0

    def processStartJson(self):
        self.ostream(f"Json Make full map: {self.jsonmake}")
        self.ostream(f"Json build process started")
        for k, v in self.jsonmake.items():
            self.ostream(f"Json build: {k}")
            newbuild = avk.make.buildSystem(v['build-dir'], self.working)
            self.ostream(f"Json Build Map: {v['json']}")
            self.ostream(f"Json Ignores: {v['json'].get('ignore', []).get("dirs", [])}")
            self.ostream(f"Json Build Dir: {v['build-dir']}")
            newbuild.build(v['json'])

    def processJsonInclude(self, filename, builddir):
        filename = os.path.join(self.working, self.processStringBloat(filename))
        builddir = os.path.join(self.working, self.processStringBloat(builddir))
        if not self._fs.isExistAndFile(filename):
            self._globerr.err(f"Json build doesn't exist: {filename}")
            sys.exit(1)
        
        if not self._fs.isExistAndDir(builddir):
            self._globerr.err(f"Json build dir doesn't exist: {builddir}")
            sys.exit(1)
        
        with open(filename, "r") as f:
            content = f.read()
            jsondat = json.loads(content)
        
        self.jsonmake[filename] = {
            "build-dir": builddir,
            "json": jsondat
        }
    
