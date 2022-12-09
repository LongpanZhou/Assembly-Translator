import ast

class StaticMemoryAllocation():

    def __init__(self, global_vars: dict()) -> None:
        self.__global_vars = global_vars

    def generate(self):
        print('; Allocating Global (static) memory')
        for n in self.__global_vars:
            # determine what type of variable it is
            # if it is constant
            if (n[0] == "_") and (n.isupper()) and (self.__global_vars[n][0] == "<class 'ast.Constant'>"):
                print(f'{str(n+":"):<9}\t.EQUATE', self.__global_vars[n][1]) # reserving memory
            
            # if it is known integer
            elif (n.isupper() == False) and (self.__global_vars[n][0] == "<class 'ast.Constant'>"):
                print(f'{str(n+":"):<9}\t.WORD', self.__global_vars[n][1]) # reserving memory

            # if it is a BinOp
            elif self.__global_vars[n][0] == "<class 'ast.BinOp'>":
                if type(self.__global_vars[n][1]) is ast.Name:
                    print(f'{str(n+":"):<9}\t.BLOCK 2') # reserving memory
                else:
                    print(f'{str(n + ":"):<9}\t.BLOCK {2 * self.__global_vars[n][1]}')  # reserving memory

            # else for now
            else:
                print(f'{str(n+":"):<9}\t.BLOCK 2') # reserving memory