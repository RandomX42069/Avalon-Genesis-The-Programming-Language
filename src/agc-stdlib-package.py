import egg.glue as glue
import os, pathlib

print(os.listdir(os.path.join(pathlib.Path(__file__).parent, "egg")))
print(os.path.join(pathlib.Path(__file__).parent, "egg"))
glue.__glue__package__(os.listdir(os.path.join(pathlib.Path(__file__).parent, "egg")))