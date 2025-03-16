call input ; get first number
mov b, a ; put it in b
call input ; get the second number
add b
out 0x03
hlt
input: in 0x02 ;get port2 status
ani 0x01
jz input ; move up if not ready
in 0x01
ret