add x31, x30, x0
addi x31, x30,0xFFF
addi x31,x30,0b11111000010
lui x1, 0x27
addi x31,x30, -27
lw x5, 0(x3 )
jal x0, 24
lw x5, 0(x7)
bge x6, x5, 0x2C
sw x6, 0(x29)
sub x5, x6, x7
addi s0, s1, 12
lh t2, -6(s3)
srai t1,t2, 29
sb t5, 45(zero)
beq s0, t5, 0x10
lui s5, 0x8cdef
jal ra, 0xa67f8
