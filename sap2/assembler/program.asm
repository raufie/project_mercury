start:
    mvi b, 0x00
    mvi c, 0x07
    
bit: 
    in 0x02
    ani 0x80
    ora b
    rar
    MOV b, a
    mvi a, 0x73

delay:
    dcr a
    jnz delay
    dcr c
    jnz bit
    in 0x02
    ani 0x80
    ora b
    sta 0x2100



