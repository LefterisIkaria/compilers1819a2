import plex

class RunError(Exception):
    pass
class ParseError(Exception):
    pass

class MyParser:
    def __init__(self):
        letter = plex.Range('azAZ')
        num = plex.Range('09')
        and_operator = plex.Str('and')
        or_operator = plex.Str('or')
        xor_operator = plex.Str('xor')
        digit = plex.Range('01')
        IDsymbol = letter + plex.Rep(letter|num)
        space = plex.Any(' \n\t')
        Keyword = plex.Str('print','PRINT')
        binary= plex.Rep1(digit)
        equals = plex.Str( '=')
        parethensys1 = plex.Str('(')
        parethensys2 = plex.Str(')')
        self.varList={}
        
        self.lexicon = plex.Lexicon([
            (Keyword, 'PRINT'),
            (and_operator, plex.TEXT),
            (or_operator, plex.TEXT),
            (xor_operator, plex.TEXT),
            (IDsymbol, 'IDENTIFIER'),             
            (binary, 'BIN_NUM'),
            (equals, '='),
            (parethensys1, '('),
            (parethensys2, ')'),
            (space, plex.IGNORE)			
        ])
        
    def createScanner(self,fp):
        self.scanner = plex.Scanner(self.lexicon,fp)
        self.la,self.text = self.next_token()

    def next_token(self):
        return self.scanner.read()
    
    def match(self,token):
        if self.la == token:
            self.la,self.text=self.next_token()
        else:
            raise ParseError("found {} instead of {}".format(self.la,token))
            
    def parse(self,fp):
        self.createScanner(fp)
        self.stmt_list()
        
    def stmt_list(self):
        if self.la == 'IDENTIFIER' or self.la == 'PRINT' : 
            self.stmt()
            self.stmt_list()
        elif self.la == None: 
            return
        else: 
            raise ParseError('Expected ID or print')
            
    def stmt(self):
        if self.la == 'IDENTIFIER': 
            varname = self.text
            self.match('IDENTIFIER')
            self.match('=')
            e = self.expr()
            self.varList[varname] = e
        elif self.la == 'PRINT': 
            self.match('PRINT')
            self.expr()
        else: 
            raise ParseError('Expected ID or print')
    
    def expr(self):
        if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIN_NUM' : 
            self.term()
            self.term_tail()
        elif self.la == ')' or self.la == 'IDENTIFIER' or self.la == None or self.la == 'PRINT' : 
            return self.term()
        else: 
            raise ParseError('Expected parethensys,ID or binary number')
            
    def term_tail(self):
        if self.la == 'xor': 
            self.match('xor')
            self.term()
            self.term_tail()
        elif self.la == ')' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None: 
            return
        else: 
            raise ParseError('Expected opperation')
            
    def term(self):
        if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIN_NUM': 
            self.factor()
            self.factor_tail()
        else: 
            raise ParseError('Expected parethensys,ID or binary number')
            
    def factor_tail(self):
        if self.la == 'or' : 
            self.match('or')
            self.factor()
            self.factor_tail()
        elif self.la == ')' or self.la == 'xor' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None: 
            return
        else: 
            raise ParseError('Expected an opperation')
            
    def factor(self):
        if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIN_NUM' : 
            self.atom()
            self.atom_tail()
        else: 
            raise ParseError('Expected parethensys,opperation or binary number')
            
    def atom_tail(self):
        if self.la == 'and' : 
            self.match('and')
            self.atom()
            self.atom_tail()
        elif self.la == ')' or self.la == 'or' or self.la == 'xor' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None: 
            return
        else: 
            raise ParseError('Expected opperation')
            
    def atom(self):
        if self.la == '(' : 
            self.match('(')
            e = self.expr()
            self.match(')')
            return(e)
        elif self.la == 'IDENTIFIER' :
            varname = self.text
            self.match('IDENTIFIER')
            if varname in self.varList:
                return self.varList[varname]
            raise RunError("no value")
        elif self.la == 'BIN_NUM' :
            BIN_NUM = self.text
            self.match('BIN_NUM')
            return BIN_NUM
        else: #Error
            raise ParseError('Expected parethensys, ID or binary number')

parser = MyParser()

with open('input.txt', 'r') as fp:
    parser.parse(fp)