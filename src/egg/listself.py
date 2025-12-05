import os, pathlib

def walk(directory):
    for dp, dn, fn in os.walk(directory):
        for f in fn:
            full = os.path.join(dp, f)
            _instance = pathlib.Path(full)
            if _instance.suffix == ".py":
                print(f"Py file: {full}")
                with open(full, "r") as f:
                    print(f.read())

walk("./src/egg")