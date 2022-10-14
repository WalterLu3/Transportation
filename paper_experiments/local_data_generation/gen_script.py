import sys
import os


INPUT_NUMBERS = sys.argv[1]

for num in range(100,int(INPUT_NUMBERS)):
    os.system('python3 gen.py {}'.format(num))
    os.system('python3 visualization_script.py local/user{}.csv {}'.format(num,num))
