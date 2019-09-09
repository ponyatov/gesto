
import os,sys

sys.stderr = sys.stdout = open(sys.argv[0][:-3]+'.log','w')

######################################### Marvin Minsky extended frame model

class Frame:
    def __init__(self,V):
        self.type = self.__class__.__name__.lower()
        self.val  = V
        self.slot = {}
        self.nest = []
        self.immed = False

    def __repr__(self):
        return self.dump()
    def dump(self,depth=0,prefix='',voc=True):
        tree = self._pad(depth) + self.head(prefix)
        if not depth: Frame._dumped = []
        if self in Frame._dumped: return tree + ' _/'
        else: Frame._dumped.append(self)
        if voc:
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
    def top(self):
        return self.nest[-1]
    def dropall(self):
        self.nest = []

    def eval(self,ctx):
        ctx // self

class Prim(Frame): pass

class Sym(Prim): pass

class Str(Prim): pass

class Cont(Frame): pass

class Vector(Cont): pass

class Active(Frame): pass

class Cmd(Active):
    def __init__(self,F,I=False):
        Active.__init__(self,F.__name__)
        self.fn = F
        self.immed = I
    def eval(self,ctx):
        self.fn(ctx)

class VM(Active):
    def __init__(self,V):
        Active.__init__(self,V)
        self.compile = []
    def __setitem__(self,key,F):
        if callable(F): self[key] = Cmd(F)
        else: return Active.__setitem__(self,key,F)
    def __lshift__(self,F):
        if callable(F): return self << Cmd(F)
        else: return Active.__lshift__(self,F)

class Meta(Frame): pass

class Module(Meta): pass

class IO(Frame): pass

class File(IO): pass

class Net(IO): pass

class Email(Net): pass
class Url(Net): pass

################################################### FORTH machine

vm = VM('metaL')

######################################################## debug

def BYE(ctx): sys.exit(0)
vm << BYE

def Q(ctx): print ctx.dump(voc=False)
vm['?'] = Q

def QQ(ctx): print ctx.dump(voc=True) ; BYE(ctx)
vm['??'] = QQ

################################################## manipulations

def DOT(ctx): ctx.dropall()
vm['.'] = DOT

def PUSH(ctx): what = ctx.pop() ; ctx.top() // what
vm['//'] = PUSH

def STOR(ctx): addr = ctx.pop().val ; ctx[addr] = ctx.pop()
vm['!'] = STOR

################################################## class wrappers

def MODULE(ctx): ctx // Module(ctx.pop().val)
vm << MODULE

def FILE(ctx): ctx // File(ctx.pop().val)
vm << FILE

def EMAIL(ctx): ctx // Email(ctx.pop().val)
vm << EMAIL

def URL(ctx): ctx // Url(ctx.pop().val)
vm << URL

################################################ no-syntax parser

import ply.lex as lex

tokens = ['sym','str']

t_ignore = ' \t\r\n'
t_ignore_comment = r'[\#].*'

states = (('str','exclusive'),)

t_str_ignore = ''

def t_str(t):
    r'\''
    t.lexer.lexstring = ''
    t.lexer.push_state('str')
def t_str_str(t):
    r'\''
    t.lexer.pop_state()
    return Str(t.lexer.lexstring)
def t_str_any(t):
    r'.'
    t.lexer.lexstring += t.value

def t_sym(t):
    r'[`]|[^ \t\r\n\#]+'
    return Sym(t.value)

def t_ANY_error(t):
    raise SyntaxError(t)

###################################################### interpreter

def QUOTE(ctx): WORD(ctx)
vm['`'] = QUOTE

def WORD(ctx):
    token = ctx.lexer.token()
    if token: ctx // token
    return token

def FIND(ctx):
    token = ctx.pop()
    try: ctx // ctx[token.val] ; return True
    except KeyError: 
        try: ctx // ctx[token.val.upper()] ; return True
        except KeyError: ctx // token ; return False

def EVAL(ctx): ctx.pop().eval(ctx)

def INTERP(ctx):
    ctx.lexer = lex.lex() ; ctx.lexer.input(ctx.pop().val)
    while True:
        if not WORD(ctx): break
        if isinstance(ctx.top(),Sym):
            if not FIND(ctx): print ; raise SyntaxError(ctx.top())
        if not ctx.compile or ctx.top().immed:
            EVAL(ctx)
        else:
            COMPILE(ctx)

########################################################## compiler

def LQ(ctx): ctx.compile += [Vector('')]
vm['['] = Cmd(LQ,I=True)

def RQ(ctx):
    compiled = ctx.compile.pop()
    try: ctx.compile[-1] // compiled
    except IndexError: ctx // compiled
vm[']'] = Cmd(RQ,I=True)

def COMPILE(ctx): ctx.compile[-1] // ctx.pop()

####################################################### system init        

if __name__ == "__main__":
    vm // Str(open(sys.argv[0][:-3]+'.gst').read()) ; INTERP(vm)
