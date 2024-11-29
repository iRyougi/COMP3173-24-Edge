from  parser import  SLRParser
def test_parser():
    slr_parser = SLRParser("slr_table.csv")
    tokens = ['let', 'int', 'id', 'be', 'num', '+', 'num', '.']
    syntax_tree = slr_parser.parse(tokens)
    print(syntax_tree)

test_parser()
