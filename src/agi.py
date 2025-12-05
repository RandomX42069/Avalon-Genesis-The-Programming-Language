import sys, egg.fs, egg.globerr, interpreter.inter

args = sys.argv[1:]
if not args:
    sys.exit(0)

_egg_fs = egg.fs.filesystem()
_egg_globerr = egg.globerr.AGC_GLOBAL()

if "-i" not in args:
    _egg_globerr.err("Missing required flag: -i")

i_index = args.index("-i")

if i_index + 1 >= len(args):
    _egg_globerr.err("Flag '-i' requires a filename argument")

agcfile = args[i_index + 1]


if not _egg_fs.isExistAndFile(agcfile):
    _egg_globerr.err(f"File does not exist: {agcfile}")

with open(agcfile, "r") as f:
    content = f.read()

_interpreter = interpreter.inter.Interpreter(
    content,
    args,
    agcfile
)

_interpreter.parse()