#!/usr/bin/python

import sys

NUM_CHARS_MATCH_INDEX = 0
QUERY_SEQ_NAME_INDEX = 9
QUERY_SEQ_LENGTH_INDEX = 10
DB_SEQ_NAME_INDEX = 13
DB_SEQ_LENGTH = 14

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
    match.numCharsMatch = int(entries[NUM_CHARS_MATCH_INDEX].strip())
    match.querySeqName = entries[QUERY_SEQ_NAME_INDEX]
    match.querySeqLength = int(entries[QUERY_SEQ_LENGTH_INDEX].strip())
    match.databaseSeqName = entries[DB_SEQ_NAME_INDEX]
    match.databaseSeqLength = int(entries[DB_SEQ_LENGTH].strip())
    return match

def readPSLFIle(filePath):
    pslMatches = []
    with open(filePath, 'r') as file:
        for line in file.readlines():
            pslMatches.append(parsePSLLine(line))
    return pslMatches

def main():
    filePath = sys.argv[1]
    pslMatches = readPSLFIle(filePath)
    print pslMatches

if __name__ == "__main__":
    main()
