import re, os

from utils import sgt_type, ops_pos_pair, LENGTH
from utils import process_line, bin2hex
from utils import ops2code, imm2code

class MIPS:
    def __init__(self, assembly_file: str) -> None:
        # start addr of segmemtation, like `.text`
        self.addr_start = None

        # map from physical addr(int) to label(str), op(str) and operands(List(str))
        self.label_dict = dict()
        self.op_dict = dict()
        self.operands_dict = dict()

        # store final result
        self.inst_store = dict()

        # init from given file
        self._init_from_file(assembly_file)


    def _init_from_file(self, filename: str):
        # assemble only
        assert filename.endswith((".s", ".S")), f"only assemble file end with .s or .S supported, not {filename.split('.')[-1]}"
        
        # read file
        with open(filename, "r") as f:
            # base addr
            while(True):
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
                    self.label_dict.update({counter: label[:-1]})
                if len(ops) == 0: continue

                # remove notes
                if ops[0].startswith("#"): continue

                opcode = ops.pop(0)
                if opcode.lower() in list(ops_pos_pair.keys()):
                    self.op_dict.update({counter: opcode.lower()})
                else:
                    raise ValueError(f"instruction in line {idx}, {opcode} is not defined, support {list(ops_pos_pair.keys())}")
                
                self.operands_dict.update({counter: ops})
                counter += (LENGTH // 4)


    def _single_inst_gen(self, addr: int):
        # generate single inst.
        info = ops_pos_pair[self.op_dict[addr]]
        
        # opcode and operands
        ret = info[0] + "0" * (LENGTH - len(info[0]))
        assert len(info[1]) == len(self.operands_dict[addr]), f"expect {len(info[1])} args but get {self.operands_dict[addr]}"

        # print(ret)
        for rng, op in zip(info[1], self.operands_dict[addr]):
            if op.startswith("$"):
                op = ops2code(op[1:])
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
        assert mode in {'b', 'h'}

        print(f"{len(self.inst_store)} instructions dump to {filename}")
        with open(filename, "w") as f:
            for _, inst in self.inst_store.items():
                if mode == 'h':
                    inst = bin2hex(inst)
                f.write(inst + "\n")



if __name__ == "__main__":
    file = "memtest0"
    mips = MIPS(f"inputs/{file}.s")
    mips.inst_generate()
    mips.dump_file(f"outputs/{file}.txt")