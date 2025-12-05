import os, pathlib

def walkDocument():
    for dp, dn, fn in os.walk("./doc"):
        for each in fn:
            ose = os.path.join(dp, each)
            pa = pathlib.Path(ose)
            if pa.suffix in (".txt", ".md"):
                print(f"Avalon Genesis Language Document: {ose}")
                with open(ose, "r") as f:
                    print(f.read())

walkDocument()