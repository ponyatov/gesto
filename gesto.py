
import os,sys

class Frame:
    def __init__(self,V):
        self.val  = V
        self.nest = []
    def __floordiv__(self,that):
        self.nest.append(that) ; return self
    def pop(self):
        return self.nest.pop(-1)

class Prim(Frame): pass

class Sym(Prim): pass

class Str(Prim): pass

class Active(Frame): pass

class VM(Active): pass

vm = VM('metaL')

import ply.lex as lex

tokens = ['sym']

t_ignore = ' \t\r\n'
t_ignore_comment = r'[\#].*'

def t_sym(t):
    r'[^ \t\r\n\#]+'
    return Sym(t.value)

def t_error(t):
    raise SyntaxError(t)

def INTERP(ctx):
    ctx.lexer = lex.lex() ; ctx.lexer.input(ctx.pop().val)
    while True:
        token = ctx.lexer.token()
        if not token: break
        print token

if __name__ == "__main__":
    vm // Str(open(sys.argv[0]+'.ini').read()) ; INTERP(vm)

