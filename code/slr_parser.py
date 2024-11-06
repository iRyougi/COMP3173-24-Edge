# slr_parser.py

from collections import namedtuple
from parser import ASTNode
from lexer import Token
import csv

Production = namedtuple("Production", ["number", "left", "right"])


class Grammar:
    def __init__(self, productions):
        self.productions = productions  # List of Production

    @staticmethod
    def from_file(file_path):
        productions = []
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # 解析产生式，例如：0. S' -> S
                parts = line.split(".", 1)
                if len(parts) != 2:
                    continue  # 跳过无效行
                number = int(parts[0].strip())
                left_right = parts[1].strip().split("->")
                if len(left_right) != 2:
                    continue  # 跳过无效行
                left = left_right[0].strip()
                right = left_right[1].strip().split()
                productions.append(Production(number, left, right))
        return Grammar(productions)


class Action:
    def __init__(self, action_type, value=None):
        self.action_type = action_type  # 'shift', 'reduce', 'accept'
        self.value = value  # 状态编号或产生式编号


class ParsingTable:
    def __init__(self, action_table, goto_table):
        self.action_table = action_table  # {(state, symbol): Action}
        self.goto_table = goto_table  # {(state, symbol): state}

    @staticmethod
    def from_csv(file_path):
        action_table = {}
        goto_table = {}

        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames

            # 第一列是 'State'，其余是终结符和非终结符
            symbols = headers[1:]

            for row in reader:
                state = int(row["State"])
                for symbol in symbols:
                    entry = row[symbol].strip()
                    if entry:
                        if entry.startswith("s"):
                            action_table[(state, symbol)] = Action(
                                "shift", int(entry[1:])
                            )
                        elif entry.startswith("r"):
                            action_table[(state, symbol)] = Action(
                                "reduce", int(entry[1:])
                            )
                        elif entry == "acc":
                            action_table[(state, symbol)] = Action("accept")
                        else:
                            # GOTO 表项
                            goto_table[(state, symbol)] = int(entry)
        return ParsingTable(action_table, goto_table)


class SLRParser:
    def __init__(self, parsing_table, grammar):
        self.parsing_table = parsing_table
        self.grammar = grammar

    def parse(self, tokens):
        stack = [0]  # 初始状态
        tokens.append(
            Token("EOF", "$", tokens[-1].line, tokens[-1].column)
        )  # 添加结束标记
        index = 0
        ast_stack = []

        while True:
            state = stack[-1]
            current_token = tokens[index]
            symbol = current_token.type
            action = self.parsing_table.action_table.get((state, symbol))

            if action is None:
                raise Exception(
                    f"Syntax error at token {current_token.lexeme} (line {current_token.line})"
                )

            if action.action_type == "shift":
                stack.append(symbol)
                stack.append(action.value)
                index += 1
                ast_stack.append(ASTNode(symbol, value=current_token.lexeme))
            elif action.action_type == "reduce":
                production = self.grammar.productions[action.value]
                rhs_length = len(production.right)
                children = []
                for _ in range(rhs_length):
                    stack.pop()  # 弹出状态
                    symbol = stack.pop()  # 弹出符号
                    node = ast_stack.pop()
                    children.insert(0, node)
                state = stack[-1]
                stack.append(production.left)
                goto_state = self.parsing_table.goto_table.get((state, production.left))
                if goto_state is None:
                    raise Exception(
                        f"GOTO error at state {state} with symbol {production.left}"
                    )
                stack.append(goto_state)
                # 创建非终结符的 AST 节点
                ast_stack.append(ASTNode(production.left, children=children))
            elif action.action_type == "accept":
                print("Parsing successful!")
                # 返回 AST 根节点
                return ast_stack[-1]
