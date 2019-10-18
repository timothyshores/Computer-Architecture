"""CPU functionality."""
# py ls8.py examples/sctest.ls8
import sys
import time

# compare values in two registers
CMP = 0b10100111
# halt the CPU and exit the emulator.
HLT = 0b00000001
# if equal flag is set (true), jump to the address stored in the given register.
JEQ = 0b01010101
# jump to the address stored in the given register
JMP = 0b01010100
# If E flag is clear (false, 0), jump to the address stored in the given register.
JNE = 0b01010110
# load "immediate", store a value in a register, or "set this register to this value"
LDI = 0b10000010
# multiply the values in two registers together and store the result in registerA.
MUL = 0b10100010
# pop the value at the top of the stack into the given register
POP = 0b01000110
# a pseudo-instruction that prints the numeric value stored in a register
PRN = 0b01000111
# push the value in the given register on the stack
PUSH = 0b01000101


class CPU:

    def __init__(self):
        self.pc = 0  # program counter, address of the currently executing instruction
        self.reg = [0] * 8  # 8 general-purpose 8-bit numeric registers R0-R7
        self.reg[7] = 255  # 7 registers, reg[8] is the stack pointer
        self.ram = [0] * 256  # 8-bit addressing or 256 bytes of RAM total
        self.fla = [0] * 8  # `FL` bits: `00000LGE`
        self.hlt = False  # set half to false

        self.ops = {
            CMP: self.op_cmp,
            HLT: self.op_hlt,
            JMP: self.op_jmp,
            JEQ: self.op_jeq,
            JNE: self.op_jne
            LDI: self.op_ldi,
            MUL: self.op_mul,
            POP: self.op_pop,
            PRN: self.op_prn,
            PUSH: self.op_push,
        }

    def op_ldi(self, address, value):
        self.reg[address] = value

    def op_prn(self, address, op_b):  # op a/b
        print(self.reg[address])  # op_a acts as address

    def op_hlt(self, op_a, op_b):
        self.hlt = True

    def op_mul(self, operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)

    def op_push(self, operand_a, operand_b):
        self.reg[7] -= 1  # decrement stack pointer
        sp = self.reg[7]  # sp variable
        self.ram[sp] = self.reg[operand_a]

    def op_pop(self, operand_a, operand_b):
        sp = self.reg[7]  # sp variable
        operand_b = self.ram[sp]
        self.reg[operand_a] = operand_b

    def op_jmp(self, address, operand_b):
        self.pc = self.reg[address]

    def op_cmp(self, operand_a, operand_b):
        value1 = self.reg[operand_a]
        value2 = self.reg[operand_b]
        if value1 < value2:
            self.fla[5] = 1
        elif value1 > value2:
            self.fla[6] = 1
        elif value1 == value2:
            self.fla[7] = 1
        else:
            print('Non-comparable values')
        # `FL` bits: `00000LGE`

    def op_jeq(self, operand_a, operand_b):
        if self.fla[7] == 1:
            self.op_jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def op_jne(self, operand_a, operand_b):
        if self.fla[7] == 0:
            self.op_jmp(operand_a, operand_b)
        else:
            self.pc += 2

    # accept the address to read and return the value stored there
    def ram_read(self, address):
        return self.ram[address]

    # accept a value to write, and the address to write it to
    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self, filename):
        address = 0
        with open(filename) as file:
            for line in file:
                comment_split = line.split('#')  # used to ignore comments
                instruction = comment_split[0]
                if instruction == '':
                    continue
                elif (instruction[0] == '0') or (instruction[0] == '1'):
                    self.ram[address] = int(instruction[:8], 2)
                    address += 1

    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            # add the value in two registers and store the result in registerA.
            self.reg[reg_a] += self.reg[reg_b]
            # multiply the values in two registers together and store the result in registerA.
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        # Print out the CPU state. Call from run() if you need help debugging.
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        # run loop while halt is False
        while self.hlt == False:
            # set internal register to
            ir = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            op_size = ir >> 6
            ins_set = ((ir >> 4) & 0b1) == 1
            if ir in self.ops:
                self.ops[ir](operand_a, operand_b)
            if not ins_set:
                self.pc += op_size + 1
