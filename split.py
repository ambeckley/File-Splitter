# Author Aaron Beckley
# 26/9/2023
# Python 3.11
#

import os
import argparse
import hashlib

def main():
    try:
        argParse = argparse.ArgumentParser(description='A simple tool for splitting larger files into smaller files written in python', prog='A file splitter and joiner')
        argParse.add_argument('-v', '--version', action='version', version='%(prog)s version 1.0')
        argParse.add_argument('-j', '--join', action='store_true', help='select if join files')
        argParse.add_argument('-s', '--split', action='store_true', help='select if split files')
        argParse.add_argument('-b', '--size', action='store', type=str, help='the file size for the split parts')
        argParse.add_argument('-m', '--verifyMode', action='store_true', help='enables automatically checking md5 checksums, slows down the process, but verifies data integrity.')
        argParse.add_argument('-o', '--output', action='store', type=str, help='change the default output directory')
        argParse.add_argument('file', action='store', type=str, help='the file patch (if join the first file [with .001], if split the file to split)')
        args = argParse.parse_args()
        if args.join and args.split:
            print('Must be either join or split.')
            exit()
        if args.join:
            if args.verifyMode:
                join(args.file, args.output, True)
            else:
                join(args.file, args.output, False)
        elif args.split:
            if args.size == None:
                print('Select a file size. Example 1gb.')
                exit()
            if args.verifyMode: #md5 checksum
                split(args.file, args.output, getBytes(args.size), True)
            else:
                split(args.file, args.output, getBytes(args.size), False)
        else:
            print('Must be either join or split.')
            exit()
    except KeyboardInterrupt:
        print(' is caught, exiting...')
        exit()

    


#https://github.com/marcomg/openhjsplit
# Provide to copy a content of a file in another file (using buffer and a limit to copy)
def __copyInFile(iF, oF, buffersize=1024, tocopy = 0):
    copied = 0
    i = 0
    while True:
        i += 1
        elsetocpy = tocopy - copied
        # free to copy all
        if (elsetocpy - buffersize > 0) or (tocopy == 0):
            tmp = iF.read(buffersize)
            if tmp == b'':
                if i == 1:
                    return False
                else:
                    return True
            else:
                oF.write(tmp)
                copied += buffersize
        # last data to copy
        else:
            tmp = iF.read(elsetocpy)
            if tmp == b'':
                if i == 1:
                    return False
                else:
                    return True
            else:
                oF.write(tmp)
                return True


#https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Split files
def split(inFileSrc, output, splitIn, checksum):
    splitNumber = 1
    try:
        inFile = open(inFileSrc, 'rb')
    except FileNotFoundError:
        print('Error: the file %s does not exists. Exiting...' % (inFileSrc))
        exit()
    if checksum:
        print("In file checksum: " + md5(inFileSrc))
    while True:
        if output == None:
            outFile = open(inFileSrc + '.' + str('%03d' % (splitNumber)), 'wb')
        else:
            outFile = open(os.path.join(output, os.path.basename(inFileSrc)) + '.' + str('%03d' % (splitNumber)), 'wb')
        if not __copyInFile(inFile, outFile, 1024, splitIn):
            outFile.close()
            if output == None:
                os.remove(inFileSrc + '.' + str('%03d' % (splitNumber)))
            else:
                os.remove(os.path.join(output, os.path.basename(inFileSrc)) + '.' + str('%03d' % (splitNumber)))
            break
        else:
            outFile.close()
            splitNumber += 1

# Join files
def join(firstFileIn, output, checksum):
    firstFileInE = firstFileIn[:-3]
    outFileSrc = firstFileInE[:-1]
    joinNumber = 1
    if output != None:
        outFileSrc = os.path.join(output, os.path.basename(outFileSrc))
    outFile = open(outFileSrc, 'wb')
    while True:
        try:
            inFile = open(firstFileInE + str('%03d' % (joinNumber)), 'rb')
            __copyInFile(inFile, outFile, 1024, 0)
            inFile.close()
            joinNumber += 1
        except FileNotFoundError:
            if joinNumber <= 1:
                print('Error: the file %s.001 does not exists. Exiting...' % (firstFileIn))
            outFile.close()
            if checksum:
                print("Out file checksum: " + md5(outFileSrc))
            return



def getBytes(inVar):
    number = int(inVar[0:len(inVar)-2]) #Strings are arrays of chars that's why this works
    unit = inVar[len(inVar)-2:len(inVar)] #Get the last two characters of input, because that will be the unit
    unit = unit.upper() #This way we don't have to check if it lower case, but user can still input lower case and it work
    match unit: #Since python 3.10 match can be used for case
        case "KB":
            return int(number * 1000)
        case "MB":
            return int(number * 1000000)
        case "GB":
            return int(number * 1000000000) 
        case _:
            print("Error: " + unit + " is unregonized.")
            exit()




if __name__ == '__main__':
    main()