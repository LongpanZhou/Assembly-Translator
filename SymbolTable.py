class SymbolTable():

    def __init__(self) -> None:

        self.all_vnames = dict()
    
    def translate(self, vname):
        if vname not in self.all_vnames:
            if vname[0] == "_" and vname.isupper():
                self.all_vnames[vname] = "_CNST" + str(len(self.all_vnames))
            else:
                self.all_vnames[vname] = "var" + str(len(self.all_vnames))
        return self.all_vnames[vname]