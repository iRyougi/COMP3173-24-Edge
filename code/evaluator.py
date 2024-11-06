# evaluator.py

class Evaluator:
    def __init__(self, ast, symbol_table):
        self.ast = ast
        self.symbol_table = symbol_table

    def evaluate(self):
        self.visit(self.ast)

    def visit(self, node):
        method_name = 'visit_' + node.type
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        pass

    def visit_Program(self, node):
        for stmt in node.children:
            self.visit(stmt)

    def visit_ShowStatement(self, node):
        expr = node.children[0]
        value = self.visit(expr)
        print("Result:", value)
        self.result = value  # 保存结果

    def visit_Identifier(self, node):
        var_name = node.value
        # 这里暂时返回一个占位值
        return 0

    def visit_Number(self, node):
        return int(node.value)
