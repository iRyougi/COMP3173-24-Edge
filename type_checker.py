#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os

###############################################################################
# 1. 常量定义
###############################################################################

# 是否开启DEBUG日志
DEBUG = False

def debug_log(msg: str):
    """打印调试信息，可自行控制是否打印"""
    if DEBUG:
        print(f"[DEBUG] {msg}")

# 类型字符串常量
TYPE_ERROR = "type_error"
TYPE_INTEGER = "integer"
TYPE_SET = "set"
TYPE_RELATION = "relation"
TYPE_PREDICATE = "predicate"
TYPE_CALCULATION = "calculation"
TYPE_DECLARATION = "declaration"
TYPE_DECLARATIONS = "declarations"
TYPE_PROGRAM = "program"
TYPE_VOID = "void"

###############################################################################
# 2. TypeChecker 类定义
###############################################################################

class TypeChecker:
    def __init__(self, parser_out_path: str, typing_out_path: str):
        self.parser_out_path = parser_out_path
        self.typing_out_path = typing_out_path
        self.symbol_table = {}  # 符号表
        self.ast_root = {}
        self.type_error_flag = False

        # 定义非终结符名称到处理方法的映射字典
        self.handler_dict = {
            "S": self.handle_S,
            "D'": self.handle_D_prime,
            "C": self.handle_C,
            "A": self.handle_A,
            "E": self.handle_E,
            "E'": self.handle_E_prime,
            "E''": self.handle_E_double_prime,
            "D": self.handle_D,
            "T": self.handle_T,
            "P": self.handle_P,
            "P'": self.handle_P_prime,
            "P''": self.handle_P_double_prime,
            "P1": self.handle_P1,
            "P2": self.handle_P2,
            "Z": self.handle_Z,
            "R": self.handle_R,
            # 添加其他非终结符及其处理方法
        }

    def load_ast(self):
        """加载 parser_out.json 并存储到 self.ast_root"""
        if not os.path.exists(self.parser_out_path):
            debug_log(f"Error: {self.parser_out_path} not found.")
            self.type_error_flag = True
            return

        with open(self.parser_out_path, "r", encoding="utf-8") as f:
            try:
                self.ast_root = json.load(f)
                debug_log(f"AST loaded successfully from {self.parser_out_path}")
            except json.JSONDecodeError:
                debug_log(f"Error: Failed to parse JSON from {self.parser_out_path}.")
                self.type_error_flag = True

    def write_typing_json(self):
        """将带有类型信息的 AST 写入 typing_out.json 或输出空文件"""
        if self.type_error_flag:
            debug_log("Type error detected. typing_out.json will be empty.")
            with open(self.typing_out_path, "w", encoding="utf-8") as f:
                f.write("")  # 写空文件
            return

        def convert_node(node: dict):
            """递归地转换 AST 节点，包含 type 信息"""
            if "token" in node:
                # 终结符
                return {
                    "token": node["token"],
                    "lexeme": node["lexeme"],
                    "type": node.get("type", TYPE_VOID)
                }
            else:
                # 非终结符
                return {
                    "name": node["name"],
                    "type": node.get("type", TYPE_VOID),
                    "children": [convert_node(child) for child in node.get("children", [])]
                }

        with open(self.typing_out_path, "w", encoding="utf-8") as f:
            json.dump(convert_node(self.ast_root), f, indent=2, ensure_ascii=False)
        debug_log(f"typing_out.json written successfully to {self.typing_out_path}")

    def type_check(self):
        """执行类型检查"""
        self.ast_root["type"] = self.type_check_node(self.ast_root)
        if self.ast_root["type"] == TYPE_ERROR:
            self.type_error_flag = True

    def type_check_node(self, node: dict) -> str:
        """
        递归地对 AST 节点进行类型检查，并将类型信息存入节点中。
        :param node: 当前 AST 节点（字典）
        :return: 节点类型字符串
        """

        # 如果已经标记为 type_error，则直接返回
        if node.get("type", None) == TYPE_ERROR:
            return TYPE_ERROR

        # 终结符节点处理
        if "token" in node:
            token = node["token"]
            lexeme = node["lexeme"]

            if token == "num":
                # 规则15: E'' -> num => E''.type = integer
                node["type"] = TYPE_INTEGER
                debug_log(f"Token num '{lexeme}' => type = {TYPE_INTEGER}")
                return TYPE_INTEGER

            elif token == "id":
                # 规则16: E'' -> id => E''.type = lookup_type(id.entry)
                if lexeme not in self.symbol_table:
                    # 使用未声明变量
                    node["type"] = TYPE_ERROR
                    debug_log(f"Identifier '{lexeme}' not declared => type_error")
                    self.type_error_flag = True
                    return TYPE_ERROR
                declared_type = self.symbol_table[lexeme]["type"]  # "int" 或 "set"
                if declared_type == "int":
                    node["type"] = TYPE_INTEGER
                elif declared_type == "set":
                    node["type"] = TYPE_SET
                else:
                    node["type"] = TYPE_ERROR
                    debug_log(f"Identifier '{lexeme}' has unknown type '{declared_type}' => type_error")
                    self.type_error_flag = True
                    return TYPE_ERROR
                debug_log(f"Identifier '{lexeme}' => type = {node['type']}")
                return node["type"]

            elif token in {
                "+", "-", "*", "U", "I",
                "<", ">", "=", "@",
                "&", "|", "!",
                "(", ")", "{", "}", ":",
                ".", "be", "let", "show", "int", "set"
            }:
                # 运算符、关键字等，类型为 void
                node["type"] = TYPE_VOID
                debug_log(f"Token '{lexeme}' ({token}) => type = {TYPE_VOID}")
                return TYPE_VOID

            else:
                # 未知 token
                node["type"] = TYPE_ERROR
                debug_log(f"Unknown token '{token}' => type_error")
                self.type_error_flag = True
                return TYPE_ERROR

        # 非终结符节点处理
        else:
            name = node.get("name", "")
            children = node.get("children", [])

            debug_log(f"Processing Non-terminal: {name}, Children count: {len(children)}")

            # 打印每个子节点的名称或 token 以便调试
            for idx, child in enumerate(children):
                if "name" in child:
                    debug_log(f"  Child {idx}: name={child['name']}")
                elif "token" in child:
                    debug_log(f"  Child {idx}: token={child['token']}")

            # 根据非终结符名称调用相应的处理函数
            handler = self.handler_dict.get(name, None)
            if handler:
                return handler(node, children)
            else:
                # 未处理的非终结符
                node["type"] = TYPE_ERROR
                debug_log(f"No handler for non-terminal '{name}' => type_error")
                self.type_error_flag = True
                return TYPE_ERROR

# 以下是各个 handle_X 方法，用于处理不同的非终结符

    # 处理 S 非终结符
    def handle_S(self, node: dict, children: list) -> str:
        """
        规则1: S -> D' C .
        规则2: S -> C .
        """
        debug_log("handle_S called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 3 and \
            children[0].get("name", "") == "D'" and \
            children[1].get("name", "") == "C" and \
            children[2].get("token", "") == ".":
            # 规则1: S -> D' C .
            d_prime_type = self.type_check_node(children[0])
            c_type = self.type_check_node(children[1])
            if d_prime_type != TYPE_ERROR and c_type != TYPE_ERROR:
                node["type"] = TYPE_PROGRAM
                debug_log("S -> D' C . => type = program")
            else:
                node["type"] = TYPE_ERROR
                debug_log("S -> D' C . type mismatch => type_error")
                self.type_error_flag = True
        elif len(children) == 2 and \
                children[0].get("name", "") == "C" and \
                children[1].get("token", "") == ".":
            # 规则2: S -> C .
            c_type = self.type_check_node(children[0])
            node["type"] = c_type
            debug_log(f"S -> C . => type = {c_type}")
        else:
            node["type"] = TYPE_ERROR
            debug_log("S production does not match any rule => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 D_prime 非终结符
    def handle_D_prime(self, node: dict, children: list) -> str:
        """
        规则3: D'1 -> D D'2
        规则4: D' -> D
        """
        debug_log("handle_D_prime called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 2:
            # 规则3: D'1 -> D D'2
            d_type = self.type_check_node(children[0])
            d_prime2_type = self.type_check_node(children[1])
            if d_type == TYPE_DECLARATION and d_prime2_type == TYPE_DECLARATIONS:
                node["type"] = TYPE_DECLARATIONS
                debug_log("D'1 -> D D'2 => type = declarations")
            else:
                node["type"] = TYPE_ERROR
                debug_log("D'1 -> D D'2 type mismatch => type_error")
                self.type_error_flag = True
        elif len(children) == 1:
            # 规则4: D' -> D
            d_type = self.type_check_node(children[0])
            if d_type == TYPE_DECLARATION:
                node["type"] = TYPE_DECLARATIONS
                debug_log("D' -> D => type = declarations")
            else:
                node["type"] = TYPE_ERROR
                debug_log("D' -> D type mismatch => type_error")
                self.type_error_flag = True
        else:
            node["type"] = TYPE_ERROR
            debug_log("D' production does not match any rule => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 D 非终结符
    def handle_D(self, node: dict, children: list) -> str:
        """
        规则5: D -> let T id be E .
        """
        debug_log("handle_D called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 6:
            # children[0]: 'let', children[1]: T, children[2]: id, children[3]: 'be', children[4]: E, children[5]: '.'
            t_node = children[1]
            id_node = children[2]
            e_node = children[4]

            t_type = self.type_check_node(t_node)
            e_type = self.type_check_node(e_node)

            if e_type != TYPE_ERROR:
                var_name = id_node["lexeme"]
                if t_type == TYPE_INTEGER:
                    self.symbol_table[var_name] = {"type": "int", "value": None}
                    debug_log(f"Declared variable '{var_name}' of type 'int'")
                elif t_type == TYPE_SET:
                    self.symbol_table[var_name] = {"type": "set", "value": None}
                    debug_log(f"Declared variable '{var_name}' of type 'set'")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log(f"T type '{t_type}' is invalid => type_error")
                    self.type_error_flag = True
                    return TYPE_ERROR
                node["type"] = TYPE_DECLARATION
                debug_log(f"Declared variable '{var_name}' of type '{t_type}'")
            else:
                node["type"] = TYPE_ERROR
                debug_log("E type_error in D production => type_error")
                self.type_error_flag = True
        else:
            node["type"] = TYPE_ERROR
            debug_log("D production does not match rule5 => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 T 非终结符
    def handle_T(self, node: dict, children: list) -> str:
        """
        规则6: T -> int
        规则7: T -> set
        """
        debug_log("handle_T called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 1 and "token" in children[0]:
            token = children[0]["token"]
            if token == "int":
                node["type"] = TYPE_INTEGER
                debug_log(f"T -> int => type = {TYPE_INTEGER}")
            elif token == "set":
                node["type"] = TYPE_SET
                debug_log(f"T -> set => type = {TYPE_SET}")
            else:
                node["type"] = TYPE_ERROR
                debug_log(f"T -> unknown token '{token}' => type_error")
                self.type_error_flag = True
        else:
            node["type"] = TYPE_ERROR
            debug_log("T production does not match any rule => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 C 非终结符
    def handle_C(self, node: dict, children: list) -> str:
        """
        规则31: C -> show A
        """
        debug_log("handle_C called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 2 and children[0].get("token", "") == "show":
            a_node = children[1]
            a_type = self.type_check_node(a_node)
            node["type"] = a_type  # "calculation" 或 "type_error"
            debug_log(f"C -> show A => A.type = {a_type}")
        else:
            node["type"] = TYPE_ERROR
            debug_log("C production does not match rule31 => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 A 非终结符
    def handle_A(self, node: dict, children: list) -> str:
        """
        规则32: A -> E
        规则33: A -> P
        """
        debug_log("handle_A called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 1:
            child = children[0]
            child_type = self.type_check_node(child)
            if child_type != TYPE_ERROR:
                node["type"] = TYPE_CALCULATION
                debug_log(f"A -> {child['name'] if 'name' in child else child['token']} => type = {TYPE_CALCULATION}")
            else:
                node["type"] = TYPE_ERROR
                debug_log("A -> child type_error => type_error")
                self.type_error_flag = True
        else:
            node["type"] = TYPE_ERROR
            debug_log("A production does not match rule32/33 => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 E 非终结符
    def handle_E(self, node: dict, children: list) -> str:
        """
        规则8: E -> E'
        规则9: E1 -> E2 U E'
        规则10: E1 -> E2 + E'
        规则11: E1 -> E2 - E'
        """
        debug_log("handle_E called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 1:
            # 规则8: E -> E'
            child_type = self.type_check_node(children[0])
            node["type"] = child_type
            debug_log(f"E -> E' => type = {child_type}")
            return node["type"]
        elif len(children) == 3:
            # 规则9,10,11: E -> E2 op E'
            e2_node = children[0]
            op_node = children[1]
            e_prime_node = children[2]

            op = op_node["lexeme"]
            e2_type = self.type_check_node(e2_node)
            e_prime_type = self.type_check_node(e_prime_node)

            if op == "U":
                # 规则9: E1 -> E2 U E'
                if e2_type == TYPE_SET and e_prime_type == TYPE_SET:
                    node["type"] = TYPE_SET
                    debug_log(f"E -> E2 U E' => type = {TYPE_SET}")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log("E -> E2 U E' type mismatch => type_error")
                    self.type_error_flag = True
            elif op == "+":
                # 规则10: E1 -> E2 + E'
                if e2_type == TYPE_INTEGER and e_prime_type == TYPE_INTEGER:
                    node["type"] = TYPE_INTEGER
                    debug_log(f"E -> E2 + E' => type = {TYPE_INTEGER}")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log("E -> E2 + E' type mismatch => type_error")
                    self.type_error_flag = True
            elif op == "-":
                # 规则11: E1 -> E2 - E'
                if e2_type == TYPE_INTEGER and e_prime_type == TYPE_INTEGER:
                    node["type"] = TYPE_INTEGER
                    debug_log(f"E -> E2 - E' => type = {TYPE_INTEGER}")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log("E -> E2 - E' type mismatch => type_error")
                    self.type_error_flag = True
            else:
                # 未知操作符
                node["type"] = TYPE_ERROR
                debug_log(f"E -> unknown operator '{op}' => type_error")
                self.type_error_flag = True
        else:
            # 不匹配的产生式
            node["type"] = TYPE_ERROR
            debug_log("E production does not match any rule => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 E_prime 非终结符
    def handle_E_prime(self, node: dict, children: list) -> str:
        """
        规则12: E' -> E''
        规则13: E'1 -> E'2 I E''
        规则14: E'1 -> E'2 * E''
        """
        debug_log("handle_E_prime called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 1:
            # 规则12: E' -> E''
            child_type = self.type_check_node(children[0])
            node["type"] = child_type
            debug_log(f"E' -> E'' => type = {child_type}")
            return node["type"]
        elif len(children) == 3:
            # 规则13,14: E'1 -> E'2 op E''
            e_prime2_node = children[0]
            op_node = children[1]
            e_double_prime_node = children[2]

            op = op_node["lexeme"]
            e_prime2_type = self.type_check_node(e_prime2_node)
            e_double_prime_type = self.type_check_node(e_double_prime_node)

            if op == "I":
                # 规则13: E'1 -> E'2 I E''
                if e_prime2_type == TYPE_SET and e_double_prime_type == TYPE_SET:
                    node["type"] = TYPE_SET
                    debug_log("E'1 -> E'2 I E'' => type = set")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log("E'1 -> E'2 I E'' type mismatch => type_error")
                    self.type_error_flag = True
            elif op == "*":
                # 规则14: E'1 -> E'2 * E''
                if e_prime2_type == TYPE_INTEGER and e_double_prime_type == TYPE_INTEGER:
                    node["type"] = TYPE_INTEGER
                    debug_log("E'1 -> E'2 * E'' => type = integer")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log("E'1 -> E'2 * E'' type mismatch => type_error")
                    self.type_error_flag = True
            else:
                # 未知操作符
                node["type"] = TYPE_ERROR
                debug_log(f"E'1 -> unknown operator '{op}' => type_error")
                self.type_error_flag = True
        else:
            # 不匹配的产生式
            node["type"] = TYPE_ERROR
            debug_log("E' production does not match any rule => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 E'' 非终结符
    def handle_E_double_prime(self, node: dict, children: list) -> str:
        """
        规则15: E'' -> num
        规则16: E'' -> id
        规则17: E'' -> ( E )
        规则18: E'' -> { Z P }
        """
        debug_log("handle_E_double_prime called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 1:
            # 规则15: E'' -> num
            # 规则16: E'' -> id
            child_type = self.type_check_node(children[0])
            node["type"] = child_type
            debug_log(f"E'' -> {children[0].get('name', children[0].get('token'))} => type = {child_type}")
            return node["type"]
        elif len(children) == 3:
            # 规则17: E'' -> ( E )
            if children[0].get("token", "") == "(" and children[2].get("token", "") == ")":
                e_node = children[1]
                e_type = self.type_check_node(e_node)
                node["type"] = e_type
                debug_log(f"E'' -> ( E ) => type = {e_type}")
                return node["type"]
            else:
                # 不是规则17
                pass
        elif len(children) == 4:
            # 规则18: E'' -> { Z P }
            if children[0].get("token", "") == "{" and children[3].get("token", "") == "}":
                z_node = children[1]
                p_node = children[2]
                z_type = self.type_check_node(z_node)
                p_type = self.type_check_node(p_node)
                if p_type == TYPE_PREDICATE:
                    node["type"] = TYPE_SET
                    debug_log("E'' -> { Z P } => type = set")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log("E'' -> { Z P } with P.type != predicate => type_error")
                    self.type_error_flag = True
                return node["type"]
            else:
                # 不是规则18
                pass

        # 如果没有匹配到任何规则
        node["type"] = TYPE_ERROR
        debug_log("E'' production does not match any rule => type_error")
        self.type_error_flag = True
        return node["type"]

    # 处理 Z 非终结符
    def handle_Z(self, node: dict, children: list) -> str:
        """
        规则19: Z -> id :
        """
        debug_log("handle_Z called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 2 and \
            children[0].get("token", "") == "id" and \
            children[1].get("token", "") == ":":
            id_node = children[0]
            var_name = id_node["lexeme"]
            # 规则19: add_type(id.entry, integer)
            self.symbol_table[var_name] = {"type": "int", "value": None}
            node["type"] = TYPE_VOID
            debug_log(f"Z -> {var_name} : => added to symbol_table as int")
        else:
            node["type"] = TYPE_ERROR
            debug_log("Z production does not match rule19 => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 P 非终结符
    def handle_P(self, node: dict, children: list) -> str:
        """
        规则21: P -> P'
        """
        debug_log("handle_P called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 1:
            child_type = self.type_check_node(children[0])
            node["type"] = child_type
            debug_log(f"P -> P' => type = {child_type}")
        else:
            node["type"] = TYPE_ERROR
            debug_log("P production does not match rule21 => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 P_prime 非终结符
    def handle_P_prime(self, node: dict, children: list) -> str:
        """
        规则22: P'1 -> P'2 & P''
        规则23: P' -> P''
        """
        debug_log("handle_P_prime called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 1:
            # 规则23: P' -> P''
            child_type = self.type_check_node(children[0])
            node["type"] = child_type
            debug_log(f"P' -> P'' => type = {child_type}")
            return node["type"]
        elif len(children) == 3:
            # 规则22: P'1 -> P'2 & P''
            p_prime2_node = children[0]
            op_node = children[1]
            p_double_prime_node = children[2]

            op = op_node["lexeme"]
            p_prime2_type = self.type_check_node(p_prime2_node)
            p_double_prime_type = self.type_check_node(p_double_prime_node)

            if op == "&":
                if p_prime2_type == TYPE_PREDICATE and p_double_prime_type == TYPE_PREDICATE:
                    node["type"] = TYPE_PREDICATE
                    debug_log("P'1 -> P'2 & P'' => type = predicate")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log("P'1 -> P'2 & P'' type mismatch => type_error")
                    self.type_error_flag = True
            else:
                # 未知操作符
                node["type"] = TYPE_ERROR
                debug_log(f"P'1 -> unknown operator '{op}' => type_error")
                self.type_error_flag = True
        else:
            # 不匹配的产生式
            node["type"] = TYPE_ERROR
            debug_log("P' production does not match any rule => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 P_double_prime 非终结符
    def handle_P_double_prime(self, node: dict, children: list) -> str:
        """
        规则24: P'' -> R
        规则25: P'' -> ( P )
        规则26: P'' -> ! R
        """
        debug_log("handle_P_double_prime called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 1:
            # 规则24: P'' -> R
            r_type = self.type_check_node(children[0])
            if r_type == TYPE_RELATION:
                node["type"] = TYPE_PREDICATE
                debug_log("P'' -> R => type = predicate")
            else:
                node["type"] = TYPE_ERROR
                debug_log("P'' -> R with R.type != relation => type_error")
                self.type_error_flag = True
        elif len(children) == 3:
            # 规则25: P'' -> ( P )
            if children[0].get("token", "") == "(" and children[2].get("token", "") == ")":
                p_node = children[1]
                p_type = self.type_check_node(p_node)
                node["type"] = p_type
                debug_log(f"P'' -> ( P ) => type = {p_type}")
            else:
                node["type"] = TYPE_ERROR
                debug_log("P'' -> ( P ) does not match rule25 => type_error")
                self.type_error_flag = True
        elif len(children) == 2:
            # 规则26: P'' -> ! R
            if children[0].get("token", "") == "!" and children[1].get("name", "") == "R":
                r_type = self.type_check_node(children[1])
                if r_type == TYPE_RELATION:
                    node["type"] = TYPE_PREDICATE
                    debug_log("P'' -> ! R => type = predicate")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log("P'' -> ! R with R.type != relation => type_error")
                    self.type_error_flag = True
            else:
                node["type"] = TYPE_ERROR
                debug_log("P'' -> ! R does not match rule26 => type_error")
                self.type_error_flag = True
        else:
            node["type"] = TYPE_ERROR
            debug_log("P'' production does not match any rule => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 P1 非终结符
    def handle_P1(self, node: dict, children: list) -> str:
        """
        规则20: P1 -> P2 | P'
        """
        debug_log("handle_P1 called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 3:
            # P1 -> P2 | P'
            p2_node = children[0]
            op_node = children[1]
            p_prime_node = children[2]

            op = op_node["lexeme"]
            p2_type = self.type_check_node(p2_node)
            p_prime_type = self.type_check_node(p_prime_node)

            if op == "|":
                if p2_type == TYPE_PREDICATE and p_prime_type == TYPE_PREDICATE:
                    node["type"] = TYPE_PREDICATE
                    debug_log("P1 -> P2 | P' => type = predicate")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log("P1 -> P2 | P' type mismatch => type_error")
                    self.type_error_flag = True
            else:
                # 未知操作符
                node["type"] = TYPE_ERROR
                debug_log(f"P1 -> unknown operator '{op}' => type_error")
                self.type_error_flag = True
        else:
            # 不匹配的产生式
            node["type"] = TYPE_ERROR
            debug_log("P1 production does not match any rule => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 P2 非终结符
    def handle_P2(self, node: dict, children: list) -> str:
        """
        规则20: P1 -> P2 | P'
        假设 P2 的定义类似于 P
        """
        debug_log("handle_P2 called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 1:
            child_type = self.type_check_node(children[0])
            node["type"] = child_type
            debug_log(f"P2 -> P => type = {child_type}")
        else:
            node["type"] = TYPE_ERROR
            debug_log("P2 production does not match any rule => type_error")
            self.type_error_flag = True
        return node["type"]

    # 处理 R 非终结符
    def handle_R(self, node: dict, children: list) -> str:
        """
        规则27: R -> E1 < E2
        规则28: R -> E1 > E2
        规则29: R -> E1 = E2
        规则30: R -> E1 @ E2
        """
        debug_log("handle_R called with children:")
        for idx, child in enumerate(children):
            if "name" in child:
                debug_log(f"  Child {idx}: name={child['name']}")
            elif "token" in child:
                debug_log(f"  Child {idx}: token={child['token']}")

        if len(children) == 3:
            e1_node = children[0]
            op_node = children[1]
            e2_node = children[2]

            op = op_node["lexeme"]
            e1_type = self.type_check_node(e1_node)
            e2_type = self.type_check_node(e2_node)

            if op in ("<", ">", "="):
                # 规则27,28,29
                if e1_type == TYPE_INTEGER and e2_type == TYPE_INTEGER:
                    node["type"] = TYPE_RELATION
                    debug_log(f"R -> E1 {op} E2 => type = {TYPE_RELATION}")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log(f"R -> E1 {op} E2 type mismatch => type_error")
                    self.type_error_flag = True
            elif op == "@":
                # 规则30
                if e1_type == TYPE_INTEGER and e2_type == TYPE_SET:
                    node["type"] = TYPE_RELATION
                    debug_log("R -> E1 @ E2 => type = relation")
                else:
                    node["type"] = TYPE_ERROR
                    debug_log("R -> E1 @ E2 type mismatch => type_error")
                    self.type_error_flag = True
            else:
                # 未知操作符
                node["type"] = TYPE_ERROR
                debug_log(f"R -> unknown operator '{op}' => type_error")
                self.type_error_flag = True
        else:
            # 不匹配的产生式
            node["type"] = TYPE_ERROR
            debug_log("R production does not match any rule => type_error")
            self.type_error_flag = True
        return node["type"]

###############################################################################
# 3. 主函数
###############################################################################

def main():
    # 假设文件路径如下，你可以根据实际情况修改
    parser_out_path = "parser_out.json"
    typing_out_path = "typing_out.json"

    # 创建 TypeChecker 实例
    type_checker = TypeChecker(parser_out_path, typing_out_path)

    try:
        # 加载 AST
        type_checker.load_ast()
        if type_checker.type_error_flag:
            print("Type Error!")
        else:
            # 运行类型检查
            type_checker.type_check()
            if type_checker.type_error_flag:
                print("Type Error!")
            else:
                print("Semantic Analysis Complete!")
    except Exception as e:
        # 捕获任何未预见的异常
        debug_log(f"Unexpected error: {e}")
        type_checker.type_error_flag = True
        print("Type Error!")
    finally:
        # 根据 type_error_flag 写出 typing_out.json
        type_checker.write_typing_json()
        debug_log("Type checking phase finished.")

    # 无论是否发生错误，程序都返回 0
    sys.exit(0)

if __name__ == "__main__":
    main()
