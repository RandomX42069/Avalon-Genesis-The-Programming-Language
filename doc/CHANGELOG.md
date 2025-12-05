DOCUMENT CHANGELOG
v0.1
Identifiers and directives usually use % or @ at the head
REGEXES:
func_call_regex = re.compile(r'(.+)\(([^()]*)\)')
ExcludedFunctionRegexDefine = re.compile(r"@exclude function (.+)\(([^()]*)\)")
FunctionRegexDefine = re.compile(r"@function\s+([A-Za-z_]\w*)\s*\((.*)\)")
varses = re.compile(r"^%(.+)\s*=\s*(.+)$")
arrayRegex = re.compile(r"%([A-Za-z]+)\s+(\w+)\s*=\s*\[([^\]]*)\]")
operatorRegex = re.compile(r'^%(\w+)\s*([+\-*/]?=)\s*(.+)$')
structRegex = re.compile(r'^%struct\s+(\w+)$')
structEndRegex = re.compile(r'^%structend\s+(\w+)$')
fieldRegex = re.compile(r'^%(\w+)\s*::\s*(.+)') # name - > 1 value - > 2
ifstatementRegex = re.compile(r'@if\s*\((.*)\)')
whileStatementRegex = re.compile(r'@while\s*\((.*)\)')
nonfunctionRegex = re.compile(r'@non-function\s*(.*)\((.*)\)')

v0.2
Identifiers are ALL UNIFIED, WHICH MEANS DIRECTIVES USES @ ONLY NOW
BUT VARIABLES DECLARATION STILL USE %
%struct -> @struct
%structend -> @structend
%structfield -> @structfield::value
