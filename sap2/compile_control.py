#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
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
    f = open("control_code.txt", 'r')
    stuff = f.read()
    pre_df = []
    for i,line in enumerate(stuff.split("\n")):
        con = line.split(":")[0]
        con_hex = decode(i)
        con_desc = "".join(line.split(':')[1:])
        pre_df.append({
            "con": con,
            "con_hex":con_hex,
            "con_desc":con_desc
        })
    df = pd.DataFrame(pre_df)

    compile_file_and_save("controller_programs/control_mini_abstraction.txt", 'controller_programs/control_rom.hex', 'controller_programs/op_rom.hex', con_debug=False, whole_debug=True)
