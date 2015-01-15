#!/usr/bin/python

import sys
sys.path.append("./..")

import fasta
import utils
from os.path import join
from optparse import OptionParser
from sequence import Sequence
from read_simulator import Mapping
import matplotlib.pyplot as plt

class Bin:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.count = 0
    
    def __repr__(self):
        return "[" + str(self.start) + ", " + str(self.end) + ")=" + str(self.count)

def updateBins(mapping, bins, binSize, readLength):
    added = 0
    seqStart = mapping.startPosition
    seqEnd = mapping.startPosition + readLength - 1

    print "SeqStart=" + str(seqStart)
    print "SeqEnd=" + str(seqEnd)

    print "Updating with mapping: " + str(mapping.readId) + "," + str(mapping.transcriptId) + "," + str(mapping.startPosition)
    for bin in bins:
        added = 0
        
        if seqStart >= bin.start and seqStart < bin.end and seqEnd >= bin.end:
            bin.count += (bin.end - seqStart) 
        elif seqStart < bin.start and seqEnd >= bin.end:
            bin.count += binSize
        elif seqStart <= bin.start and seqEnd >= bin.start and seqEnd <= bin.end:
            bin.count += (seqEnd - bin.start) + 1       
        elif seqStart >= bin.start and seqEnd <= bin.end:
            bin.count += (seqEnd - seqStart) + 1

def generateEmptyBins(binSize, sequenceLength, readLength):
    bins = []
    for i in range(0, sequenceLength, binSize):
        if i + binSize > sequenceLength:
            bins.append(Bin(i, sequenceLength+1))
        else:
            bins.append(Bin(i, i + binSize))
    return bins

    

def readMappings(mappingFilePath, transcriptId):
    mappings = []
    file = open(mappingFilePath, 'r')
    for line in file:
        entries = line.split(",")
        if entries[1] == transcriptId:
            mappings.append( Mapping(entries[0], entries[1], int(entries[2]), utils.strToBool(entries[3])))
    file.close()
    return mappings

def fillBins(mappings, bins, binSize, readLength):
    for mapping in mappings:
        updateBins(mapping, bins, binSize, readLength)

def getLeftSideOfBars(bins):
    sides = []
    for bin in bins:
        sides.append(bin.start)
    return sides

def getCounts(bins, binSize):
    counts = []
    for bin in bins:
        counts.append(bin.count / float(binSize))
    return counts

def plotBins(bins, binSize):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    counts = getCounts(bins, binSize)
    sides = getLeftSideOfBars(bins)
    rects = ax.bar(left=sides, height=counts, width=binSize)
    plt.show()

def getSequence(options):
    """
    If user specificied a root directory, then sequence file option should just be a file name.  If no root
    directory was specified, the sequence file option should be a path to the sequence file.
    """
    seq = None
    if options.root == None:
        seq = fasta.readFastaFile(options.sequence_file)[options.sequence_name]
    else:
        seq = fasta.readFastaFile(join(options.root, options.sequence_file))[options.sequence_name]
    print seq
    return seq

def getMappings(options):
    """
    If user specificied a root directory, then the mappings file file option should just be a file name.  If no root
    directory was specified, the mapping file option should be a path to the mapping file.
    """
    mappings = None
    if options.root == None:
        mappings = readMappings(options.mapping_file, options.sequence_name)
    else:
        mappings = readMappings(join(options.root, options.mapping_file), options.sequence_name)
    return mappings

def main():
    parser = OptionParser()

    parser.add_option("-r", "--root", help="The directory in which the map file and sequence file are both stored")
    parser.add_option("-m", "--mapping_file", help="Name of file that contains read mapping data")
    parser.add_option("-l", "--read_length", type="int", help="Length of each read in the mapping")
    parser.add_option("-f", "--sequence_file", help="Name of file that contains the transcripts")
    parser.add_option("-b", "--bin_size", type="int", help="Number of base pairs in which to start positions")
    parser.add_option("-s", "--sequence_name", help="Name of sequence for which to generate coverage data")
    (options, args) = parser.parse_args()

    print options
 
    readMappingPath = options.mapping_file
    readLength = options.read_length
    binSize = options.bin_size

    seq = getSequence(options)
    bins = generateEmptyBins(binSize, len(seq.sequence), options.read_length)
    mappings = getMappings(options)
    fillBins(mappings, bins, binSize, readLength)
    print bins

    plotBins(bins, binSize)

if __name__ == "__main__":
    main()

