#!/usr/bin/python

import sys

class PSLMatch:

    def __init__(self):
        self.numCharsMatch = None
        self.querySeqName = None
        self.querySeqLength = None
        self.databaseSeqName = None
        self.databaseSeqLength = None

def parsePSLLine(line):
    entries = line.split('\t')
    match = PSLMatch()
    match.numCharsMatch = int(entries[0].strip())
    match.querySeqName = entries[9]
    match.querySeqLength = int(entries[10].strip())
    match.databaseSeqName = entries[13]
    match.databaseSeqLength = int(entries[14].strip())
    return match

def readPSLFIle(filePath):
    file = open(filePath, 'r')
    pslMatches = []
    for line in file.readlines():
        pslMatches.append(parsePSLLine(line))
    return pslMatches

def main():
    filePath = sys.argv[1]
    pslMatches = readPSLFIle(filePath)
    print pslMatches


if __name__ == "__main__":
    main()
