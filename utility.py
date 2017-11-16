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
    concept = []
    for keys in partitionset:
        concept.append(keys)
        partset.append(set(partitionset[keys]))
    return partset,concept


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


def LEM1(S, R):
    """
    Alternate to LEM1 which takes attribute value pairs and calculate rules set
    from them
    """
    R_partitions = computePartitions(R)
    S_partitions = computePartitions(S)
    P = S[:]
    if(isConsistent(S_partitions[0], R_partitions[0])):
        tempS = tupleToDict(S)

        df = pd.DataFrame(tempS)
        for i in range(len(df.columns)-1):
            df = df.iloc[:,1:]
            Q = df.T.to_dict().values()
            Q1 = dictToTuple(Q)
            Q_partitions = computePartitions(Q1)
            if (isConsistent(Q_partitions[0], R_partitions[0])):
                P = Q1[:]
        return P
    return """ Something went wrong with LOWER and UPPER approximations !!! """


def cutpointStrategy(listOfDict):
    """
    Convert numerical column to symbol columns using all cutpoint Strategy
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
    dic = []
    for i in range(len(tup)):
        dic.append(dict(tup[i]))
    return dic


def dictToTuple(dic):
    tup = []
    for i in range(len(dic)):
        tup.append(dic[i].items())
    return tup


# def droppingConditions(rules, DF):
"""
Compute partitions for (feel, hard) and (size, big) and the intersection will give you
the cases where we have (feel, hard) and (size, big) and then check for that is equal to
(z, negative or not)
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
            listofsets.append(set(combinedDF[combinedDF[ruleTuple[i][j][0]] == ruleTuple[i][j][1]].index.values))

        for m in range(len(listofsets)):
            if (len(listofsets) > 1):
                appendlast = listofsets.pop(0)

            u = set.intersection(*listofsets)

            if (not u.issubset(ruleset)):
                listofsets.append(appendlast)
            elif(len(ruleTuple[i]) > 1):
                ruleTuple[i].pop(m-count)
                count = count + 1

    return list(set([tuple(i) for i in ruleTuple]))


def lowerApprox(concept, attrPartitions, decPartitions):
    """ generates a vector with that decision"""
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
    desRow = [concept if (i in lowA) else 'madhu' for i in range(numCases+1)]
    for m in range(len(desRow)):
        lowAConcet[dictKey] = desRow[m]
        lowAConcept.append(lowAConcet.items())
    return lowAConcept


def upperApprox(concept, attrPartitions, decPartitions):
    """ generates a vector with that decision"""
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
    desRow = [concept if (i in upA) else 'madhu' for i in range(numCases+1)]
    for m in range(len(desRow)):
        upAConcet[dictKey] = desRow[m]
        upAConcept.append(upAConcet.items())
    return upAConcept


def writeToFile(ruleset, className, classValue, fp):
    size = len(ruleset)
    if (size != 0):
        for i in range(size):
            j=0
            while(j<len(ruleset[i])-1):
                fp.write(str(ruleset[i][j]).replace("'", "")+' & ')
                j = j+1
            fp.write(str(ruleset[i][j]).replace("'", "")+" -> ("+className+", "+classValue+") \n")
    fp.close()
