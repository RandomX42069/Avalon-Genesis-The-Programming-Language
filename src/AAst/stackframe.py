import re, os, colorama
import egg.fs as fs
import egg.logic as brain
import egg.string as stranger

globattrExistSet = re.compile(r'@ignore-exists\s+(.+)\s*') # true or false

frameRegex = re.compile(r'@file\s+(.+)\,\s*(.+)\s*') # 1: file 2: mode
cpyframeRegex = re.compile(r'@cpy-file\s+(.+)\,\s*(.+)\s*') # 1: file 2: file
mvframeRegex = re.compile(r'@mv-file\s+(.+)\,\s*(.+)\s*') # 1: file 2: file
endFrameRegex = re.compile(r'@efile\s*') 

newdirRegex = re.compile(r'@new-dir\s+(.+)\s*') # 1: dirname
rmdirRegex = re.compile(r'@rmdir\s+(.+)\s*') # 1: dir

class MarginFilesystemParser:
    def __init__(self, srccode, srcfile, args=[]):
        self.srccode = srccode
        self.srcfile = srcfile
        self._fs = fs.filesystem()
        self.pos = 0
        self.signed = True
        self.args = args
        self.dbg = False
        self.ignores = {
            "exists": False
        }
        self.dbgp("Initialized parser")

    def parseArgs(self):
        self.dbgp("Parsing args")
        for a in self.args:
            a = a.strip()
            self.dbgp(f"Arg found: {a}")
            if a in ("--verbose", "--dbg", "--debug"):
                self.dbg = True
                self.dbgp("Debug mode enabled")

    def err(self, string):
        self.signed = False
        print(f"{colorama.Fore.RED}[ ERROR ]: {string} at: Index: {self.pos}{colorama.Fore.RESET}")
        self.dbgp("Error triggered")

    def dbgp(self, string):
        if self.dbg:
            print(f"[ Stackframe Parser ] [ DEBUG ] {string}")

    def parse(self):
        self.dbgp("Starting parse()")
        if not isinstance(self.srccode, list):
            self.dbgp("Splitting srccode into lines")
            self.srccode = self.srccode.splitlines()

        while self.pos < len(self.srccode) and self.signed:
            self.dbgp(f"Processing line index: {self.pos}")
            line = self.srccode[self.pos].strip()
            self.dbgp(f"Raw line: '{self.srccode[self.pos]}'")
            self.dbgp(f"Stripped line: '{line}'")

            if not line:
                self.dbgp("Skipping empty line")
                self.pos += 1
                continue

            nbloat = self.processStringBloat

            frameMatch = frameRegex.match(line)
            cpyframeMatch = cpyframeRegex.match(line)
            mvframeMatch = mvframeRegex.match(line)
            newdirMatch = newdirRegex.match(line)
            rmdirMatch = rmdirRegex.match(line)
            globattrExistSetMatch = globattrExistSet.match(line)

            self.dbgp("Regex checks complete")

            if frameMatch:
                self.dbgp("Matched @file frame")
                self.pos += 1
                self.processFrame(nbloat(frameMatch.group(1)), nbloat(frameMatch.group(2)))
                self.dbgp(
                    f"frame regex matched: {', '.join([nbloat(frameMatch.group(1)), nbloat(frameMatch.group(2))])}"
                )
            elif newdirMatch:
                self.dbgp(f"Matched @new-dir: {newdirMatch.group(1)}")
                os.makedirs(nbloat(newdirMatch.group(1)), exist_ok=True)
            elif rmdirMatch:
                self.dbgp(f"Matched @rmdir: {rmdirMatch.group(1)}")
                self._fs.rmdir(nbloat(rmdirMatch.group(1)))
            elif cpyframeMatch:
                self.dbgp("Matched @cpy-file")
                self._fs.cpyfile(nbloat(cpyframeMatch.group(1)), nbloat(cpyframeMatch.group(2)))
            elif mvframeMatch:
                self.dbgp("Matched @mv-file")
                self._fs.mvfile(nbloat(mvframeMatch.group(1)), nbloat(mvframeMatch.group(2)))
            elif globattrExistSetMatch:
                self.dbgp("Matched @ignore-exists")
                self.globExistSet(nbloat(globattrExistSetMatch.group(1)))
            else:
                self.dbgp("No regex matched")
                self.err(f"Unknown grammar: {self.srccode[self.pos].strip()}")

            self.dbgp(f"Position: {self.pos}")
            self.pos += 1

        self.dbgp("Finished parse()")

    def processStringBloat(self, string:str) -> str:
        self.dbgp(f"processStringBloat input: {string}")
        if not string: string
        if string[-1] == "\"" or string[-1] == "\'":
            string = string[0:-1]
            self.dbgp(f"Trimmed trailing quote, now: {string}")
        if string[0] == "\"" or string[0] == "\'":
            string = string[1:]
            self.dbgp(f"Trimmed leading quote, now: {string}")
        return string

    def processFrame(self, fn, mode):
        self.dbgp(f"processFrame called with fn={fn}, mode={mode}")

        fn = self.processStringBloat(fn)
        md = self.processStringBloat(mode)

        self.dbgp(f"Final fn={fn}, md={md}")

        if self._fs.isExistAndFile(fn) and not self.ignores["exists"]:
            self.dbgp("File exists before creating frame")
            self.err(f"Frame Error: file already exists: {fn}")

        content = ""
        self.dbgp("Beginning to collect frame content")

        while self.pos < len(self.srccode):
            line = self.srccode[self.pos]
            self.dbgp(f"Frame content line: '{line}'")
            if endFrameRegex.match(line):
                self.dbgp("Matched @efile, closing frame")
                self.pos += 1
                break
            content += line + "\n"
            self.pos += 1

        self.dbgp(f"Final collected content length: {len(content)}")

        if md == "w":
            self.dbgp("Writing file in mode w")
            self._fs.writeToFile(fn, content)
        elif md == "a":
            self.dbgp("Appending file in mode a")
            self._fs.appendToFile(fn, content)
        elif md == "c":
            self.dbgp("Creating file in mode c")
            self._fs.createFile(fn)
        elif md == "wc":
            self.dbgp("Creating and writing file in mode wc")
            self._fs.createFile(fn)
            self._fs.writeToFile(fn, content)

        else:
            self.dbgp("Unknown mode inside frame")
            self.err(f"Frame Error: Unknown mode: {md}")

    def globExistSet(self, string):
        def _raise(): self.err(f"globExistSet input is invalid: {string}")
        def _sett(): self.ignores["exists"] = True
        def _setf(): self.ignores["exists"] = False
        string = stranger.StringTool(string)._language_safe()
        r = brain.pAst_if(f"\"{string}\" not in (\"true\", \"True\", \"false\", \"False\")")
        r2 = brain.pAst_if(f"\"{string}\" in (\"true\", \"True\")")
        r3 = brain.pAst_if(f"\"{string}\" in (\"false\", \"False\")")
        brain.doFuncWhenIfMatch([_raise, _sett, _setf], [r, r2, r3])