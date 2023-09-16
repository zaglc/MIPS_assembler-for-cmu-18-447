import os
import re

from utils import (
    LENGTH,
    bin2hex,
    imm2code,
    ops2code,
    ops_pos_pair,
    process_line,
    sgt_type,
    label2code,
)


class MIPS:
    def __init__(self, assembly_file = None) -> None:
        # start addr of segmemtation, like `.text`
        self.addr_start = None

        # map from physical addr(int) to label(str), op(str) and operands(List(str))
        self.label_dict = dict()
        self.op_dict = dict()
        self.operands_dict = dict()

        # store final result
        self.inst_store = dict()

        # init from given file
        if assembly_file is not None:
            self._init_from_file(assembly_file)

    def reset(self):
        self.label_dict = dict()
        self.op_dict = dict()
        self.operands_dict = dict()
        self.inst_store = dict()


    def _init_from_file(self, filename: str):
        # assemble only
        assert filename.endswith((".s", ".S")), f"only assemble file end with .s or .S supported, not {filename.split('.')[-1]}"
        
        # read file
        with open(filename, "r") as f:
            # base addr
            while True:
                head = f.readline().lower()
                head = re.sub("\s", "", head)
                if not head.startswith("#"):
                    break
            
            if head in sgt_type:
                self.addr_start = sgt_type[head]
            else:
                raise ValueError(f"segmemt types contain {list(sgt_type.keys())}, not include {head}")
            
            # assembly code
            codes = f.readlines()
            counter = self.addr_start
            for idx, line in enumerate(codes):
                ops = process_line(line)
                if len(ops) == 0: continue

                if ops[0].endswith(":"):
                    label = ops.pop(0)
                    self.label_dict.update({label[:-1]: counter})
                if len(ops) == 0: continue

                # remove notes
                if ops[0].startswith("#"): continue

                opcode = ops.pop(0)
                if opcode.lower() in list(ops_pos_pair.keys()):
                    self.op_dict.update({counter: opcode.lower()})
                else:
                    raise ValueError(f"instruction in line {idx}, {opcode} is not defined, support {list(ops_pos_pair.keys())}")
                
                self.operands_dict.update({counter: ops})
                counter += (LENGTH // 8)


    def _single_inst_gen(self, addr: int):
        # generate single inst.
        info = ops_pos_pair[self.op_dict[addr]]
        
        # opcode and operands
        ret = info[0] + "0" * (LENGTH - len(info[0]))
        assert len(info[1]) == len(self.operands_dict[addr]), f"expect {len(info[1])} args but get {self.operands_dict[addr]}"

        for rng, op in zip(info[1], self.operands_dict[addr]):
            if op.startswith("$"):
                op = ops2code(op[1:])

            elif op in list(self.label_dict.keys()):
                if self.op_dict[addr] in {"j", "jal"}:
                    op = label2code(addr, self.label_dict[op], rng[0] - rng[1] + 1)
                else:
                    op = imm2code(str((self.label_dict[op] - addr)//4), rng[0] - rng[1] + 1)

            else:
                op = imm2code(op, rng[0] - rng[1] + 1)
            ret = ret[:LENGTH-rng[0]-1] + op + ret[LENGTH-rng[1]:]

        # second opcode
        if len(info) == 3:
            op2 = info[2]
            ret = ret[:LENGTH-op2[1][0]-1] + op2[0] + ret[LENGTH-op2[1][1]:]

        return ret
    

    def inst_generate(self):
        # generate all insts.
        for addr in list(self.op_dict.keys()):
            code = self._single_inst_gen(addr)
            self.inst_store.update({addr: code})


    def dump_file(self, filename: str, mode = 'b'):
        assert mode in {'b', 'x'}

        print(f"{len(self.inst_store)} instructions dump to {filename}")
        with open(filename, "w") as f:
            for _, inst in self.inst_store.items():
                if mode == 'x':
                    inst = bin2hex(inst)
                f.write(inst + "\n")



if __name__ == "__main__":
    mips = MIPS()
    input_dir = "inputs/"
    mode = "x"
    for file in os.listdir("inputs/"):
        if not file.endswith(".s"): continue
        mips._init_from_file(input_dir + file)
        mips.inst_generate()
        outf = file.split(".")[0]
        mips.dump_file(f"outputs/{mode}/{outf}.{mode}", mode)
        mips.reset()

    