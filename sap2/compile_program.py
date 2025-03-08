#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
import argparse

def decode(n: int, size=64):
    s = ["0"] * size
    s[size-n-1] = "1"
    bit_string = "".join(s)
    return hex(int(bit_string, 2))[2:].zfill(size // 4)

def hex_or(hex1: str, hex2: str):
    return hex(int(hex1, 16) | int(hex2, 16))[2:].zfill(len(hex1))

def get_control_or(df,*args):
    hex_fin = None
    for arg in args:

        out = df[df['con']==arg]['con_hex'].item()
        if hex_fin is None:
            hex_fin = out
        else:
            hex_fin = hex_or(hex_fin, out)
    return hex_fin

class ControlRom:
    def __init__(self, addr_width=256, data_width=64, debug=True):
        n_nibbles = data_width // 4
        self.data = ['0' * n_nibbles] * addr_width
        self.debug = debug
    def __getitem__(self, index):
        return bytes.fromhex(self.data[index])
    
    def __setitem__(self, index, value):
        """
        index: hex integer i.e 0x0f
        value: string value
        """
        if type(index) is not int:
            index = int(index, base=16)
        if self.debug:
            print(value)
        self.data[index] = value
    
    def save_as_hex(self, fname='control_rom_try.hex'):
        with open(fname, 'wb') as f:
            for line in self.data:
                f.write(bytes.fromhex(line))

def compile_file_and_save(fpath, con_save_path, op_save_path, con_debug=False, whole_debug=False):
    with open(fpath, 'r') as file:
        data = file.read()
        # turn it into lines
        lines = data.split("\n")
        # first lines are fetch cycles
        rom = ControlRom(debug=con_debug) # sequencer
        op_rom = ControlRom(data_width=8, debug=False) # controller
        for line in lines:
            if len(line.strip())==0 or line[0]=='/':
                continue

            ctype, rest = line.split("-")
            if ctype == 'CON':
                rest1, rest2 = rest.split("=")
                addr = rest1.strip()
                cons = rest2.strip().split(" ")
                rom[addr] = get_control_or(df, *cons)
            if ctype == 'OP':
                rest1, rest2 = rest.split("=")
                
                addr = rest1.strip()
                value = rest2.strip()

                op_rom[addr] = value.split("x")[1]
        
        rom.save_as_hex(con_save_path)
        op_rom.save_as_hex(op_save_path)

        if whole_debug:
            print("\033[93m" + "*"*10 + " - Control ROM" + "\033[0m")
            print(*rom.data)
            print("\033[95m" + "*"*10 + " - OP ROM" + "\033[0m")

            print(*op_rom.data)




if __name__ == '__main__':
    isa = open("instruction_set_map.txt", 'r').read()
    isa_mapping = {}
    for line in isa.split('\n'):
        instr, addr = line.split("=")
        instr, addr = instr.strip(), addr.strip()
        isa_mapping[instr] = addr
    
    parser = argparse.ArgumentParser(description="Process a file argument.")
    parser.add_argument("--file", type=str, required=True, help="Path to the file")

    args = parser.parse_args()
    output_fname = args.file.split('.')[-2]+'.o'
    program = open(args.file,'r').read()
    program_code = []
    stack = []
    for line in program.split('\n'):
        line_code = []
        extras = []
        instr = line
        # check for the operator
        splits = instr.strip().split(" ")
        # check for the operand
        # print(instr)
        if len(splits) == 1:
            # just store address
            prec = splits[0]
        elif len(splits) == 2:
            if len(splits[1])>=2 and splits[1][:2]=='0x':
                if len(splits[1])==6:
                    # 0xhhhh
                    if splits[0].strip().lower() == 'call':
                        extras.append('0xFF')
                        extras.append('0xFF')
                        extras.append('0xFe')
                        extras.append('0xFF')
                    prec = splits[0]+ " 0xHHHH"
                    # SWAP BYTES (LITTLE ENDIAN)
                    extras.append('0x'+splits[1].split('x')[1][2:])
                    extras.append('0x'+splits[1].split('x')[1][:2])

                elif len(splits[1])==4:
                    prec = splits[0]+ " 0xHH"
                    extras.append(splits[1])
            else:
                prec = " ".join(splits)                    
        if len(splits) == 3:
            last_one = splits[-1]
            prec = " ".join(splits[:-1])
            if len(last_one) > 1:
                prec+=' 0xHH'
                extras.append(last_one)
                # print(hex(int(last_one, 16)))
            else:
                prec+=' '+ last_one
                # print('register', last_one)
            # print(prec)
            # print("OP __")
            # print(instr)
        line_code.append(isa_mapping[prec])
        line_code.extend(extras)

        program_code.append(line_code)
        stack.extend(program_code[-1])
    rom = ControlRom(addr_width=2**16, data_width=8)
    for i, row in enumerate(stack):
        rom[i] = row.split('x')[1]
    rom.save_as_hex(output_fname)