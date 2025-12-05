class StringTool:
    def __init__(self, string:str):
        self.string = string

    def _asm_define_from_string(self):
        match self._asm_strType():
            case "str": return "db"
            case "int": return "dd"
            case "bool": return "db"
            case "float": return "dq"

    def _asm_strType(self):
        if self._is_pure_string():
            return "str"
        elif self._is_int():
            return "int"
        elif self._is_float():
            return "float"
        elif self._is_bool():
            return "bool"
        return "Unknown"

    def _asm_def(self, name):
        raw = self.string.replace("\"", "\\\"")
        db_parts = []
        i = 0
        s = raw
        while i < len(s):
            if s.startswith("\\n", i):
                db_parts.append("0x0A")
                i += 2
                continue
            if s.startswith("\\r", i):
                db_parts.append("0x0D")
                i += 2
                continue
            db_parts.append(f"'{s[i]}'")
            i += 1
        db_parts.append('0')

        db_line = (f"{name} db " + ", ".join(db_parts)).strip(", ")
        return db_line

    def _string_split(self, splits, t=1):
        if t == 1:
            _res = []
            for each in splits:
                _res.append(self.string.split(each))
            
            return _res
        
        elif t == 2:
            _res = {}
            for each in splits:
                _res[each] = self.string.split(each)

            return _res


    def _is_bool(self):
        return self.string.lower() in ("true", "false")

    def _is_int(self):
        try:
            int(self.string)
            return True
        except Exception:
            return False
        
    def _is_float(self):
        if self._is_int():
            return False
        try:
            float(self.string)
            return True
        except Exception:
            return False

    def _is_pure_string(self):
        return (
            (self.string.startswith('"') and self.string.endswith('"')) or
            (self.string.startswith("'") and self.string.endswith("'"))
        )
    
    def _retend(self, endstring=""):
        return self.string + endstring
    
    def _truncate(self,  length, trailings="..."):
        if len(self.string) > length:return self.string[:length] + trailings
        return self.string 
    
    def _language_safe(self):
        return self.string.replace("\"", "\\\"").replace("\'", "\\'")