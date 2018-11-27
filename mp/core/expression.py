class Expression:

    IS = ['=']
    DIS = [':=']
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

    SHELL_RR = ['()']
    SHELL_SS = ['[]']
    SHELL_AA = ['{}']

    FROM = ['from']
    SAVE = ['save']
    DELETE = ['del']
    PRINT = ['print']

    METHOD = ['def']
    REQUIRED = ['required']

    INDENT = [' ', '\t', ]

    EM = ['!']

    DOT = '.'
    COMMA = ','
    COMMENT = '#'
    BACKSLASH = '\\'
    NEXTLINE = '\n'

    BOOL = 'b'
    INT = 'i'
    FLOAT = 'f'
    INT_DEFAULT = 'i64'
    FLOAT_DEFAULT = 'f32'

    INDICES = '^'

    CODE_CONST = '/'
    CODE_PLACEHOLDER = '__placeholder__'
    CODE_SELF = 'self%s' % DOT
    CODE_PARAM = '$'

    # DIR_CURRENT = 'now'
    # DIR_UP = 'up'

    TENSOR = 'tensor'
    EVENT = None

    EXTENSION_SOURCE = 'mp'
    EXTENSION_BINARY = 'npy'

    Signs = RBO + RBC + ABO + ABC + SBO + SBC + ADD + SUB + MAT + MOD + [DOT, COMMA, COMMENT, BACKSLASH]
    Signs_DoubleSingle = ADD + SUB + MUL + TDIV + MAT + MOD + GT + LT + IS + IDX + EM
    Signs_DoubleDouble = POW + FDIV + GE + LE + EQ + DIS + NEQ + IADD + ISUB + IMUL + ITDIV + IMAT + IMOD
    Signs_DoubleTriple = IPOW + IFDIV
    Signs_All = Signs + Signs_DoubleSingle + Signs_DoubleDouble + Signs_DoubleTriple

    Tokens_Operator = IS + DIS + IDX + IADD + ISUB + IMUL + ITDIV + IMAT + IMOD + IPOW + IFDIV + \
                      EQ + NEQ + GT + GE + LT + LE + ADD + SUB + MAT + MUL + TDIV + MOD + FDIV + POW

    Tokens_Prefix = FROM + SAVE + DELETE + PRINT
    Tokens_Open = RBO + ABO + SBO
    Tokens_Close = RBC + ABC + SBC
    Tokens_Shell = SHELL_RR + SHELL_SS + SHELL_AA
    Tokens_Inplace = IADD + ISUB + IMUL + ITDIV + IMAT + IMOD + IPOW + IFDIV + IS + DIS

    Tokens_Order = {
            tuple(IS): 0, tuple(DIS): 0, tuple(IDX): 0,
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
            tuple(SHELL_RR): 8, tuple(SHELL_SS): 8, tuple(SHELL_AA): 8,
    }
    Tokens_Order = {op: order for ops, order in Tokens_Order.items() for op in ops}

    Tokens_In2Out = {
            tuple(IADD): ADD[0], tuple(ISUB): SUB[0], tuple(IMUL): MUL[0], tuple(ITDIV): TDIV[0],
            tuple(IMAT): MAT[0], tuple(IMOD): MOD[0], tuple(IPOW): POW[0], tuple(IFDIV): FDIV[0],
    }
    Tokens_In2Out = {op: order for ops, order in Tokens_In2Out.items() for op in ops}

    Tokens_Shell_Pair = {
        tuple(RBO): tuple(RBC),
        tuple(SBO): tuple(SBC),
        tuple(ABO): tuple(ABC),
    }

    TYPES_DEFAULT = [INT_DEFAULT, FLOAT_DEFAULT, ]
