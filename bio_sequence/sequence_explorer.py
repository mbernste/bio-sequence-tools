#!/usr/bin/python

import sys
import sequence
import statistics
import fasta

def totalSeqLength(seqs):
    totalLength = 0
    for seq in seqs.values():
        totalLength += len(seq.sequence)
    return totalLength

def averageSeqLength(seqs):
    lengths = []
    for seq in seqs:
        lengths.append(len(seq.sequence))
    return statistics.mean(lengths)

def readSequences(file):
    return fasta.readFastaFile(file)    

def main():
    file = open(sys.argv[1], 'r')
    seqs = readFastaFile(file)
    print seqs

if __name__ == "__main__":
    main()

