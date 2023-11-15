from typing import List

# Tokens
LPAREN = 0
RPAREN = 1
DIGITS = 2
DOT = 3
PLUS = 4
MINUS = 5
TIMES = 6
DIVIDE = 7
EXPONENT = 8
WORD = 9
EOF = 10
LET = 11
EQ = 12
IN = 13
COMMA = 14

# Tree Labels
Add = 0
Sub = 1
Mul = 2
Div = 3
Pow = 4
Num = 5
Var = 6
Fun = 7
Let = 8
Def = 9
Tup = 10

def _show_tree(tree):
    if(type(tree) is not tuple):
        print(tree, end="")
        return
    tokens = ["Add", "Sub", "Mul", "Div", "Pow", "Num", "Var", "Fun", "Let", "Def", "Tup"]
    print(tokens[tree[0]] + "(", end="")
    for i, v in enumerate(tree[1:]):
        if i != 0:
            print(", ", end="")
        _show_tree(v)
    print(")", end="")

def show_tree(tree):
    _show_tree(tree)
    print()


class LinkedList:
    def __init__(self, value, rest=None):
        self.value = value
        self.next = rest
    def __radd__(self, other):
        return LinkedList(other, self)
    def __iter__(self):
        current = self
        while current is not None and current.value != (EOF,):
            yield current.value
            current = current.next
    def next(self):
        return self.next
    def value(self):
        return self.value
    def __eq__(self, other):
        return self.value == other
    def __str__(self):
        return str(self.value) + " -> " + (str(self.next) if self.next is not None else "end")
    def __repr__(self):
        return self.value.__repr__() + " -> " + (self.next.__repr__() if self.next is not None else "END")
    

def lex(string: str) -> LinkedList:
    if string == "": return LinkedList((EOF,))
    if string[0] in {"\t", "\n", " "}: return lex(string[1:])
    if string.startswith("("):
        return (LPAREN,) + lex(string[1:])
    if string.startswith(")"):
        return (RPAREN,) + lex(string[1:])
    if string.startswith("."):
        return (DOT,) + lex(string[1:])
    if string.startswith("+"):
        return (PLUS,) + lex(string[1:])
    if string.startswith("-"):
        return (MINUS,) + lex(string[1:])
    if string.startswith("*"):
        return (TIMES,) + lex(string[1:])
    if string.startswith("/"):
        return (DIVIDE,) + lex(string[1:])
    if string.startswith("^"):
        return (EXPONENT,) + lex(string[1:])
    if string.startswith("="):
        return (EQ,) + lex(string[1:])
    if string.startswith(","):
        return (COMMA,) + lex(string[1:])
    if string[0].isdigit():
        i = 1
        while i <= len(string) and string[:i].isdigit(): i += 1
        return (DIGITS, string[:i-1]) + lex(string[i-1:])
    if string[0].isalpha():
        i = 1
        while i <= len(string) and string[:i].isalpha(): i += 1
        if string[:i-1] == "let":
            return (LET,) + lex(string[i-1:])
        if string[:i-1] == "in":
            return (IN,) + lex(string[i-1:])
        return (WORD, string[:i-1]) + lex(string[i-1:])
    raise ValueError(f"Lexing Failed, token invalid: {string[0]}")

'''
Context Free Grammar:
L -> let V = A in A | let F V = A in A | A
A -> A + M | A - M | M
M -> M * E | M / E | E
E -> E ^ P | P
P -> (L) | N | -N | V | F P | let V = A in A | let F V = A in A
N -> d.d | d | .d
V -> w
F -> w
'''

def parse_N(tokens):
    if tokens[-1][0] != DIGITS:
        return None, None
    if len(tokens) == 1:
        return (Num, tokens[-1][1], "0"), []
    if tokens[-2][0] != DOT:
        return (Num, tokens[-1][1], "0"), tokens[:-1]
    if len(tokens) == 2:
        return (Num, "0", tokens[-1][1]), []
    if tokens[-3][0] != DIGITS:
        return (Num, "0", tokens[-1][1]), tokens[:-2]
    if len(tokens) == 3:
        return (Num, tokens[-3][1], tokens[-1][1]), []
    return (Num, tokens[-3][1], tokens[-1][1]), tokens[:-3]

def parse_P(tokens):
    if tokens[-1][0] == WORD:
        if len(tokens) > 1 and tokens[-2][0] == WORD:
            return (Fun, tokens[-2][1], (Var, tokens[-1][1])), tokens[:-2]
        return (Var, tokens[-1][1]), tokens[:-1]
    
    # Assume N
    N, rem = parse_N(tokens)
    if N is not None:
        if len(rem) > 0 and rem[-1][0] == MINUS:
            N = (N[0], "-"+N[1], N[2])
            rem = rem[:-1]
        if len(rem) == 0:
            return N, []
        # either N or F N
        if rem[-1][0] == WORD:
            return (Fun, rem[-1][1], N), rem[:-1]
        return N, rem
    if tokens[-1][0] == RPAREN:
        if len(tokens) > 1 and tokens[-2][0] == LPAREN:
            if len(tokens) > 2 and tokens[-3][0] == WORD:
                return (Fun, tokens[-3][1], (Tup,)), tokens[:-3]
            return (Tup,), tokens[:-2]
        istup = False
        if len(tokens) > 1 and tokens[-2][0] == COMMA:
            istup = True
            tokens.pop(-2)
        L, rem = parse_L(tokens[:-1])
        if len(rem) > 0 and rem[-1][0] == LPAREN:
            if istup: L = (Tup, L)
            if len(rem) > 1 and rem[-2][0] == WORD:
                return (Fun, rem[-2][1], L), rem[:-2]
            return L, rem[:-1]
        elif len(rem) > 0 and rem[-1][0] == COMMA:
            gentup = LinkedList(L)
            while(len(rem) > 0 and rem[-1][0] == COMMA):
                L, rem = parse_L(rem[:-1])
                gentup = L + gentup
            if len(rem) > 0 and rem[-1][0] == LPAREN:
                if len(rem) > 1 and rem[-2][0] == WORD:
                    return (Fun, rem[-2][1], (Tup,) + tuple(gentup)), rem[:-2]
                return (Tup,) + tuple(gentup), rem[:-1]
        else:
            raise ValueError(f"Parsing Failed in P, saw closing parenthesis without opening parenthesis")
    if tokens[-1][0] == EQ:
        raise ValueError(f"Invalid use of \"=\"")
    else:
        raise ValueError(f"Parsing Failed in P, no match to digit, function call, or parenthesized statement")

def parse_E(tokens):
    P, rem = parse_P(tokens)
    if rem == []: return P, rem
    if rem[-1][0] == EXPONENT:
        E, rem = parse_E(rem[:-1])
        return (Pow, E, P), rem
    else:
        return P, rem


def parse_M(tokens):
    E, rem = parse_E(tokens)
    if rem == []: return E, rem
    if rem[-1][0] == TIMES:
        M, rem = parse_M(rem[:-1])
        return (Mul, M, E), rem
    if rem[-1][0] == DIVIDE:
        M, rem = parse_M(rem[:-1])
        return (Div, M, E), rem
    else:
        return E, rem

def parse_A(tokens):
    M, rem = parse_M(tokens)
    if rem == []: return M, rem
    if rem[-1][0] == PLUS:
        A, rem = parse_A(rem[:-1])
        return (Add, A, M), rem
    if rem[-1][0] == MINUS:
        A, rem = parse_A(rem[:-1])
        return (Sub, A, M), rem
    return M, rem

def parse_L(tokens):
    A, rem = parse_A(tokens)
    if len(rem) == 0 or rem[-1][0] != IN:
        return A, rem
    A2, rem = parse_A(rem[:-1])
    if len(rem) == 0 or rem[-1][0] != EQ:
        raise ValueError(f"Parsing Failed, saw \"in\" but not \"=\"")
    if len(rem) < 3:
        raise ValueError(f"Invalid Use of \"=\"")
    if len(rem) == 3:
        bind = True
    else:
        if rem[-3][0] == WORD:
            bind = False
        else:
            bind = True
    if bind:
        if rem[-3][0] == LET and rem[-2][0] == WORD and rem[-1][0] == EQ:
            return (Let, rem[-2][1], A2, A), rem[:-3]
        else:
            print(rem)
            raise ValueError(f"Invalid let binding")
    else:
        if len(rem) < 4:
            raise ValueError(f"Invalid Use of \"=\"")
        if rem[-4][0] == LET and rem[-3][0] == WORD and rem[-2][0] == WORD and rem[-1][0] == EQ:
            return (Def, rem[-3][1], rem[-2][1], A2, A), rem[:-4]
        else:
            raise ValueError(f"Invalid let binding")

def parse(tokens):
    parsed, remaining = parse_L(list(tokens))
    if remaining != []:
        raise ValueError(f"Parsing Failed, trailing tokens {remaining}")
    return parsed

def evaluate(tree, funs, var):
    match tree[0]:
        case 0: # Add
            return evaluate(tree[1], funs, var) + evaluate(tree[2], funs, var)
        case 1: # Sub
            return evaluate(tree[1], funs, var) - evaluate(tree[2], funs, var)
        case 2: # Mul
            return evaluate(tree[1], funs, var) * evaluate(tree[2], funs, var)
        case 3: # Div
            return evaluate(tree[1], funs, var) / evaluate(tree[2], funs, var)
        case 4: # Pow
            return evaluate(tree[1], funs, var) ** evaluate(tree[2], funs, var)
        case 5: # Num
            if tree[2] == "0":
                return int(tree[1])
            return float(tree[1]+"."+tree[2])
        case 6: # Var
            if tree[1] in var:
                return var[tree[1]]
            else:
                raise NameError(f"name '{tree[1]}' is not defined")
        case 7: # Fun
            if tree[1] in funs:
                return funs[tree[1]](evaluate(tree[2], funs, var))
            else:
                raise NameError(f"name '{tree[1]}' is not defined")
        case 8: # Let
            new_var = dict(var)
            new_var[tree[1]] = evaluate(tree[2], funs, var)
            return evaluate(tree[3], funs, new_var)
        case 9: # Def
            new_funs = dict(funs)
            def this_fun(parameter):
                new_var = dict(var)
                new_var[tree[2]] = parameter
                return evaluate(tree[3], funs, new_var)
            new_funs[tree[1]] = this_fun
            return evaluate(tree[4], new_funs, var)
        case 10: # Tup
            return tuple((evaluate(subtree, funs, var) for subtree in tree[1:]))
        case _: raise ValueError(f"Invalid tree option {tree[0]}")

def repl_run(command, funs, var):
    try:
        lexed = lex(command)
    except ValueError as e:
        print("!!!", e)
        return None
    try:
        parsed = parse(lexed)
    except ValueError as e:
        print("!!!", e)
        return None
    try:
        result = evaluate(parsed, funs, var)
    except Exception as e:
        print("!!!", e)
        return None
    return result
'''
def use_module(module, funs):
    with open(module, "r")
'''

def use_defaults(funs, var):
    import math
    funs["sin"] = math.sin
    funs["sinh"] = math.sinh
    funs["asin"] = math.asin
    funs["asinh"] = math.asinh
    funs["cos"] = math.cos
    funs["cosh"] = math.cosh
    funs["acos"] = math.acos
    funs["acosh"] = math.acosh
    funs["tan"] = math.tan
    funs["tanh"] = math.tanh
    funs["atan"] = math.atan
    funs["atanh"] = math.atanh
    funs["ceil"] = math.ceil
    funs["abs"] = math.fabs
    funs["factorial"] = math.factorial
    funs["floor"] = math.floor
    funs["trunc"] = math.trunc
    funs["ln"] = math.log
    funs["lg"] = math.log2
    funs["log"] = math.log10
    funs["sqrt"] = math.sqrt
    funs["degrees"] = math.degrees
    funs["radians"] = math.radians
    funs["erf"] = math.erf
    funs["gamma"] = math.gamma
    var["pi"] = math.pi
    var["e"] = math.e
    var["tau"] = math.tau
    funs["print"] = lambda a: print(*a)



if __name__ == "__main__":
    funs = {}
    var = {}
    use_defaults(funs, var)
    running = True
    while running:
        cmd = input("\n~ ")
        if cmd[0] == "#":
            if cmd.upper() in {"#EXIT", "#QUIT"}:
                print("Goodbye!")
                running = False
            elif cmd.upper().startswith("#SETVAR") and (cmd[7] == " " if len(cmd) >= 8 else True):
                if len(cmd) <= 8:
                    print("Usage: #SETVAR x")
                    continue
                cmd = cmd[8:]
                if cmd.isalpha():
                    val = repl_run(input(f"Set {cmd} to ~ "), funs, var)
                    if val is not None:
                        print(f"{cmd} <- {val}")
                        var[cmd] = val
                else:
                    print("Usage: #SETVAR x\nx must be only alphabetical characters")
                '''elif cmd.upper().startswith("#DEFINE") and (cmd[7] == " " if len(cmd) >= 8 else True):
                    if len(cmd) <= 8:
                        print("Usage: #DEFINE func x")
                        continue
                    cmd = cmd[8:]
                    cmd = cmd.split(" ")
                    if len(cmd) != 2:
                        print("Usage: #DEFINE func x")
                        continue'''
                
            else:
                print("Invalid # Directive")
        else:
            val = repl_run(cmd, funs, var)
            if val is not None:
                print(f"-> {val}")

