import csv
from semantic import SemanticAnalyzer

# 定义 Token 类型
class Token:
    def __init__(self, token, lexeme=None):
        self.token = token
        self.lexeme = lexeme

    def __repr__(self):
        return f"Token({self.token}, {self.lexeme})"


# 语法树节点类
class TreeNode:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children if children else []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"TreeNode({self.node_type}, {self.value}, {self.children})"


# 解析器类
class SLRParser:
    def __init__(self, slr_table_file):
        self.slr_table = self.load_slr_table(slr_table_file)
        self.stack = [0]  # 初始栈，包含起始状态
        self.input_tokens = []  # 记录输入的 token
        self.syntax_tree = TreeNode("root")  # 创建语法树的根节点
        self.current_token_index = 0  # 当前输入 token 的索引
        self.semantic_analyzer = SemanticAnalyzer()  # 语义分析器

    # 读取 SLR 解析表
    def load_slr_table(self, file_path):
        slr_table = {}
        slr_symbols = ['.', 'let', 'id', 'be', 'int', 'set', 'U', '+', '-', 'I', '*', 'num', '(', ')', '{', '}', ':',
                       '|', '&', '!', '<', '>', '=', '@', 'show', '$', 'S\'', 'S', 'D\'', 'D', 'T', 'E', 'E\'', 'E\'\'',
                       'Z', 'P', 'P\'', 'P\'\'', 'R', 'C', 'A']  # 确保符号列表的顺序和数量
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header
            for row in reader:
                state = row[0].strip()  # First column is state
                if state:  # Only process rows that have a state
                    state = int(state)  # Convert to int
                    if state not in slr_table:  # Initialize the state dictionary if needed
                        slr_table[state] = {}
                    # Check the length of the row against slr_symbols
                    for i, symbol in enumerate(row[1:]):
                        if i >= len(slr_symbols):  # Check if i exceeds the length of slr_symbols
                            break  # Skip processing if there are too many columns
                        symbol = symbol.strip()
                        if symbol:  # Only process non-empty symbols
                            slr_table[state][slr_symbols[i]] = symbol
        return slr_table

    # 根据输入 token 进行解析
    def parse(self, tokens):
        self.input_tokens = tokens
        lookahead_token = '$'  # 用 '$' 表示输入结束
        while True:
            # 获取栈顶状态
            top_state = self.stack[-1]
            current_token = self.input_tokens[self.current_token_index].token if self.current_token_index < len(
                self.input_tokens) else lookahead_token

            # 查找解析表，获取当前操作
            action = self.slr_table.get(int(top_state), {}).get(current_token, None)
            if action is None:
                raise ValueError(f"Parsing error at state {top_state}, symbol {current_token}")

            if action.startswith('s'):  # 移进操作
                next_state = int(action[1:])  # 获取移进后的状态
                self.stack.append(next_state)  # 推入新的状态
                self.syntax_tree.add_child(
                    TreeNode('terminal', self.input_tokens[self.current_token_index].lexeme))  # 添加语法树的叶子节点
                self.current_token_index += 1  # 移动到下一个 token

            elif action.startswith('r'):  # 规约操作
                production_index = int(action[1:])  # 获取规约产生式索引
                self.reduce(production_index)

            elif action == 'acc':  # 接受操作
                print("Parsing complete!")
                break

            else:
                raise ValueError(f"Parsing error at state {top_state}, symbol {current_token}")

    def get_production(self,production_index):
        return {
            0: {'left': "S'", 'right': ['S']},
            1: {'left': 'S', 'right': ['D\'', 'C']},
            2: {'left': 'S', 'right': ['C']},
            3: {'left': 'D\'', 'right': ['D', 'D\'']},
            4: {'left': 'D\'', 'right': ['D']},
            5: {'left': 'D', 'right': ['let', 'T', 'id', 'be', 'E']},
            6: {'left': 'T', 'right': ['int']},
            7: {'left': 'T', 'right': ['set']},
            8: {'left': 'E', 'right': ['E\'']},
            9: {'left': 'E', 'right': ['E', 'U', 'E\'']},
            10: {'left': 'E', 'right': ['E', '+', 'E\'']},
            11: {'left': 'E', 'right': ['E', '-', 'E\'']},
            12: {'left': 'E\'', 'right': ['E\'\'']},
            13: {'left': 'E\'', 'right': ['E\'', 'I', 'E\'\'']},
            14: {'left': 'E\'', 'right': ['E\'', '*', 'E\'\'']},
            15: {'left': 'E\'\'', 'right': ['num']},
            16: {'left': 'E\'\'', 'right': ['id']},
            17: {'left': 'E\'\'', 'right': ['(', 'E', ')']},
            18: {'left': 'E\'\'', 'right': ['{', 'Z', 'P', '}']},
            19: {'left': 'Z', 'right': ['id', ':']},
            20: {'left': 'P', 'right': ['P', '|', 'P\'']},
            21: {'left': 'P', 'right': ['P\'']},
            22: {'left': 'P\'', 'right': ['P\'', '&', 'P\'\'']},
            23: {'left': 'P\'', 'right': ['P\'\'']},
            24: {'left': 'P\'\'', 'right': ['R']},
            25: {'left': 'P\'\'', 'right': ['(', 'P', ')']},
            26: {'left': 'P\'\'', 'right': ['!', 'R']},
            27: {'left': 'R', 'right': ['E', '<', 'E']},
            28: {'left': 'R', 'right': ['E', '>', 'E']},
            29: {'left': 'R', 'right': ['E', '=', 'E']},
            30: {'left': 'R', 'right': ['E', '@', 'E']},
            31: {'left': 'C', 'right': ['show', 'A']},
            32: {'left': 'A', 'right': ['E']},
            33: {'left': 'A', 'right': ['P']},
        }

    def reduce(self, production_index):
        # 获取产生式
        production = self.get_production(production_index)

        # 确保 production 中有 'left' 和 'right' 键
        if 'left' not in production or 'right' not in production:
            return

        # 执行规约操作：根据生产式更新栈
        production_length = len(production['right'])
        for _ in range(production_length):
            self.stack.pop()

        left_symbol = production['left']
        goto_state = self.slr_table.get(int(self.stack[-1]), {}).get('goto', {}).get(left_symbol, 0)
        self.stack.append(goto_state)

        # 创建新的语法树节点，非终结符
        new_node = TreeNode('non-terminal', f"{production['left']} -> {' '.join(production['right'])}")
        self.syntax_tree.add_child(new_node)

        # 调用语义分析器处理当前规约
        self.semantic_analyzer.analyze_semantics(new_node)

    def save_syntax_tree(self, file_path):
        import json
        tree = self.syntax_tree
        stack = [(tree, [])]
        syntax_tree_json = []
        while stack:
            node, path = stack.pop()
            node_dict = {
                'node_type': node.node_type,
                'value': node.value,
                'children': []
            }
            path.append(node_dict)
            if node.children:
                for child in node.children:
                    stack.append((child, [node_dict]))
            else:
                syntax_tree_json.append(node_dict)
        with open(file_path, 'w') as f:
            json.dump(syntax_tree_json, f, indent=4)
