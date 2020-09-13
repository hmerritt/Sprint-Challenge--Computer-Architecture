"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0b00000000] * 255
        self.reg = [0] * 8
        self.reg[7] = 255 # SP
        self.pc = 0
        self.ir = 0
        self.mar = 0
        self.mdr = 0
        self.fl = 0

    def load(self):
        """Load a program into memory."""
        filename = sys.argv[1]
        address = 0
        try:
            with open(filename) as f:
                for line in f:
                    split_line = line.split('#')
                    code_value = split_line[0].strip()

                    if code_value == '':
                        continue

                    num = int(code_value, 2)
                    self.ram[address] = num
                    address += 1

        except FileNotFoundError:
            print(f"{filename} file not found")
            sys.exit(2)


    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')


        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
        print(self.ram)

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            self.ir = self.ram[self.pc] # get current instruction using program counter

            if self.ir == 0b00000001: # HALT
                # self.trace()
                running = False

            elif self.ir == 0b10000010: # LDI
                self.reg[self.ram[self.pc + 1]] = self.ram[self.pc + 2]
                self.pc += 2

            elif self.ir == 0b01000101: # PUSH
                register = self.ram[self.pc + 1]
                value = self.reg[register]
                # decrement the Stack Pointer
                self.reg[7] -= 1
                # write the value of the given register to memory AT the SP location
                self.ram[self.reg[7]] = value
                self.pc += 1

            elif self.ir == 0b01000110: # POP
                register = self.ram[self.pc + 1]
                # write the value in memory at the top of stack to the given register
                value = self.ram[self.reg[7]]
                self.reg[register] = value
                # increment the stack pointer
                self.reg[7] += 1
                self.pc += 1

            elif self.ir == 0b01010000: # CALL
                # push address of next instruction to the stack
                ret_addr = self.pc + 2
                self.reg[7] -= 1
                self.ram[self.reg[7]] = ret_addr

                # call sub-routine
                reg_addr = self.ram[self.pc + 1]
                self.pc = self.reg[reg_addr]
                continue

            elif self.ir == 0b00010001: # RET
                # pop return address off the stack
                ret_addr = self.ram[self.reg[7]]
                self.reg[7] += 1
                self.pc = ret_addr
                continue

            elif self.ir == 0b01000111: # PRN R0
                self.pc += 1
                print(self.reg[self.ram[self.pc]])

            elif self.ir == 0b10100000: # ADD
                self.alu("ADD", self.ram[self.ir + 1], self.ram[self.ir + 2])
                self.pc += 2

            elif self.ir == 0b10100000: # SUB
                self.alu("SUB", self.ram[self.ir + 1], self.ram[self.ir + 2])
                self.pc += 2

            elif self.ir == 0b10100010: # MLT
                self.alu("MUL", self.ram[self.ir + 1], self.ram[self.ir + 2])
                self.pc += 2

            else:
                print(f"Unknown instruction: {self.ir}")
                sys.exit(1)

            self.pc += 1 # increment program counter
