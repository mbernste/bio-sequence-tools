#!/usr/bin/python

import random
from optparse import OptionParser
from markov_chain import MarkovChain
from custom_discrete_distribution import CustomDiscreteDistribution 
from phred import QScoreModel
import cPickle as pickle

Q_SCORE_LINE = 3
MAX_Q_SCORE = 93
#MAX_Q_SCORE = 10
MIN_ASCII = 32

def getReadLength(inputPath):
    with open(inputPath, 'r') as infile:
        for i, line in enumerate(infile):
            if i == Q_SCORE_LINE:
                return len(line)

def buildEmptyTransitionCounts(qScoreIntervalSize, psuedocount):
    intervalToCount = {}
    for i in range(0, MAX_Q_SCORE, qScoreIntervalSize):
        intervalToCount[i] = {}
        for j in range(0, MAX_Q_SCORE, qScoreIntervalSize):
            intervalToCount[i][j] = psuedocount
            #print "Interval [" + str(i) + ", " + str(i + qScoreIntervalSize) + "] --> [" + str(j) + ", " + str(j + qScoreIntervalSize) + "] : " + str(intervalToCount[i][j])
    return intervalToCount    
    
def buildEmptyStartCounts(qScoreIntervalSize, psuedocount):
    intervalToCount = {}
    for i in range(0, MAX_Q_SCORE, qScoreIntervalSize):
        intervalToCount[i] = 1
    return intervalToCount

def buildEmptyPositionToTransitionCounts(readLength, qScoreIntervalSize, psuedocount):
    positionToTransCounts = []
    for i in range(0, readLength):
        positionToTransCounts.append( buildEmptyTransitionCounts(qScoreIntervalSize, psuedocount) )
    return positionToTransCounts

def getBinVal(score, qScoreIntervalSize):
    """
    Get the bin value for a given score.  For example, the score falls into the bin [20, 25] and has a bin value of 25.

    Argument:
    score -- the target score
    qScoreIntervalSize -- the size of the interval of the Q-score at each state of the Markov chain   
    """
    #print "Received score " + str(score)
    for binVal in range(0, MAX_Q_SCORE, qScoreIntervalSize):
        if score < binVal + qScoreIntervalSize:
            return binVal

def updateCounts(positionToTransCounts, startCounts, line, qScoreIntervalSize):
    #print "Q-score line: " + line

    # Update the counts of the very first score
    startScore = ord(line[0]) - MIN_ASCII
    #print "The start score is: " + str(startScore)
    startBin = getBinVal(startScore, qScoreIntervalSize)
    #print "The start bin is: " + str(startBin)
    startCounts[startBin] += 1

    # Update the transition counts for the Markov chain at each position
    for i in range(1, len(line)):
        #print "****"
        #print "Score " + line[i-1] + " to " + line[i]

        currScore = ord(line[i]) - MIN_ASCII 
        currBin = getBinVal(currScore, qScoreIntervalSize)   
        
        prevScore = ord(line[i-1]) - MIN_ASCII
        prevBin = getBinVal(prevScore, qScoreIntervalSize)

        #print "Origin score: " + str(ord(line[i-1]) - MIN_ASCII)
        #print "Origin bin: " + str(prevBin)
        #print "Destination score: " + str(ord(line[i]) - MIN_ASCII)
        #print "Destination bin: " + str(currBin)

        positionToTransCounts[i][prevBin][currBin] += 1

def buildMarkovChain(counts):
    markovChain = MarkovChain()

    print "Counts: " + str(counts)

    for origin in counts.keys():
 
        # Get sum of outgoing edges from current origin to determine denominator of probability calculation
        totalOutSum = 0
        for count in counts[origin].values():
            totalOutSum += count

        # Calculate transition probabilities from current origin
        transitionProbabilities = {}
        for destination, count in counts[origin].iteritems():
            transitionProbabilities[destination] = count / float(totalOutSum)

        markovChain.addState(origin, transitionProbabilities)
    
    print "Built Markov chain:\n" + str(markovChain)
    return markovChain    

def buildMarkovChainsFromCounts(positionToTransCounts):
    markovChains = []
    for transCounts in positionToTransCounts:
        markovChains.append( buildMarkovChain(transCounts) )
    return markovChains

def buildStartProbabilities(startCounts):
    startProbabilities = {}
    total = sum(startCounts.values())
    for bin, count in startCounts.iteritems():
        startProbabilities[bin] = count / float(total)
    return startProbabilities

def buildQScoreModel(inputPath, qScoreIntervalSize, psuedocount):
    """
    Build the QScore model from an input FASTQ file.

    Arguments:
    inputPath -- path to the FASTQ input file
    qScoreIntervalSize -- the size of the interval of the Q-score at each state of the Markov chain
    """
    readLength = getReadLength(inputPath)
    positionToTransCounts = buildEmptyPositionToTransitionCounts(readLength, qScoreIntervalSize, psuedocount)
    startCounts = buildEmptyStartCounts(qScoreIntervalSize, psuedocount)
    
    with open(inputPath, 'r') as infile:
        updateCount = 0
        for i, line in enumerate(infile):
            if (i + 1) % (Q_SCORE_LINE + 1) == 0:
                updateCount += 1
                if updateCount % 10000 == 0:
                     print "Processing read " + str(updateCount) + "..."
                updateCounts(positionToTransCounts, startCounts, line.strip(), qScoreIntervalSize)    
    positionToMarkovChain = buildMarkovChainsFromCounts(positionToTransCounts)

    #printCounts(positionToTransCounts)
    print startCounts

    return QScoreModel(positionToMarkovChain, qScoreIntervalSize, buildStartProbabilities(startCounts))

def printCounts(positionToTransCounts):
    for position in positionToTransCounts.keys():
        print "--------- Position " + str(position) + " ---------"
        for origin in positionToTransCounts[position].keys():
            print "\tOrigin " + str(origin)
            for destination in positionToTransCounts[position][origin].keys():
                print "\t\tDestination " + str(destination) + ": " + str(positionToTransCounts[position][origin][destination])

def writePickledModel(qScoreModel, outputPath):
    """
    Pickle the model and write it to a file.

    Arguments:
    qScoreModel -- the model
    outputPath -- the path to the file with the pickled model
    """
    f = open(outputPath, 'w')
    pickle.dump(qScoreModel, f)
    f.close()

def main():
    parser = OptionParser()
    parser.add_option("-i", "--input_path", help="Path to input FASTQ file.")
    parser.add_option("-q", "--q_score_interval_size", type="int", help="Size of the interval of the Q-Score at each state of each Markov chain.")
    parser.add_option("-c", "--psuedocount", type="int", help="Psuedocount to use when calculating parameters of each Markov chain.")
    parser.add_option("-o", "--output_path", help="Output path to file where the pickled model will be written")
    (options, args) = parser.parse_args()

    qScoreModel = buildQScoreModel(options.input_path, options.q_score_interval_size, options.psuedocount)
    writePickledModel(qScoreModel, options.output_path)

    for i in range(0, 10):
        print qScoreModel.generateQScoreString()
        #print qScoreModel.generateQScoreSequence()

if __name__ == "__main__":
    main()


