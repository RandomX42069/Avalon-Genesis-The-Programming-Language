import egg.fs
import os

_fs = egg.fs.filesystem()

def __glue__(filenames: list[str]) -> str:
    parts = []
    script_dir = os.path.dirname(os.path.abspath(__file__))  # folder containing your glue script
    for fp in filenames:
        abs_fp = os.path.join(script_dir, fp)  # join with script dir
        if _fs.isExistAndFile(abs_fp):
            content = _fs.readFromFile(abs_fp).decode("utf-8", errors="replace")
            parts.append(f"# src file: {abs_fp}\n{content}")
            
    return "\n\n".join(parts)


def __glue__package__(filenames, output="bundled.py"):
    _fs.createFile(output)
    data = __glue__(filenames)
    out_dir = os.path.dirname(os.path.abspath(output))
    if out_dir and not _fs.isExistAndDir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    _fs.writeToFile(output, data.encode("utf-8"))