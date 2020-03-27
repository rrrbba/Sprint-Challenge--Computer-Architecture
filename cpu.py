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
SP = 7 

#flags for cmp
E = 0
L = 0
G = 0

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8 #general purpose register (has 8 bits)
        self.ram = [0] * 256 #to hold 256 bytes of memory
        self.pc = 0 #program counter
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
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                E = 1
            elif self.reg[reg_a] < self.reg[reg_b]:
                L = 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                G = 1
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
        

    def run(self):
        """Run the CPU."""

        running = True

        while running: 
            IR = self.ram[self.pc] #fetch value from RAM and then use that value to look up handler function in the branch table
            self.branchtable[IR]()












# Add list properties to the CPU class to hold 256 bytes of memory and general-purpose registers
    #Also add properties for any internal registers

#In CPU, add method ram_read() and ram_write() that access the RAM inside the CPU object
    #ram_read() should accept the address to read and return the value stored there
    #ram_write() should accept a value to write, and address to write it to

#Implement the core of the CPU's run() method
    # needs to read to memory address that's stored in register PC -> store that result in IR, the Instruction Register. This can just be a local variable in run()
    # some instructions requires up to the next bytes of data after the PC in memory
    # using ram_read(), read the bytes at pc + 1 and pc + 2 from RAM into variables operand_a and operand_b in case the instruction needs them
    # Depending on the value of the opcode, perform the actions needed for the instruction per the LS-8 spec. (if-elif)
    # the PC needs to be updated to point to the next instruction for the next iteration of the loop in run()

#Implement the HLT instruction handler to cpu.py
    # So that you can refer to it by name instead of by numeric value
    # in run() in your switch, exit the loop if a HLT instruction is encountered, regardless of whether or not there are more lines of code in the LS-8 program 
    # consider HLT similar to exit()
    # halt the CPU and exits the emulator

# Add the LDI instruction handler
    # This instruction sets a specified register to a specified value
    # load "immediate", store a value in a register, or "set this register to this value"

# Add the PRN instruction handler
    # Similar to adding LDI, but the handler is simpler
    # At this point, you can run the program and have it print 8 to console.
    # a pseudo-instruction that prints the numeric value stored in a register

#PUSH and POP (the stack)
    # so the stack is in memory (self.ram). It starts at self.ram[F3] as per the spec, and the stack pointer points to the value at the top of the stack. Since the stack is "growing down" in memory, the stack pointer is decremented every time something is added to the top. 
    # so if the stack is empty and we push two values, the stack pointer becomes F2 (pointing to the top value).
    # we initialize our stack pointer to F4 instead of F3 because at the beginning there’s nothing in it