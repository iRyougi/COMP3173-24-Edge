# main.py

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from evaluator import Evaluator
import sys
import json

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python main.py <test_file>")
        sys.exit(1)

    file_name = sys.argv[1]

    with open(file_name, 'r') as f:
        source_code = f.read()
        lexer = Lexer(source_code)
        tokens = lexer.tokens()

        # 将标记转换为字典列表
        tokens_output = [token.to_dict() for token in tokens]

        # 写入 lexer_out.json
        with open('lexer_out.json', 'w') as outfile:
            json.dump(tokens_output, outfile, indent=4)


    # 语义分析
    analyzer = SemanticAnalyzer(ast)
    analyzer.analyze()

    # 输出类型检查结果
    typing_output = {'variables': analyzer.symbol_table, 'errors': []}
    with open('typing_out.json', 'w') as outfile:
        json.dump(typing_output, outfile, indent=4)
        
    # 表达式评估
    evaluator = Evaluator(ast, analyzer.symbol_table)
    evaluator.evaluate()

    # 输出计算结果
    evaluation_output = {'result': evaluator.result}
    with open('evaluation_out.json', 'w') as outfile:
        json.dump(evaluation_output, outfile, indent=4)
