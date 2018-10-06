class Expression:

    IS = ['=']
    OIS = [':=']
    IDX = [':']

    IADD = ['+=']
    ISUB = ['-=']
    IMUL = ['*=']
    ITDIV = ['/=']
    IMAT = ['@=']
    IMOD = ['%=']
    IPOW = ['**=']
    IFDIV = ['//=']

    EQ = ['==']
    NEQ = ['!=']

    GT = ['>']
    GE = ['>=']
    LT = ['<']
    LE = ['<=']

    ADD = ['+']
    SUB = ['-']

    MAT = ['@']

    MUL = ['*']
    TDIV = ['/']
    MOD = ['%']
    FDIV = ['//']

    POW = ['**']

    NUMBER = 'n'
    VARIABLE = 'v'
    TUPLE = 't'
    ABSTRACT_TYPES = [NUMBER, VARIABLE, TUPLE]

    RBO = ['(']
    RBC = [')']
    ABO = ['{']
    ABC = ['}']
    SBO = ['[']
    SBC = [']']

    NEXT = ['next']
    FROM = ['from']
    SAVE = ['save']
    DELETE = ['del']

    REQUIRED = ['required']

    EM = ['!']

    DOT = '.'
    COMMA = ','
    COMMENT = '#'
    BACKSLASH = '\\'
    NEXTLINE = '\n'

    INT = 'i'
    FLOAT = 'f'
    INT_DEFAULT = 'i64'
    FLOAT_DEFAULT = 'f64'

    INDICES = '^'

    # DIR_CURRENT = 'now'
    # DIR_UP = 'up'

    ARRAY = 'array'
    BUILTINS = {ARRAY: NotImplemented, }

    MAGIC_PYTHON = ['py', 'python']

    EXTENSION_SOURCE = 'mp'
    EXTENSION_BINARY = 'mpb'

    Signs = RBO + RBC + ABO + ABC + SBO + SBC + ADD + SUB + MAT + MOD + [DOT, COMMA, COMMENT, BACKSLASH]
    Signs_DoubleSingle = ADD + SUB + MUL + TDIV + MAT + MOD + GT + LT + IS + IDX + EM
    Signs_DoubleDouble = POW + FDIV + GE + LE + EQ + OIS + NEQ + IADD + ISUB + IMUL + ITDIV + IMAT + IMOD
    Signs_DoubleTriple = IPOW + IFDIV
    Signs_Indent = [' ', '\t', ]  # TODO
    Signs_All = Signs + Signs_DoubleSingle + Signs_DoubleDouble + Signs_DoubleTriple

    Tokens_Prefix = NEXT + FROM + SAVE + DELETE
    Tokens_Open = RBO + ABO + SBO
    Tokens_Close = RBC + ABC + SBC
    Tokens_Shell = ['()', '[)', '(]', '[]', '{}', ]  # TODO
    Tokens_Inplace = IADD + ISUB + IMUL + ITDIV + IMAT + IMOD + IPOW + IFDIV + IS + OIS

    Tokens_Order = {
            tuple(IS): 0, tuple(OIS): 0, tuple(IDX): 0,
            tuple(IADD): 0, tuple(ISUB): 0, tuple(IMUL): 0, tuple(ITDIV): 0,
            tuple(IMAT): 0, tuple(IMOD): 0, tuple(IPOW): 0, tuple(IFDIV): 0,
            tuple(EQ): 1, tuple(NEQ): 1,
            tuple(GT): 2, tuple(GE): 2, tuple(LT): 2, tuple(LE): 2,
            tuple(ADD): 3, tuple(SUB): 3,
            tuple(MAT): 4,
            tuple(MUL): 5, tuple(TDIV): 5, tuple(MOD): 5, tuple(FDIV): 5,
            tuple(POW): 6,
            (NUMBER,): 7, (VARIABLE,): 7, (TUPLE,): 7,
            tuple(RBO): 8, tuple(ABO): 8, tuple(SBO): 8,
            ('()',): 8, ('[)',): 8, ('(]',): 8, ('[]',): 8, ('{}',): 8,  # TODO
        }
    Tokens_Order = {op: order for ops, order in Tokens_Order.items() for op in ops}

    MAGIC_CODES = MAGIC_PYTHON + []
