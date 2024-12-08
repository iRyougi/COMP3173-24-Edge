import csv
import json
import sys

# Grammar rules are defined here in parser.py
# 更新后的语法规则
GRAMMAR = {
    "S'": [['S']],
    'S': [["D'", 'C', '.'], ['C', '.']],
    "D'": [['D', "D'"], ['D']],
    'D': [['let', 'T', 'id', 'be', 'E', '.']],
    'T': [['int'], ['set']],
    'C': [['show', 'A']],
    'A': [['E'], ['P']],
    'E': [["E'"], ['E', 'U', "E'"], ['E', '+', "E'"], ['E', '-', "E'"]],
    "E'": [["E''"], ["E'", 'I', "E''"], ["E'", '*', "E''"]],
    "E''": [['num'], ['id'], ['(', 'E', ')'], ['{', 'Z', 'P', '}']],
    'Z': [['id', ':']],
    'P': [['P', '|', "P'"], ["P'"]],
    "P'": [["P'", '&', "P''"], ["P''"]],
    "P''": [['R'], ['(', 'P', ')'], ['!', 'R']],
    'R': [['E', '<', 'E'], ['E', '>', 'E'], ['E', '=', 'E'], ['E', '@', 'E']],
}


def load_parsing_table(parsing_table_file):
    action_table = {}
    goto_table = {}
    
    with open(parsing_table_file, 'r') as f:
        lines = f.readlines()
        # 获取第一行，确定 'action' 和 'goto' 的列范围
        header_line = lines[0]
        header_fields = [name.strip() for name in header_line.strip().split(',')]
        
        # 找到 'action' 和 'goto' 的列索引
        try:
            action_index = header_fields.index('action')
            goto_index = header_fields.index('goto')
        except ValueError:
            raise ValueError("CSV 文件缺少 'action' 或 'goto' 列标题。")
        
        # 获取第二行，包含终结符和非终结符
        symbol_line = lines[1]
        symbols = [name.strip() for name in symbol_line.strip().split(',')]
        
        # 将第一列设置为 'state'，如果为空的话
        if symbols[0] == '':
            symbols[0] = 'state'
        
        # 确定终结符和非终结符列表
        action_symbols = symbols[action_index : goto_index]
        goto_symbols = symbols[goto_index +1 : ]
        
        # 构建完整的字段名列表
        fieldnames = symbols
        
        # 打印字段名用于调试
        # print("Field names:", fieldnames)
        # print("Action symbols:", action_symbols)
        # print("Goto symbols:", goto_symbols)
        
        # 读取剩余的行作为数据
        data_lines = lines[2:]
        
        # 创建 CSV DictReader
        reader = csv.DictReader(data_lines, fieldnames=fieldnames)
        
        for row in reader:
            # 跳过空行
            state_value = row['state'].strip()
            if not state_value:
                continue
            
            try:
                state = int(state_value)
            except ValueError:
                # print(f"Skipping invalid row with state value: {state_value}")
                continue
            
            # 初始化状态的 ACTION 和 GOTO 表项
            if state not in action_table:
                action_table[state] = {}
            if state not in goto_table:
                goto_table[state] = {}
            
            for key, value in row.items():
                key = key.strip()
                value = value.strip()
                
                if key and value and key != 'state':
                    if key in action_symbols:
                        # ACTION 表条目
                        action_table[state][key] = value
                    elif key in goto_symbols:
                        # GOTO 表条目
                        if value.isdigit():
                            goto_table[state][key] = int(value)
                        else:
                            print("Syntax Error!")
                            with open("syntax_out.json", "w") as json_file:
                                json.dump({}, json_file)
                            sys.exit(0)  # Exit with code 0
        
        # 打印构建的 ACTION 和 GOTO 表用于调试
        # print("Action Table:", action_table)
        # print("Goto Table:", goto_table)
        return action_table, goto_table

class SLRParser:
    def __init__(self, tokens, action_table, goto_table):
        self.tokens = tokens
        self.stack = [0]  # 起始状态
        self.cursor = 0
        self.syntax_tree = []
        self.action_table = action_table
        self.goto_table = goto_table
        self.input = tokens + [{'token': '$', 'lexeme': '$'}]  # 结束标记

        # 使用提供的规则编号和产生式，构建产生式字典
        self.productions = {
            0: ("S'", ['S']),
            1: ('S', ["D'", 'C', '.']),
            2: ('S', ['C', '.']),
            3: ("D'", ['D', "D'"]),
            4: ("D'", ['D']),
            5: ('D', ['let', 'T', 'id', 'be', 'E', '.']),
            6: ('T', ['int']),
            7: ('T', ['set']),
            8: ('E', ["E'"]),
            9: ('E', ['E', 'U', "E'"]),
            10: ('E', ['E', '+', "E'"]),
            11: ('E', ['E', '-', "E'"]),
            12: ("E'", ["E''"]),
            13: ("E'", ["E'", 'I', "E''"]),
            14: ("E'", ["E'", '*', "E''"]),
            15: ("E''", ['num']),
            16: ("E''", ['id']),
            17: ("E''", ['(', 'E', ')']),
            18: ("E''", ['{', 'Z', 'P', '}']),
            19: ('Z', ['id', ':']),
            20: ('P', ['P', '|', "P'"]),
            21: ('P', ["P'"]),
            22: ("P'", ["P'", '&', "P''"]),
            23: ("P'", ["P''"]),
            24: ("P''", ['R']),
            25: ("P''", ['(', 'P', ')']),
            26: ("P''", ['!', 'R']),
            27: ('R', ['E', '<', 'E']),
            28: ('R', ['E', '>', 'E']),
            29: ('R', ['E', '=', 'E']),
            30: ('R', ['E', '@', 'E']),
            31: ('C', ['show', 'A']),
            32: ('A', ['E']),
            33: ('A', ['P']),
        }

    def parse(self):
        syntax_stack = []
        while True:
            state = self.stack[-1]
            current_token = self.input[self.cursor]['token']
            print(f"Current stack: {self.stack}, current token: {current_token}")

            # 查找当前状态和符号的动作
            action = self.action_table.get(state, {}).get(current_token)

            # 打印动作用于调试
            print(f"Action lookup for state {state} and token '{current_token}': {action}")

            if action == 'accept' or action == 'acc':
                print("Accepted!")  # 调试信息
                break

            if action and action.startswith('s'):
                # 移入操作
                next_state = int(action[1:])
                self.stack.append(next_state)
                self.cursor += 1
                # 将终结符作为叶子节点推入语法树栈
                syntax_stack.append({'token': current_token, 'lexeme': self.input[self.cursor - 1]['lexeme']})
                print(f"Shift: Move to state {next_state}, stack now: {self.stack}")
            elif action and action.startswith('r'):
                # 归约操作
                rule_number = int(action[1:])
                if rule_number not in self.productions:
                    raise ValueError(f"Invalid rule number: {rule_number}")
                lhs, rhs = self.productions[rule_number]
                print(f"Reduce: Applying rule {rule_number} ({lhs} -> {' '.join(rhs)})")
                num_to_pop = len(rhs)
                if rhs == ['']:
                    num_to_pop = 0  # 对于空产生式，不弹出栈
                # 从栈中弹出与产生式右部长度相同的状态
                self.stack = self.stack[:-num_to_pop]
                # 从语法树栈中弹出相应数量的节点
                children = syntax_stack[-num_to_pop:] if num_to_pop > 0 else []
                syntax_stack = syntax_stack[:-num_to_pop] if num_to_pop > 0 else syntax_stack
                # children.reverse()
                current_state = self.stack[-1]
                next_state = self.goto_table.get(current_state, {}).get(lhs)
                if next_state is None:
                    raise SyntaxError(f"No goto state for {lhs} after reduction from state {current_state}")
                self.stack.append(next_state)
                # 创建新的父节点并推入语法树栈
                syntax_stack.append({'name': lhs, 'children': children})
                print(f"Reduced: New stack: {self.stack}")
            else:
                # 处理错误
                print("Syntax Error!")
                with open("parser_out.json", "w") as json_file:
                    json.dump({}, json_file)
                sys.exit(0)  # 退出程序

        # 输出语法树到 JSON 文件
        if syntax_stack:
            self.syntax_tree = syntax_stack[-1]  # 使用栈的最后一个元素作为语法树根节点
        else:
            self.syntax_tree = {}
        self.output_json()




    
    def output_json(self):
        with open('parser_out.json', 'w') as f:
            json.dump(self.syntax_tree, f, indent=2)
            print("Syntactic Analysis Complete!")
