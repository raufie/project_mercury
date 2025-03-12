import sys
import argparse



class Assembler:
    def parse_program(self ,lines):
        program_lines = []
        label = None
        for i, line in enumerate(lines.split("\n")):
            # check for label
            if line.__contains__(":"):
                label = line.split(":")[0].strip()
                continue
            
            program_lines.append({"label":label,"raw_line":line.strip()})
            label = None
        return program_lines
    
    def construct_symbol_table(self, symbol_table_file):
        pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file argument.")
    parser.add_argument("--path", type=str, required=True, help="Path to the assembly file")