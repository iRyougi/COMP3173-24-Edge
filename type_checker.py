# type_checker.py
import json
from typing import List, Optional, Dict, Any


class ParseTreeNode:
    def __init__(
        self,
        name: Optional[str] = None,
        token: Optional[str] = None,
        lexeme: Optional[str] = None,
    ):
        self.name = name  # 非终结符名称
        self.token = token  # 终结符令牌
        self.lexeme = lexeme  # 终结符词素
        self.children: List["ParseTreeNode"] = []  # 子节点列表
        self.type: Optional[str] = None  # 节点类型

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ParseTreeNode":
        if "token" in data:
            node = ParseTreeNode(token=data["token"], lexeme=data["lexeme"])
            node.type = data.get("type")
        else:
            node = ParseTreeNode(name=data["name"])
            node.type = data.get("type")
            for child in data.get("children", []):
                node.children.append(ParseTreeNode.from_dict(child))
        return node

    def to_dict(self) -> Dict[str, Any]:
        if self.token:
            # 终结符节点
            return {"token": self.token, "lexeme": self.lexeme, "type": self.type}
        else:
            # 非终结符节点
            return {
                "name": self.name,
                "type": self.type,
                "children": [child.to_dict() for child in self.children],
            }


class SymbolTable:
    def __init__(self):
        self.table: Dict[str, Dict[str, Any]] = {}

    def add(self, var_name: str, var_type: str):
        self.table[var_name] = {
            "type": var_type,
            "value": None,  # 初始值为 None，实际实现中可扩展
        }
        print(f"Added to symbol table: {var_name} with type {var_type}")  # 调试信息

    def lookup(self, var_name: str) -> Optional[str]:
        if var_name in self.table:
            var_type = self.table[var_name]["type"]
            print(f"Lookup: {var_name} has type {var_type}")  # 调试信息
            return var_type
        else:
            print(f"Lookup Error: {var_name} not found in symbol table")  # 调试信息
            return None


KEYWORDS = {"let", "be", "show", "int", "set", "simplify"}
# 定义标点符号集合，根据您的lexer正则表达式
PUNCTUATION = {".", "{", "}", "(", ")", ":", ";"}


class TypeChecker:
    def __init__(self, root: ParseTreeNode):
        self.root = root
        self.symbol_table = SymbolTable()
        self.type_error_found = False

    def type_check(self) -> bool:
        print("Starting type checking...")
        self._check_node(self.root)
        return not self.type_error_found

    def _normalize_node_name(self, node_name: str) -> str:
        """
        将节点名称中的特殊字符转换为有效的 Python 方法名称。
        例如:
            "P'"  -> "P_prime"
            "P''" -> "P_double_prime"
        """
        normalized = node_name.replace("''", "_double_prime").replace("'", "_prime")
        return normalized

    def _check_node(self, node: ParseTreeNode):
        if node.token:
            print(f"Processing terminal node: {node.token}")
            self._check_terminal(node)
        else:
            normalized_name = self._normalize_node_name(node.name)
            handler_name = f"_check_{normalized_name}"
            print(f"Processing non-terminal node: {node.name}, handler: {handler_name}")
            handler = getattr(self, handler_name, self._check_default)
            print(f"Calling handler: {handler_name} for node: {node.name}")
            handler(node)

    def _check_terminal(self, node: ParseTreeNode):
        # 处理终结符节点
        if node.token == "num":
            node.type = "integer"
        elif node.token == "id":
            # 将id节点的类型设置为"void"
            node.type = "void"
        elif node.token in ["<", ">", "=", "@"]:
            node.type = "void"  # 将运算符类型设置为"void"
        elif node.token in ["&", "|", "!"]:
            node.type = "void"  # 修正为 "void" 而非 "predicate"
        elif node.token in ["U", "I", "+", "-", "*"]:
            node.type = "operator"
        elif node.token in KEYWORDS:
            node.type = "void"
        elif node.token in PUNCTUATION:
            node.type = "void"
        else:
            # 如果token未匹配，尝试根据lexeme设置type
            if node.lexeme in ["&", "|", "!"]:
                node.type = "void"
            else:
                node.type = None  # 其他终结符，如标点符号，不赋类型
        print(f"Processed token node: {node.token}, type: {node.type}")  # 调试用代码

    def _check_S(self, node: ParseTreeNode):
        # 规则 1,2: S -> D' C . | C .
        print(f"Entering _check_S for node: {node.name}")
        if len(node.children) == 3:
            # S -> D' C .
            D_prime, C, dot = node.children
            self._check_node(D_prime)  # 先处理 D'
            self._check_node(C)  # 再处理 C
            self._check_node(dot)
            if D_prime.type != "type_error" and C.type != "type_error":
                node.type = "program"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: S -> D' C . with type_error in D' or C")
        elif len(node.children) == 2:
            # S -> C .
            C, dot = node.children
            self._check_node(C)
            self._check_node(dot)
            node.type = C.type
            print(f"Processed node S: type set to {node.type}")
        print(f"Exiting _check_S, node type: {node.type}")

    def _check_D_prime(self, node: ParseTreeNode):
        # 规则 3: D' -> D D'
        # 规则 4: D' -> D
        print(f"Entering _check_D_prime for node: {node.name}")
        if len(node.children) == 2:
            # D' -> D D'
            D, D_prime = node.children
            self._check_node(D)
            self._check_node(D_prime)
            if D.type == "declaration" and D_prime.type == "declarations":
                node.type = "declarations"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: D' -> D D' with invalid types")
        elif len(node.children) == 1:
            # D' -> D
            D = node.children[0]
            self._check_node(D)
            if D.type == "declaration":
                node.type = "declarations"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: D' -> D with D.type != 'declaration'")
        print(f"Exiting _check_D_prime, node type: {node.type}")

    def _check_D(self, node: ParseTreeNode):
        # 规则 5: D -> let T id be E .
        print(f"Entering _check_D for node: {node.name}")
        if len(node.children) == 6:
            let, T, id_node, be, E, dot = node.children
            self._check_node(let)
            self._check_node(T)
            self._check_node(be)
            self._check_node(E)
            self._check_node(dot)

            if E.type != "type_error":
                # 只有当 E.type 不是 type_error 时，才将变量添加到符号表
                var_type = T.type
                self.symbol_table.add(id_node.lexeme, var_type)
                id_node.type = "void"  # 设置 id_node 的类型为 void
                print(f"Set id node '{id_node.lexeme}' type to 'void'")  # 调试信息
                node.type = "declaration"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: E.type is type_error in D")
        print(f"Exiting _check_D, node type: {node.type}")

    def _check_Z(self, node: ParseTreeNode):
        # 规则 19: Z -> id :
        print(f"Entering _check_Z for node: {node.name}")
        if len(node.children) == 2:
            id_node, colon = node.children
            # 直接添加 id 到符号表，类型为 integer
            self.symbol_table.add(id_node.lexeme, "integer")
            self._check_node(id_node)
            self._check_node(colon)
            id_node.type = "void"  # 设置 id_node 的类型为 void
            colon.type = "void"  # 设置 colon 的类型为 void
            node.type = "void"
            print(f"Set id node '{id_node.lexeme}' type to 'void' and colon type to 'void'")  # 调试信息
        print(f"Exiting _check_Z, node type: {node.type}")

    def _check_T(self, node: ParseTreeNode):
        # 规则 6和7: T -> int | set
        print(f"Entering _check_T for node: {node.name}")
        if len(node.children) == 1:
            token_node = node.children[0]
            self._check_node(token_node)
            if token_node.token == "int":
                node.type = "integer"
            elif token_node.token == "set":
                node.type = "set"
            print(f"Processed node T: type set to {node.type}")
        print(f"Exiting _check_T, node type: {node.type}")

    def _check_C(self, node: ParseTreeNode):
        # 规则 31: C -> show A
        print(f"Entering _check_C for node: {node.name}")
        if len(node.children) == 2:
            show, A = node.children
            self._check_node(show)
            self._check_node(A)
            if A.type != "type_error":
                node.type = "calculation"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: A.type is type_error in C")
            print(f"Processed node C: type set to {node.type}")
        print(f"Exiting _check_C, node type: {node.type}")

    def _check_A(self, node: ParseTreeNode):
        # 规则 32和33: A -> E | P
        print(f"Entering _check_A for node: {node.name}")
        if len(node.children) == 1:
            A_child = node.children[0]
            self._check_node(A_child)
            if A_child.type != "type_error":
                node.type = "calculation"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: A -> E | P with child.type == type_error")
            print(f"Processed node A: type set to {node.type}")
        print(f"Exiting _check_A, node type: {node.type}")

    def _check_E(self, node: ParseTreeNode):
        # 规则 8: E -> E'
        print(f"Entering _check_E for node: {node.name}")
        if len(node.children) == 1:
            E_prime = node.children[0]
            self._check_node(E_prime)
            node.type = E_prime.type
            print(f"Processed node E: type set to {node.type}")
        print(f"Exiting _check_E, node type: {node.type}")

    def _check_E1(self, node: ParseTreeNode):
        # 规则 9,10,11,14: E1 -> E2 U E' | E2 + E' | E2 - E' | E2 * E'
        print(f"Entering _check_E1 for node: {node.name}")
        if len(node.children) == 3:
            E2, op, E_prime = node.children
            self._check_node(E2)
            self._check_node(op)
            self._check_node(E_prime)
            if op.token == "U":
                if E2.type == "set" and E_prime.type == "set":
                    node.type = "set"
                else:
                    node.type = "type_error"
                    self.type_error_found = True
                    print("Type Error: E1 -> E2 U E' with incorrect types")
            elif op.token in ["+", "-"]:
                if E2.type == "integer" and E_prime.type == "integer":
                    node.type = "integer"
                else:
                    node.type = "type_error"
                    self.type_error_found = True
                    print(f"Type Error: E1 -> E2 {op.token} E' with incorrect types")
            elif op.token == "*":
                if E2.type == "integer" and E_prime.type == "integer":
                    node.type = "integer"
                else:
                    node.type = "type_error"
                    self.type_error_found = True
                    print("Type Error: E1 -> E2 * E' with incorrect types")
            print(f"Processed node E1: type set to {node.type}")
        print(f"Exiting _check_E1, node type: {node.type}")

    def _check_E_prime(self, node: ParseTreeNode):
        # 规则 12和13: E' -> E'' | E' I E''
        print(f"Entering _check_E_prime for node: {node.name}")
        if len(node.children) == 1:
            E_double_prime = node.children[0]
            self._check_node(E_double_prime)
            node.type = E_double_prime.type
            print(f"Processed node E': single child, type set to {node.type}")
        elif len(node.children) == 3:
            E_prime2, I_op, E_double_prime = node.children
            self._check_node(E_prime2)
            self._check_node(E_double_prime)
            if E_prime2.type == "set" and E_double_prime.type == "set":
                node.type = "set"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: E' -> E' I E'' with incorrect types")
            print(f"Processed node E': type set to {node.type}")
        print(f"Exiting _check_E_prime, node type: {node.type}")

    def _check_E_double_prime(self, node: ParseTreeNode):
        # 规则 15,16,17,18: E'' -> num | id | ( E ) | { Z P }
        print(f"Entering _check_E_double_prime for node: {node.name}")
        if len(node.children) == 1:
            child = node.children[0]
            self._check_node(child)
            if child.token:
                if child.token == "num":
                    node.type = "integer"
                elif child.token == "id":
                    var_type = self.symbol_table.lookup(child.lexeme)
                    if var_type:
                        node.type = var_type
                    else:
                        node.type = "type_error"
                        self.type_error_found = True
                        print(f"Type Error: Undefined identifier '{child.lexeme}' in E''")
                else:
                    node.type = "type_error"
                    self.type_error_found = True
                    print(f"Type Error: Invalid token '{child.token}' in E''")
        elif len(node.children) == 3 and node.children[0].token == "(":
            # 规则 17: ( E )
            _, E, _ = node.children
            self._check_node(E)
            node.type = E.type
            print(f"Processed node E'': ( E ), type set to {node.type}")
        elif len(node.children) == 4 and node.children[0].token == "{":
            # 规则 18: { Z P }
            _, Z, P, _ = node.children
            # 递归处理所有子节点，包括 "{" 和 "}"
            self._check_node(node.children[0])  # 处理 "{"
            self._check_node(Z)
            self._check_node(P)
            self._check_node(node.children[3])  # 处理 "}"
            if P.type == "predicate":
                node.type = "set"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: P.type != 'predicate' in E'' -> { Z P }")
            print(f"Processed node E'': {node.name}, type set to {node.type}")
        print(f"Exiting _check_E_double_prime, node type: {node.type}")

    def _check_P(self, node: ParseTreeNode):
        # 规则 21: P -> P'
        # 规则 20: P -> P' | P''
        print(f"Entering _check_P for node: {node.name}")
        if len(node.children) == 1:
            # P -> P'
            P_prime = node.children[0]
            self._check_node(P_prime)
            node.type = P_prime.type
            print(f"Processed node P: type set to {node.type}")
        elif len(node.children) == 3:
            # P -> P' | P''
            P_prime, pipe, P_double_prime = node.children
            self._check_node(P_prime)
            self._check_node(pipe)  # 确保处理 '|' 运算符节点
            self._check_node(P_double_prime)
            # The '|' token is already processed as a terminal node with type 'void'
            # We set P.type to 'predicate' if both P_prime and P_double_prime are 'predicate'
            if P_prime.type == "predicate" and P_double_prime.type == "predicate":
                node.type = "predicate"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: P -> P' | P'' with incorrect types")
            print(f"Processed node P: type set to {node.type}")
        else:
            # Unexpected number of children
            node.type = "type_error"
            self.type_error_found = True
            print(f"Type Error: P has unexpected number of children: {len(node.children)}")
        print(f"Exiting _check_P, node type: {node.type}")

    def _check_P1(self, node: ParseTreeNode):
        # 规则 20: P1 -> P2 | P'
        print(f"Entering _check_P1 for node: {node.name}")
        if len(node.children) == 3:
            P2, pipe, P_prime = node.children
            self._check_node(P2)
            self._check_node(P_prime)
            if P2.type == "predicate" and P_prime.type == "predicate":
                node.type = "predicate"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: P1 -> P2 | P' with incorrect types")
            print(f"Processed node P1: type set to {node.type}")
        print(f"Exiting _check_P1, node type: {node.type}")

    def _check_P_prime(self, node: ParseTreeNode):
        # 规则 22和23: P' -> P'' | P' & P'' | P' | P''
        print(f"Entering _check_P_prime for node: {node.name}")
        if len(node.children) == 1:
            P_double_prime = node.children[0]
            self._check_node(P_double_prime)
            node.type = P_double_prime.type
            print(f"Processed node P': single child, type set to {node.type}")
        elif len(node.children) == 3:
            P_prime2, op, P_double_prime = node.children
            self._check_node(P_prime2)
            self._check_node(op)  # 新增：确保处理运算符节点
            self._check_node(P_double_prime)
            if (
                P_prime2.type == "predicate"
                and P_double_prime.type == "predicate"
                and op.token in ["&", "|", "!"]  # 添加对 "&" 和 "|" 运算符的处理
            ):
                node.type = "predicate"
                print(f"Processed node P': {op.token} operation, type set to {node.type}")
            else:
                node.type = "type_error"
                self.type_error_found = True
                print(f"Type Error: P' -> P' {op.token} P'' with incorrect types")
        print(f"Final type for node P': {node.type}")
        print(f"Exiting _check_P_prime, node type: {node.type}")


    def _check_P_double_prime(self, node: ParseTreeNode):
        # 规则 24,25,26: P'' -> R | ( P ) | ! R
        print(f"Entering _check_P_double_prime for node: {node.name}")
        if len(node.children) == 1:
            R = node.children[0]
            self._check_node(R)
            if R.type == "relation":
                node.type = "predicate"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: P'' -> R with R.type != 'relation'")
            print(f"Processed node P'': {node.name}, type set to {node.type}")
        elif len(node.children) == 3 and node.children[0].token == "(":
            # 规则 25: ( P )
            _, P, _ = node.children
            self._check_node(P)
            node.type = P.type
            print(f"Processed node P'': ( P ), type set to {node.type}")
        elif len(node.children) == 2 and node.children[0].token == "!":
            # 规则 26: ! R
            exclamation, R = node.children
            self._check_node(exclamation)  # 处理 '!' 节点
            self._check_node(R)            # 处理 'R' 节点
            if R.type == "relation":
                node.type = "predicate"
            else:
                node.type = "type_error"
                self.type_error_found = True
                print("Type Error: P'' -> ! R with R.type != 'relation'")
            print(f"Processed node P'': ! R, type set to {node.type}")
        print(f"Exiting _check_P_double_prime, node type: {node.type}")


    def _check_R(self, node: ParseTreeNode):
        # 规则 27,28,29,30: R -> E1 < E2 | E1 > E2 | E1 = E2 | E1 @ E2
        print(f"Entering _check_R for node: {node.name}")
        if len(node.children) == 3:
            E1, op, E2 = node.children
            self._check_node(E1)
            self._check_node(op)
            self._check_node(E2)
            if op.lexeme in ["<", ">", "="]:
                if E1.type == "integer" and E2.type == "integer":
                    node.type = "relation"
                else:
                    node.type = "type_error"
                    self.type_error_found = True
                    print(f"Type Error: R -> E1 {op.lexeme} E2 with non-integer types")
            elif op.lexeme == "@":
                if E1.type == "integer" and E2.type == "set":
                    node.type = "relation"
                else:
                    node.type = "type_error"
                    self.type_error_found = True
                    print("Type Error: R -> E1 @ E2 with incorrect types")
        print(f"Processed node R: type set to {node.type}")
        print(f"Exiting _check_R, node type: {node.type}")

    def _check_default(self, node: ParseTreeNode):
        # 默认处理方法，递归处理子节点
        print(f"Entering _check_default for node: {node.name}")
        for child in node.children:
            self._check_node(child)
        # 根据具体语法规则设置类型
        # 这里可以添加更多的规则处理
        print(f"Processed default non-terminal node: {node.name}, type: {node.type}")
        print(f"Exiting _check_default, node type: {node.type}")

    @staticmethod
    def serialize_tree(node: ParseTreeNode) -> Any:
        return node.to_dict()

    def write_typing_out(
        self, tree: Optional[ParseTreeNode], filename: str = "typing_out.json"
    ):
        if tree is None:
            # 写入空的 JSON 文件
            with open(filename, "w") as f:
                json.dump([], f)
        else:
            # 写入包含类型信息的解析树
            tree_dict = self.serialize_tree(tree)
            with open(filename, "w") as f:
                json.dump(tree_dict, f, indent=4)


def load_parse_tree(filename: str) -> Optional[ParseTreeNode]:
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            # 假设 data 是一个字典格式的解析树
            if isinstance(data, dict):
                return ParseTreeNode.from_dict(data)
            else:
                print(
                    "Error: The parser_out.json does not contain a single dictionary as the parse tree root."
                )
                return None
    except Exception as e:
        print(f"Error reading parse tree: {e}")
        return None


def type_check_with_error_handling(
    root: ParseTreeNode, filename: str = "typing_out.json"
) -> bool:
    type_checker = TypeChecker(root)
    success = type_checker.type_check()
    if success:
        print("Semantic Analysis Complete!")
        type_checker.write_typing_out(root, filename)
    else:
        print("Type Error!")
        type_checker.write_typing_out(None, filename)
    return success


def main_type_checker():
    # 这部分通常不会被调用，因为主函数在 main.py 中
    pass

# 如果您希望直接运行 type_checker.py，请取消以下注释：
# if __name__ == "__main__":
#     parse_tree = load_parse_tree("parser_out.json")
#     if parse_tree:
#         type_check_with_error_handling(parse_tree)
