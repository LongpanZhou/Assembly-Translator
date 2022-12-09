import ast
from visitors.SubLevelProgram import SubLevelProgram
from generators.SubEntryPoint import SubEntryPoint
from generators.DynamicMemoryAllocation import DynamicMemoryAllocation
from visitors.LocalVariables import LocalVariableExtraction

LabeledInstruction = tuple[str, str]


class FunctionCall(ast.NodeVisitor):
    """We supports assignments and input/print calls"""

    def __init__(self, dic) -> None:
        super().__init__()
        self.dict = dic

    ####
    ## handling function calls
    ####

    def visit_FunctionDef(self, node):
        """We do not visit function definitions, they are not top level"""
        extractor = LocalVariableExtraction()
        extractor.visit(node)
        memory_alloc = DynamicMemoryAllocation(extractor.results)
        memory_alloc.generate()
        num = memory_alloc.get()
        for n,i in enumerate(node.args.args):
            self.dict[node.name][n].append(i.arg)
        try: f = SubLevelProgram(num, self.dict[node.name], node.name)
        except: f = SubLevelProgram(num, {}, node.name)
        for contents in node.body:
            f.visit(contents)
        fg = SubEntryPoint(f.finalize())
        fg.generate()