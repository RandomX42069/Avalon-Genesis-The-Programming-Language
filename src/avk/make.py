import subprocess, time, os, shutil, sys, egg.fs, re, shlex
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from avk.log import *
from egg.colorful import *

class buildSystem:
    def __init__(self, target_dir=None, log_dir=None):
        self.buildDirectory = target_dir
        self.log_dir = log_dir
        self.working = target_dir
        self.IndicatorPrefix = "[ AGK ] "

        self.total_tries = 0
        self.buildable_files = 0
        self.failed = 0
        self.success = 0
        self.successList = []
        self.failedList = []

        self.log = loggingSystem(self.buildDirectory)
        self._log_lock = Lock()
        self._counter_lock = Lock()
        self._fs = egg.fs.filesystem()

    def ostream(self, msg):
        print(f"{FBLUE}{self.IndicatorPrefix}{FRESET} {msg}")

    def err(self, msg):
        print(f"{FRED}{self.IndicatorPrefix} [ ERROR ] {FRESET} {msg}")
        sys.exit(1)

    def BuildCheck(self, thing: str):
        def importErrorHandler(module: str):
            try:
                __import__(module)
            except ImportError:
                print(f"{module} wasn't installed")
                with self._log_lock:
                    if module == "PyInstaller":
                        self.log.log(os.path.join(self.log_dir, "AvalonGenesisLogs/MissingModule-PyInstaller.log"), "PyInstaller is missing")
                    elif module == "nuitka":
                        self.log.log(os.path.join(self.log_dir, "AvalonGenesisLogs/MissingModule-Nuitka.log"), "Nuitka is missing")
                sys.exit(1)
        if thing.lower() == "pyinstaller":
            importErrorHandler("PyInstaller")
        elif thing.lower() == "nuitka":
            importErrorHandler("nuitka")

    def build(self, buildDiction: dict):
        localTime = time.localtime()
        timestamp = f"{localTime.tm_year:04}-{localTime.tm_mon:02}-{localTime.tm_mday:02}-{localTime.tm_hour:02}-{localTime.tm_min}-{localTime.tm_sec:02}-"
        log_path = os.path.join(f"{self.log_dir}/AvalonGenesisLogs", f"{timestamp}build-Project-{Path(self.buildDirectory).parts[-1]}.AvalonMakefileLog")

        name = buildDiction.get("name", "")
        metadata = buildDiction.get("metadata", {})
        builders = buildDiction.get("builders", {})
        toolChainInit = buildDiction.get("$tool-chain", {})

        languages = buildDiction.get("$languages", {})
        clanguage = languages.get("$c", {})
        msys2Dll = clanguage.get("$msys-dll-path", "")

        gccConfig = toolChainInit.get("$gcc", {})
        clangConfig = toolChainInit.get("$clang", {})

        gccCopyDLL = gccConfig.get("copy-msys2-dll", False)
        gccPath = gccConfig.get("path", "")
        
        clangCopyDLL = clangConfig.get("copy-msys2-dll", False)
        clangPath = clangConfig.get("path", "")

        print(f"{name}")
        def metaData_analyzer():
            repo = metadata.get("$github-repo", "")
            description = metadata.get("$description", "")
            print(f"Repo: {repo}")
            print(f"Desc: {description}")
        metaData_analyzer()

        

        build_C = ".c" in builders
        build_asm = ".asm" in builders
        build_py = ".py" in builders
        build_cpp = ".cpp" in builders
        build_cs = ".cs" in builders
        build_oc = ".m" in builders
        build_rust = ".rs" in builders
        build_go = ".go" in builders
        build_ts = ".ts" in builders
        build_ag = ".ag" in builders
        
        link_obj = ".obj" in builders

        cArgs = buildDiction.get("builders", {}).get(".c", {}).get("args", [])
        cSpefic = buildDiction.get("builders", {}).get(".c", {}).get("spefic", {})
        cPath = buildDiction.get("builders", {}).get(".c", {}).get("path", f"{self.IndicatorPrefix}C-Compiler-Unknown-Path")

        cppArgs = buildDiction.get("builders", {}).get(".cpp", {}).get("args", [])
        cppSpefic = buildDiction.get("builders", {}).get(".cpp", {}).get("spefic", {})
        cppPath = buildDiction.get("builders", {}).get(".cpp", {}).get("path", f"{self.IndicatorPrefix}C++-Compiler-Unknown-Path")

        csArgs = buildDiction.get("builders", {}).get(".cs", {}).get("args", [])
        csSpefic = buildDiction.get("builders", {}).get(".cs", {}).get("spefic", {})
        csPath = buildDiction.get("builders", {}).get(".cs", {}).get("path", f"{self.IndicatorPrefix}C#-Compiler-Unknown-Path")

        ocArgs = buildDiction.get("builders", {}).get(".m", {}).get("args", [])
        ocSpefic = buildDiction.get("builders", {}).get(".m", {}).get("spefic", {})
        ocPath = buildDiction.get("builders", {}).get(".m", {}).get("path", f"{self.IndicatorPrefix}Objective-C-Compiler-Unknown-Path")

        rustArgs = buildDiction.get("builders", {}).get(".rs", {}).get("args", [])
        rustSpefic = buildDiction.get("builders", {}).get(".rs", {}).get("spefic", {})
        rustPath = buildDiction.get("builders", {}).get(".rs", {}).get("path", f"{self.IndicatorPrefix}Rust-Compiler-Unknown-Path")

        goArgs = buildDiction.get("builders", {}).get(".go", {}).get("args", [])
        goSpefic = buildDiction.get("builders", {}).get(".go", {}).get("spefic", {})
        goPath = buildDiction.get("builders", {}).get(".go", {}).get("path", f"{self.IndicatorPrefix}Go-Compiler-Unknown-Path")

        tsArgs = buildDiction.get("builders", {}).get(".ts", {}).get("args", [])
        tsSpefic = buildDiction.get("builders", {}).get(".ts", {}).get("spefic", {})
        tsPath = buildDiction.get("builders", {}).get(".ts", {}).get("path", f"{self.IndicatorPrefix}TS-Compiler-Unknown-Path")

        asmArgs = buildDiction.get("builders", {}).get(".asm", {}).get("args", [])
        asmSpefic = buildDiction.get("builders", {}).get(".asm", {}).get("spefic", {})
        asmPath = buildDiction.get("builders", {}).get(".asm", {}).get("path", f"{self.IndicatorPrefix}Assembly-Assembler-Unknown-Path")

        pyArgs = buildDiction.get("builders", {}).get(".py", {}).get("args", [])
        pySpefic = buildDiction.get("builders", {}).get(".py", {}).get("spefic", {})
        pyNuitka = bool(buildDiction.get("builders", {}).get(".py", {}).get("use-nuitka"))
        pyNuitkaInitialize = buildDiction.get("builders", {}).get(".py", {}).get("nuitka-init", {})

        objArgs = buildDiction.get("builders", {}).get(".obj", {}).get("args", [])
        objSpefic = buildDiction.get("builders", {}).get(".obj", {}).get("spefic", {})
        objPath = buildDiction.get("builders", {}).get(".obj", {}).get("path", f"{self.IndicatorPrefix}Linker-Unknown-Path")

        agArgs = buildDiction.get("builders", {}).get(".ag", {}).get("args", [])
        agSpefic = buildDiction.get("builders", {}).get(".ag", {}).get("spefic", {})
        agPath = buildDiction.get("builders", {}).get(".ag", {}).get("path", f"{self.IndicatorPrefix}Avalon-Genesis-Language-Unknown-Path")

        ignoresDiction = buildDiction.get("ignore", {})
        ignoreDir = ignoresDiction.get("dirs", {})
        ignoreFile = ignoresDiction.get("file", {})
        ignoreExtension = ignoresDiction.get("ext", [])
        ignorePattern = ignoresDiction.get("pattern", [])

        supported_suffixes = [
            ext for ext, flag in [
                (".c", build_C),
                (".cpp", build_cpp),
                (".cs", build_cs),
                (".m", build_oc),
                (".rs", build_rust),
                (".go", build_go),
                (".ts", build_ts),
                (".asm", build_asm),
                (".py", build_py),
                (".obj", link_obj),
                (".ag", build_ag),
            ] if flag
        ]

        self.ostream(f"Build directory: {self.buildDirectory}")
        self.ostream(f"Supported suffixes: {supported_suffixes}")
        self.ostream(f"Ignore dirs: {ignoreDir}")
        self.ostream(f"Starting file scan...")

        startTime = time.time()
        futures = []

        def handleReturnCode(file_path, code):
            with self._counter_lock:
                self.total_tries += 1
                if code != 0:
                    self.failed += 1
                    self.failedList.append(str(file_path))
                else:
                    self.success += 1
                    self.successList.append(str(file_path))

        def safe_log(file, InformationList: list, level: int = 0):
            with self._log_lock:
                self.log.logThread(file, InformationList, level)

        def build_file(file_path: Path):
            rel_path = file_path.relative_to(self.buildDirectory).as_posix()
            suffix = file_path.suffix

            self.ostream(f"Current file relative path: {rel_path}")
            self.ostream(f"Suffix='{suffix}'")
            self.ostream(f"About to check conditions...")

            if any(part in ignoreDir for part in file_path.parts):
                self.ostream(f"{FYELLOW}[ SKIPPED ]{FRESET} In ignored directory: {file_path}")
                return

            if rel_path in ignoreFile:
                self.ostream(f"{FYELLOW}[ SKIPPED ]{FRESET} Ignored file: {file_path}")
                return
        
            if file_path.suffix in ignoreExtension:
                self.ostream(f"{FYELLOW}[ SKIPPED ]{FRESET} Ignored file: extension: {ignoreExtension[ignoreExtension.index(file_path.suffix)]} file: {file_path}")
                return
            
            for each in ignorePattern:
                regexCom = re.compile(each)
                if regexCom.match(rel_path):
                    self.ostream(f"{FYELLOW}[ SKIPPED ]{FRESET} Ignored file: pattern: {each}, file:{file_path}")
              
            self.ostream(f"Passed ignore check, entering language checks")
            def _anti_repetitive(getfrom, argfrom, comPath, language, suffixxx, outputDirective, SS, addCArg=False):
                if not self._fs.isExistAndFile(comPath):
                    self.err(f"Compiler: Language: {language}, Name/Path: {comPath}, Status: Doesn't Exist")
                args = getfrom.get(rel_path, argfrom)
                output_file = file_path.with_suffix(suffixxx)
                

                if comPath.endswith("bash.exe"):
                    posix_file_path = file_path.as_posix()

                    if len(posix_file_path) > 1 and posix_file_path[1] == ":":
                        posix_file_path = f"/{posix_file_path[0].lower()}{posix_file_path[2:]}"

                    posix_output_path = output_file.as_posix()
                    if len(posix_output_path) > 1 and posix_output_path[1] == ":":
                        posix_output_path = f"/{posix_output_path[0].lower()}{posix_output_path[2:]}"

                    if len(args) >= 2 and args[0] == "-lc":
                        compiler_cmd = args[1]
                        compiler_extra_args = args[2:] if len(args) > 2 else []
                        bash_cmd = f'{compiler_cmd} {" ".join(compiler_extra_args)} \'{posix_file_path}\' {outputDirective} \'{posix_output_path}\''
                        cmd = [comPath, "-lc", f"{bash_cmd}"]
                    else:
                        cmd = [comPath] + args + [str(file_path), outputDirective, str(output_file)]
                    
                else:
                    if addCArg:
                        cmd = [comPath] + args + ["-c", str(file_path), outputDirective, str(output_file)]
                    else:
                        cmd = [comPath] + args + [str(file_path), outputDirective, str(output_file)]


                result = subprocess.run(cmd, capture_output=True, text=True)
                self.ostream(f"{FBLUE}[ SUBPROCESS ]{FRESET} {FGREEN}RUN:{FRESET} {(" ".join(cmd).strip()).strip()}")
                if result.stdout:
                    self.ostream(f"{FBLUE}[ SUBPROCESS ]{FRESET} {FGREEN}IO: STDOUT:{FRESET} {result.stdout.strip()}")
                if result.stderr:
                    self.ostream(f"{FBLUE}[ SUBPROCESS ]{FRESET} {FGREEN}IO: STDERR:{FRESET} {result.stderr.strip()}")
                safe_log(
                    log_path,
                    [f"Build {language} file: {file_path}", [
                        f"Return Code: {result.returncode}",
                        f"Stdout     : {result.stdout if result.stdout else '(None)'}",
                        f"Stderr     : {result.stderr if result.stderr else '(None)'}"
                    ]],
                    1
                )
                handleReturnCode(file_path, result.returncode)
                return cmd

            if suffix == ".c" and build_C:
                getcm = shlex.split(_anti_repetitive(cSpefic, cArgs, cPath, "C", ".exe", "-o", ".c")[2])
                self.ostream(f"C Build: Getcm: {getcm}")
                self.ostream("Language check: Valid: True, Lang: C")

                if cPath.endswith("bash.exe"):
                     
                    output_file = file_path.with_suffix(".exe")
                    def resolveC():
                            dll_src = msys2Dll
                            dll_dst = output_file.parent / "msys-2.0.dll"
                            if Path(dll_src).exists() and not dll_dst.exists():
                                try:
                                    shutil.copy(dll_src, str(dll_dst))
                                    self.ostream(f"Copied msys-2.0.dll to output directory")
                                except Exception as e:
                                    self.ostream(f"Warning: Could not copy msys-2.0.dll: {e}")
                    gcc = Path(gccPath)
                    clang = Path(clangPath)
                    if gccCopyDLL and gcc.name in ("gcc.exe", "gcc") and getcm[0] == "gcc":
                        resolveC()
                    if clangCopyDLL and clang.name in ("clang.exe", "clang") and getcm[0] == "clang":
                        resolveC()
                        

            elif suffix == ".cpp" and build_cpp:
                _anti_repetitive(cppSpefic, cppArgs, cppPath, "C++", ".exe", "-o", ".cpp")
                self.ostream("Language check: Valid: True, Lang: C++")

            elif suffix == ".cs" and build_cs:
                _anti_repetitive(csSpefic, csArgs, csPath, "C#", ".exe", "/out:", ".cs")
                self.ostream("Language check: Valid: True, Lang: C#")

            elif suffix == ".m" and build_oc:
                _anti_repetitive(ocSpefic, ocArgs, ocPath, "Objective-C", ".exe", "-o", ".m")
                self.ostream("Language check: Valid: True, Lang: Objective-C")

            elif suffix == ".rs" and build_rust:
                _anti_repetitive(rustSpefic, rustArgs, rustPath, "Rust", ".exe", "-o", ".rs")
                self.ostream("Language check: Valid: True, Lang: Rust")

            elif suffix == ".go" and build_go:
                _anti_repetitive(goSpefic, goArgs, goPath, "Go", ".exe", "-o", ".go")
                self.ostream("Language check: Valid: True, Lang: Go")

            elif suffix == ".ts" and build_ts:
                _anti_repetitive(tsSpefic, tsArgs, tsPath, "TypeScript", ".exe", "--outFile", ".ts")
                self.ostream("Language check: Valid: True, Lang: TypeScript")

            elif suffix == ".obj" and link_obj:
                _anti_repetitive(objSpefic, objArgs, objPath, "Object", ".exe", "-o", ".obj")
                self.ostream("Language check: Valid: True, Lang/Type: Object-file")

            elif suffix == ".ag" and build_ag:
                _anti_repetitive(agSpefic, agArgs, agPath, "AGLang", "", "-o", ".ag", True)
                self.ostream("Language check: Valid: True, Lang: AGLang")

            elif suffix == ".asm" and build_asm:
                self.ostream("Language check: Valid: True, Lang: Assembly")
                args = asmSpefic.get(rel_path, asmArgs)
                output_suffix = ".bin"
                for each in args:
                    if each in ("-f win32", "-f win64"):
                        output_suffix = ".obj"
                output_file = file_path.with_suffix(output_suffix)
                cmd = [asmPath] + args + [str(file_path), "-o", str(output_file)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                safe_log(
                    log_path,
                    [f"Build ASM file: {file_path}", [
                        f"Return Code: {result.returncode}",
                        f"Stdout     : {result.stdout.strip() if result.stdout else '(None)'}",
                        f"Stderr     : {result.stderr.strip() if result.stderr else '(None)'}"
                    ]],
                    1
                )
                handleReturnCode(file_path, result.returncode)

            elif suffix == ".py" and build_py:
                self.ostream("Language check: Valid: True, Lang: Python")
                args = pySpefic.get(rel_path, pyArgs)

                if pyNuitka:
                    base_name = Path(file_path).stem
                    possible_dirs = [
                        f"{base_name}.dist",
                        f"{base_name}.build",
                        f"{base_name}.onefile",
                        f"{base_name}.onefile-build",
                        "__pycache__"
                    ]

                    cmd = [f"\"{sys.executable}\"", "-m", "nuitka"] + args + [str(f"\"{file_path}\"")] # type: list

                    activateVCVarsCheck = pyNuitkaInitialize.get("activate-vcvars", False)
                    vcVarsFile = pyNuitkaInitialize.get("vcvars-path", "")
                    if activateVCVarsCheck:
                        if not self._fs.isExistAndFile(vcVarsFile):
                            self.err(f"vcvars-path not found: {vcVarsFile}")
                        cmd.insert(0, f"\"{vcVarsFile}\"")
                        cmd.insert(1, "&&")

                    def nuitka_check():
                        for d in possible_dirs:
                            dir_path = file_path.parent / d
                            if dir_path.exists() and dir_path.is_dir():
                                shutil.rmtree(dir_path)

                    nuitka_check()

                    self.BuildCheck("nuitka")

                    self.ostream(f"Running NUITKA: {' '.join(cmd)}")
                    self.ostream(f"Current Dir: {file_path.parent}")
                    self.ostream(f"PATH: {os.environ['PATH']}")

                    result = subprocess.run(" ".join(cmd), capture_output=True, text=True, cwd=str(file_path.parent))

                    nuitka_check()
                else:
                    self.BuildCheck("PyInstaller")
                    dist_dir = Path(file_path.parent) / "dist"
                    pyache = Path(file_path.parent) / "__pycache__"
                    if dist_dir.exists():
                        shutil.rmtree(dist_dir)
                    if pyache.exists():
                        shutil.rmtree(pyache)
                    cmd = ["pyinstaller", str(file_path), "--distpath", str(dist_dir)] + args
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    
                safe_log(
                    log_path,
                        [f"Build Python file: {file_path}", [
                        f"Return Code: {result.returncode}",
                        f"Stdout     : {result.stdout.strip() if result.stdout else '(None)'}",
                        f"Stderr     : {result.stderr.strip() if result.stderr else '(None)'}"
                    ]],
                    1
                )
                handleReturnCode(file_path, result.returncode)
            else:
                self.ostream(f"[ X ] No language detected from: file: '{rel_path}', suffix: '{suffix}'")

        MAX_WORKERS = max(1, os.cpu_count() - 1)
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for dp, dn, fn in os.walk(str(self.buildDirectory)):
                for file_name in fn:
                    file_path = Path(dp) / file_name
                    self.ostream(f"Found file: {file_name} (suffix: {file_path.suffix})")
                    if file_path.suffix.lower() in supported_suffixes:
                        with self._counter_lock:
                            self.buildable_files += 1
                        self.ostream(f"[ OK ] Queued for build: {file_path}")
                        futures.append(executor.submit(build_file, file_path))
                    else:
                        self.ostream(f"{FYELLOW}[ SKIPPED ]{FRESET} File not supported: {file_name}")

            for f in as_completed(futures):
                try:
                    f.result()
                except Exception as e:
                    self.ostream(f"{FRED}[ ERROR ]{FRESET} Build task failed: {e}")

        endTime = time.time()
        totalTime = endTime - startTime

        safe_log(
            log_path,
            [
                "Summary:", [
                    f"Total tries   : {self.total_tries}",
                    f"Buildable     : {self.buildable_files}",
                    f"Success       : {self.success}",
                    f"Failed        : {self.failed}",
                    f"Elapsed time  : {totalTime:2f}s\n",
                ]
            ],
            1
        )

        safe_log(log_path, ["Success list  :"], 2)
        if self.successList:
            for eachSuccessFile in self.successList:
                safe_log(log_path, [eachSuccessFile], 3)
        else:
            safe_log(log_path, ["(empty)"], 3)

        safe_log(log_path, ["Failed list   :"], 2)
        if self.failedList:
            for eachFailedFile in self.failedList:
                safe_log(log_path, [eachFailedFile], 3)
        else:
            safe_log(log_path, ["(empty)"], 3)
        
