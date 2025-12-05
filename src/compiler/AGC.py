import re, os, platform, datetime, sys, colorama, subprocess

import egg.string as string
import egg.fs as fs
import egg.listery as lst

from AAst.main import *
from compiler.util import guid
from interpreter.inter import *
from pathlib import Path

stringVariableNameIndex = 0
floatVarNameI = 0
fileNameIndex = 0
time_index    = 0
ifstament_index = 0
runtimeContinue = 0
passedIf = False
root = Path(__file__).parent

_fs = fs.filesystem()
nasmAssembler = _fs.recursiveFind(reserve=4, fileName="nasm.exe")

class Compiler:
    def __init__(self, ast_nodes:list=[], output="output.asm", sourceFileName="Unknown", OptimizationLevel:int=0, document:str="", args:list=["--fx86_64-linux","--debug", "--dbg,val"], signed=True, infunction=False):
        self.funcin = infunction
        self.name = "Avalon Genesis Compiler"
        self.signed = signed
        self.srcfile = sourceFileName
        self.srcDoc = document
        self.argvs = args
        self.debugPreflix = f"[ DEBUG ] {self.name}: Debug: "

        self.x86_64_linux = False
        self.useWSLLD = False
        self.clo = False
        self.cloa = False

        self.debuggingMapping = {
            1: "built-in",
            2: "user-defined",
            3: "unknown",
            4: "compiler-only"
        }
        self.functionMapping = {
            1: "Sub-Function",
            2: "Boostrap-Function",
            3: "Lambda-Function"
        }
        self.variables = {
            "True": {
                "Type": "int",
                "value": "1"
            },
            "False": {
                "Type": "int",
                "value": "0"
            }
        }
        self.onetimeVar = {}
        self.func = {}
        self.structs = {}
        self.nonfunc = {}
        self.excludedFunctions = {}
        self.operatorMapping = {
            # --- Integer arithmetic ---
            "+":   {"int": "add",   "float": "addsd"},   # +  (scalar double add)
            "-":   {"int": "sub",   "float": "subsd"},   # -  (scalar double sub)
            "*":   {"int": "imul",  "float": "mulsd"},   # *  (scalar double mul)
            "/":   {"int": "idiv",  "float": "divsd"},   # /  (scalar double div)
            "%":   {"int": "mod",   "float": ""},        # %  (mod not valid for float)
            
            # --- Compound assignments ---
            "+=":  {"int": "add",   "float": "addsd"},
            "-=":  {"int": "sub",   "float": "subsd"},
            "*=":  {"int": "imul",  "float": "mulsd"},
            "/=":  {"int": "idiv",  "float": "divsd"},
            "%=":  {"int": "mod",   "float": ""}
        }
        self.agcf = Path(os.path.abspath(output))
        self.agcData = {
            "AGC Version": "v0.2",
            "AGC Optimization Level": f"O{OptimizationLevel}",
            "AGC Python Runtime Version": f"{sys.version}",
            "AGC Syntax Version": "AGLang/AG v0.2",
            "AGC Path": __file__
        }
        self.nodes = ast_nodes
        self.outputFiles = output
        self.index = 0

        self.host_info = {
            "OS Name": os.name,
            "System": platform.system(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Architecture": platform.machine(),
        }

        self.metaData = self.generate_banner()
        self.x86_64_asmMacroSection = """"""
        self.x86_64_asmstructSection = """"""
        self.x86_64_asmRODSection = """"""
        self.x86_64_asmDataSection = """
section .data
"""
        self.x86_64_asmFunctionSection = """
section .text
global _start
"""
        self.x86_64_asmInstructionMain = """
_start:
    ; jmp main
    jmp main

main:

"""
        self.x86_64_asmErrorChunk = """
    jmp _exit_success ; jump to exit        
        
_exit_success:
    sys_exit 0

_exit_error_code_1:
    sys_exit 1

_exit_error_code_2:
    sys_exit 2

_exit_error_code_126:
    sys_exit 126

_exit_error_code_127:
    sys_exit 127

_exit_fatal_code_130:
    sys_exit 130

_exit_fatal_code_137:
    sys_exit 137

_exit_fatal_code_143:
    sys_exit 143

meta_data:
.null_block db 0 ; prevent empty label
"""

        self.errors = {
            0: "", 1: "Unknown Node", 2: "Unknown Function", 3: "Not Enough Arguements", 4: "Way Too Much Arguements"
        }

        self.linuxChunk = ""

    def startSetup(self):
        with open(os.path.join(root, "x86_64-linux.abi"), "r") as f:
            x86_64_linuxm = f.read()
        self.x86_64_asmMacroSection = x86_64_linuxm

    def checkName(self):
        if self.funcin:
            self.name = "Avalon Genesis In-Function Compiler"
        else:
            self.name = "Avalon Genesis Compiler"

    def generate_banner(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info = "\n".join(
            f"; Host's OS {k:<13}: {v}" for k, v in self.host_info.items()
        )
        agcInfo = "\n".join(
            f"; {k:<13}: {v}" for k, v in self.agcData.items()
        )
        art = """
;                    ##                    
;       **           ##                 ###     
;      *++*          ##                ####     
;   **+=--=+**      ###             ######      
;  *++-:..:-=+*     # ##           ####         
;   **+=--=+**      # ##          ####
;      *++*         # ###        ####      
;       **        ### ###     #######      
;                 ### ###  ######          
;                 ### ##########     *     
;                ##########        *++*    
;              ############       *+=-+**  
;          ##########   ####   **+-::.:-=+*
;      ############      ###     *+=-:-++* 
; ########## #####       ####     *++=+**  
;           ####          ####      **     
;       #######            #####           
;       #####                ####          
;     #####                   ####         
;  #######                     ###         
; #####                          #####     
; ###                             ####
; AGC Creator: RandomX""" + f"" + """
; AGC Used In """ + self.detect_env() + "'s Environment" + f"""
{agcInfo}
; Transpiled by AGC
; Transpiled Source File: Unknown
; Transpiled Output File: test.asm
; Transpiled ID: """ + guid.GUIDgen() + """
; Transpiled Time: """ + now + "\n" + info + "\n; x86_64 ASM/NASM Codes\n\n" + """

section .note.AGC
    db "AGC v0.2 generated code", 0
"""
        return art
    
    def parseArgs(self):
        global debug, valdbg
        for each in self.argvs:
            if each == "--debug":
                debug = True
            elif each == "--dbg,val":
                valdbg = True
            elif each == "--fx86_64-linux":
                self.x86_64_linux = True
            elif each == "--wslld":
                self.useWSLLD = True
            elif each == "--clo": # clear object output
                self.clo = True
            elif each == "--cloa": # clear asm output
                self.cloa = True

    def advance(self):
        self.index += 1

    def err(self, string, type=0):
        self.signed = False
        try:
            print(f"{colorama.Fore.RED}[ ERROR ]  {self.name}: {self.errors[type] + ":" if len(self.errors[type]) >= 1 else ""} {string} at: Index: {self.index}, Class: {self.nodes[self.index]}{colorama.Fore.RESET}", end="\r")
        except IndexError:
            print(f"{colorama.Fore.RED}[ ERROR ]  {self.name}: {self.errors[type] + ":" if len(self.errors[type]) >= 1 else ""} {string} at: Index: {self.index}{colorama.Fore.RESET}", end="\r")

    def err2(self, string):
        self.signed = False
        print(f"{colorama.Fore.RED}[ FATAL ]: [ EXTERNAL ]: {string}", end="\r")

    def sucess(self, string):
        print(f"{colorama.Fore.LIGHTWHITE_EX}{colorama.Back.GREEN}[ SUCCESS ]{colorama.Back.RESET}{colorama.Fore.RESET} {string}")

    def detect_env(self):
        if "WSL_DISTRO_NAME" in os.environ:
            return "WSL"
        elif "MSYSTEM" in os.environ:
            return f"MSYS2 ({os.environ['MSYSTEM']})"
        elif platform.system() == "Linux":
            return "Linux Native"
        elif platform.system() == "Windows":
            return "Windows Native"
        else:
            return "Unknown"
        
    def dprint(self, string:str):
        print(f"{self.debugPreflix}{string}")

    def phaseChunk(self, chunk, addToMain=True, addToFunc=False, keepEndLabel=True, internalfunction=False, limit=-1):
        """
        Main second-phase parser that translates AST nodes into NASM ASM text.
        """
        amain = addToMain
        afunc = addToFunc
        limitCount = 0

        if debug:
            self.dprint(f"Nodes: {chunk}")
        self.parseArgs()
        if internalfunction:
            self.funcin = True
        self.checkName()
        if not self.signed:
            print(f"{colorama.Fore.RED}[FATAL]  {self.name} Locked: Signed: False{colorama.Fore.RESET}")
            print(f"{colorama.Fore.RED}[FATAL]  {self.name} cannot run because of an error report from parser or direct report from compiler{colorama.Fore.RESET}")
            return
        
        outer_index = self.index
        outer_current_chunk = getattr(self, '_current_chunk', None)
        using_own_index = (chunk is not self.nodes)
        if using_own_index:
            self._current_chunk = chunk
            self.index = 0

        while self.index < len(chunk) and self.signed:
            node = chunk[self.index]
            if not limit == -1:
                if limitCount >= limit:
                    amain = True
                    afunc = False
            if debug:
                self.dprint(f"ASM Main chunk: \n==============================\n{self.x86_64_asmInstructionMain}\n==============================\n")
                self.dprint(f"ASM Function chunk: \n==============================\n{self.x86_64_asmFunctionSection}\n==============================\n")

            if isinstance(node, UnknownAstNode):
                node.alert()
                self.err(f"node: {node}", 1)
                break

            elif isinstance(node, NormalFunction):
                self.processFunctionDeclare(node)
                if debug:
                    self.dprint(f"Normal Function Declare: Name: \'{node.name}\', Value: \'{node.value}\' Params: {node.param}")
                if valdbg:
                    self.dprint(f"Normal Function Declare: Name: \'{node.value}\', Code: \n{node.realcode}")

            elif isinstance(node, ArbitraryHeader):
                node.emit()

            elif isinstance(node, SegmentedFile):
                segment_compiler = Compiler(node.ast_nodes)
                segment_compiler.phase2Parse()

                self.x86_64_asmDataSection += segment_compiler.asmDataSection
                self.x86_64_asmInstructionMain += segment_compiler.asmInstructionMain

            elif isinstance(node, FunctionCall):
                self.proccess(node, amain, afunc)
            
            elif isinstance(node, VarArray):
                self.processArray(node)

            elif isinstance(node, Var):
                self.proccess(node, amain, afunc)

            elif isinstance(node, Operator):
                self.processOperator(node)

            elif isinstance(node, StructDef):
                self.processStruct(node)

            elif isinstance(node, Ifstament):
                self.processIf(node, addToMain, addToFunc, keepEndLabel)

            elif isinstance(node, LabelAdd):
                self.processLabel(node)

            elif isinstance(node, ExcludedFunction):
                self.processExcludedFunction(node)

            elif isinstance(node, NonFunction):
                self.processNonFunction(node)

            elif isinstance(node, Chain):
                self.chainer(node)
                continue
            limitCount += 1

            if debug and self.signed:
                self.dprint(f"Phase 2 Parser position tracking: {self.index}")
            self.advance()
            if debug and self.signed:
                self.dprint(f"Phase 2 Parser position advanced")
            
            if valdbg and self.signed:
                self.dprint(f"Current user-defined function: {self.func}")

        if using_own_index:
            self._current_chunk = outer_current_chunk
            self.index = outer_index

        self.funcin = False
        self.checkName()

    def phase2Parse(self):
        self.startSetup()
        self.phaseChunk(self.nodes)

    def processExcludedFunction(self, node:ExcludedFunction):
        self.excludedFunctions[node.value] = {
            "code": node.code,
            "param": node.param
        }
    
    def processFunctionDeclare(self, obj: NormalFunction):
        self.x86_64_asmFunctionSection += f"""
{obj.name}""" + ":\n"
        if debug:
            self.dprint(f"Function Declaration: Name: \'{obj.name}\'(From processFunctionDeclare)")
        self.func[obj.name] = {"param": obj.param}
        self.phaseChunk(obj.code, False, True, False, len(obj.code))
        self.x86_64_asmFunctionSection += "    ret\n"

    def chainer(self, chain):
        """
        Flatten a Chain node into regular AST nodes (e.g. FunctionCalls)
        and insert them into the current node list.
        """
        func_call_regex = re.compile(r'^(\w+)\s*\(([^()]*)\)$')
        new_nodes = []

        for child in chain.children:
            # Convert statements into function calls if possible
            if getattr(child, "node_type", None) == "Statement":
                match = func_call_regex.match(child.value)
                if match:
                    func_name = match.group(1)
                    params = [p.strip() for p in match.group(2).split(",")] if match.group(2) else []
                    new_nodes.append(FunctionCall(param=params, name=func_name))
                else:
                    new_nodes.append(child)
            else:
                new_nodes.append(child)
        chunk_ref = getattr(self, '_current_chunk', self.nodes)
        chunk_ref[self.index:self.index + 1] = new_nodes

    def proccess(self, obj, addtomain, addToFunc):
        """
        Handle known function calls (e.g., printf)
        """
        if isinstance(obj, FunctionCall):
            oldParams = list(getattr(obj, "param"))
            if debug:
                self.dprint(f"FunctionCall: Name: \'{obj.name}\', OldParams: {oldParams}")
            varscope = False
            for each in obj.param:
                if self.processString(each)["varref"]:
                    if debug:
                        self.dprint(f"FunctionCall Param: \'{obj.param.index(each)}\' Replaced with: \'{self.variables[each]["value"]}\'")
                    varscope = self.processString(each)["varref"]
                    obj.param[obj.param.index(each)] = self.variables[each]["value"]
            if debug:
                self.dprint(f"[ CHECK ] FunctionCall: Name: \'{obj.name}\', OldParams: {oldParams}")

            if obj.name == "printf":
                self.proccessPrintf(obj.param[0], addtomain, addToFunc, varscope, oldParams[0])
            elif obj.name == "input":
                self.proccessInput(obj.param[0], addtomain, addToFunc)
            elif obj.name == "clearInputBuffer":
                self.proccessClearBuffer(obj.param[0], addtomain, addToFunc)
            elif obj.name == "create_file":
                self.proccessCreateFile(obj.param[0], addtomain, addToFunc)
            elif obj.name == "wait":
                self.proccessWait(obj.param[0], addtomain, addToFunc)
            elif obj.name == "asmm":
                self.processASMM(obj.param)
            elif obj.name == "asmd":
                self.processASMD(obj.param)
            elif obj.name == "asmmi":
                self.processASMMI(obj.param)
            elif obj.name == "asmdi":
                self.processASMDI(obj.param)
            elif obj.name == "agcp":
                self.processAGCP(obj.param)
            elif obj.name == "agcpd":
                self.processAGCPD()
            elif obj.name in self.excludedFunctions:
                self.processEXFUNCCall(obj.name, obj.param)
            elif obj.name in self.func:
                self.x86_64_asmInstructionMain += f"{" " * 4}call {obj.name}\n"
                if debug:
                    self.dprint(f"User function call: call {obj.name}")
            elif obj.name in self.nonfunc:
                self.processNONFUNCCALL(obj.name, obj.param)
            else:
                self.err(f"Unrecognised Function: Name: {obj.name}, Param: {obj.param}", 2)

        elif isinstance(obj, Var):
            self.processVar(obj.name, obj.value)
        elif isinstance(obj, Operator):
            self.processOperator(obj, addtomain, addToFunc)
        elif isinstance(obj, StructDef):
            self.processStruct(obj)
        
    def processNONFUNCCALL(self, name, params):
        fget = self.nonfunc[name]
        fparam = fget["param"]
        fnode = fget["node"]

        if len(params) > len(fparam):
            self.err(f"Function: Name: {name}", 4)
            return
        if len(params) < len(fparam):
            self.err(f"Function: Name: {name}", 3)
            return

        self.phaseChunk(fnode, True, False, True)

    def processEXFUNCCall(self, name, param):
        code = self.excludedFunctions[name]["code"]
        paramf = self.excludedFunctions[name]["param"]
        code = "\n".join(code)
        s = Interpreter(code, self.argvs, self.srcfile)
        for n in range(len(paramf)):
            s.variables[paramf[n]] = param[n]
        s.parseArgs()
        s.parse()
        if debug:
            self.dprint(f"EXFUNC Call: Name: {name}, Params: {" ".join(param) if len(param) >= 1 else "(Empty)"}")

    def processNonFunction(self, obj:NonFunction):
        name = obj.name
        param = obj.params
        nodes = obj.nodes
        self.nonfunc[name] = {
            "param": param,
            "node": nodes
        }

    def processAGCP(self, param):
        string = self.processStringBloat(param[0])
        preflix = param[1]
        if debug:
            if preflix == 1:
                print(f"Avalon Genesis Source File \'{self.srcfile}\' Message Preflix Enabled")
            else:
                print(f"Avalon Genesis Source File \'{self.srcfile}\' Message Preflix Disabled")

        if preflix:
            self.dprint(f"Avalon Genesis Source File \'{self.srcfile}\' Message: {string}")
        else:
            print(f"Avalon Genesis Source File \'{self.srcfile}\' Message: {string}")
        
    def processDAGCP(self, param):
        if debug:
            for i in range(len(param)):
                string = self.processStringBloat(param[i])
                self.dprint(f"Avalon Genesis Source File \'{self.srcfile}\' Message: {string}")

    def processDVAGCP(self, param):
        if valdbg:
            for i in range(len(param)):
                string = self.processStringBloat(param[i])
                self.dprint(f"Avalon Genesis Source File \'{self.srcfile}\' Message: {string}")

    def processAGCPD(self):
        print(f"""
Avalon Genesis Source File: \'{self.srcfile}\' document:
{self.srcDoc}
""")

    def processASMM(self, asm):
        self.processASM(asm=asm, func="ASMM", main=True, data=False, oneline=False)

    def processASMD(self, asm):
        self.processASM(asm=asm, func="ASMD", main=False, data=True, oneline=False)

    def processASMMI(self, asm):
        self.processASM(asm=asm, func="ASMMI", main=True, data=False, oneline=True)

    def processASMDI(self, asm):
        self.processASM(asm=asm, func="ASMDI", main=False, data=True, oneline=True)    

    def processASM(self, asm, func, main: bool=True, data: bool=True, oneline: bool=False):
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function {func} used: ASM:")

        if oneline:
            for i in asm:
                chuck = i.strip("\"'").replace("\n", "")
                if main:
                    self.x86_64_asmInstructionMain += chuck
                if data:
                    self.x86_64_asmDataSection += chuck 
                if debug:
                    print(chuck.rstrip("\n"))
        else:
            for i in asm:
                chuck = i.strip("\"'") + f"   ; {func}\n"
                if main:
                    self.x86_64_asmInstructionMain += chuck
                if data:
                    self.x86_64_asmDataSection += chuck
                if debug:
                    print(chuck.rstrip("\n"))

    def processLabel(self, obj:LabelAdd):
        global runtimeContinue
        if obj.ltype == "rtr":
            self.x86_64_asmInstructionMain += f"runtimeReturn_{runtimeContinue}:\n"
            runtimeContinue += 1


    def processIf(self, obj: Ifstament, addtomain, addtofunc, keepEndLabel=True):
        global ifstament_index, runtimeContinue, passedIf

        condition = (obj.state or [])
        if not condition:
            raise ValueError("Empty if condition")

        comparisonRegex = re.compile(
            r'(!==|===|!=<|!>=|!<=|u>=|u<=|u>|u<|==0|!=0|0!=|0=|==|!=|>=|<=|>==|>|<|!>|!<|true|false)'
        )
        condition = lst.clear_empty_gap(condition)
        
        mappingTable = {
            "==": "je", "!=": "jne", "===": "je", "!==": "jne",
            "0=": "jz", "0!=": "jnz", "==0": "jz", "!=0": "jnz",
            ">": "jg", "<": "jl", ">=": "jge", "<=": "jle",
            "u>": "ja", "u<": "jb", "u>=": "jae", "u<=": "jbe",
            "!>": "jnle", "!<": "jnge", "!>=": "jnge", "!<=": "jnle",
            ">==": "jge", "!=<": "jnle", "!===": "jne",
            "true": "jmp", "false": "nop",
        }
        
        true_label = f"if_true_{ifstament_index}"
        end_label  = f"if_end_{ifstament_index}"
        asm = ""
        
        for i, each in enumerate(condition):
            m = comparisonRegex.search(each)
            if not m:
                raise ValueError(f"No valid operator found in if-statement: {condition}")
            op = m.group(0)

            lhs, rhs = each.split(op, 1)
            lhs = lhs.strip()
            rhs = rhs.strip()

            jump_op = mappingTable.get(op)
            if jump_op is None:
                raise ValueError(f"Unknown operator in if-statement: {op}")

            if op == "true":
                pass
            elif op == "false":
                asm += f"    jmp {end_label}\n"
            else:
                asm += f"    mov rax, {lhs}\n"
                asm += f"    cmp rax, {rhs}\n"
                asm += f"    j{self._invert_jump(jump_op)} {end_label}\n" 

        asm += f"{true_label}:\n"

        if addtomain:
            if self.x86_64_linux:
                self.x86_64_asmInstructionMain += asm
        if addtofunc:
            if self.x86_64_linux:
                self.x86_64_asmFunctionSection += asm
        
        self.phaseChunk(obj.value, addtomain, addtofunc, False)

        if keepEndLabel:
            if self.x86_64_linux:
                self.x86_64_asmInstructionMain += f"{end_label}:\n"

        ifstament_index += 1
        if debug:
            self.dprint(f"If statement processed: '{condition}' -> true_label={true_label}, end_label={end_label}")
        runtimeContinue += 1
        passedIf = True
    
    def _invert_jump(self, jump_op):
        """Convert a jump instruction to its inverse (e.g., je -> jne)"""
        invert_map = {
            "je": "ne", "jne": "e", "jz": "nz", "jnz": "z",
            "jg": "le", "jl": "ge", "jge": "l", "jle": "g",
            "ja": "be", "jb": "ae", "jae": "b", "jbe": "a",
            "jnle": "<", "jnge": ">", "jnle": "<=", "jnge": ">="
        }
        return invert_map.get(jump_op, jump_op)

    def isPureString(self, string):
        if not self.isString(string):
            return False

        if len(string) < 2:
            return False

        start = string[0]
        end = string[-1]

        if start == end and start in ("'", '"'):
            return True

        return False

    def processOp(self, name, value, op, reg="rax"):
        
        mov = "mov"
        sd = "int"
        if self.isFloat(value):
            mov = "movsd"
            sd = "float"

        instruction = f"""
     {mov} {reg}, [{name}] ; Store in reg

"""
        pipe = f" {reg}, {value}"
        instruction = self.operatorMapping[op][sd]
        full = " " + instruction + pipe + f"      ; Op: {op}, Name: {name}\n"
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}{self.functionMapping[1]} processOp: Name: {name}, Value: {value}, Op: {op}, Reg: {reg}")
        return full
    
    def split_arg(self, string):
        pattern = r'''((?:[^,"'()\[\]]+|"[^"]*"|'[^']*'|\([^\(\)]*\)|\[[^\[\]]*\])+)'''
        return [a.strip() for a in re.findall(pattern, string.strip(), re.VERBOSE)]

    def processOperator(self, obj:Operator, addtomain, addToFunc):
        
        full = ""
        name = obj.name
        oep = obj.value
        reg = "rax"
        mover = "mov"
        section = "section .rodata\n"
        if section not in self.x86_64_asmRODSection:
            self.x86_64_asmRODSection += section

        if self.variables[name]["Type"] == "int":
            reg = "eax"
        elif self.variables[name]["Type"] == "bool":
            reg = "al"
        elif self.variables[name]["Type"] == "float":
            reg = "xmm0"
            mover += "sd"

        full += f"""
    {mover} {reg}, [{name}] ; Load
"""

        pattern = re.compile(r'([+\-/*]?\s*\d+(?:\.\d+)?)')
        chunks = pattern.findall(oep)
        chunks = [c.replace(" ", "") for c in chunks]

        for each in chunks:
            if each[0] in "+-*/":
                op = each[0]
                val = each[1:]
            else:
                op = "+"
                val = each
            VVAR = f"float_constant_{floatVarNameI} dq {val}\n"
            if self.isFloat(val):   
                self.x86_64_asmRODSection += VVAR
                val = f"[float_constant_{floatVarNameI}]"
                floatVarNameI += 1
            full += "   " + self.processOp(name, val, op, reg)     

        if addtomain:
            self.x86_64_asmInstructionMain += "\n" + full + f"{" "*4}{mover} [{name}], {reg} ; Store back in {name}\n"
        if addToFunc:
            self.x86_64_asmFunctionSection += "\n" + full + f"{" "*4}{mover} [{name}], {reg} ; Store back in {name}\n"
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function processOperator: Param_1: {obj}")
        
    def processArray(self, obj: VarArray):
        
        define_type = obj.define
        for each in obj.value:
            if each in self.variables:
                obj.value[obj.value.index(each)] = self.variables[each]
        values = ", ".join(self.processString(item) if self.isString(item) else str(item) for item in obj.value)
        asm_line = f"{obj.name} {define_type} {values} ; List\n"
        self.x86_64_asmDataSection += asm_line
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function processArray: Param_1: {obj}")


    def isInteger(self, inputI: str):
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function isInteger: Param_1: {inputI}")
        try:
            int(inputI)
            return True
        except ValueError:
            return False

    def isFloat(self, inputF: str):
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function isFloat: Param_1: {inputF}")
        try:
            float(inputF)
            return not self.isInteger(inputF)
        except ValueError:
            return False
    
    def isString(self, s):
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function isString: Param_1: {s}")
        return (
            isinstance(s, str)
            and (
                (s.startswith('"') and s.endswith('"'))
                or
                (s.startswith("'") and s.endswith("'"))
            )
        )
    
    def isChar(self, inputC):
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function isChar: Param_1: {inputC}")
        if self.isString(inputC) and len(inputC) == 1:
            return True
        return False

    def isBool(self, inputB):
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function isBool: Param_1: {inputB}")
        if inputB.strip() in ["false", "true", "True", "False"]:
            return True
        return False

    def isArray(self, inputl):
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function isArray: Param_1: {inputl}")
        try:
            list(inputl)
            return True
        except ValueError:
            return False
    
    
    def processStruct(self, obj: StructDef):
        
        full = f"{obj.name}: ; Struct Start\n"
        offset = 0
        self.structs[obj.name] = {}
        
        for k, v in obj.fields.items():
            new_instance = string.StringTool(v)
            define = new_instance._asm_define_from_string()
            full += f"    {define} {v} ; {k} placeholder\n"
            self.structs[obj.name][k] = {"offset": offset, "value": v}
            
            match define:
                case "db": offset += 1
                case "dd": offset += 4
                case "dq": offset += 8
        self.x86_64_asmDataSection += full
        if debug:
            self.dprint(f"")

    def processString(self, inputString: str) -> str:
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function ProcessString: Param: {inputString}")
        inputString = inputString.strip('"').replace('"', '\\"')
        parts = inputString.split("\\n")
        
        db_parts = []
        for part in parts:
            if part:
                db_parts.append(f'"{part}"')
            db_parts.append('0x0A')
        if db_parts and db_parts[-1] == '0x0A':
            db_parts = db_parts[:-1]
        
        db_parts.append('0')
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function ProcessString: Output: {", ".join(db_parts)}, isVarRefernce: {inputString in self.variables}")
        return {
            "output": ", ".join(db_parts),
            "varref": inputString in self.variables
        }
    
    def processStringBloat(self, string:str) -> str:
        if debug:
            self.dprint(f"processStringBloat {self.debuggingMapping[4]} Function: String: {string}")
        if string[-1] == "\"" or string[-1] == "\'":
            string = string[0:-1]
        if string[0] == "\"" or string[0] == "\'":
            string = string[1:]
        return string

    def proccessCreateFile(self, filename, addtomain, addToFunc):
        if self.x86_64_linux:
            global stringVariableNameIndex, floatVarNameI, fileNameIndex, time_index
            filename = self.processString(filename)["output"]
            filedef = f"file_{fileNameIndex} db {filename}, 0 ; file\n"
            constants = """
    file_mode equ 0o644        ; Permissions: rw-r--r-- (octal)
    O_CREAT equ 0o100          ; Flag to create the file if it doesn't exist
    O_WRONLY equ 0o1           ; Flag to open the file for writing only\n
    """
            self.x86_64_asmDataSection += filedef
            if constants not in self.x86_64_asmDataSection:
                self.x86_64_asmDataSection += constants

            instruction = f"""
    sys_create_file file_{fileNameIndex}
    """
            if addtomain:
                self.x86_64_asmInstructionMain += instruction
            if addToFunc:
                self.x86_64_asmFunctionSection += instruction
            fileNameIndex += 1

    def proccessWait(self, time, addtomain, addToFunc):
        if self.x86_64_linux:
            global stringVariableNameIndex, floatVarNameI, fileNameIndex, time_index
            dataSection = f"""
time_section_{time_index}:
    tv_sec  dq {time}   ; Second
    tv_nsec dq 0        ; Nano second\n
    """
            instruction = f"""
    sys_ns_sleep time_section_{time_index}
    """
            self.x86_64_asmDataSection += dataSection
            if addtomain:
                self.x86_64_asmInstructionMain += instruction
            if addToFunc:
                self.x86_64_asmFunctionSection += instruction
            time_index += 1

    def proccessClearBuffer(self, count, addtomain, addToFunc):
        if self.x86_64_linux:
            clearFunction = """
    clearInputBuffer:
        test rsi, rsi
        jz .done
        xor rax, rax
        mov rcx, rsi
        rep stosb
    .done:
        ret
    """
            if clearFunction not in self.x86_64_asmFunctionSection:
                self.x86_64_asmFunctionSection += clearFunction

            if addtomain:
                self.x86_64_asmInstructionMain += f"""
    clear_input_buffer {count}
    """
            if addToFunc:
                self.x86_64_asmFunctionSection += f"""
    clear_input_buffer {count}
    """
            if debug:
                self.dprint(f"clearInputBuffer {self.debuggingMapping[1]} function used: Buffer: {count}")
    
    def proccessInput(self, string, addtomain, addToFunc):
        if self.x86_64_linux:
            global stringVariableNameIndex, floatVarNameI, fileNameIndex, time_index
            idx = stringVariableNameIndex
            safe_string = self.processString(string)["output"]

            defineString = f'string_{idx} db {safe_string} ; AGC Input Function String'
            defineStringLength = f"string_length_{idx} equ $-string_{idx}"
            defineBuffer = "buffer times 256 db 0 ; AGC default buffer" if "buffer times 256 db 0 ; AGC default buffer" not in self.x86_64_asmDataSection else ""

            PrintInstruction = f"""
    sys_write string_{idx}, string_length_{idx}
    """
            InputInstruction = f"""
    sys_read buffer\n
    """

            self.x86_64_asmDataSection += defineString + "\n" + defineStringLength + "\n" + defineBuffer + "\n"
            stringVariableNameIndex += 1

            if addtomain:
                self.x86_64_asmInstructionMain += PrintInstruction + "\n" + InputInstruction + "\n"
            if addToFunc:
                self.x86_64_asmFunctionSection += PrintInstruction + "\n" + InputInstruction + "\n"

            if debug:
                self.dprint(f"input {self.debuggingMapping[1]} function used: String: {defineString}, Len: {defineStringLength}")

    def proccessPrintf(self, string, addtomain, addToFunc, VarScope, rawValue):
        if self.x86_64_linux:
            global stringVariableNameIndex, floatVarNameI, fileNameIndex, time_index
            idx = stringVariableNameIndex
            safe_string = self.processString(string)["output"]
            targetstr = f"string_{idx}"
            lengthstr = f"string_length_{idx}"

            defineString = ""
            defineStringLength = ""

            if VarScope:
                targetstr = f"{self.variables[rawValue]["name"]}"
                lengthstr = f"{self.variables[rawValue]["name"]}_length"
                self.x86_64_asmDataSection += f"{lengthstr} db $-{self.variables[rawValue]["name"]}"
            else:
                defineString = f'string_{idx} db {safe_string} ; AGC String'
                defineStringLength = f"string_length_{idx} equ $-string_{idx}"
                self.x86_64_asmDataSection += defineString + "\n" + defineStringLength + "\n"
                stringVariableNameIndex += 1
                

            instruction = f"""
    sys_write {targetstr}, {lengthstr}
    """
                
            if addtomain:
                self.x86_64_asmInstructionMain += "\n" + instruction + "\n"
            if addToFunc:
                self.x86_64_asmFunctionSection += "\n" + instruction + "\n"
            
            if debug:
                self.dprint(f"printf {self.debuggingMapping[1]} function used: Len: {defineStringLength}, Str: {defineString}")
                self.dprint(f"proccessPrintf function: String: {string}")

    def processVar(self, name, value):
        
        self.variables[name] = {
            "val": value,
            "value": value,
            "name": name
        }
        if self.isInteger(str(value)):
            self.x86_64_asmDataSection += f"{name} dd {value} ; Integer\n"
            self.variables[name]["Type"] = "int"

        elif self.isBool(value):
            bool_val = str(value).lower()
            bool_val = '1' if bool_val == 'true' else '0'
            self.x86_64_asmDataSection += f"{name} db {bool_val} ; Bool\n"
            self.variables[name]["Type"] = "bool"

        elif self.isFloat(str(value)):
            self.x86_64_asmDataSection += f"{name} dq _float64_({value}) ; Float\n"
            self.variables[name]["Type"] = "float"

        elif self.isString(value):
            processed_str = self.processString(value)["output"]
            self.x86_64_asmDataSection += f"{name} db {processed_str} ; String\n"
            self.variables[name]["Type"] = "string"

        else:
            self.x86_64_asmDataSection += f"; UnknownVariableTypeException: {name} type is undefined\n"
            self.variables[name]["Type"] = "die"
        if debug:
            self.dprint(f"Variable: {name} Type: {self.variables[name]["Type"]}, Value: {self.variables[name]["value"]}")
            self.dprint(f"Current Variable Diction: {self.variables}")

    def resolvePlatforms(self):
        xx86_64_linux = (
                    self.metaData + "\n" +
                    self.x86_64_asmRODSection + "\n" +
                    self.x86_64_asmDataSection + "\n" +
                    self.x86_64_asmstructSection + "\n" +
                    self.x86_64_asmMacroSection + "\n" +
                    self.x86_64_asmFunctionSection + "\n" +
                    self.x86_64_asmInstructionMain + "\n" +
                    self.x86_64_asmErrorChunk + "\n" +
                    '.ident db "Built by AGC compiler v0.1"\n'
                )
        if self.x86_64_linux:
            self.linuxChunk = xx86_64_linux + ".platform db \"x86_64-linux\" "
            
    def writeOutput(self):
        self.resolvePlatforms()
        if self.signed:
            if self.x86_64_linux:
                output = f"{Path(self.outputFiles).stem}-x86_64-linux.asm"
                with open(output, "w") as f:
                    f.write(self.linuxChunk)

                print(f"[+] x86_64-Linux ASM output written to {output}")
        else:
            print(f"{colorama.Fore.RED}[FATAL]  {self.name} Output Assembly Locked: Signed: False{colorama.Fore.RESET}")
            print(f"{colorama.Fore.RED}[REPEAT] {self.name} cannot run because of an error report from parser or direct report from compiler{colorama.Fore.RESET}")
            return
        
    def runAssembler(self):
        base_name = Path(self.outputFiles).stem
        if self.x86_64_linux:
            output_asm = f"{base_name}-x86_64-linux.asm"
            object_file = f"{base_name}-x86_64-linux.o"

            nasm_cmd = [
                nasmAssembler,
                "-f", "elf64",
                output_asm,
                "-o", object_file
            ]
            try:
                subprocess.run(nasm_cmd, check=True)
            except subprocess.CalledProcessError:
                self.err2(f"Assembler failed to assemble")

            exe_file = base_name
            if self.useWSLLD:
                ld_cmd = f'wsl ld "{object_file}" -o "{exe_file}"'
                subprocess.run(ld_cmd, shell=True, check=True)
            else:
                ld_cmd = ["ld", object_file, "-o", exe_file]
                subprocess.run(ld_cmd, check=True)

    def checkAssembler(self):
        if not os.path.exists(nasmAssembler):
            self.err(f"NASM Assembler not found: {nasmAssembler}")
        else:
            self.sucess(f"NASM Assembler founded: {nasmAssembler}")

    def fullCheck(self):
        self.checkName()
        self.checkAssembler()

    def isExistAndFile(self, string):
        if os.path.isfile(string) and os.path.exists(string):
            return True
        else:
            return False

    def clearOutput(self):
        if self.clo:
            base_name = Path(self.outputFiles).stem
            if self.x86_64_linux:
                object_file = f"{base_name}-x86_64-linux.o"
                if self.isExistAndFile(object_file):
                    os.remove(object_file)
                else:
                    self.err2(f"Clear output error: object file isn't a file: {object_file}")

        if self.cloa:
            base_name = Path(self.outputFiles).stem
            if self.x86_64_linux:
                output_asm = f"{base_name}-x86_64-linux.asm"
                if self.isExistAndFile(output_asm):
                    os.remove(output_asm)
                else:
                    self.err2(f"Clear output error: object file isn't a file: {object_file}")

    def pipeline(self):
        if self.signed:
            self.fullCheck()

            self.phase2Parse()
            self.resolvePlatforms()
            self.writeOutput()
            self.runAssembler()
            self.clearOutput()