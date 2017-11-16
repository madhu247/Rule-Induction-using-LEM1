#!usr/bin/python
"""
    main.py, by Madhu Chegondi, 10-06-2017
    This program takes a data file and generate rules for the data separate
"""
import utility
import os
import pandas as pd
import time

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
    inputFile = raw_input("Please Enter Name Of Input DataFile >> ")
    # outputFileName = raw_input("Please enter desired output data filename with rules >> ")
    print "\n"
    outputFile = raw_input("Please Enter the Name Of Output DataFile >> ")
    print '\n'
    outputFile1 = outputFile + '.certain.r'
    outputFile2 = outputFile + '.possible.r'
    if not os.path.exists('output'):
        os.makedirs('output')

    """ Reading File using f open in python"""
    fp = open(inputFile, 'r')
    fpout1 = open('output/'+outputFile1, 'w')
    fpout2 = open('output/'+outputFile2, 'w')

    fpout1.close()
    fpout2.close()

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
            try:
                if(type(float(columns[i])) == float):
                    sourceAttr[AttNames[i]] = float(columns[i])
            except ValueError:
                sourceAttr[AttNames[i]] = columns[i]

        # attr list of dictionaries
        attr.append(sourceAttr)
        sourceDes[desNames] = columns[-1]
        # decisions is list of list of tuples
        decisions.append(sourceDes.items())
    fp.close()


    initial_time = time.time()
    updatedAttr = utility.cutpointStrategy(attr)
    final_time = time.time()
    # To test the updated decision table after applying all cutpoint Strategy
    # Please uncomment the below print statement
    # print pd.DataFrame(updatedAttr)
    print "time for executing cut point strategy", final_time - initial_time

    # Converiting list of dictionaries to "list of List of tuples"
    attributes = utility.dictToTuple(updatedAttr)
    # print decisions

    initial_time = time.time()
    desPart =  utility.computePartitions(decisions)
    attrPart = utility.computePartitions(attributes)
    final_time = time.time()
    print "time for Compute Partitions", final_time - initial_time


    x = utility.tupleToDict(decisions)
    numClasses = len(pd.DataFrame(x).drop_duplicates())
    classes = [i for i in pd.DataFrame(x).drop_duplicates()[desNames]]

    initial_time = time.time()
    for i in range(numClasses):
        lowerClass = utility.lowerApprox(classes[i], attrPart[0], desPart)
        singleLowerCovering = utility.LEM1(attributes, lowerClass)
        ruleset = utility.generateRules(singleLowerCovering, lowerClass)
        fpout1 = open('output/'+outputFile1, 'a')
        utility.writeToFile(ruleset, desNames, classes[i], fpout1)

    for i in range(numClasses):
        if(utility.isConsistent(attrPart[0], desPart[0])):
            fpout2 = open('output/'+outputFile2, 'a')
            fpout2.write("! Possible rule set is not shown since it is identical with the certain rule set")
            fpout2.close()
            break
        else:
            upperClass = utility.upperApprox(classes[i], attrPart[0], desPart)
            singleUpperCovering = utility.LEM1(attributes, upperClass)
            ruleset = utility.generateRules(singleUpperCovering, upperClass)
            fpout2 = open('output/'+outputFile2, 'a')
            utility.writeToFile(ruleset, desNames, classes[i], fpout2)
    final_time = time.time()
    print "time for generating Rules", final_time - initial_time



if __name__ == "__main__":
    main()
