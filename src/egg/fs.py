import os, pathlib, egg.globerr, egg.listery, shutil

class filesystem:
    def __init__(self):
        self.recursiveSteps = 0
        self._glob = egg.globerr.AGC_GLOBAL()
        self._lstool = egg.listery

    def isExistAndFile(self, path):return pathlib.Path(os.path.abspath(path)).is_file()
    def isExistAndDir(self, path):return pathlib.Path(os.path.abspath(path)).is_dir()
    
    def _mode_write(self, mode, files, tdata):
        if not self._lstool.cmpLLen(files, tdata): self._glob.err(f"List length doesn't match: lst1: {len(files)}, lst2: {len(tdata)}")
        for i, each in enumerate(files):
            if mode == "ab":
                self.appendToFile(each, tdata[i])
            elif mode == "wb":
                self.writeToFile(each, tdata[i])

    def rmdir(self, directory):
        shutil.rmtree(directory, True)

    def rmEachDir(self, directories):
        for each in directories:
            self.rmdir(each)

    def createFile(self, filename):
        with open(filename, "w") as f:
            f.write("")

    def createEachFile(self, files):
        for file in files:
            self.createFile(file)

    def mvfile(self, file, newdir):
        if not self.isExistAndFile(file):self._glob.err(f"File doesn't exists: {file}")
        if not self.isExistAndDir(newdir):self._glob.err(f"Dir doesn't exists: {newdir}")
        shutil.move(file, newdir)

    def cpyfile(self, file, newdir):
        if not self.isExistAndFile(file):self._glob.err(f"File doesn't exists: {file}")
        if not self.isExistAndDir(newdir):self._glob.err(f"Dir doesn't exists: {newdir}")
        shutil.copy(file, newdir)

    def filebufferlen(self, filename):
        data = self.readFromFile(filename)
        return self._lstool.ulen(data)
    
    def mfilesbufferlen(self, filesNames:list):
        data = self.readEachFile(filesNames)
        return self._lstool.ulen(data)
    
    def dirbufferlen(self, directory:str):
        if not self.isExistAndDir(directory):self._glob.err(f"Dir doesn't exists: {directory}")
        return self._lstool.ulen(self.dirlist(directory))
    
    def dirlist(self, directory:str):
        if not self.isExistAndDir(directory):self._glob.err(f"Dir doesn't exists: {directory}")
        full = []
        for dp, dn, fn in os.walk(directory):
            for each in dn:
                full.append(each)
            for f in fn:
                full.append(f)
        
        return full

    def appendToFile(self, filename, content):
        if not self.isExistAndFile(filename):self._glob.err(f"File doesn't exists: {filename}")
        if not isinstance(content, bytes):content = content.encode("utf-8")
        with open(filename, "ab") as f:f.write(content)
    
    def appendEachFile(self, files:list, tdata:list):
        self._mode_write("ab", files, tdata)

    def writeToFile(self, filename, content):
        if not self.isExistAndFile(filename):self._glob.err(f"File doesn't exists: {filename}")
        if not isinstance(content, bytes):content = content.encode("utf-8")
        with open(filename, "wb") as f:f.write(content)

    def writeEachFile(self, files:list, tdata:list):
        self._mode_write("wb", files, tdata)

    def readFromFile(self, filename):
        if not self.isExistAndFile(filename):self._glob.err(f"File doesn't exists: {filename}") 
        with open(filename, "rb") as f:data = f.read()
        return data
    
    def readEachFile(self, files:list):
        mdata = []
        for each in files:
            data = self.readFromFile(each)
            mdata.append(data)
    
        return mdata

    def recursiveFind(self, reserve=2, fileName=None):
        target = pathlib.Path(fileName)
        reserved = []

        while self.recursiveSteps <= reserve:
            if self.recursiveSteps == 0:
                expanded = target
            else:
                expanded = pathlib.Path("../" * self.recursiveSteps) / target
            reserved.append(expanded)

            if expanded.is_file():
                self.recursiveSteps = 0
                return expanded

            self.recursiveSteps += 1

        self.recursiveSteps = 0
        self._glob.err(f"Reserved file paths don't exist: {reserved}")