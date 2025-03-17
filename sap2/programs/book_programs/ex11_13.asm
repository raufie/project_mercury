in 0x02
ani 0b00000001
jz no
yes: mvi a, 'Y'
jmp done
no: mvi a, 'N'
done: out 0x03
hlt