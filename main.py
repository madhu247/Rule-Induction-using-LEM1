#!usr/bin/python
"""
    main.py, by Madhu Chegondi, 10-06-2017
    This program takes a data file and genrate rules for the data separate
"""
import utility

def main():
    """
    Initialize the Program
    """
    print "+----------------------------------------------------------------+"
    print "|                                                                |"
    print "|       PROGRAM TO GENERATE RULES FROM THE GIVEN DATASET         |"
    print "|       Author : Madhu Chegondi                                  |"
    print "|       Date   : 10/06/2017                                      |"
    print "|                                                                |"
    print "+----------------------------------------------------------------+"
    print ""
    filename = raw_input("Please enter input data filename >> ")
    outputFileName = raw_input("Please enter desired output data filename with rules >> ")
    print "\n"

    """ Reading File using f open in python"""
    fp = open(filename, 'r')

    # Wrote in an assumption that first 2 lines of the input data filename have
    # < a a a d >
    # [ attribute1 attribute2 attribute3 decision ]
    header1 = fp.readline()
    header2 = fp.readline().strip().split()
    AttNames = header2[1:-2]
    desNames = header2[-2]
    attr = []
    decisions = []
    for line in fp:
        if line.strip()[0] == '!':
            continue
        line = line.strip()
        columns = line.split()
        sourceAttr = {}
        sourceDes = {}
        for i in range(len(columns)-1):
            sourceAttr[AttNames[i]] = columns[i]
        attr.append(sourceAttr)
        sourceDes[desNames] = columns[-1]
        decisions.append(sourceDes.items())
    fp.close()

    attributes = utility.dictToTuple(attr)

    singleCovering = utility.LEM1(attributes, decisions)
    ruleset = utility.generateRules(singleCovering, decisions)
    print ruleset


if __name__ == "__main__":
    main()
