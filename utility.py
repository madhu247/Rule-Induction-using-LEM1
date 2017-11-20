import numpy as np
import pandas as pd

def computePartitions(S):
    """
    Takes a list of list of list of tuples and gives you two vectors that
    stores both partition sets and concept name of that partition set
    """
    # gets unique list of cases which are used as keys for dictionaries
    a = list(set([tuple(i) for i in S]))
    partitionset = dict.fromkeys(a, [])
    for i in range(len(a)):
        # Creating a dictionary with all unique cases
        partitionset[a[i]] = []
    for i in range(len(a)):
        for j in range(len(S)):
            if(a[i] == tuple(S[j])):
                partitionset[a[i]].append(j)
    partset = []
    concept = []
    for keys in partitionset:
        concept.append(keys)
        partset.append(set(partitionset[keys]))
    return partset,concept


def isConsistent(attrPartitions, decPartitions):
    """
    inputs          : output of compute Partitions
    Returns true    : when A* is subset of d*
    Returns false   : when A* is not subset of d*
    """
    for t in attrPartitions:
        logicalValue = False
        for s in decPartitions:
            # returns false if all the A* elements are not subset of d*
            # because d* is a list of sets for unique concepts
            logicalValue = logicalValue or t.issubset(s)
        if(logicalValue == False):
            return False
    return True


def LEM1(S, R):
    """
    input       : list of list of tuples of attributes and decisions
    output      : list of list of tuples after applying LEM1 with
                  few attribute values
    """
    R_partitions = computePartitions(R)
    S_partitions = computePartitions(S)
    P = S[:]
    if(isConsistent(S_partitions[0], R_partitions[0])):
        tempS = tupleToDict(S)

        df = pd.DataFrame(tempS)
        # collect all the column names to keep track of removed attribute name
        XColNames = list(df.columns.values)
        for i in range(len(df.columns)-1):
            # Reomve first column Name and pass to the dataFrame
            bkpCol = XColNames.pop(0)
            Q = df.ix[:, XColNames].T.to_dict().values()
            Q1 = dictToTuple(Q)
            Q_partitions = computePartitions(Q1)
            if (isConsistent(Q_partitions[0], R_partitions[0])):
                P = Q1[:]
            else:
                # after removing column if the dataset if not consistent append the
                # column to the end of Column Names. Cause everytime we are removing
                # the first element from the Column Names
                XColNames.append(bkpCol)
        return P
    return """ Something went wrong with LOWER and UPPER approximations !!! """


def cutpointStrategy(listOfDict):
    """
    Applying discritization using all cutpoint strategy
    """
    df = pd.DataFrame(listOfDict)
    resultDF = df.copy(deep=True)
    for i in df.columns:
        if(df[i].dtype == np.float64):
            distNumValues = list(set(df.loc[:,i].values))
            distNumValues.sort()
            cutPoints = [(distNumValues[j]+distNumValues[j+1])/2 for j in range(len(distNumValues)-1)]
            del resultDF[i]
            for k in range(len(cutPoints)):
                for j in range(df.shape[0]):
                    if(df.loc[j,i] < cutPoints[k]):
                        resultDF.loc[j,i+str(cutPoints[k])] = str(min(distNumValues)) + ".." + str(cutPoints[k])
                    else:
                        resultDF.loc[j,i+str(cutPoints[k])] = str(cutPoints[k]) + ".." + str(max(distNumValues))
    return resultDF.T.to_dict().values()


def tupleToDict(tup):
    """convets a tuple to dictionary"""
    dic = []
    for i in range(len(tup)):
        dic.append(dict(tup[i]))
    return dic


def dictToTuple(dic):
    """Converts a ditionary to tuple"""
    tup = []
    for i in range(len(dic)):
        tup.append(dic[i].items())
    return tup


def generateRules(singleCovering, decisions):
    """
    Generate Rules from the given single covering to the decisions
    """
    tempCovering = tupleToDict(singleCovering)
    tempDecisions = tupleToDict(decisions)

    coverDF = pd.DataFrame(tempCovering)
    decisionsDF = pd.DataFrame(tempDecisions)

    combinedDF = pd.concat([coverDF, decisionsDF], axis=1)

    ruleDF = combinedDF[combinedDF.iloc[:,-1] != 'madhu']
    # ruleDF = ruleDF.drop_duplicates()
    conceptblockDF = ruleDF.copy(deep=True)
    del conceptblockDF['class']

    ruleDict = conceptblockDF.T.to_dict().values()
    ruleTuple = dictToTuple(ruleDict)


    ruleset = set(ruleDF.index.values)

    for i in range(len(ruleTuple)):
        listofsets = []
        count = 0

        for j in range(len(ruleTuple[i])):
            # collect the cases that are satisfying a rule from the ruleTuple
            listofsets.append(set(combinedDF[combinedDF[ruleTuple[i][j][0]] == ruleTuple[i][j][1]].index.values))

        for m in range(len(listofsets)):
            if (len(listofsets) > 1):
                # drop the first condition from the rule
                appendlast = listofsets.pop(0)

            # compute the case Numbers thar are satifying the ruleTUple
            u = set.intersection(*listofsets)

            if (not u.issubset(ruleset)):
                # Check whether the remaining attributes satisfy the cases
                # if not append the condition to the attribute list
                listofsets.append(appendlast)
            elif(len(ruleTuple[i]) > 1):
                # if yes remove the dropped attribute from the list
                ruleTuple[i].pop(m-count)
                count = count + 1

    return list(set([tuple(i) for i in ruleTuple]))


def lowerApprox(concept, attrPartitions, decPartitions):
    """ generates a decision vector satisfying lower approximations"""
    conceptList = []
    dictKey = 'class' #'LowerApprox['+concept+']'
    lowAConcet = {}
    lowAConcept = []
    conceptList.append(concept)
    lowA = set()
    for i in range(len(decPartitions[0])):
        if conceptList == [j[1] for j in decPartitions[1][i]]:
            for a in attrPartitions:
                if(a.issubset(decPartitions[0][i])):
                    lowA = lowA.union(a)
    numCases = max([max(a) for a in attrPartitions])
    # Add place holder for the cases that doesnt belong to the concept
    desRow = [concept if (i in lowA) else 'madhu' for i in range(numCases+1)]
    for m in range(len(desRow)):
        lowAConcet[dictKey] = desRow[m]
        lowAConcept.append(lowAConcet.items())
    return lowAConcept


def upperApprox(concept, attrPartitions, decPartitions):
    """ generates a vector with that decision satisfying upper Approximations"""
    conceptList = []
    dictKey = 'class'     #'UpperApprox['+concept+']'
    upAConcet = {}
    upAConcept = []
    conceptList.append(concept)
    upA = set()
    for i in range(len(decPartitions[0])):
        if (conceptList == [j[1] for j in decPartitions[1][i]]):
            for a in attrPartitions:
                if(a.intersection(decPartitions[0][i])):
                    upA = upA.union(a)
    numCases = max([max(a) for a in attrPartitions])
    # Add place holder for the cases that doesnt belong to the concept
    desRow = [concept if (i in upA) else 'madhu' for i in range(numCases+1)]
    for m in range(len(desRow)):
        upAConcet[dictKey] = desRow[m]
        upAConcept.append(upAConcet.items())
    return upAConcept


def writeToFile(ruleset, className, classValue, fp):
    """ Writes the Rules to a file in the desired format"""
    size = len(ruleset)
    if (size != 0):
        for i in range(size):
            j=0
            while(j<len(ruleset[i])-1):
                fp.write(str(ruleset[i][j]).replace("'", "")+' & ')
                j = j+1
            fp.write(str(ruleset[i][j]).replace("'", "")+" -> ("+className+", "+classValue+") \n")
    fp.close()
