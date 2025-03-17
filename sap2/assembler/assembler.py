import os
import sys
import argparse



class Assembler:
    def __init__(self, symbol_table_file_path):
        self.symbol_table = self.construct_symbol_table(symbol_table_file_path)

    def assemble(self, program_file_path, output_path=None):
        f = open(program_file_path,'r')
        lines = f.read()
        f.close()
        parsed_program_lines = self.parse_program(lines)
        namespace = self.construct_namespace(parsed_program_lines)
        translated_lines = []
        for i, program_line in enumerate(parsed_program_lines):
            if len(program_line['raw_line'].strip()) == 0:
                continue
            translated_lines.append(self.translate_line(i+1,program_line['raw_line'], self.symbol_table, namespace))

        if output_path is None or output_path == '':
            f = open('bruh.o', 'wb')
        else:
            f = open(output_path, 'wb')
        for item, arg in translated_lines:
            f.write(bytes.fromhex(item['op_code'][2:]))
            print(item['op_code'][2:], end='')
            if arg is not None:
                f.write(bytes.fromhex(arg[2:]))
                print(arg[2:], end='')
        print("\nassembled successfully")
        f.close()

    def parse_program(self, lines):
        program_lines = []
        label = None
        for i, line in enumerate(lines.split("\n")):
            # check for comments
            if line.__contains__(";"):
                line = line.split(";")[0]
            # check for label
            if line.__contains__(":"):
                label = line.split(":")[0].strip()
                line = line.split(":")[1].strip()
            program_lines.append({"label":label,"raw_line":line.strip()})
            label = None
        return program_lines
    
    def is_arg_char(self, arg):
        try:
            if arg[0] == "'" and arg[2] == "'":
                return True
        except:
            return False
        return False
    
    def parse_arg_as_hex(self, arg:str, arg_len:str, little_endian = True):
        length = len(arg_len.split('x')[1])
        hex_string = ""
        if self.is_arg_char(arg):
            arg = f"{ord(arg[1])}"

        if arg.__contains__("x"):
            hex_string = arg.split("x")[1].zfill(length)
        elif arg.__contains__("b"):
            n_str = arg.split("b")[1]
            hex_string = str(hex(int(n_str, base=2)))[2:].zfill(length)
        else:
            hex_string = str(hex(int(arg, base=10)))[2:].zfill(length)  

        if length == 4 and little_endian:
            hex_string = hex_string[2:]+hex_string[:2]
        return '0x'+hex_string
            
    def construct_namespace(self, program_lines):
        namespace = {}
        count = 0
        for line in program_lines:
            label = line['label']
            raw_line = line['raw_line']
            if len(raw_line.strip())==0:
                continue            
            comps = raw_line.split(" ") 
            agg = ""
            is_op_found = False
            for i, component in enumerate(comps):
                agg+=component
                if agg in self.symbol_table:
                    if label is not None:
                        namespace[label] = self.parse_arg_as_hex(str(count),'0xHHHH')
                    count+= self.symbol_table[agg]['count']
                    is_op_found = True            

            if not is_op_found:
                raise Exception(f"Line-{count}: SyntaxError: Can't find the op\n {line}")
            
        return namespace
                
    
    def construct_symbol_table(self, symbol_table_file):
        f = open(symbol_table_file,'r')
        symbol_table_file = f.read()

        symbol_table = {}
        for line in symbol_table_file.split('\n'):
            # print(line)
            mnemonic, op_code = line.split('=')
            op_code, count = op_code.strip().split(' ')
            count = int(count.strip()[1])
            # clean mnemonic
            mnemonic_arr = mnemonic.split(" ")
            mnemonic_arr.remove('')
            mnemonic_key = "".join(mnemonic_arr)
            mnemonic_op=''
            mnemonic_arg = None
            for val in mnemonic_arr:
                if val != '0xHHHH' and val != '0xHH':
                    mnemonic_op+=val
                else:
                    mnemonic_arg=val
            # print(mnemonic_arr, end=' ')
            # print(op_code)
            symbol_table[mnemonic_op] = {
                'op_code' : op_code,
                'count' : count,
                'key':mnemonic_key,
                'arg':mnemonic_arg,
                'base':mnemonic_arr[0],
                'full_mnemonic':mnemonic
            }
        return symbol_table
    
    def translate_line(self, line_no, line, symbol_table, namespace):
        comps = line.split(" ")
        agg = ""
        for i, component in enumerate(comps):
            agg+=component.lower()
            if agg in symbol_table:
                arg = None
                if symbol_table[agg]['arg'] is not None:
                    if len(comps) < i+2:
                        raise Exception(f"Line-{line_no}: {symbol_table[agg]['base']} expected an Argument type {symbol_table[agg]['arg']}\nPlease use the template {symbol_table[agg]['full_mnemonic']}")    
                    if line.__contains__("' '"):
                        arg = "' '"
                    else:    
                        arg = comps[i+1]
                    if arg in namespace:
                        arg = namespace[arg]
                    else:
                        arg = self.parse_arg_as_hex(arg, symbol_table[agg]['arg'])
                    if len(arg)!=len(symbol_table[agg]['arg']):
                        raise Exception(f"Line-{line_no}: Length of argument in hex is {len(arg)-2}, but it should be {len(symbol_table[agg]['arg'])-2}, please make sure its not too large")
                return symbol_table[agg], arg
        raise Exception(f"Line-{line_no}: SyntaxError: Can't find the op\n {line}")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file argument.")
    parser.add_argument("--instruction_set_map", type=str, required=True, help="Path to the instruction set mapping")
    parser.add_argument("--path", type=str, required=True, help="Path to the assembly file")
    parser.add_argument("--output", type=str, required=True, help="Path to output file")
    
    args = parser.parse_args()
    
    assembler = Assembler(args.instruction_set_map)
    assembler.assemble(args.path, args.output)