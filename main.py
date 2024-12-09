import argparse
import json
from lexer import Lexer
from parser import (
    SLRParser,
    load_parsing_table,
)  # Assuming parser.py and this file are in the same directory
from type_checker import (
    load_parse_tree,
    type_check_with_error_handling,
)  # 导入类型检查器功能


def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(
        description="Run lexer and parser on a source code file."
    )
    parser.add_argument("input_file", help="The input file containing source code.")
    args = parser.parse_args()

    # Step 1: 词法分析
    # 读取指定的输入文件
    try:
        with open(args.input_file, "r") as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{args.input_file}' was not found.")
        return

    # 创建 Lexer 实例并进行词法分析
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    # 将 token 信息保存为 JSON 格式到 lexer_out.json 文件
    with open("lexer_out.json", "w") as json_file:
        json.dump(tokens, json_file, indent=2)
    print("Lexical Analysis Complete!")  # 调试用代码，显示文件输出

    # Step 2: 语法分析
    # 读取解析表 (固定路径为 'SLR Parsing Table.csv')
    action_table, goto_table = load_parsing_table("SLR Parsing Table.csv")

    # 创建 SLRParser 实例并进行语法分析
    parser = SLRParser(tokens, action_table, goto_table)
    parser.parse()

    # Step 3: 语义分析（类型检查）
    # 加载解析树
    parse_tree_root = load_parse_tree("parser_out.json")
    if not parse_tree_root:
        print("Failed to load parse tree.")
        # 生成空的 typing_out.json 文件
        with open("typing_out.json", "w") as f:
            json.dump([], f)
        return

    # 执行类型检查
    type_check_success = type_check_with_error_handling(
        parse_tree_root, "typing_out.json"
    )

    # 根据类型检查结果输出
    if type_check_success:
        # 如果类型检查成功，且已经在类型检查器中输出了 "Semantic Analysis Complete!"
        pass
    else:
        # 如果类型检查失败，已经在类型检查器中输出了 "Type Error!"
        pass

    # 读取并打印 typing_out.json 内容
    try:
        with open("typing_out.json", "r") as f:
            typing_out = json.load(f)
            print(json.dumps(typing_out, indent=4))
    except Exception as e:
        print(f"Error reading typing_out.json: {e}")


if __name__ == "__main__":
    main()
