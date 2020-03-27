"""CPU functionality."""

import sys

#Opcodes = instructions
LDI = 0b10000010 # Set the value of a register to an integer.
PRN = 0b01000111 # Print numeric value stored in the given register.
HLT = 0b00000001 # Halt the CPU (and exit the emulator).
MUL = 0b10100010 # Multiply the values in two registers together and store the result in registerA
POP = 0b01000110 # Pop the value at the top of the stack into the given register.
PUSH = 0b01000101 # Push the value in the given register on the stack.
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111 # Compare the values in two registers.
JMP = 0b01010100 # Jump to the address stored in the given register.
JEQ = 0b01010101 # If equal flag is set (true), jump to the address stored in the given register.
JNE = 0b01010110 #If E flag is clear (false, 0), jump to the address stored in the given register.
SP = 7 


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8 #general purpose register (has 8 bits)
        self.ram = [0] * 256 #to hold 256 bytes of memory
        self.pc = 0 #program counter
        self.fl = False #equal flag
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[POP] = self.handle_POP
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE

    def ram_read(self, mar): 
        #should accept the address to read and 
        mdr = self.ram[mar] #MAR = contains ADDRESS that is being read or written to
        #return the value stored there
        return mdr #MDR = contains the DATA that was read or the data to write

    def ram_write(self, mar, value):
        #should accept a value to write, and address to write it to
        self.ram[mar] = value #can put mdr instead of value

    def load(self, program):
        """Load a program into memory."""

        address = 0
        program = sys.argv[1]
        try:
            with open(program) as p:
                for line in p:
                    # Ignore comments
                    comment_split = line.split("#")
                    # Strip out whitespace
                    num = comment_split[0].strip()
                    # Ignore blank lines
                    if num == '':
                        continue
                    instruction = int(num, 2) #base 2
                    self.ram[address] = instruction #memory[address]
                    address += 1
        except FileNotFoundError:
            print("File not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD": # a = a + b
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL": # Multiply the values in two registers together and store the result in registerA
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP": # Compare the values in two registers.
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = True

        elif op == "JMP": # Jump to the address stored in the given register.
            self.pc = self.reg[reg_a]
        
        elif op == "JEQ": # If equal flag is set (true), jump to the address stored in the given register.
            if self.fl is True:
                self.pc = self.reg[reg_a]
            else:
                self.pc += 2

        elif op == "JNE": # If E flag is clear (false, 0), jump to the address stored in the given register.
            if self.fl is False:
                self.pc = self.reg[reg_a]
            else:
                self.pc += 2



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

    def handle_LDI(self): # sets a specified register to a specified value
        operand_a = self.ram_read(self.pc + 1) 
        operand_b = self.ram_read(self.pc + 2)

        self.reg[operand_a] = operand_b
        self.pc += 3 # skip down 3 to PRN

    def handle_PRN(self): # prints the numeric value stored in a register
        operand_a = self.ram_read(self.pc + 1) 

        print(self.reg[operand_a])
        self.pc += 2 #skip down 2 to HLT

    def handle_MUL(self): # Multiply the values in two registers together and store the result in registerA
        operand_a = self.ram_read(self.pc + 1) 
        operand_b = self.ram_read(self.pc + 2)

        self.alu("MUL", operand_a, operand_b) #call the alu.mul and use operand_a and operand_b
        self.pc += 3 #increment the program counter 3
    
    def handle_ADD(self): # Add the value in two registers and store the result in registerA.
        operand_a = self.ram_read(self.pc + 1) 
        operand_b = self.ram_read(self.pc + 2)

        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def handle_CMP(self):
        operand_a = self.ram_read(self.pc + 1) 
        operand_b = self.ram_read(self.pc + 2)

        self.alu("CMP", operand_a, operand_b)
        self.pc += 3


    def handle_HLT(self):
        sys.exit(0) #exit without an error unlike sys.exit 1 which means an error

    def handle_POP(self):
        reg = self.ram_read(self.pc +1)
        value = self.ram_read(self.reg[SP]) #calls memory and gets the F5 value
        #Copy the value
        self.reg[reg] = value
        #increment the stack pointer
        self.reg[SP] += 1
        self.pc += 2

    def handle_PUSH(self):
        reg = self.ram_read(self.pc+1)
        value = self.reg[reg]
        #Decrement the stack pointer
        self.reg[SP] -= 1 #= (Register[SP]-1 % (len(memory)))
        #Copy the value  in given register tot he address pointed to by stack pointer
        self.ram_write(self.reg[SP], value)
        self.pc += 2 #because one argument

    def handle_CALL(self):
        # The address of the instruction directly after CALL is pushed onto the stack.
        # This allows us to return to where we left off when the subroutine finishes executing.
        self.reg[SP] -= 1
        address = self.pc + 2
        self.ram[self.reg[SP]] = address
        # The PC is set to the address stored in the given register.
        # We jump to that location in RAM and execute the first instruction in the subroutine.
        # The PC can move forward or backwards from its current location.
        reg = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg]
        

    def handle_RET(self):
        # Return from subroutine.
        # Pop the value from the top of the stack and store it in the PC.
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    def handle_JMP(self):
        # Jump to the address stored in the given register
        # Set the PC to the address stored in the given register.

        operand_a = self.ram_read(self.pc + 1) 
        self.alu("JMP", operand_a, None) #None b/c we don't need operand_b


    def handle_JEQ(self):
        # If equal flag is set (true), jump to the address stored in the given register.
        operand_a = self.ram_read(self.pc + 1) 

        self.alu("JEQ", operand_a, None) #None b/c we don't need operand_b


    def handle_JNE(self):
        # If E flag is clear (false, 0), jump to the address stored in the given register.
        operand_a = self.ram_read(self.pc + 1) 

        self.alu("JNE", operand_a, None) #None b/c we don't need operand_b


    def run(self):
        """Run the CPU."""

        running = True

        while running: 
            IR = self.ram[self.pc] #fetch value from RAM and then use that value to look up handler function in the branch table
            self.branchtable[IR]()