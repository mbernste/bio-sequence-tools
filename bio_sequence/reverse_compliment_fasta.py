#!/usr/bin/python

import fasta
import os
import sequence
from os.path import join, isfile
from sequence import Sequence
from optparse import OptionParser

def reverseComplimentFasta(inputPath):
    """
    Read all sequences from a fasta file, compute their reverse compliments.
    """
    reverseSeqs = []
    namesToSeqs = fasta.readFastaFile(inputPath)
    for name, seq in namesToSeqs.iteritems():
        reverseSeq = sequence.reverseCompliment(seq.sequence)
        reverseSeqs.append(Sequence(name=name, sequence=reverseSeq))
    return reverseSeqs    

def main():
    parser = OptionParser()
    parser.add_option("-p", "--input_file_path", help="Path to input fasta file")
    parser.add_option("-o", "--output_file_path", help="Path of file to write the reverse complimented FASTA to.")
    (options, args) = parser.parse_args()

    print options

    reverseSeqs = reverseComplimentFasta(options.input_file_path)
    fasta.writeFastaFile(options.output_file_path, reverseSeqs)
    
if __name__ == "__main__":
    main()
