#!/usr/bin/python

import sys
import sequence

from sequence import Sequence

FASTA_DESCRIPT_BEGIN = '>'
SPACE = ' '
NEW_LINE = '\n'

def formatSequenceToFasta(sequence):
    """
    Convert a sequence into the string corresponding to its entry in a FASTA file.

    Keyword arguments:
    sequence -- the sequence object
    """
    name = sequence.name
    seq = sequence.sequence
    entry = FASTA_DESCRIPT_BEGIN + name + NEW_LINE
    entry += seq
    return entry

def formatSequencesToFasta(sequences):
    fastaFormat = ""
    for seq in sequences:
        fastaFormat += formatSequenceToFasta(seq) + NEW_LINE
    return fastaFormat

def writeFastaFile(filePath, sequences):
    with open(filePath, 'w') as file:
        for seq in sequences:
            file.write(formatSequenceToFasta(seq) + NEW_LINE)

def readFastaFile(filePath):
    seqs = {}
    currSeq = Sequence()
    with open(filePath, 'r') as file: 
        for line in file:
            if not (line == None or len(line) == 0):
                if line[0] == FASTA_DESCRIPT_BEGIN:
                    if currSeq.name != None:
                        seqs[currSeq.name] = currSeq
                    currSeq = Sequence(sequence="")
                
                    currSeq.name = line[1:].strip()
                    currSeq.name = currSeq.name.replace (" ", "_")
                else:
                    currSeq.sequence = currSeq.sequence + line.strip()
        if currSeq.name != None and currSeq.sequence != None:
            seqs[currSeq.name] = currSeq
    return seqs
        
def main():
    seqs = readFastaFile(sys.argv[1])
    print seqs

if __name__ == "__main__":
    main()

