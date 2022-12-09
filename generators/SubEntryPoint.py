class SubEntryPoint():

    def __init__(self, instructions) -> None:
        self.__instructions = instructions

    def generate(self):
        print('; Sub Level instructions')
        for label, instr in self.__instructions:
            s = f'\t\t{instr}' if label == None else f'{str(label+":"):<9}\t{instr}'
            print(s)