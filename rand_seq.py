#!/usr/bin/python

import sys
import random
from sequence import Sequence
import fasta

def randNucleotide():
    nucleotides = ['A', 'C', 'T', 'G']
    i = random.randint(0, 3)
    return nucleotides[i]

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
