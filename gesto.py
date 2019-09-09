
import os,sys

class Frame:
    def __init__(self,V):
        self.type = self.__class__.__name__.lower()
        self.val  = V
        self.slot = {}
        self.nest = []

    def __repr__(self):
        return self.dump()
    def dump(self,depth=0,prefix=''):
        tree = self._pad(depth) + self.head(prefix)
        for i in self.slot:
            tree += self.slot[i].dump(depth+1,prefix=i+' = ')
        for j in self.nest:
            tree += j.dump(depth+1)
        return tree
    def head(self,prefix=''):
        return '%s<%s:%s> @%x' % (prefix,self.type,self._val(),id(self))
    def _pad(self,depth):
        return '\n' + '\t' * depth
    def _val(self):
        return str(self.val)
    
    def __getitem__(self,key):
        return self.slot[key]
    def __setitem__(self,key,that):
        self.slot[key] = that ; return self
    def __lshift__(self,that):
        self[that.val] = that ; return self
    def __floordiv__(self,that):
        self.nest.append(that) ; return self

    def pop(self):
        return self.nest.pop(-1)

class Prim(Frame): pass

class Sym(Prim): pass

class Str(Prim): pass

class Active(Frame): pass

class Cmd(Active):
    def __init__(self,F):
        Active.__init__(self,F.__name__)

class VM(Active):
    def __setitem__(self,key,F):
        if callable(F): self[key] = Cmd(F)
        else: return Active.__setitem__(self,key,F)
    def __lshift__(self,F):
        if callable(F): return self << Cmd(F)
        else: return Active.__lshift__(self,F)

################################################### FORTH machine

vm = VM('metaL')

######################################################## debug

def BYE(ctx): sys.exit(0)
vm << BYE

def Q(ctx): print ctx
vm['?'] = Q

################################################ no-syntax parser

import ply.lex as lex

tokens = ['sym']

t_ignore = ' \t\r\n'
t_ignore_comment = r'[\#].*'

def t_sym(t):
    r'[^ \t\r\n\#]+'
    return Sym(t.value)

def t_error(t):
    raise SyntaxError(t)

###################################################### interpreter

def WORD(ctx):
    token = ctx.lexer.token()
    if token: ctx // token
    return token

def FIND(ctx):
    token = ctx.pop()
    ctx // ctx[token.val] ; return True
    return False

def INTERP(ctx):
    ctx.lexer = lex.lex() ; ctx.lexer.input(ctx.pop().val)
    while True:
        if not WORD(ctx): break
        if not FIND(ctx): raise SyntaxError(ctx)
        print vm

####################################################### system init        

if __name__ == "__main__":
    vm // Str(open(sys.argv[0]+'.ini').read()) ; INTERP(vm)

