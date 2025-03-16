mvi a, 0
mvi b, 12
mvi c, 8
call multiply
out 0x03
hlt


multiply: add b
dcr c
jz done
jmp multiply
done: ret