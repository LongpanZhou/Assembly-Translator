class DynamicMemoryAllocation():

    def __init__(self, local_vars: dict()) -> None:
        self.__local_vars = local_vars

    def generate(self):
        print('; Allocating Local memory')
        for i,n in enumerate(self.__local_vars):
            print(f'{str(n + ":"):<9}\t.EQUATE', 2*i)  # reserving memory
    
    def get(self):
        return len(self.__local_vars)