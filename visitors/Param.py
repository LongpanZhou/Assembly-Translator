import  ast

class Param(ast.NodeVisitor):
    """We supports assignments and input/print calls"""

    def __init__(self) -> None:
        super().__init__()
        self.dict = {}

    ####
    ## handling function calls
    ####

    def visit_Call(self, node):
        functions = ['int','input','print']
        if node.func.id not in functions:
            for n, i in enumerate(node.args):
                self.dict[node.func.id] = [[] for j in range(len(node.args))]
                self.dict[node.func.id][n] = []
                self.dict[node.func.id][n].append(i.id)
        else:
            pass

    def getdic(self):
        return self.dict