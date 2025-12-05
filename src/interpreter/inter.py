import re, sys, shlex, ast, threading
from compiler.util.guid import *
from interpreter.AGT import AvalonTkinter

functionCallRegex = re.compile(r"([^(]+)\(([^)]*)\)")
variableRegex = re.compile(r"%(\w+)\s*=\s*(.+)")
ifstatementRegex = re.compile(r'@if\s*\((.*)\)')

class Interpreter:
    def __init__(self, code:str, flags:list=["--debug", "--dbg,val"], sourcefile:str=""):
        self.acronym = "AGI"
        self.ident = GUIDgen()
        self.srcfile = sourcefile
        self.cf = flags
        self.code = code
        self.dbg = False
        self.variables = {
            "True": "1",
            "False": "0",
            "CURRENT_FILE": str(self.srcfile),
            "AGC_FLAGS": ", ".join(self.cf).strip(","),
            "AGC_BUILD_MODE": "Normal",
            "AGC_VERSION": "v0.2",
            "AGI_VERSION": "v0.2"
        }
        self.pos = 0
        self.preflix = "Avalon Genesis Interpreter: "
        self.debuggingMapping = {
            1: "built-in",
            2: "user-defined",
            3: "unknown",
            4: "compiler-only"
        }
        self.virtualpos = 0
        self.tkinterInstance = AvalonTkinter(self.dbg, True)

    def dprint(self, msg):
        print(f"{self.preflix}{msg}")

    def parseArgs(self):
        for each in self.cf:
            if each == "--debug":
                self.dbg = True
                self.variables["AGC_BUILD_MODE"] = "DEBUG"

    def strip_comments(self, line: str) -> str:
        if self.dbg:
            self.dprint(f"strip_comments {self.debuggingMapping[4]} function used: Line: {line}")
        markers = ["//", "#", ";"]
        for marker in markers:
            if marker in line:
                line = line.split(marker, 1)[0]
        return line.strip()

    def parse(self):
        if self.dbg:
            self.dprint(f"Avalon Genesis Interpreter Parser has started parsing: id: {self.ident}")
        self.code = self.code.splitlines()
        while self.pos < len(self.code):
            if self.dbg:
                self.dprint(f"Interpreter Parser Position: Index: {self.pos}, Context: {self.code[self.pos]}")
            line = self.strip_comments(self.code[self.pos])
            if ifstatementRegex.match(line):
                self.processIfStatement()
            elif functionCallRegex.match(line):
                self.processFunctionName()
            elif variableRegex.match(line):
                self.processVariable()
            self.pos += 1

    def countIfSkip(self):
        index = 0
        self.virtualpos = self.pos
        line = self.strip_comments(self.code[self.virtualpos])
        while line.lower() != "@endif" and self.virtualpos < len(self.code):
            index += 1
            self.virtualpos += 1
            if self.virtualpos > len(self.code):
                break
            line = self.strip_comments(self.code[self.virtualpos])
        return index
    
    def runIfStatement(self):
        while self.pos < len(self.code):
            line = self.strip_comments(self.code[self.pos])
            if self.dbg:
                self.dprint(f"Interpreter Parser Position: Index: {self.pos}, Context: {self.code[self.pos]}")
            if line.lower() == "@endif":
                break
            if functionCallRegex.match(line):
                self.processFunctionName()
            elif variableRegex.match(line):
                self.processVariable()
            self.pos += 1

    def processIfStatement(self):
        line = self.strip_comments(self.code[self.pos])

        count = self.countIfSkip()
        ifs = ifstatementRegex.match(line)
        splitn = self.processParentheseBloat(ifs.group(1)).split()

        con1 = splitn[0]
        op = splitn[1]
        con2 = splitn[2]
        if self.dbg:
            self.dprint(f"If statement: con1: {con1}, con2: {con2}, op: {op}")
        if con1 in self.variables:
            con1 = self.variables[con1]
        if con2 in self.variables:
            con2 = self.variables[con2]

        invalid = False
        if op == "==":
            if con1 == con2:
                self.runIfStatement()
            else:
                self.pos += count
                invalid = True
        elif op == "!=":
            if con1 != con2:
                self.runIfStatement()
            else:
                self.pos += count 
                invalid = True
        else:
            self.pos += count

        if self.dbg:
            if invalid:
                self.dprint(f"If statement: con1: {con1}, con2: {con2}, op: {op} is invalid")
            else:
                self.dprint(f"If statement: con1: {con1}, con2: {con2}, op: {op} is valid")

    def processVariable(self):
        line = self.strip_comments(self.code[self.pos])
        var = variableRegex.match(line)
        name = var.group(1)
        value = var.group(2)
        self.variables[name] = value

    def split_arg(self, string):
        pattern = r'''((?:[^,"'()\[\]]+|"[^"]*"|'[^']*'|\([^\(\)]*\)|\[[^\[\]]*\])+)'''
        return [a.strip() for a in re.findall(pattern, string.strip(), re.VERBOSE)]

    def processFunctionName(self):
        line = self.strip_comments(self.code[self.pos])
        c = functionCallRegex.match(line)
        funcn = c.group(1)
        funcp = tuple(self.variables.get(a, self.processStringBloat(a)) for a in self.split_arg(c.group(2)))
        if self.dbg:
            self.dprint(f"Function: Name: {funcn} Args: {funcp}")

        if funcn == "printf":
            self.processPrintf(funcp)
        elif funcn == "tk.window.initializeWindow":
            self._tkinter_process_initializeWindow(funcp)
        elif funcn == "tk.window.startWindow":
            self._tkinter_process_StartWindow()
        elif funcn == "tk.widget.AddWidgetButton":
            self._tkinter_process_addWidgetButton(funcp)
        elif funcn == "tk.widget.SetButtonStateEnable":
            self._tkinter_process_setButtonState(funcp)

    def _tkinter_process_setButtonState(self, args):
        self.tkinterInstance.setButtonStateEnable(self.processStringBloat(args[0]))

    def _tkinter_process_addWidgetButton(self, args):
        name = self.processStringBloat(args[0])
        text = self.processStringBloat(args[1])

        pos = (0, 0)
        if len(args) >= 3:
            pos = self.processStringBloat(args[2])

            if "," in pos:
                try:
                    pos = tuple(int(x.strip()) for x in pos.strip("[]").split(","))
                except ValueError:
                    pos = (0, 0) 
            else:
                pos = (0, 0)

        size = (100, 30)
        if len(args) >= 4:
            size = self.processStringBloat(args[3])
            if "," in size:
                try:
                    size = tuple(int(x.strip()) for x in size.strip("[]").split(","))
                except ValueError:
                    size = (100, 30) 
            else:
                size = (100, 30)

        self.tkinterInstance.addButtonWidget(name, text, pos, size)

    def _tkinter_process_initializeWindow(self, args):
        windowName = self.processStringBloat(args[0])
        windowSizeRaw = self.processStringBloat(args[1])
        
        if "," in windowSizeRaw:
            try:
                windowSize = tuple(int(x.strip()) for x in windowSizeRaw.strip("[]").split(","))
            except ValueError:
                windowSize = (300, 200) 
        else:
            windowSize = (300, 200)

        self.tkinterInstance.initialize(windowName, windowSize)

    
    def _tkinter_process_StartWindow(self):

        def _instance():
            self.tkinterInstance.run()

        newThread = threading.Thread(target=_instance)
        newThread.start()
        self.dprint(f"New Interpreter Thread: ID: {GUIDgen()}, Library: Tkinter")

    def antibloat(self, s: str, c1: str, c2: str) -> str:
        if not s:
            return s
        if s[-1] in (c1, c2):
            s = s[:-1]

        if s and s[0] in (c1, c2):
            s = s[1:]
            
        if self.dbg:
            self.dprint(f"processStringBloat {self.debuggingMapping[4]} Function: String: {s}")
        return s

    def processStringBloat(self, string):
        a = self.antibloat(string, "'", '"')
        return a
    
    def processParentheseBloat(self, string):
        a = self.antibloat(string, "(", ")")
        return a
    
    def processPrintf(self, params):
        for each in params:
            each = self.processStringBloat(each).replace("\\n", "\x0A")
            sys.stdout.write(each)
            sys.stdout.flush()