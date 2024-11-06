# slr_parser.py
from lexer import Lexer

class Action:
    def __init__(self, action_type, value=None):
        self.action_type = action_type  # 'shift', 'reduce', 'accept'
        self.value = value              # 状态编号或产生式编号

class ParsingTable:
    def __init__(self, action_table, goto_table):
        self.action_table = action_table  # {(state, terminal): Action}
        self.goto_table = goto_table      # {(state, non_terminal): state}

class SLRParser:
    def __init__(self, parsing_table, grammar):
        self.parsing_table = parsing_table
        self.grammar = grammar  # 包含产生式列表

    def parse(self, tokens):
        stack = [0]  # 初始状态为 0
        tokens.append(Token('EOF', '$', tokens[-1].line, tokens[-1].column))  # 加入结束标记
        index = 0

        while True:
            state = stack[-1]
            current_token = tokens[index]
            action = self.parsing_table.action_table.get((state, current_token.type))

            if action is None:
                raise Exception(f"Syntax error at token {current_token.lexeme} (line {current_token.line})")

            if action.action_type == 'shift':
                stack.append(current_token)
                stack.append(action.value)  # 下一个状态
                index += 1
            elif action.action_type == 'reduce':
                production = self.grammar.productions[action.value]
                rhs_length = len(production.right) * 2  # 每个符号有一个状态和一个符号
                stack = stack[:-rhs_length]
                state = stack[-1]
                stack.append(production.left)
                goto_state = self.parsing_table.goto_table.get((state, production.left))
                if goto_state is None:
                    raise Exception(f"GOTO error at state {state} with symbol {production.left}")
                stack.append(goto_state)
            elif action.action_type == 'accept':
                print("Parsing successful!")
                return  # 或者返回语法树
