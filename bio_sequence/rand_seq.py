#!/usr/bin/python

import sys
import random
from sequence import Sequence
import fasta

NUCLEOTIDES = ['A', 'C', 'T', 'G']

def randNucleotide():
    i = random.randint(0, 3)
    return NUCLEOTIDES[i]

def randNucleotideExlude(excludedNucleotides):
    pickFrom = [nucl for nucl in NUCLEOTIDES if nucl not in excludedNucleotides]
    i = random.randint(0, len(pickFrom)-1)
    return pickFrom[i]    

def genSequence(length):
    seq = ""
    for i in range(0, length):
        seq += randNucleotide()
    return seq

def randomSequence(name, length):
    seq = genSequence(length)
    return Sequence(name, seq)

def main():
    name = sys.argv[1]
    length = int(sys.argv[2])
    seq = randomSequence(name, length)
    print fasta.formatSequenceToFasta(seq)

if __name__ == "__main__":
    main()
