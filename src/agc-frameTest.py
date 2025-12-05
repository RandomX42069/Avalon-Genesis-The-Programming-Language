from AAst.stackframe import *

srcCode = """
@ignore-exists True

@file "newfile.txt", "wc"
print("hi")
@efile

@new-dir "newdir"
@mv-file "newfile.txt", "./newdir"
"""
margin = MarginFilesystemParser(srcCode, "Unknown", ["--dbg"])
margin.parseArgs()
margin.parse()