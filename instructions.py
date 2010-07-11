import hardware

#getting registers (the list indexes)
I_F = 5
N_F = 0
Z_F = 6
C_F = 7

#convert to signed 8-bit
def castSigned8Bit(i):
    return(i + 2**7) % 2**8 - 2**7     

#Sign flag: this is set if the result of an operation is
#negative, cleared if positive.
def setN(nesSystem, result):
    if (result & 0x80) == 0x80:
        nesSystem.cpu.status[N_F] = 1
    else:
        nesSystem.cpu.status[N_F] = 0

#Zero flag: this is set to 1 when any arithmetic or logical
#operation produces a zero result, and is set to 0 if the result is
#non-zero.        
def setZ(nesSystem, result):
    if result == 0:
        nesSystem.cpu.status[Z_F] = 1
    else:
        nesSystem.cpu.status[Z_F] = 0

#Carry flag:
def setC(nesSystem, item1, item2):
    if item1 >= item2:
        nesSystem.cpu.status[C_F] = 1
    else:
        nesSystem.cpu.status[C_F] = 0
        
        
def pushStack(nesSystem, byte):
    nesSystem.cpu.stackP.append(byte)
    
def popStack(nesSystem):
    return nesSystem.cpu.stackP.pop()
        
#0x78. Set interrupt disable status
def SEI(nesSystem, cpu):
    nesSystem.cpu.status[I_F] = 1
    nesSystem.cpu.programCounter += 1
    return 2
   
#0xD8. Clear decimal mode
def CLD(nesSystem, cpu):
    nesSystem.cpu.programCounter += 1
    return 2
    
#0xA9. Load accumulator with memory IMMEDIATE
def LDA_Immediate(nesSystem, cpu):
    cpu.operand = cpu.getNextByte()
    nesSystem.cpu.accumulator = cpu.operand
    setN(nesSystem, nesSystem.cpu.accumulator)
    setZ(nesSystem, nesSystem.cpu.accumulator)
    nesSystem.cpu.programCounter += 2
    return 2
    
#0x10. Branch on result plus. Jump back the RELATIVE number of bytes. 
#If the operand was FB, then we jump back FB - FF+1 number of bytes (-5) 
def BPL(nesSystem, cpu):
    address = cpu.getNextByte()
    s8Address = castSigned8Bit(address)
    tickcount = 0
    if nesSystem.cpu.status[N_F] == 0:
        nesSystem.cpu.programCounter += 2
        #if (nesSystem.cpu.programCounter & 0xFF00) != (nesSystem.cpu.programCounter + (address - (0xFF + 1))):
        if ((nesSystem.cpu.programCounter & 0xFF00) != ((nesSystem.cpu.programCounter + s8Address +2) & 0xFF00)):
            tickcount +=1
        
        nesSystem.cpu.programCounter = nesSystem.cpu.programCounter + s8Address
        tickcount +=1
    
    else:
        nesSystem.cpu.programCounter += 2
    tickcount +=2
        
    return tickcount   
        
#0x8D. Store the byte in the accumulator into memory     
def STA_Absolute(nesSystem, cpu):
    address = cpu.getNextWord()
    cpu.writeMemory(address, nesSystem.cpu.accumulator)
    #nesSystem.cpu.cpuMemory[cpu.operand] = nesSystem.cpu.accumulator
    nesSystem.cpu.programCounter += 3
    return 4
       
def JSR(nesSystem, cpu):
    address = cpu.getNextWord()
    nesSystem.cpu.stackP.append(nesSystem.cpu.programCounter + 2)
    nesSystem.cpu.programCounter = address
    return 6
    
 
#0xA2. load register X with next byte
def LDX(nesSystem, cpu):
    address = cpu.getNextByte()
    nesSystem.cpu.registerX =  address
    setN(nesSystem, nesSystem.cpu.registerX)
    setZ(nesSystem, nesSystem.cpu.registerX)
    
    nesSystem.cpu.programCounter += 2
    return 2
    
#0x9A. Transfers the byte in X Register into the Stack Pointer. Not many roms use this
def TXS(nesSystem, cpu):
    pushStack(nesSystem, nesSystem.cpu.registerX)
    nesSystem.cpu.programCounter += 1
    return 2

    
#0xAD.Loads a byte of memory into the accumulator setting the zero and negative flags as appropriate.
def LDA_Absolute(nesSystem, cpu):
    address = cpu.getNextWord()
    nesSystem.cpu.accumulator = cpu.readMemory(address)
    setZ(nesSystem, nesSystem.cpu.accumulator)
    setN(nesSystem, nesSystem.cpu.accumulator)
    nesSystem.cpu.programCounter += 3
    return 4
    
    
def LDY_Immediate(nesSystem, cpu):
    address = cpu.getNextByte()
    nesSystem.cpu.registerY = address
    setZ(nesSystem, nesSystem.cpu.registerY)
    setN(nesSystem, nesSystem.cpu.registerY)
    nesSystem.cpu.programCounter += 2
    return 2
    
def LDA_AbsoluteX(nesSystem, cpu):
    address = cpu.getNextWord()
    nesSystem.cpu.accumulator = cpu.readMemory(address + nesSystem.cpu.registerX)
    setZ(nesSystem, nesSystem.cpu.accumulator)
    setN(nesSystem, nesSystem.cpu.accumulator) 
    nesSystem.cpu.programCounter += 3
    return 4
    
def CMP(nesSystem, cpu):
    address = cpu.getNextByte()
    setC(nesSystem, nesSystem.cpu.accumulator, address)
    setZ(nesSystem, nesSystem.cpu.accumulator - address)
    setN(nesSystem, nesSystem.cpu.accumulator - address)
    nesSystem.cpu.programCounter += 2
    return 2

def DEX(nesSystem, cpu):
    nesSystem.cpu.registerX -= 1
    setN(nesSystem, nesSystem.cpu.registerX)
    setZ(nesSystem, nesSystem.cpu.registerX)
    nesSystem.cpu.programCounter += 1
    return 2
    
def STA_ZeroPage(nesSystem, cpu):
    address = cpu.getNextByte()
    cpu.writeMemory(address, nesSystem.cpu.accumulator)
    nesSystem.cpu.programCounter += 2
    return 3

def STX_ZeroPage(nesSystem, cpu):
    address = cpu.getNextByte()
    cpu.writeMemory(address, nesSystem.cpu.registerX)
    nesSystem.cpu.programCounter += 2
    return 3

def CPX(nesSystem, cpu):
    address = cpu.getNextByte()
    setC(nesSystem, nesSystem.cpu.registerX, address)
    setZ(nesSystem, nesSystem.cpu.registerX)
    setN(nesSystem, nesSystem.cpu.registerX)
    nesSystem.cpu.programCounter += 2
    return 2

def STA_IndirectY(nesSystem, cpu):
    return 6
    
def BNE(nesSystem, cpu):
    address = cpu.getNextByte()
    s8Address = castSigned8Bit(address)
    tickcount = 0
    if nesSystem.cpu.status[Z_F] == 0:
        nesSystem.cpu.programCounter += 2
        if ((nesSystem.cpu.programCounter & 0xFF00) != ((nesSystem.cpu.programCounter + s8Address + 2) & 0xFF00)):
            tickcount +=1
        nesSystem.cpu.programCounter = nesSystem.cpu.programCounter + s8Address
        tickcount +=1
    
    else:
        nesSystem.cpu.programCounter += 2
    tickcount +=2
        
    return tickcount  

def BCS(nesSystem, cpu):
    address = cpu.getNextByte()
    s8Address = castSigned8Bit(address)
    tickcount = 0
    if nesSystem.cpu.status[C_F] == 1:
        nesSystem.cpu.programCounter += 2
        if ((nesSystem.cpu.programCounter & 0xFF00) != ((nesSystem.cpu.programCounter + s8Address + 2) & 0xFF00)):
            tickcount +=1
        nesSystem.cpu.programCounter = nesSystem.cpu.programCounter + s8Address
        tickcount +=1
    
    else:
        nesSystem.cpu.programCounter += 2
    tickcount +=2
        
    return tickcount   

    
def toggleVblank(nesSystem, cpu):
    nesSystem.cpu.cpuMemory[0x2002] = 128
    