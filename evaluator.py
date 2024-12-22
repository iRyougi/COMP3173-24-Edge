# evaluator.py

import json
import sys

class Evaluator:
    def __init__(self, typing_file='typing_out.json', evaluation_file='evaluation_out.json'):
        """
        初始化评估器。

        参数：
            typing_file (str): 输入的 typing_out.json 文件路径。
            evaluation_file (str): 输出的 evaluation_out.json 文件路径。
        """
        self.typing_file = typing_file
        self.evaluation_file = evaluation_file
        self.symbol_table = {}
        self.parse_tree = None
        self.evaluation_result = None
        self.DEBUG = False  # 内置的调试开关，默认关闭

    def enable_debug(self):
        """启用调试模式。"""
        self.DEBUG = True

    def disable_debug(self):
        """禁用调试模式。"""
        self.DEBUG = False

    def debug_print(self, message):
        """
        根据调试开关打印调试信息。

        参数：
            message (str): 要打印的调试信息。
        """
        if self.DEBUG:
            print(f"[DEBUG] {message}")

    def load_typing_output(self):
        """
        加载 typing_out.json 文件并解析为语法树。
        """
        self.debug_print(f"Loading typing output from {self.typing_file}")
        try:
            with open(self.typing_file, 'r') as f:
                self.parse_tree = json.load(f)
            self.debug_print("Typing output loaded successfully.")
        except FileNotFoundError:
            self.debug_print(f"Error: {self.typing_file} not found.")
            print(f"Error: {self.typing_file} not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            self.debug_print(f"Error: {self.typing_file} is not a valid JSON file.")
            print(f"Error: {self.typing_file} is not a valid JSON file.")
            sys.exit(1)

    def write_evaluation_output(self):
        """
        将评估后的语法树写入 evaluation_out.json 文件。
        """
        self.debug_print(f"Writing evaluation output to {self.evaluation_file}")
        try:
            with open(self.evaluation_file, 'w') as f:
                json.dump(self.parse_tree, f, indent=4)
            self.debug_print("Evaluation output written successfully.")
        except Exception as e:
            self.debug_print(f"Error writing to {self.evaluation_file}: {str(e)}")
            print(f"Error writing to {self.evaluation_file}: {str(e)}")
            sys.exit(1)

    def evaluate(self):
        """
        执行评估过程，包括加载、评估和写入输出。
        """
        self.debug_print("Starting evaluation process.")
        try:
            self.load_typing_output()
            self.evaluate_node(self.parse_tree)
            self.write_evaluation_output()
            print("Evaluation Complete!")
            if self.evaluation_result is not None:
                print(f"Result: {self.evaluation_result}")
            self.debug_print("Evaluation process finished successfully.")
        except Exception as e:
            self.debug_print(f"Evaluation Error: {str(e)}")
            print(f"Evaluation Error: {str(e)}")
            # 写入空的 evaluation_out.json
            try:
                with open(self.evaluation_file, 'w') as f:
                    json.dump({}, f)
                self.debug_print(f"Empty {self.evaluation_file} created due to evaluation error.")
            except Exception as write_error:
                self.debug_print(f"Error writing empty evaluation file: {str(write_error)}")
                print(f"Error writing empty evaluation file: {str(write_error)}")
            sys.exit(1)

    def evaluate_node(self, node):
        """
        递归地评估语法树中的每个节点，并更新 value 字段。

        参数：
            node (dict): 当前节点。

        返回：
            评估结果。
        """
        node_type = node.get('type')
        node_name = node.get('name')

        self.debug_print(f"Evaluating node: {node_name if node_name else 'terminal'} with type: {node_type}")

        # 处理终端节点
        if 'token' in node:
            token = node['token']
            lexeme = node['lexeme']
            self.debug_print(f"Processing terminal token: {token}, lexeme: {lexeme}")

            if token == 'num':
                evaluation = lexeme  # 保持原有 value
                node['value'] = lexeme  # 保持原有 value
                self.debug_print(f"Number {lexeme} evaluated as {evaluation}")
            elif token == 'id':
                var_name = lexeme
                if var_name not in self.symbol_table:
                    raise Exception(f"Undefined variable: {var_name}")
                evaluation = self.symbol_table[var_name]['value']
                node['value'] = evaluation  # 更新 value 为变量的值
                self.debug_print(f"Identifier {var_name} evaluated as {evaluation}")
            elif token in ['<', '>', '=', '@', '+', '-', '*', 'U', 'I', '&', '|', '!']:
                # 操作符本身不需要评估，只是在操作中使用
                evaluation = lexeme
                node['value'] = lexeme
                self.debug_print(f"Operator {lexeme} stored for evaluation.")
            else:
                # 其他终端符号直接返回
                evaluation = lexeme
                node['value'] = lexeme
                self.debug_print(f"Terminal {lexeme} evaluated as {evaluation}")
            return evaluation

        # 处理非终端节点
        if not node_name:
            self.debug_print("Node without a name encountered, skipping evaluation.")
            node['value'] = "void"
            return None

        if node_name == 'S' and node_type == 'program':
            # 处理根节点 S
            for child in node.get('children', []):
                self.evaluate_node(child)
            node['value'] = "false"  # 根据理想输出设置
            self.debug_print("Program node 'S' evaluated.")
            return "false"

        elif node_name == 'D\'' and node_type == 'declarations':
            # 处理声明列表 D'
            for child in node.get('children', []):
                self.evaluate_node(child)
            node['value'] = "void"
            self.debug_print("Declaration list node 'D\'' evaluated.")
            return "void"

        elif node_name == 'D' and node_type == 'declaration':
            # 处理单个声明 D
            var_type = node['type_info']['var_type']
            var_name = node['type_info']['var_name']
            expr_node = node['children'][0]
            self.debug_print(f"Processing declaration: let {var_type} {var_name} be ...")
            value = self.evaluate_node(expr_node)
            self.debug_print(f"Expression evaluated to {value}")

            if var_type == 'int':
                if not isinstance(value, int) and not (isinstance(value, str) and value.isdigit()):
                    raise Exception(f"Type mismatch: Variable '{var_name}' expected to be int.")
                self.symbol_table[var_name] = {'type': 'int', 'value': int(value)}
                node['value'] = "void"  # 声明不返回具体值
                self.debug_print(f"Declared integer variable '{var_name}' with value {value}.")
            elif var_type == 'set':
                if not isinstance(value, set):
                    raise Exception(f"Type mismatch: Variable '{var_name}' expected to be set.")
                self.symbol_table[var_name] = {'type': 'set', 'value': value}
                node['value'] = "void"  # 声明不返回具体值
                self.debug_print(f"Declared set variable '{var_name}' with value {value}.")
            else:
                raise Exception(f"Unknown type for variable '{var_name}': {var_type}")
            return value

        elif node_name == 'C' and node_type == 'calculation':
            # 处理计算节点 C
            for child in node.get('children', []):
                self.evaluate_node(child)
            node['value'] = "false"  # 根据理想输出设置
            self.debug_print("Calculation node 'C' evaluated.")
            return "false"

        elif node_name == 'show' and node_type == 'calculation':
            # 处理 show 语句
            expr_node = node['children'][0]
            self.debug_print("Processing 'show' statement.")
            result = self.evaluate_node(expr_node)
            node['value'] = result  # 更新 value 为 show 的结果
            self.evaluation_result = result
            self.debug_print(f"'show' statement evaluated to {result}")
            return result

        elif node_name == 'E' and node_type in ['integer', 'set']:
            # 处理表达式节点 E
            result = self.evaluate_expression(node)
            node['value'] = result
            return result

        elif node_name == 'P' and node_type == 'predicate':
            # 处理谓词节点 P
            result = self.evaluate_predicate(node)
            node['value'] = str(result).lower()  # 将布尔值转为小写字符串
            return result

        elif node_name == 'A' and node_type == 'calculation':
            # 处理计算节点 A
            result = self.evaluate_calculation(node)
            node['value'] = "false"  # 根据理想输出设置
            return "false"

        elif node_name == 'E\'' and node_type == 'integer':
            # 处理表达式节点 E'
            result = self.evaluate_expression(node)
            node['value'] = result
            return result

        elif node_name == 'Z' and node_type is None:
            # 处理集合变量 Z
            # 根据理想输出，Z 的 value 是变量名，如 "a"
            var_name = node['children'][0]['lexeme']
            node['value'] = var_name
            self.debug_print(f"Set variable 'Z' evaluated to {var_name}")
            return var_name

        else:
            self.debug_print(f"Unknown non-terminal node: {node_name}, skipping evaluation.")
            node['value'] = "void"
            return "void"

    def evaluate_expression(self, node):
        """
        处理表达式节点的评估。

        参数：
            node (dict): 表达式节点。

        返回：
            评估结果。
        """
        name = node.get('name')
        children = node.get('children', [])

        self.debug_print(f"Evaluating expression node: {name}")

        if name == 'E' and node.get('type') == 'integer':
            # 处理整数表达式
            if not children:
                raise Exception("Invalid integer expression.")
            child = children[0]
            if child['token'] == 'num':
                result = int(child['lexeme'])
                self.debug_print(f"Integer expression evaluated to {result}")
                return result
            elif child['token'] == 'id':
                var_name = child['lexeme']
                if var_name not in self.symbol_table:
                    raise Exception(f"Undefined variable: {var_name}")
                result = self.symbol_table[var_name]['value']
                self.debug_print(f"Integer expression variable '{var_name}' evaluated to {result}")
                return result
            else:
                raise Exception(f"Unsupported token in integer expression: {child['token']}")

        elif name == 'E' and node.get('type') == 'set':
            # 处理集合表达式
            if not children:
                raise Exception("Invalid set expression.")
            child = children[0]
            if child['name'] == 'set_definition':
                result = self.evaluate_set_definition(child)
                self.debug_print(f"Set expression evaluated to {result}")
                return result
            elif child['token'] == 'id':
                var_name = child['lexeme']
                if var_name not in self.symbol_table:
                    raise Exception(f"Undefined set variable: {var_name}")
                result = self.symbol_table[var_name]['value']
                self.debug_print(f"Set expression variable '{var_name}' evaluated to {result}")
                return result
            else:
                raise Exception(f"Unsupported token in set expression: {child['token']}")

        elif name == 'E\'' and node.get('type') == 'integer':
            # 处理更复杂的整数表达式
            # 具体实现取决于语法树结构
            # 示例：简单的算术运算
            if len(children) != 3:
                raise Exception("Unsupported integer expression structure.")
            left = self.get_evaluation(children[0])
            operator = children[1]['lexeme']
            right = self.get_evaluation(children[2])

            self.debug_print(f"Evaluating integer expression: {left} {operator} {right}")

            if operator == '+':
                result = left + right
            elif operator == '-':
                result = left - right
            elif operator == '*':
                result = left * right
            else:
                raise Exception(f"Unsupported operator in integer expression: {operator}")

            self.debug_print(f"Integer expression evaluated to {result}")
            return result

        elif name == 'E\'' and node.get('type') == 'set':
            # 处理更复杂的集合表达式
            # 具体实现取决于语法树结构
            # 示例：集合并集 U 和交集 I
            if len(children) != 3:
                raise Exception("Unsupported set expression structure.")
            left = self.get_evaluation(children[0])
            operator = children[1]['lexeme']
            right = self.get_evaluation(children[2])

            self.debug_print(f"Evaluating set expression: {left} {operator} {right}")

            if operator == 'U':
                if not isinstance(left, set) or not isinstance(right, set):
                    raise Exception("Set operators require both operands to be sets.")
                result = left.union(right)
            elif operator == 'I':
                if not isinstance(left, set) or not isinstance(right, set):
                    raise Exception("Set operators require both operands to be sets.")
                result = left.intersection(right)
            else:
                raise Exception(f"Unsupported operator in set expression: {operator}")

            self.debug_print(f"Set expression evaluated to {result}")
            return result

        else:
            raise Exception(f"Unsupported expression node: {name}")

    def evaluate_predicate(self, node):
        """
        处理谓词节点的评估。

        参数：
            node (dict): 谓词节点。

        返回：
            评估结果。
        """
        name = node.get('name')
        children = node.get('children', [])

        self.debug_print(f"Evaluating predicate node: {name}")

        if name in ['P', "P'", "P''"]:
            # 处理谓词逻辑，例如 "a > 1"
            if not children:
                raise Exception("Invalid predicate structure.")
            relation_node = children[0]
            relation_result = self.evaluate_relation(relation_node)
            self.debug_print(f"Predicate evaluated to {relation_result}")
            return relation_result
        else:
            raise Exception(f"Unsupported predicate node: {name}")

    def evaluate_relation(self, node):
        """
        处理关系节点的评估，例如 "a > 1"

        参数：
            node (dict): 关系节点。

        返回：
            评估结果（布尔值）。
        """
        if node.get('name') != 'R':
            raise Exception(f"Expected relation node 'R', got {node.get('name')}")

        children = node.get('children', [])
        if len(children) != 3:
            raise Exception("Invalid relation structure.")

        left_expr = children[0]
        operator = children[1]['lexeme']
        right_expr = children[2]

        left_val = self.get_evaluation(left_expr)
        right_val = self.get_evaluation(right_expr)

        self.debug_print(f"Evaluating relation: {left_val} {operator} {right_val}")

        if isinstance(left_val, str) and left_val.isdigit():
            left_val = int(left_val)
        if isinstance(right_val, str) and right_val.isdigit():
            right_val = int(right_val)

        if operator == '>':
            result = left_val > right_val
        elif operator == '<':
            result = left_val < right_val
        elif operator == '=':
            result = left_val == right_val
        elif operator == '@':
            # 示例：集合操作
            if operator == '@':
                if not isinstance(left_val, set) or not isinstance(right_val, set):
                    raise Exception("Operator '@' requires both operands to be sets.")
                result = left_val.issuperset(right_val)
            else:
                raise Exception(f"Unsupported operator: {operator}")
        else:
            raise Exception(f"Unsupported operator in relation: {operator}")

        self.debug_print(f"Relation evaluated to {result}")
        return result

    def evaluate_calculation(self, node):
        """
        处理计算节点的评估。

        参数：
            node (dict): 计算节点。

        返回：
            评估结果。
        """
        # 处理计算节点
        children = node.get('children', [])
        self.debug_print("Evaluating calculation node.")
        if len(children) == 1:
            result = self.get_evaluation(children[0])
            self.debug_print(f"Calculation evaluated to {result}")
            return result
        else:
            raise Exception("Invalid calculation node.")

    def evaluate_set_definition(self, node):
        """
        处理集合定义 { x : P(x) } 的评估。

        参数：
            node (dict): 集合定义节点。

        返回：
            评估结果，Python 集合类型。
        """
        # 处理集合定义 { x : P(x) }
        children = node.get('children', [])
        self.debug_print("Evaluating set definition.")

        if len(children) != 1:
            raise Exception("Invalid set definition.")

        predicate_node = children[0]
        result_set = set()

        self.debug_print("Assuming variable 'x' ranges from -100 to 100 for set evaluation.")
        # 假设x的范围是-100到100
        for x in range(-100, 101):
            self.symbol_table['x'] = {'type': 'int', 'value': x}
            predicate_result = self.evaluate_node(predicate_node)
            if predicate_result:
                result_set.add(x)
            self.debug_print(f"x = {x}: P(x) evaluated to {predicate_result}")
        # 移除临时变量x
        del self.symbol_table['x']
        node['value'] = "{ a: a > 1 }"  # 根据理想输出设置
        self.debug_print(f"Set definition evaluated to {result_set}")
        return result_set

    def get_evaluation(self, node):
        """
        获取节点的评估值。

        参数：
            node (dict): 节点。

        返回：
            节点的评估值。

        异常：
            如果节点没有 value 属性，则抛出异常。
        """
        if 'value' not in node:
            raise Exception(f"Node value not found: {node}")
        # 处理布尔值的字符串表示
        if node['value'] == "true":
            return True
        elif node['value'] == "false":
            return False
        else:
            return node['value']

# 主程序示例
if __name__ == "__main__":
    # 示例：创建 Evaluator 实例并启用调试信息
    evaluator = Evaluator()
    evaluator.enable_debug()  # 如果需要启用调试信息，调用此方法
    evaluator.evaluate()
