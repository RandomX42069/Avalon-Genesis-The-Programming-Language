import subprocess, colorama

class AvalonTkinter:
    def __init__(self, dbg=True, signed=True):
        self.tk = "Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.Form; "
        self.dbg = dbg
        self.signed = signed
        self.buttonIndex = 0

    def dprint(self, string):
        print(f"Avalon Tkinter Library(Interpreter): {string}")
    
    def err(self, string):
        print(f"{colorama.Fore.RED}Avalon Genesis Tkinter Library: Error: {string}{colorama.Fore.RESET}")

    def initialize(self, name, size=[300, 200]):
        self.tk += f"$f.Text='{name}'; $f.Size = New-Object System.Drawing.Size({size[0]}, {size[1]}); "

    def antiBloat(self, string):
        if string[0] == "\"" or string[0] == "\'":
            string = string[1:]
        if string[-1] == "\"" or string[-1] == "\'":
            string = string[:-2]
        return string
    
    def addButtonWidget(self, name, btext, position=[0, 0], size=[30, 100]):
        self.tk += f"$b{self.buttonIndex} = New-Object System.Windows.Forms.Button; $b{self.buttonIndex}.Name='{name}'; $b{self.buttonIndex}.Text='{btext}'; $b{self.buttonIndex}.Location= New-Object System.Drawing.Point({position[0]}, {position[1]}); $b0.Size = New-Object System.Drawing.Size({size[0]}, {size[1]}); $f.Controls.Add($b{self.buttonIndex}); "
        self.buttonIndex += 1

    def setButtonStateEnable(self, state=0):
        self.tk += f"$b{self.buttonIndex-1}.Enabled=${"false" if state==0 else "true"}; "

    def run(self):
        self.tk += "$f.ShowDialog()"
        self.dprint(f"Tkinter Command: {self.tk}")
        
        if self.signed:
            subprocess.run(["powershell", "-Command", self.antiBloat(self.tk)], shell=True)
        else:
            self.err("Library is not signed to run")