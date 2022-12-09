import ast

LabeledInstruction = tuple[str, str]


class SubLevelProgram(ast.NodeVisitor):
    """We supports assignments and input/print calls"""

    def __init__(self, n, params, entry_point) -> None:
        super().__init__()
        self.__instructions = list()
        self.__record_instruction('NOP1', label=entry_point)
        self.n = n
        self.__instructions.append((None, f'SUBSP {2*self.n},i'))
        self.__should_save = True
        self.__current_variable = None
        self.__elem_id = 0
        for _ in params:
            self.__instructions.append((None, f'LDWA {_[0]},d'))
            self.__instructions.append((None, f'STWA {_[1]},s'))

    def finalize(self):
        self.__instructions.append((None, f'ADDSP {2*self.n},i'))
        self.__instructions.append((None, 'RET'))
        return self.__instructions

    ####
    ## Handling returning
    ####

    def visit_Return(self, node):
        self.__current_variable = node.value.id
        self.__record_instruction(f'LDWA {self.__current_variable},s')
        self.__record_instruction(f'STWA retval,s')

    ####
    ## Handling Assignments (variable = ...)
    ####

    def visit_Assign(self, node):
        # remembering the name of the target
        self.__current_variable = node.targets[0].id
        # visiting the left part, now knowing where to store the result
        self.visit(node.value)
        if self.__should_save:
            self.__record_instruction(f'STWA {self.__current_variable},s')
        else:
            self.__should_save = True
        self.__current_variable = None

    def visit_Constant(self, node):
        self.__record_instruction(f'LDWA {node.value},i')

    def visit_Name(self, node):
        self.__record_instruction(f'LDWA {node.id},s')

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Mult):
            return
        self.__access_memory(node.left, 'LDWA')
        if isinstance(node.op, ast.Add):
            self.__access_memory(node.right, 'ADDA')
        elif isinstance(node.op, ast.Sub):
            self.__access_memory(node.right, 'SUBA')
        else:
            raise ValueError(f'Unsupported binary operator: {node.op}')

    def visit_Call(self, node):
        match node.func.id:
            case 'int':
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case 'input':
                # We are only supporting integers for now
                self.__record_instruction(f'DECI {self.__current_variable},s')
                self.__should_save = False  # DECI already save the value in memory
            case 'print':
                # We are only supporting integers for now
                self.__record_instruction(f'DECO {node.args[0].id},s')
            case _:
                self.__record_instruction(f'CALL {node.func.id}')

    ####
    ## Handling While loops (only variable OP variable)
    ####

    def visit_While(self, node):
        loop_id = self.__identify()
        inverted = {
            ast.Lt: 'BRGE',  # '<'  in the code means we branch if '>='
            ast.LtE: 'BRGT',  # '<=' in the code means we branch if '>'
            ast.Gt: 'BRLE',  # '>'  in the code means we branch if '<='
            ast.GtE: 'BRLT',  # '>=' in the code means we branch if '<'
            ast.NotEq: 'BREQ',  # '!=' in the code means we branch if '='
            ast.Eq: 'BRNEQ',  # '==' in the code means we branch if '!='
        }
        # left part can only be a variable
        self.__access_memory(node.test.left, 'LDWA', label=f'test_{loop_id}')
        # right part can only be a variable
        self.__access_memory(node.test.comparators[0], 'CPWA')
        # Branching is condition is not true (thus, inverted)
        self.__record_instruction(f'{inverted[type(node.test.ops[0])]} end_l_{loop_id}')
        # Visiting the body of the loop
        for contents in node.body:
            self.visit(contents)
        self.__record_instruction(f'BR test_{loop_id}')
        # Sentinel marker for the end of the loop
        self.__record_instruction(f'NOP1', label=f'end_l_{loop_id}')

    ####
    ## Not handling function calls
    ####

    def visit_FunctionDef(self, node):
        """We do not visit function definitions, they are not top level"""
        pass

    ####
    ## Handling if statements
    ####

    def visit_If(self, node):
        condition_id = self.__identify()
        op = {
            ast.Lt: 'BRLT',
            ast.LtE: 'BRLE',
            ast.Gt: 'BRGT',
            ast.GtE: 'BRGE',
            ast.NotEq: 'BRNEQ',
            ast.Eq: 'BREQ',
        }
        # left part can only be a variable
        self.__access_memory(node.test.left, 'LDWA', label=f'if_{condition_id}')
        # right part can only be a variable
        self.__access_memory(node.test.comparators[0], 'CPWA')
        # Branching is condition is not true (thus, inverted)
        self.__record_instruction(f'{op[type(node.test.ops[0])]} con_{condition_id}')
        # Visiting or else of the loop
        for contents in node.orelse:
            self.visit(contents)
        self.__record_instruction(f'BR end_{condition_id}')
        # Visiting the body of the loop
        self.__record_instruction(f'NOP1', label=f'con_{condition_id}')
        for contents in node.body:
            self.visit(contents)
        self.__record_instruction(f'NOP1', label=f'end_{condition_id}')

    ####
    ## Helper functions to
    ####

    def __record_instruction(self, instruction, label=None):
        self.__instructions.append((label, instruction))

    def __access_memory(self, node, instruction, label=None):
        if isinstance(node, ast.Constant):
            self.__record_instruction(f'{instruction} {node.value},i', label)
        elif instruction == "ADDA":
            self.__record_instruction(f'{instruction} {node.id},i', label)
        else:
            self.__record_instruction(f'{instruction} {node.id},s', label)

    def __identify(self):
        result = self.__elem_id
        self.__elem_id = self.__elem_id + 1
        return result