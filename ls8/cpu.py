import sys
import time

# compare values in two registers
CMP = 0b10100111
# decrement (subtract 1 from) the value in the given register
DEC = 0b01100110
# divide the value in the first register by the value in second register, store quotient in registerA
DIV = 0b10100011
# halt the CPU and exit the emulator.
HLT = 0b00000001
# increment the value in the given register
INC = 0b01100101
# if equal flag is set (true), jump to the address stored in the given register
JEQ = 0b01010101
# jump to the address stored in the given register
JMP = 0b01010100
# If E flag is clear (false, 0), jump to the address stored in the given register
JNE = 0b01010110
# load "immediate", store a value in a register, or "set this register to this value"
LDI = 0b10000010
# multiply the values in two registers together and store the result in registerA
MUL = 0b10100010
# pop the value at the top of the stack into the given register
POP = 0b01000110
# a pseudo-instruction that prints the numeric value stored in a register
PRN = 0b01000111
# push the value in the given register on the stack
PUSH = 0b01000101
# subtract the value in the second register from the first, storing the result in registerA.
SUB = 0b10100001


class CPU:
    def __init__(self):
        self.pc = 0  # program counter, address of the currently executing instruction
        self.reg = [0] * 8  # 8 general-purpose 8-bit numeric registers R0-R7
        self.reg[7] = 255  # 7 registers, reg[8] is the stack pointer
        self.ram = [0] * 256  # 8-bit addressing or 256 bytes of RAM total
        self.fla = [0] * 8  # `FL` bits: `00000LGE`
        self.hlt = False  # set half to false

        self.ops = {
            DEC: self.op_dec,  # decrement the value in the given register
            DIV: self.op_div,  # divide registerA by registerA, store quotient in registerA
            CMP: self.op_cmp,  # compare values in two registers
            HLT: self.op_hlt,  # halt CPU and exit emulator
            INC: self.op_inc,  # increment the value in the given register
            JMP: self.op_jmp,  # jump to address stored in given register
            JEQ: self.op_jeq,  # if equal flag is true, jump to address in given register
            JNE: self.op_jne,  # If equal flag is false, jump to address in given register
            LDI: self.op_ldi,  # set the value of a register to an integer
            MUL: self.op_mul,  # store result of two integers multiplcation in registerA
            POP: self.op_pop,  # pop value at the top of the stack into the given register
            PRN: self.op_prn,  # print  value stored in the given register
            PUSH: self.op_push,  # push  value in given register on the stack
            SUB: self.op_sub,  # push  value in given register on the stack
        }

    # set the value of a register to an integer
    def op_ldi(self, address, value):
        self.reg[address] = value

    # print value stored in the given register
    def op_prn(self, address, op_b):  # op a/b
        print(self.reg[address])  # op_a acts as address

    # halt the CPU
    def op_hlt(self, op_a, op_b):
        self.hlt = True

    # Multiply the values in two registers together and store the result in registerA.
    def op_mul(self, operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)

    # divide the value in the first register by the value in second register, store quotient in registerA
    def op_div(self, operand_a, operand_b):
        self.alu('DIV', operand_a, operand_b)

    # increment the value in the given register
    def op_inc(self, operand_a, operand_b):
        self.alu('INC', operand_a, operand_b)

    # increment the value in the given register
    def op_sub(self, operand_a, operand_b):
        self.alu('SUB', operand_a, operand_b)

    # Push the value in the given register on the stack
    def op_push(self, operand_a, operand_b):
        self.reg[7] -= 1  # decrement stack pointer
        sp = self.reg[7]  # sp variable
        self.ram[sp] = self.reg[operand_a]

    # pop the value at the top of the stack into the given register.
    def op_pop(self, operand_a, operand_b):
        sp = self.reg[7]  # sp variable
        operand_b = self.ram[sp]
        self.reg[operand_a] = operand_b

    # jump to the address stored in the given register
    def op_jmp(self, address, operand_b):
        # set the PC to the address stored in the given register
        self.pc = self.reg[address]

    # compare  values in two registers
    def op_cmp(self, operand_a, operand_b):
        self.alu('CMP', operand_a, operand_b)

    # decrement (subtract 1 from) the value in the given register.
    def op_dec(self, operand_a, operand_b):
        self.alu('DEC', operand_a, operand_b)

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
        # add the value in two registers and store the result in registerA.
        if op == "ADD":
            # add the value in two registers and store the result in registerA.
            self.reg[reg_a] += self.reg[reg_b]
        # subtract the value in the second register from the first
        elif op == "SUB":
            # store the result in registerA
            self.reg[reg_a] -= self.reg[reg_b]
        # multiply the values in two registers together and store the result in registerA.
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        # divide the value in the first register by the value in second register
        elif op == "DIV":
            # If  value in the second register is 0
            if self.reg[reg_b] == 0:
                # print an error message and halt
                print("Unable to divide by 0")
                raise Exception("Unable to divide by 0")
            # storing the quotient in registerA
            self.reg[reg_a] /= self.reg[reg_b]
        # compare the values in two registers.
        elif op == "CMP":
            # registerA is less than registerB,
            if self.reg[reg_a] < self.reg[reg_b]:
                # set the Less-than L flag to 1
                self.fla[5] = 1
            # registerA is greater than registerB
            elif self.reg[reg_a] > self.reg[reg_b]:
                # set the Greater-than G flag to 1
                self.fla[6] = 1
            # registerA and registerB are equal
            elif self.reg[reg_a] == self.reg[reg_b]:
                # set the Equal E flag to 1
                self.fla[7] = 1
            else:
                print('Non-comparable values')
        elif op == "DEC":
            self.reg[reg_a] -= 1
        elif op == "INC":
            self.reg[reg_a] += 1
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
            # set internal register to the program counter index of the 256 byte RAM list
            ir = self.ram[self.pc]
            # set operand_a to the next program counter index
            operand_a = self.ram_read(self.pc + 1)
            # set operand_b to the following program counter index after operand_a
            operand_b = self.ram_read(self.pc + 2)
            # set op_suze to internal register shifted 6 bits to the right
            op_size = ir >> 6
            ins_set = ((ir >> 4) & 0b1) == 1
            if ir in self.ops:
                self.ops[ir](operand_a, operand_b)
            if not ins_set:
                self.pc += op_size + 1
