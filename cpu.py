"""CPU functionality."""

import sys

OP1 = 0b10000010  # LDI
OP2 = 0b01000111  # PRN
OP3 = 0b10100010  # MULT
OP4 = 0b01000101  # PUSH
OP5 = 0b01000110  # POP
OP6 = 0b01010000  # CALL
OP7 = 0b00010001  # RET
OP8 = 0b10100000  # ADD


class CPU:
    """Main CPU class."""

    def __init__(self, memory=None, registers=None, bytes=None):
        """Construct a new CPU."""
        self.bytes = 256
        self.memory = [0] * self.bytes
        self.reg = [0] * 8
        self.pc = 0
        self.branchtable = {}
        self.branchtable[OP1] = self.handle_op1
        self.branchtable[0b01000111] = self.handle_op2
        self.branchtable[0b10100010] = self.handle_op3
        self.branchtable[OP4] = self.handle_op4
        self.branchtable[OP5] = self.handle_op5
        self.branchtable[OP6] = self.handle_op6
        self.branchtable[OP7] = self.handle_op7
        self.branchtable[OP8] = self.handle_op8

        self.SP = 7

    def load(self):
        """Load a program into memory."""

        filename = sys.argv
        print(f"start load fileaname is {filename}")
        if len(filename) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)

        if len(filename) == 2:
            try:
                with open(filename[1]) as f:

                    address = 0
                    for line in f:
                        # Ignore comments
                        comment_split = line.split('#')

                        # strip whitespace
                        num = comment_split[0].strip()

                        # ignore blank lines
                        if num == '':
                            continue

                        converted = int("0b"+num, 2)  # converted to dec

                        self.memory[address] = converted
                        # print(
                        # f"dec: {converted}, bin_c: {bin_c} memory: {type(self.memory[address])} {type(converted)}")
                        address += 1

            except FileNotFoundError:
                print("file not found")
                sys.exit(2)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_op1(self):
        # 130/LDI
        print("store!")
        self.reg[self.ram_read(self.pc+1)] = self.ram_read(self.pc+2)
        self.pc += 3

    def handle_op2(self):
        print("print!")
        print(self.reg[self.ram_read(self.pc+1)])
        self.pc += 2

    def handle_op3(self):
        # mult 2 values in 2 regs together
        print("mult!")
        regA_val = self.reg[self.ram_read(self.pc+1)]
        regB_val = self.reg[self.ram_read(self.pc+2)]
        mult_val = regA_val * regB_val
        # store the result in regA
        self.reg[self.ram_read(self.pc+1)] = mult_val
        self.pc += 3

    def handle_op4(self):
        # PUSH register
        # Push the value in the given register on the stack.
        # Decrement the SP.
        # Copy the value in the given register to the address pointed to by SP.
        reg = self.ram_read(self.pc+1)
        val = self.reg[reg]
        self.reg[self.SP] -= 1
        self.ram_write(val, self.reg[self.SP])
        self.pc += 2

    def handle_op5(self):
        # POP the value at the top of the stack into the given register.
        # Copy the value from the address pointed to by SP to the given register.
        # Increment SP.
        reg = self.ram_read(self.pc+1)
        val = self.ram_read(self.reg[self.SP])
        self.reg[reg] = val
        self.reg[self.SP] += 1
        self.pc += 2

    def handle_op6(self):
        print("CALL!")
        # The address of the instruction directly after CALL is PUSHED ONTO STACK
        # decrement our SP to push instructions to stack
        self.reg[self.SP] -= 1
        # This allows us to return to address where we left off when the subroutine finishes executing.
        self.ram_write(self.pc+2, self.reg[self.SP])
        # The PC is set to the address stored in the given register.
        # We jump to that location in RAM and execute the first instruction in the subroutine.
        reg = self.ram_read(self.pc+1)
        self.pc = self.reg[reg]

    def handle_op7(self):
        print("RETURN!")
        # Return from subroutine.
        # Pop the value from the top of the stack and store it in the PC.
        self.pc = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1

    def handle_op8(self):
        print("ADD")
        regA = self.reg[self.ram_read(self.pc+1)]
        regB = self.reg[self.ram_read(self.pc+2)]
        val = regA + regB
        self.reg[self.ram_read(self.pc+1)] = val
        self.pc += 3

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        num_operannds = op >> 6
        if op == 130:  # LOAD
            print("store!")
            self.reg[self.ram_read(self.pc+1)] = self.ram_read(self.pc+2)
            # increment to next value in memory (after 1.opcode, 2. reg#, 3.value)
            self.pc += (num_operannds + 1)

        elif op == 162:
            print("mult1!")
            # this needs to be self.reg
            regA_val = self.reg[self.ram_read(self.pc+1)]
            regB_val = self.reg[self.ram_read(self.pc+2)]

            mult_val = regA_val * regB_val
            # store the result in regA
            self.reg[self.ram_read(self.pc+1)] = mult_val
            # increment to next value in memory (after 1.opcode, 2. reg#, 3.value)
            self.pc += (num_operannds + 1)

        else:
            raise Exception("Unsupported ALU operation")

    def run(self):

        running = True
        print("start running")

        while running:

            # read the memory address that's stored in register PC == memory data
            instruction = self.ram_read(self.pc)

            # self.trace()
            if instruction == 0b00000001:
                running = False
            elif instruction >> 7 == 1:
                # if instruction >> 7 == 1:
                # invoke self.alu
                self.alu(instruction, self.ram_read(
                    self.pc+1), self.ram_read(self.pc+2))
            else:
                self.branchtable[instruction]()

    def ram_read(self, address):
        # print(
        # f"Ram address is {address}, value at this address is {self.memory[address]} ")

        return self.memory[address]

    def ram_write(self, value, address):
        self.memory[address] = value
        return self.memory[address]
