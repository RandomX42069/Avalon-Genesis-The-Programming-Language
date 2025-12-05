x64_linux = ["--fx86_64-linux", "--wslld", "--clo", "--cloa"]

class process_arg:
    def __init__(self, args:list):
        self.args = args

    def foreach(self):
        for each in self.args:
            if each == "--x64-linux":
                self.args.pop(self.args.index("--x64-linux"))
                self.args.extend(x64_linux)