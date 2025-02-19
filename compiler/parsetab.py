
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'COLON COMMENT EQUALS FN LBRACE LET LPAREN NUMBER PRINTLN RBRACE RPAREN STRING SYMBOLstatements : statement\n    | statements statementexpression : STRINGexpression : SYMBOLexpression : NUMBERstatement : COMMENT SYMBOLstatement : SYMBOL LPAREN RPARENstatement : PRINTLN LPAREN expression RPARENstatement : LET SYMBOL COLON SYMBOL EQUALS expressionstatement : FN SYMBOL LPAREN RPAREN LBRACE statements RBRACEstatement : FN SYMBOL LPAREN SYMBOL COLON SYMBOL RPARENstatement : FN SYMBOL LPAREN RPAREN COLON SYMBOLstatement : FN SYMBOL LPAREN SYMBOL COLON SYMBOL RPAREN COLON SYMBOL'
    
_lr_action_items = {'COMMENT':([0,1,2,8,9,14,16,17,18,21,27,29,31,32,33,34,36,],[3,3,-1,-2,-6,-7,-3,-4,-5,-8,3,-9,3,-12,-11,-10,-13,]),'SYMBOL':([0,1,2,3,6,7,8,9,11,14,16,17,18,19,20,21,25,26,27,28,29,31,32,33,34,35,36,],[4,4,-1,9,12,13,-2,-6,17,-7,-3,-4,-5,22,23,-8,17,30,4,32,-9,4,-12,-11,-10,36,-13,]),'PRINTLN':([0,1,2,8,9,14,16,17,18,21,27,29,31,32,33,34,36,],[5,5,-1,-2,-6,-7,-3,-4,-5,-8,5,-9,5,-12,-11,-10,-13,]),'LET':([0,1,2,8,9,14,16,17,18,21,27,29,31,32,33,34,36,],[6,6,-1,-2,-6,-7,-3,-4,-5,-8,6,-9,6,-12,-11,-10,-13,]),'FN':([0,1,2,8,9,14,16,17,18,21,27,29,31,32,33,34,36,],[7,7,-1,-2,-6,-7,-3,-4,-5,-8,7,-9,7,-12,-11,-10,-13,]),'$end':([1,2,8,9,14,16,17,18,21,29,32,33,34,36,],[0,-1,-2,-6,-7,-3,-4,-5,-8,-9,-12,-11,-10,-13,]),'RBRACE':([2,8,9,14,16,17,18,21,29,31,32,33,34,36,],[-1,-2,-6,-7,-3,-4,-5,-8,-9,34,-12,-11,-10,-13,]),'LPAREN':([4,5,13,],[10,11,20,]),'RPAREN':([10,15,16,17,18,20,30,],[14,21,-3,-4,-5,24,33,]),'STRING':([11,25,],[16,16,]),'NUMBER':([11,25,],[18,18,]),'COLON':([12,23,24,33,],[19,26,28,35,]),'EQUALS':([22,],[25,]),'LBRACE':([24,],[27,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'statements':([0,27,],[1,31,]),'statement':([0,1,27,31,],[2,8,2,8,]),'expression':([11,25,],[15,29,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> statements","S'",1,None,None,None),
  ('statements -> statement','statements',1,'p_statements','parser.py',23),
  ('statements -> statements statement','statements',2,'p_statements','parser.py',24),
  ('expression -> STRING','expression',1,'p_expression_string','parser.py',32),
  ('expression -> SYMBOL','expression',1,'p_expression_symbol','parser.py',37),
  ('expression -> NUMBER','expression',1,'p_expression_number','parser.py',42),
  ('statement -> COMMENT SYMBOL','statement',2,'p_statement_comment','parser.py',46),
  ('statement -> SYMBOL LPAREN RPAREN','statement',3,'p_statement_fn0_invoke','parser.py',51),
  ('statement -> PRINTLN LPAREN expression RPAREN','statement',4,'p_statement_println','parser.py',56),
  ('statement -> LET SYMBOL COLON SYMBOL EQUALS expression','statement',6,'p_statement_let','parser.py',62),
  ('statement -> FN SYMBOL LPAREN RPAREN LBRACE statements RBRACE','statement',7,'p_statement_fn_0_void','parser.py',73),
  ('statement -> FN SYMBOL LPAREN SYMBOL COLON SYMBOL RPAREN','statement',7,'p_statement_fn_1_void','parser.py',78),
  ('statement -> FN SYMBOL LPAREN RPAREN COLON SYMBOL','statement',6,'p_statement_fn_0','parser.py',83),
  ('statement -> FN SYMBOL LPAREN SYMBOL COLON SYMBOL RPAREN COLON SYMBOL','statement',9,'p_statement_fn_1','parser.py',88),
]
