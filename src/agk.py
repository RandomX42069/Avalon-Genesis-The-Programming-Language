import sys, os, pathlib , egg.fs, egg.globerr, avk.parse, avk.log

args = sys.argv[1:]

_egg_fs = egg.fs.filesystem()
_egg_globerr = egg.globerr.AGC_GLOBAL()
agmk_path = os.path.join(os.getcwd(), "agmk")

if not _egg_fs.isExistAndFile(agmk_path):
    _egg_globerr.err(f"Avalon Genesis Makefile doesn't exist: {agmk_path}")

with open(agmk_path, "r") as f:
    content = f.read()

instance = pathlib.Path(agmk_path)
print(f"AGMK Path: {os.path.normpath(str(instance))}")
print(f"AGMK Parent Dir: {instance.parent}")

log_dir = instance.parent / "AvalonGenesisLogs"
os.makedirs(log_dir, exist_ok=True)

_logger = avk.log.loggingSystem("")
_logger.checkLogs(log_dir)

_parser = avk.parse.MakefileParser(content, instance.parent)
_parser._parse()

if _parser.func:
    for each in args:
        if each in _parser.func:
            _parser.processFunctionCall(each)
