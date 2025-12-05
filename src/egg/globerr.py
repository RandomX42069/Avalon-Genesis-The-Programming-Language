import colorama, sys

class AGC_GLOBAL:
    def __init__(self):
        pass

    def err(self, msg, raiseException=True):
        if not raiseException:
            print(f"{colorama.Fore.RED}[ FATAL ]: [ GLOBAL ]: {msg}{colorama.Fore.RESET}")
            sys.exit(1)
        
        raise RuntimeError(f"{colorama.Fore.RED}[ FATAL ]: [ GLOBAL ]: {msg}{colorama.Fore.RESET}")

    def ok(self, msg):
        print(f"{colorama.Fore.GREEN}[ OK ]: {msg}{colorama.Fore.RESET}")