import numpy as np
import pandas as pd

def computePartitions(S):
    """
    Takes a matrix as input and computes partitions of given matrix
    Convert the given matrix to a list abd convert the list to tuples
    Create a dictionary with keys as unique tuples from the given matrix
    Assign a separate list to each key so each array is different
    """
    a = list(set([tuple(i) for i in S]))
    partitionset = dict.fromkeys(a, [])
    for i in range(len(a)):
        partitionset[a[i]] = []
    for i in range(len(a)):
        for j in range(len(S)):
            if(a[i] == tuple(S[j])):
                partitionset[a[i]].append(j)
    partset = []
    for keys in partitionset:
        partset.append(set(partitionset[keys]))
    return partset

def isConsistent(attrPartitions, decPartitions):
    """
    This function takes list of sets and checks for atleast one set that is not
    a subset of other.
    """
    for t in attrPartitions:
        logicalValue = False
        for s in decPartitions:
            logicalValue = logicalValue or t.issubset(s)
        if(logicalValue == False):
            return False
    return True


def tupleToDict(tup):
    dic = []
    for i in range(len(tup)):
        dic.append(dict(tup[i]))
    return dic

def dictToTuple(dic):
    tup = []
    for i in range(len(dic)):
        tup.append(dic[i].items())
    return tup


def LEM1(S, R):
    """
    Alternate to LEM1 which takes attribute value pairs and calculate rules set
    from them
    """
    R_partitions = computePartitions(R)
    S_partitions = computePartitions(S)
    P = S[:]
    if(isConsistent(S_partitions, R_partitions)):
        tempS = tupleToDict(S)

        df = pd.DataFrame(tempS)

        for i in range(len(df.columns)-1):
            df = df.iloc[:,:-1]
            Q = df.T.to_dict().values()
            Q1 = dictToTuple(Q)
            Q_partitions = computePartitions(Q1)
            if (isConsistent(Q_partitions, R_partitions)):
                P = Q1[:]
        return P
    return """
                ***** GIVEN DATASET IS NOT CONSISTENT *****
           """

def generateRules(singleCovering, decisions):
    """
    Generate Rules from the given single covering to the decisions
    """
    tempCovering = tupleToDict(singleCovering)
    tempDecisions = tupleToDict(decisions)

    coverDF = pd.DataFrame(tempCovering)
    decisionsDF = pd.DataFrame(tempDecisions)

    combinedDF = pd.concat([coverDF, decisionsDF], axis=1)

    print combinedDF
    ruleDict = combinedDF.T.to_dict().values()


    ruleTuple = dictToTuple(ruleDict)
    return list(set([tuple(i) for i in ruleTuple]))
