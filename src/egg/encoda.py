def encodeChar(char):
    return ord(char)

def encodeStr(string):
    string = string.strip()
    final = 0
    for char in string:
        final += encodeChar(char)
    return final

def encodeStrReversible(s):
    b = s.encode('utf-8')
    return b

def decodeStrReversible(b):
    return b.decode('utf-8')

def encodeStrToInt(s):
    result = 0
    for c in s:
        result = (result << 16) | ord(c)
    return result

def decodeIntToStr(n):
    chars = []
    while n > 0:
        chars.append(chr(n & 0xFFFF))
        n >>= 16
    return ''.join(reversed(chars))

def encodeFixed8(s: str) -> int:
    b = s.encode("utf-8")
    b = b[:8]  
    b = b.ljust(8, b'\x00') 
    return int.from_bytes(b, "little")

def decodeFixed8(n: int) -> str:
    b = n.to_bytes(8, "little")
    return b.rstrip(b'\x00').decode("utf-8")
