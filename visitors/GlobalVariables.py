import ast
from SymbolTable import SymbolTable

class GlobalVariableExtraction(ast.NodeVisitor):
    """ 
        We extract all the left hand side of the global (top-level) assignments
    """
    
    def __init__(self) -> None:
        super().__init__()
        #self.results = set()

        # make a dictionary for global variables 
        self.results = dict()
        self.symboltable = SymbolTable()

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise ValueError("Only unary assignments are supported")

        variable_name = node.targets[0].id

        if len(variable_name) > 8:
            new_var = self.symboltable.translate(variable_name)
            variable_name = new_var

        #self.results.add(node.targets[0].id)
        if variable_name not in self.results:

            # for now check if the type is of type Constant
            if type(node.value) is ast.Constant:
                self.results[variable_name] = [str(type(node.value)), node.value.value] # save the value of the costant
            # check if it is list contains BinOp
            elif type(node.value) is ast.BinOp:
                if type(node.value.right) is ast.Name:
                    self.results[variable_name] = [str(type(node.value)), node.value.right]
                else:
                    self.results[variable_name] = [str(type(node.value)), node.value.right.value]
            elif type(node.value) is ast.Subscript:
                pass
            # for now just show type of value and the object
            else:
                self.results[variable_name] = [str(type(node.value)), node.value]

        # we can access node.targets for the variable name
        # we can also access node.value for information on what type of variable it is and its value

    def visit_FunctionDef(self, node):
        """We do not visit function definitions, they are not global by definition"""
        pass
