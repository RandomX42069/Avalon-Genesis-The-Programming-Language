import time, os
from pathlib import Path

class loggingSystem:
    
    def __init__(self, work):
        self.work = work
        self.log_dir = os.path.join(self.work, "AvalonGenesisLogs")
        self.name = "Avalon Logging System: "
        self.output(f"Logging Dir: {self.log_dir}")
    
    def output(self, msg):
        print(f"{self.name}{msg}")

    def get_dir_size(self, directory):
        return sum(f.stat().st_size for f in Path(directory).rglob('*') if f.is_file())
    
    def find_depth(self, lst, target, current_depth=1):
        for item in lst:
            if item == target:
                return current_depth
            elif isinstance(item, list):
                deeper = self.find_depth(item, target, current_depth + 1)
                if deeper:
                    return deeper
        return None
    
    def cleanLogs(self, path:str):
        for dp, dn, fn in os.walk(path):
            for f in fn:
                pathy = os.path.join(dp, f)
                pather = Path(pathy)
                if pather.suffix in [".log", ".AvalonMakefileLog"]:
                    os.remove(pathy)
                    print(f"Deleted: {pathy}")

    def checkLogs(self, path:str):
        if self.get_dir_size(path) > 52428800 and os.path.isdir(path):
            self.cleanLogs(path)

    def log(self, file, information: str, indent: int = 0):
        t = time.localtime()
        indent_str = "  " * indent
        timestamp = f"[Y:{t.tm_year}/Mo:{t.tm_mon:02}/D:{t.tm_mday:02}/H:{t.tm_hour:02}/Mi:{t.tm_min:02}/S:{t.tm_sec:02}]"

        file_path = os.path.normpath(str(file))
        work_norm = os.path.normpath(str(self.work))
        if not file_path.startswith(work_norm):
            file_path = os.path.join(self.log_dir, file_path)

        with open(file_path, "a") as f:
            f.write(f"{indent_str}{timestamp} {information}\n")


    def logThread(self, file, InformationList: list, level: int = 0):
        for item in InformationList:
            if isinstance(item, list):
                self.logThread(file, item, level + 1)
            else:
                self.log(file, item, level)