#!/usr/bin/python

import fasta
import os
from os.path import join, isfile
from sequence import Sequence
from optparse import OptionParser

def hasFastaExtension(filePath):
    """
    Check if file at given path has a FASTA extension
    
    Arguments:
    filePath -- the path to the file of question
    """
    if isfile(filePath):
        extension = filePath.split(".")[-1]
        if extension == "fa" or extension == "fasta":
            return True

    return False


def sequenceExists(sequence, nameToSequences):
    """
    Check if sequence is in a dictionary of sequences names to sequence objects.  Only checks equality of
    of the sequence string itself and disregards name.

    Arguments:
    sequence -- the target sequence
    nameToSequence -- a dictionary mapping sequence names to sequence objects
    """
    for name, seq in nameToSequences.iteritems():
        print str(sequence.sequence) + " against " + str(seq.sequence)
        if sequence.sequence == seq.sequence:
            print "Match"
            return True
    return False

def getAllFastaFiles(path):
    """
    Return paths to all FASTA files in a given directory.

    Arguments:
    path -- the path to the directory for which to list the FASTA files
    """
    filePaths = []
    for f in os.listdir(path):
        filePath = join(path, f)
        if hasFastaExtension(filePath):
            filePaths.append(filePath)
    return filePaths

def getAllSequences(path, ommitDuplicateSequences):
    mergedNameToSeqs = {}
    for filePath in getAllFastaFiles(path):
        namesToSeqs = fasta.readFastaFile(filePath)
        for name, seq in namesToSeqs.iteritems():
            if not (ommitDuplicateSequences and sequenceExists(seq, mergedNameToSeqs) ):
                if name in mergedNameToSeqs.keys():
                    seq.name = seq.name + "+"
                    mergedNameToSeqs[name + "+"] = seq
                else:
                    mergedNameToSeqs[name] = seq
    return mergedNameToSeqs

def mergeFastaFiles(path, mergedFilePath, ommitDuplicateSequences):
    seqs = getAllSequences(path, ommitDuplicateSequences)
    fasta.writeFastaFile(mergedFilePath, seqs.values())
    print "Merged fasta files in " + path + " into " + mergedFilePath + "."

def main():
    parser = OptionParser()
    parser.add_option("-p", "--path_to_fastas", help="Path of directory that contains the FASTA files to be merged.")
    parser.add_option("-o", "--output_file_path", help="Path of file to write the merged FASTA to.")
    parser.add_option("-d", "--ommit_duplicates", action="store_true", help="Ommit duplicate sequences when merging.")
    (options, args) = parser.parse_args()

    print options

    mergeFastaFiles(options.path_to_fastas, options.output_file_path, options.ommit_duplicates)

if __name__ == "__main__":
    main()

