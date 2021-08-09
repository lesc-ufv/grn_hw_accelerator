READ = "r"
WRITE = "w"

NUM_NODES = "REPLACE_NUM_NODES"
ASSIGN_CODE = "REPLACE_ASSIGN_CODE"
TEMPLATE = "./base_code.txt"

import sys

def readInput(filename):
    fin = open(filename, READ)
    data = []
    for line in fin:
        data.append("")
        for c in line:
            if c == '(' or c == ')' or c == '=':
                data[-1] += ' ' + c + ' '
            elif c != '\n':
                data[-1] += c
    fin.close()
    return data

def writeCpp(filename, data):
    fout = open(filename, WRITE)
    fout.write(data)
    fout.close()
    return

def main():
    key_words = {"and", "or", "not", "(", ")", "=", ""}
    
    filename_in = sys.argv[1]
    lines = readInput(filename_in)
    
    all_words = []
    for l in lines:
        for w in l.split(' '):
            if w not in key_words:
                all_words.append(w.lower())
    
    all_words = sorted(list(set(all_words)))

    replace_dict = {
        "and":"&&", 
        "or":"||",
        "not":"!"  
    }
    for l in lines:
        for w in l.split(' '):
            if w.lower() in all_words:
                replace_dict[w.lower()] = all_words.index(w.lower())
    
    code_string = ""
    for l in lines:
        before = True
        for w in l.split(' '):
            w_lower = w.lower()
            if w_lower in replace_dict.keys():
                if w_lower not in all_words:
                    code_string += replace_dict[w_lower] + " "
                elif(before):
                    code_string += "aux[" + str(replace_dict[w_lower]) + "] "
                else:
                    code_string += "vet[" + str(replace_dict[w_lower]) + "] "
            else:
                if(w == '='):
                    before = False
                code_string += w + " "
        code_string += ";\n    "
        
    
    ftemp = open(TEMPLATE, READ)
    str_out = ftemp.read()
    ftemp.close()
    str_out = str_out.replace(NUM_NODES, str(len(all_words))).replace(ASSIGN_CODE, code_string)

    writeCpp(sys.argv[2], str_out)

    return


if __name__ == "__main__":
    main()