import compiler.AGC, AAst.main, args_handler.args, egg.fs, egg.globerr, egg.listery
import sys

args = sys.argv[1:]
if not args:
    sys.exit(0)

for arg in args:
    if arg in ("--help", "-h", "-help", "--h"):
        print("""
Avalon Genesis Compiler(AGC) v0.2 By RandomX
Help commands:
    All-in-one(AIO):
        arg: --x64-linux
        description: 
            normal x64 linux compilation
            expands to: --fx86_64-linux --wslld --clo --cloa

    Debug:
        arg: --debug
        description: normal debug
        
        arg: --dbg,val
        description: debug values      

    abi:
        arg: --fx86_64-linux
        description: x86_64-linux assembly output

    WSL-related:
        arg: --wslld
        description: use WSL's ld
    
    after-output:
        arg: -clo
        description: clear object output
              
        arg: -cloa
        description: clear assembly output
              
    help:
        show all the arguments in help and help makes agc exits without any compilation
""")
        sys.exit(0)

_egg_fs = egg.fs.filesystem()
_egg_globerr = egg.globerr.AGC_GLOBAL()

_instance_arg = args_handler.args.process_arg(args)
_instance_arg.foreach()
_pointer = _instance_arg.args

getval = lambda lst, flag: egg.listery.get_flag_value(lst, flag)

content = ""

agcfile = getval(_pointer, "-c")

if agcfile is None:
    _egg_globerr.err("No input file provided with -c")

elif not _egg_fs.isExistAndFile(agcfile):
    _egg_globerr.err(f"Input file doesn't exist: {agcfile}")

else:
    with open(agcfile, "r") as f:
        content = f.read()

outputfile = getval(_pointer, "-o")

if outputfile is None:
    _egg_globerr.err("No output file provided with -o")

elif _egg_fs.isExistAndFile(outputfile):
    _egg_globerr.err(f"Output file already exists: {outputfile}")

print("Avalon Genesis Compiler(AGC) v0.2 By RandomX")
print(f"Selected Options: {' '.join(_pointer) if len(_pointer) >= 1 else '(Empty)'}")

parser = AAst.main.Parser(content, args=_pointer, srcFile=agcfile)
parser.parseArgs()
ast_nodes = parser.parse()

compiler_instance = None

if outputfile:
    compiler_instance = compiler.AGC.Compiler(
        ast_nodes,
        outputfile,
        agcfile,
        0,
        parser.document,
        _pointer,
        parser.signed
    )

    compiler_instance.pipeline()
else:
    compiler_instance = compiler.AGC.Compiler(
        ast_nodes,
        agcfile,
        0,
        parser.document,
        _pointer,
        parser.signed
    )

    compiler_instance.pipeline()