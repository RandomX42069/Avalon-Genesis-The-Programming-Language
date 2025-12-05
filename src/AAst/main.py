import re, colorama, shlex
import AAst.stackframe as stackframe

func_call_regex = re.compile(r'(.+)\(([^()]*)\)')
ExcludedFunctionRegexDefine = re.compile(r"@exclude function (.+)\(([^()]*)\)")
FunctionRegexDefine = re.compile(r"@function\s+([A-Za-z_]\w*)\s*\((.*)\)")
varses = re.compile(r"^%(.+)\s*=\s*(.+)$")
arrayRegex = re.compile(r"%([A-Za-z]+)\s+(\w+)\s*=\s*\[([^\]]*)\]")
operatorRegex = re.compile(r'^%(\w+)\s*([+\-*/]?=)\s*(.+)$')
structRegex = re.compile(r'^@struct\s+(\w+)$')
structEndRegex = re.compile(r'^@structend\s+(\w+)$')
fieldRegex = re.compile(r'^@(\w+)\s*::\s*(.+)') # name - > 1 value - > 2
ifstatementRegex = re.compile(r'@if\s*\((.*)\)')
whileStatementRegex = re.compile(r'@while\s*\((.*)\)')
nonfunctionRegex = re.compile(r'@non-function\s*(.*)\((.*)\)')
indexingRegex = re.compile(r'(.+)\[(.+)\]\s*=\s*(.+)\s*')
filesystemMarginRegex = re.compile(r'^@fs-margin\s*')
filesystemEndMarginRegex = re.compile(r'^@fs-endmargin\s*')
debug = False
valdbg = False
segmentParser = 1

class ASTNode:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []

    def __repr__(self, level=0):
        indent = "  " * level
        result = f"{indent}{self.node_type}: {self.value}\n"
        for child in self.children:
            result += child.__repr__(level + 1)
        return result


class ArbitraryHeader(ASTNode):
    def __init__(self, file_name=None, content: str = None):
        super().__init__("ArbitraryHeader", file_name)
        self.content = content or ""

    def emit(self):
        """Write the content to the file represented by self.value (filename)."""
        if not self.value:
            raise ValueError("No filename specified for ArbitraryHeader.")
        with open(self.value, "w") as f:
            f.write(self.content)
        print(f"[+] Written header to {self.value}")

class SegmentedFile(ASTNode):
    def __init__(self, nodet="Segment", fileName:str=None, content:str=None):
        super().__init__(nodet, fileName)
        self.file = fileName
        self.content = content or ""

    def include(self):
        try:
            with open(self.file, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"[!] Segment file {self.file} not found")
            return ""

class Chain(ASTNode):
    def __init__(self, chunk: str, nodet="Chain"):
        super().__init__(nodet)
        self.lines = [code.strip() for code in chunk.split("::") if code.strip()]

class FunctionCall(ASTNode):
    def __init__(self, param: list[str], name="Lambda", nodet="FunctionCall"):
        super().__init__(nodet)
        self.name = name
        self.param = param 

class Var(ASTNode):
    def __init__(self, name="Lambda", value=None, nodet="Var"):
        super().__init__(nodet, value)
        self.name = name
    
class VarArray(ASTNode):
    def __init__(self, value=None, nodet="Array", define="db", name="Lambda"):
        super().__init__(nodet, value)
        self.define = define
        self.name = name

class Operator(ASTNode):
    def __init__(self, nodet="Operator", name:str="", op:str="", opes:list=[]):
        super().__init__(nodet, opes, None)
        self.name = name
        self.operator = op

class StructDef(ASTNode):
    def __init__(self, name, fields:dict):
        super().__init__("StructDef")
        self.name = name
        self.fields = fields  # list of field names (no default values)

class StructInstance(ASTNode):
    def __init__(self, name, value):
        super().__init__("StructInstance")
        self.name = name
        self.value = value

class Ifstament(ASTNode):
    def __init__(self, nodet="IfStatement", value=None, statement=None):
        super().__init__(nodet, value)
        self.state = statement

class LabelAdd(ASTNode):
    def __init__(self, nodet="LabelNameAddtion", value=None, type=None):
        super().__init__(nodet, value)
        self.ltype = type



class NormalFunction(ASTNode):
    def __init__(self, nodet="Function-Declare", value=None, name="", code=None, param=None):
        super().__init__(nodet, value)
        self.code = code if code is not None else []
        self.name = name
        self.realcode = ""
        self.param = param if param is not None else []

class NonFunction(ASTNode):
    def __init__(self, nodet="Non-Function", nodes=[], param=[], name=""):
        super().__init__(nodet, None, None)
        self.nodes = nodes
        self.params = param
        self.name = name

class ExcludedFunction(ASTNode):
    def __init__(self, nodet="Non-included Function", value=None, code=[], param=[]):
        super().__init__(nodet, value) # value = name
        self.code = code # lines
        self.param = param

class AGCExceptionBlock:
    def __init__(self, errorName:str="", message:str=""):
        self.name = errorName
        self.msg = message
        self.handled = False
    
    def alert(self):
        print(f"{self.name}: {self.msg}")
        self.handled = True

class UnknownAstNode(AGCExceptionBlock):
    def __init__(self, errorName = "UnknownAstNode", chunk=""):
        super().__init__(errorName, f"Unknown ast node: {chunk}")
        
    
class Parser:
    def __init__(self, source_code: str, doc:str=None, args:list=["--debug", "--dbg,val"], srcFile:str=""):
        self.srcfile = srcFile
        self.in_ml_comment = False
        self.signed = True
        self.argvs = args
        self.debugPreflix = "[ DEBUG ] Avalon Genesis Parser: Debug: "
        self.debugExternal = "[ DEBUG ]Avalon Genesis Parser: External: "
        self.error = "[ ERROR ]  Avalon Genesis Parser: "
        self.source_code = source_code.splitlines()
        self.pos = 0
        self.ast_nodes = []
        self.document = doc or ""
        self.variable = {}
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
        self.functionAttributeMapping = {
            1: "Normal",
            2: "No Return"
        }
        self.errors = {
            0: "", 1: "FunctionCallError: Cannot have more than 255 args", 2: "UnknownAstNodeError", 3: "SegmentRecursiveInclude", 4: "SyntaxError"
        }

    def parseArgs(self):

        global debug, valdbg
        for each in self.argvs:
            if each == "--debug":
                debug = True
            elif each == "--dbg,val":
                valdbg = True

    def dprint(self, string:str):
        print(f"{self.debugPreflix}{string} at: Index: {self.pos}")

    def eprint(self, string:str):
        print(f"{self.debugExternal}{string}")

    def err(self, string:str, errorType=0):
        def tru(input_str, length):
            if len(input_str) > length:
                return input_str[:length] + "..."
            else:
                return input_str
        
        print(f"{colorama.Fore.RED}{self.error}{self.errors[errorType]}: {string} at Line: Number: {self.pos}, Context: {tru(self.source_code[self.pos], 20)}{colorama.Fore.RESET}")
        self.signed = False

    def strip_signleline_comment(self, line: str) -> str:
        if debug:
            self.dprint(f"strip_comments {self.debuggingMapping[4]} function used: Line: {line}")
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

    def parse(self):
        while self.signed and self.pos < len(self.source_code):
            line = self.source_code[self.pos].strip()
            line = self.strip_comments(line)
            if debug:
                self.dprint(f"Line: {line}")
            if not line:
                self.pos += 1
                continue
            if line.lower().startswith("@head"):
                self.ast_nodes.append(self.parse_header())
            elif line.lower().startswith("@segment"):
                self.ast_nodes.extend(self.parse_segment())
            elif line.lower().startswith("@file_doc"):
                self.parse_doc()
            elif line.lower().startswith("@struct"):
                self.parse_struct()
            elif line.lower().startswith("@if"):
                self.parse_statement()
            else:
                self.parseChain()

            if debug:
                self.dprint(f"Parser position tracking: {self.pos}")
            self.pos += 1
            if debug:
                self.dprint(f"Parser position advanced")

        return self.ast_nodes

    def parse_statement(self):
        line = self.source_code[self.pos].strip()
        line = self.strip_comments(line)
        matches = ifstatementRegex.match(line)

        if not matches:
            self.err(f"Invalid if statement syntax")
            return

        cap = matches.group(1).strip()
        cap = re.split(r'\s*(?:&&|\|\|)\s*', cap)
        contents = []
        self.pos += 1

        while self.pos < len(self.source_code):
            current_line = self.source_code[self.pos].strip()
            if current_line.lower().startswith("@endif"):
                break
            contents.append(self.strip_comments(current_line))
            self.pos += 1

        if self.pos > len(self.source_code):
            if not self.source_code[self.pos].strip().lower().startswith("@endif"):
                self.err(f"Missing @endif for if-statement starting")
        else:
            self.pos += 1

        inner_parser = Parser("\n".join(contents))
        inner_parser.parse()

        if_node = Ifstament(value=inner_parser.ast_nodes, statement=cap)
        self.ast_nodes.append(if_node)

        if debug:
            self.dprint(f"parse_statement {self.debuggingMapping[4]} Function used: State: {cap}")
        if valdbg:
            self.dprint(f"parse_statement {self.debuggingMapping[4]} Function if statement values: {if_node.value}")

    def processStringBloat(self, string:str) -> str:
        if debug:
            self.dprint(f"processStringBloat {self.debuggingMapping[4]} Function: String: {string}")
        if string[-1] == "\"" or string[-1] == "\'":
            string = string[0:-1]
        if string[0] == "\"" or string[0] == "\'":
            string = string[1:]
        return string

    def parse_header(self):
        line = self.source_code[self.pos].strip()
        line = self.strip_comments(line)
        _, file_name = shlex.split(line)
        self.pos += 1

        content_lines = []
        while self.pos < len(self.source_code):
            line = self.source_code[self.pos]
            if line.lower().strip() == "@end":
                self.pos += 1
                break
            content_lines.append(line)
            self.pos += 1

        content = "\n".join(content_lines)
        self.ast_nodes.append(ArbitraryHeader(file_name=self.processStringBloat(file_name), content=content))
    
    def parse_struct(self):
        fields = {}

        self.pos += 1
        while self.pos < len(self.source_code):
            line = self.source_code[self.pos].strip()
            line = self.strip_comments(line)

            field = fieldRegex.match(line)
            end = structEndRegex.match(line)

            if field:
                fields[field.group(1)] = field.group(2)
            elif end:
                struct_name = end.group(1)
                self.pos += 1
                break

            self.pos += 1

        self.ast_nodes.append(StructDef(struct_name, fields))

    def parse_segment(self):
        global segmentParser
        if debug:
            self.eprint(f"Segment Parser {segmentParser}:")
            segmentParser += 1
        line = self.strip_comments(self.source_code[self.pos].strip())
        _, fileName = shlex.split(line)

        segment = SegmentedFile(fileName=self.processStringBloat(fileName))
        segment.content = segment.include()
        check = f"@segment {self.srcfile}"
        check2 = f"@segment \"{self.srcfile}\""
        check3 = f"@segment \'{self.srcfile}\'"
        if check in segment.content or check2 in segment.content or check3 in segment.content:
            self.err(f"Recursive segment include: file 1: {self.srcfile}, file 2: {fileName}", 3)
            return []
        if debug:
            self.eprint(f"AG source segment file included: {fileName}")

        segment_parser = Parser(segment.content)
        segment_parser.parse()
        segment = segment_parser.ast_nodes
        
        return segment


    def parse_excludeFunction(self):
        add = []
        
        while self.pos < len(self.source_code):
            line = self.strip_comments(self.source_code[self.pos].strip())
            if line.startswith("@endexfunc") or line.startswith("@endfunc"):
                self.pos += 1
                break
            else:
                add.append(line)
            self.pos += 1
        return add
    
    def parse_defFunction(self):
        add = []
        
        while self.pos < len(self.source_code):
            line = self.strip_comments(self.source_code[self.pos].strip())
            if line.startswith("@endfunc"):
                self.pos += 1
                break
            else:
                add.append(line)
            self.pos += 1
        return add

    def parse_nonFunction(self):
        add = []
        
        while self.pos < len(self.source_code):
            line = self.strip_comments(self.source_code[self.pos].strip())
            if line.startswith("@endnf"):
                self.pos += 1
                break
            else:
                add.append(line)
            self.pos += 1
        return add

    def parse_doc(self):
        """
        note: THIS WILL APPEND TO THE SELF.DOCUMENT NO MATTER WHAT
        AST NODE STORE IS TOO DANGEROUS
        """
        line = self.source_code[self.pos].strip()
        line = self.strip_comments(line)
        
        _, fileName = line.split(maxsplit=1)
        if debug:
            self.dprint(f"parse_doc {self.debuggingMapping[4]} function used: file: {fileName}")

        try:
            with open(fileName, "r") as f:
                self.document += f.read()
            if debug:
                self.dprint(f"parse_doc {self.debuggingMapping[4]} function: File founded: {fileName}")
        except FileNotFoundError:
            self.err(f"[!] Document file {fileName} not found")
            if debug:
                self.dprint(f"parse_doc {self.debuggingMapping[4]} function: File not founded: {fileName}")

    def isInteger(self, inputI: str):
        if debug:
            self.dprint(f"{self.debuggingMapping[4]}Function isInteger: Param_1: {inputI}")
        try:
            int(inputI)
            return True
        except ValueError:
            return False

    def processVariableName(self, string:str):
        unallowedChars = ["~", "`", "@", "$", "%", "^", "&", "*", ";", ":", "'", '"', "|", "\\", ",", ".", "<", ">", "?", "/"]
        if self.isInteger(string[0]):
            self.err(f"Variable name start withs a number: {string[0]}", 4)
        for e in string:
            if e in unallowedChars:
                self.err(f"Variable name have unallowed character", 4)
        
    def split_arg(self, string):
        pattern = r'''((?:[^,"'()\[\]]+|"[^"]*"|'[^']*'|\([^\(\)]*\)|\[[^\[\]]*\])+)'''
        return [a.strip() for a in re.findall(pattern, string.strip(), re.VERBOSE)]

    def parseChain(self):
        line = self.strip_comments(self.source_code[self.pos].strip())
        if not line:
            return

        funcCall = func_call_regex.match(line)
        var = varses.match(line)
        array = arrayRegex.match(line)
        operate = operatorRegex.match(line)
        excludefunction = ExcludedFunctionRegexDefine.match(line)
        functiondeclare = FunctionRegexDefine.match(line)
        nonfunc = nonfunctionRegex.match(line)

        if excludefunction:
            func_n = excludefunction.group(1)
            func_param = excludefunction.group(2)
            par = [n.strip() for n in self.split_arg(func_param)] if func_param else []
            if debug:
                self.dprint(f"Exclude Function Regex Debug: Name: \'{func_n}\', Params: {par}")
            self.pos += 1
            chunk = self.parse_excludeFunction()
            if debug:
                self.dprint(f"Excluded Function Define: Name: {func_n}, Param: {", ".join(par).strip(",") if par else "(empty)"}")
            self.ast_nodes.append(ExcludedFunction(value=func_n, code=chunk, param=par))
            return
        
        elif nonfunc:
            func_name = nonfunc.group(1)
            func_param = nonfunc.group(2)
            params = [n.strip() for n in self.split_arg(func_param)] if func_param else []
            chunk = self.parse_nonFunction()[1:]
            if debug:
                self.dprint(f"Non-Function Define: Name: {func_name}, Param: {", ".join(params).strip(",") if params else "(empty)"}")
                self.dprint(f"Exclude Function Regex Debug: Name: \'{func_name}\', Params: {params}")
            innerParser = Parser("\n".join(chunk), self.document, self.argvs, self.srcfile)
            innerParser.parseArgs()
            innerParser.parse()
            self.ast_nodes.append(NonFunction(nodes=innerParser.ast_nodes, param=params, name=func_name))
            return

        elif array:
            arrayDefine = array.group(1)
            arrayName = array.group(2)
            arrayValueStr = array.group(3)

            # convert string to list of values
            arrayValues = [v.strip() for v in arrayValueStr.split(",") if v.strip()]

            deff = "db"
            if arrayDefine == "DoubleArray":
                deff = "dw"
            elif arrayDefine == "DDArray":
                deff = "dd"
            elif arrayDefine == "QArray":
                deff = "dq"
            elif arrayDefine == "Array":
                deff = "db"
            
            self.ast_nodes.append(VarArray(value=arrayValues, define=deff, name=arrayName))
            return
        
        
        elif functiondeclare:
            func_nameeeee = functiondeclare.group(1)
            func_param = functiondeclare.group(2)
            par = [n.strip() for n in self.split_arg(func_param)] if func_param else []
            self.pos += 1
            chunk = self.parse_defFunction()
            if debug:
                self.dprint(f"Function Define: Name: {func_nameeeee}, Param: {", ".join(par).strip(",") if par else "(empty)"}")
            pare = Parser("\n".join(chunk), self.document, self.argvs, self.srcfile)
            pare.parseArgs()
            pare.parse()
            self.ast_nodes.append(NormalFunction("Function-Declare", func_nameeeee, func_nameeeee, pare.ast_nodes, func_param))
            return
        
        elif funcCall:
            func_name = funcCall.group(1)
            param_str = funcCall.group(2)
            params = [p.strip() for p in self.split_arg(param_str)] if param_str else []

            if len(params) > 255:
                self.err(f"Function \'{func_name}\'", 1)
            self.ast_nodes.append(FunctionCall(param=params, name=func_name))
            if debug:
                self.dprint(f"Function Call: Name: {func_name}, Params: {" ".join(params) if len(params) >= 1 else "(Empty)"}")
            return

        elif var:
            var_name = var.group(1).strip("'\"").strip(" ")
            self.processVariableName(var_name)
            var_value = var.group(2)
            self.variable[var_name] = var_value
            self.ast_nodes.append(Var(name=var_name, value=var_value))
            return

        elif operate:
            varName = operate.group(1)
            operator = operate.group(2)
            operated = operate.group(3)

            self.ast_nodes.append(Operator(opes=operated, name=varName, op=operator))
            return
        else:
            self.err(f"In source code: {self.source_code[self.pos]}", 2)