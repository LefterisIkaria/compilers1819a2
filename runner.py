import plex

class RunError(Exception):
    pass
class ParseError(Exception):
    pass

class MyParser:
    def __init__(self):
        letter = plex.Range('azAZ')
        and_operatorop = plex.Str('and')
        or_operatorop = plex.Str('or')
        xor_operatorop = plex.Str('xor')
        num = plex.Range('09')
        digit = plex.Range('01')
        ID = letter + plex.Rep(letter|digit)
        space = plex.Any(' \n\t')
        Keyword = plex.Str('print','PRINT')
        binary= plex.Rep1(digit)
        equals = plex.Str( '=')
        parethensys1 = plex.Str('(')
        parethensys2 = plex.Str(')')
        self.varList={}
        self.lexicon = plex.Lexicon([
            (Keyword, 'PRINT'),
            (and_operatorop, plex.TEXT),
            (or_operatorop, plex.TEXT),
            (xor_operatorop, plex.TEXT),
            (ID, 'IDENTIFIER'),             #name = letter + plex.Rep(letter|digit)
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
        #print(self.la)
        if self.la == token:
            self.la,self.text=self.next_token()
        else:
            raise ParseError("found {} instead of {}".format(self.la,token))
            

    def parse(self,fp):
        self.createScanner(fp)
        self.stmt_list()
        
    def stmt_list(self):
        if self.la == 'IDENTIFIER' or self.la == 'PRINT' : #first set: id,print
            self.stmt()
            self.stmt_list()
        elif self.la == None: #follow set: None
            return
        else: #Error
            raise ParseError('Expected id or print')
            
    def stmt(self):
        if self.la == 'IDENTIFIER': #first,follow set: id,print
            varname = self.text
            self.match('IDENTIFIER')
            self.match('=')
            e = self.expr()
            
            self.varList[varname] = e
            return {'type' : '=', 'text' : varname, 'expr' : e}
        elif self.la == 'PRINT': #first,follow set: id,print
            self.match('PRINT')
            e = self.expr()
            print('= {:b}'.format(e))
            return {'type' : 'print' , 'expr' : e}
        else: #Error
            raise ParseError('Expected id or print')
    
    def expr(self):
        if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIN_NUM' : #first set: ( , id , binary number
            t = self.term()
            while self.la == 'xor':
                self.match('xor')
                t2 = self.term()
                print('{:b} xor {:b} '.format(t,t2))
                t = t^t2
            if self.la == ')' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None:
                return t
            raise ParseError('Expected "xor" operator')
        else: #Error
            raise ParseError('Expected parethensys,id or binary number')
            
    def term(self):
        if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIN_NUM': #first set: (,id,binary number
            f = self.factor()
            while self.la == 'or':
                self.match('or')
                f2 = self.factor()
                print('{:b} or {:b} '.format(f,f2))
                f = f|f2
            if self.la == ')' or self.la == 'xor' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None:
                return f
            raise ParseError('Expected "or" operator')
        else: #Error
            raise ParseError('Expected parethensys, id or binary number')
            
    def factor(self):
        if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIN_NUM' : #first set: ( , id , binary number
            a = self.atom()
            while self.la == 'and':
                self.match('and')
                a2 = self.atom()
                print('{:b} and {:b} '.format(a,a2))
                a = a&a2
            if self.la == ')' or self.la == 'or' or self.la == 'xor' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None:
                return a
            raise ParseError('Expected "and" operator')
        else: #Error
            raise ParseError('Expected parethensys, opperation or binary number')
            
    def atom(self):
        if self.la == '(' : #first set: ( , id , binary number
            self.match('(')
            e = self.expr()
            self.match(')')
            return(e)
        elif self.la == 'IDENTIFIER' :
            varname = self.text
            self.match('IDENTIFIER')
            if varname in self.varList:
                return self.varList[varname]
            raise RunError("no variable name")
        elif self.la == 'BIN_NUM' :
            BIN_NUM = int(self.text,2)
            self.match('BIN_NUM')
            return (BIN_NUM)
        else: #Error
            raise ParseError('Expected parethensys, id or binary number')
    
parser = MyParser()

with open('input.txt', 'r') as fp:
    parser.parse(fp)