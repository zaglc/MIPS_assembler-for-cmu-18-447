from typing import List

# global
REG_LEN = 5
LENGTH = 32

# segment type
sgt_type = {
    ".data": 0x10000000, 
    ".text": 0x00400000,
    ".stack": 0x7ff00000,
    ".kdata": 0x90000000,
    ".ktext": 0x80000000,
}

# decode operands position in one instruction
# op: [opcode, [op_pos...], [second_opc, pos]]
ops_pos_pair = {
    "j": ["000010", [[25, 0]]],
    "jal": ["000011", [[25, 0]]],
    "jr": ["000000", [[25, 21]], ["001000", [5, 0]]],
    # TODO: default rd: 31
    "jalr": ["000000", [[15, 11], [25, 21]], ["001001", [5, 0]]],

    "beq": ["000100", [[25, 21], [20, 16], [15, 0]]],
    "bne": ["000101", [[25, 21], [20, 16], [15, 0]]],
    "blez": ["000110", [[25, 21], [15, 0]]],
    "bgtz": ["000111", [[25, 21], [15, 0]]],
    "bltz": ["000001", [[25, 21], [15, 0]], ["00000", [20, 16]]],
    "bgez": ["000001", [[25, 21], [15, 0]], ["00001", [20, 16]]],
    "bltzal": ["000001", [[25, 21], [15, 0]], ["10000", [20, 16]]],
    "bgezal": ["000001", [[25, 21], [15, 0]], ["10001", [20, 16]]],

    "addi": ["001000", [[20, 16], [25, 21], [15, 0]]],
    "addiu": ["001001", [[20, 16], [25, 21], [15, 0]]],
    "slti": ["001010", [[20, 16], [25, 21], [15, 0]]],
    "sltiu": ["001011", [[20, 16], [25, 21], [15, 0]]],
    "andi": ["001100", [[20, 16], [25, 21], [15, 0]]],
    "ori": ["001101", [[20, 16], [25, 21], [15, 0]]],
    "xori": ["001110", [[20, 16], [25, 21], [15, 0]]],
    "lui": ["001111", [[20, 16], [15, 0]]],
    "add": ["000000", [[15, 11], [25, 21], [20, 16]], ["100000", [5, 0]]],
    "addu": ["000000", [[15, 11], [25, 21], [20, 16]], ["100001", [5, 0]]],
    "sub": ["000000", [[15, 11], [25, 21], [20, 16]], ["100010", [5, 0]]],
    "subu": ["000000", [[15, 11], [25, 21], [20, 16]], ["100011", [5, 0]]],
    "and": ["000000", [[15, 11], [25, 21], [20, 16]], ["100100", [5, 0]]],
    "or": ["000000", [[15, 11], [25, 21], [20, 16]], ["100101", [5, 0]]],
    "xor": ["000000", [[15, 11], [25, 21], [20, 16]], ["100110", [5, 0]]],
    "nor": ["000000", [[15, 11], [25, 21], [20, 16]], ["100111", [5, 0]]],
    "slt": ["000000", [[15, 11], [25, 21], [20, 16]], ["101010", [5, 0]]],
    "sltu": ["000000", [[15, 11], [25, 21], [20, 16]], ["101011", [5, 0]]],
    "mult": ["000000", [[25, 21], [20, 16]], ["011000", [5, 0]]],
    "multu": ["000000", [[25, 21], [20, 16]], ["011001", [5, 0]]],
    "div": ["000000", [[25, 21], [20, 16]], ["011010", [5, 0]]],
    "divu": ["000000", [[25, 21], [20, 16]], ["011011", [5, 0]]],

    "lb": ["100000", [[20, 16], [15, 0], [25, 21]]], 
    "lbu": ["100100", [[20, 16], [15, 0], [25, 21]]], 
    "lh": ["100001", [[20, 16], [15, 0], [25, 21]]], 
    "lhu": ["100101", [[20, 16], [15, 0], [25, 21]]], 
    "lw": ["100011", [[20, 16], [15, 0], [25, 21]]], 
    "sb": ["101000", [[20, 16], [15, 0], [25, 21]]], 
    "sh": ["101001", [[20, 16], [15, 0], [25, 21]]], 
    "sw": ["101011", [[20, 16], [15, 0], [25, 21]]],
    "mfhi": ["000000", [[15, 11]], ["010000", [5, 0]]],
    "mflo": ["000000", [[15, 11]], ["010010", [5, 0]]],
    "mthi": ["000000", [[25, 21]], ["010001", [5, 0]]],
    "mtlo": ["000000", [[25, 21]], ["010011", [5, 0]]],

    "sll": ["000000", [[15, 11], [20, 16], [10, 6]], ["000000", [5, 0]]],
    "srl": ["000000", [[15, 11], [20, 16], [10, 6]], ["000010", [5, 0]]],
    "sra": ["000000", [[15, 11], [20, 16], [10, 6]], ["000011", [5, 0]]],
    "sllv": ["000000", [[15, 11], [20, 16], [25, 21]], ["000100", [5, 0]]],
    "srlv": ["000000", [[15, 11], [20, 16], [25, 21]], ["000110", [5, 0]]],
    "srav": ["000000", [[15, 11], [20, 16], [25, 21]], ["000111", [5, 0]]],

    "syscall": ["000000", [], ["001100", [5, 0]]],
}

# name of register
register_name = {
    "zero": 0,
    "at": 1,
    "v0": 2, "v1": 3,
    "a0": 4, "a1": 5, "a2": 6, "a3": 7,
    "t0": 8, "t1": 9, "t2": 10, "t3": 11, "t4": 12, "t5": 13, "t6": 14, "t7": 15,
    "s0": 16, "s1": 17, "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22, "s7": 23,
    "t8": 24, "t9": 25,
    "k0": 26, "k1": 27,
    "gp": 28,
    "sp": 29,
    "fp": 30,
    "ra": 31,
}

# convert a single sentence into list of opcode and operands
def process_line(line: str) -> list[str]:
    pos = 0
    ret = []

    for i in range(len(line)):
        if line[i] in {"\t", "\n", " ", ",", "(", ")"}:
            if i > pos:
                ret.append(line[pos:i])
            pos = i+1

    if pos != len(line):
        ret.append(line[pos:len(line)])
    
    return ret

# convert biniary string code to heximal string code
def bin2hex(line: str):
    if len(line) % 4 != 0:
        line = "0"*(len(line) // 4) + line
    
    res = ""
    for i in range(0, len(line), 4):
        code = line[i:i+4]
        r = int(code[0]) * 8 + int(code[1]) * 4 + int(code[2]) * 2 + int(code[3])
        res += hex(r)[2:]

    return res

# convert raw string op to binary with appropriate length 
def ops2code(op: str):
    if op in list(register_name.keys()):
        ret = register_name[op]
    elif op in list([str(i) for i in range(32)]):
        ret = int(op)
    else:
        raise ValueError(f"{op} is invalid, support {list(register_name.keys())}")
    
    ret = bin(ret)[2:]
    ret = "0"*(REG_LEN - len(ret)) + ret

    return ret

# convert raw immidiate num to binary
def imm2code(imm: str, bit: int):
    if imm.startswith("0x"):
        ret = int(imm, 16)
    elif imm.startswith("0b"):
        ret = int(imm, 2)
    else:
        ret = int(imm)

    if ret > (1 << bit) - 1 or ret < -(1 << bit):
        raise ValueError(f"{ret} out of range {-(1 << bit)}-{(1 << bit) - 1}")
    
    if ret == -(1 << bit):
        ret = "1" + "0" * (bit - 1)
    elif ret < 0:
        ret = bin(ret)[3:]
        ret = "0"*(bit-len(ret)) + ret
        flag = 0
        res = ""
        for i in range(len(ret)-1, -1, -1):
            if ret[i] == "0" and flag:
                res = "1" + res
            elif ret[i] == "1" and flag:
                res = "0" + res
            elif ret[i] == "1" and not flag:
                flag = 1
                res = "1" + res
            else:
                res = "0" + res
        ret = res
    else:
        ret = bin(ret)[2:]
        ret = "0"*(bit-len(ret)) + ret

    return ret

# convert label addr to binary
def label2code(addr: int, label: int, bit: int):
    msk = int("0b"+"1"*(LENGTH-bit)+"0"*(bit), 2)
    if (msk & addr == msk & label):
        ret = str(bin((label % msk) // 4)[2:])
    else:
        raise ValueError(f"unable to jump from {hex(addr)} to {hex(label)}")
    ret = "0"*(bit-len(ret)) + ret
    return ret
