#!/usr/bin/python

import sys
sys.path.append("./..")
sys.path.append("./../fastq_error")

import fasta
import sequence
import random
import phred
import cPickle as pickle
import rand_seq
import numpy
from os.path import join
from numpy.random import dirichlet
from phred import QScoreModel
from sequence import Sequence
from custom_discrete_distribution import CustomDiscreteDistribution
from optparse import OptionParser

UNIFORM_ARG = "uniform"
DIRICHLET_ARG = "dirichlet"
CUSTOM_ARG = "custom"

FRAGMENT_LENGTH_MEAN = 200
FRAGMENT_LENGTH_STDEV = 20

FORWARD_SUFFIX = "/1"
REVERSE_SUFFIX = "/2"

class Mapping:
    def __init__(self, readId, transcriptId, startPosition, isForward):
        self.readId = readId
        self.transcriptId = transcriptId
        self.startPosition = startPosition
        self.isForward = isForward

    def __repr__(self):
        return "<" + "ReadId: " + str(self.readId) + ", TranscriptId: " + str(self.transcriptId) + ", StartPosition: " + str(self.startPosition) + ", IsForward: " + str(self.isForward) + ">" 

def modifyBaseWithError(base, qScore):
    pError = phred.convertQScoreToProbability(qScore)
    #print "ASCII Score: " + str(phred.convertQScoreToAscii(qScore)) + ", P: " + str(phred.convertQScoreToProbability(qScore)) 
    if random.random() < pError:
        #print "Introducing error!"
        return rand_seq.randNucleotideExlude([base])        
    else:
         return base

def modifySequenceWithErrors(seqStr, qScoreModel):
    modifiedSeqStr = ""
    qScores = qScoreModel.generateQScoreSequence()
    for i, base in enumerate(seqStr):
         modifiedSeqStr += modifyBaseWithError(base, qScores[i])
    return modifiedSeqStr

def generatePairedEndReadFromTranscript(transcript, readLength, qScoreModel=None):
    """
    Generate a paired-end read from a given transcript.
    """

    # Generate fragment
    fragmentLength = int(numpy.random.normal(FRAGMENT_LENGTH_MEAN, FRAGMENT_LENGTH_STDEV, 1)[0])
    startPos = random.randint(0, len(transcript.sequence) - fragmentLength)
    fragment = transcript.sequence[startPos : startPos + fragmentLength]
    
    # Generate reads from ends of fragment
    forwardSeq = fragment[0:readLength]
    reverseSeq = sequence.reverseCompliment(fragment)[0:readLength]
    if qScoreModel != None:
        forwardSeq = modifySequenceWithErrors(forwardSeq, qScoreModel)
        reverseSeq = modifySequenceWithErrors(reverseSeq, qScoreModel)
    forwardStartPos = startPos
    reverseStartPos = startPos + len(fragment) - readLength

    return ((forwardSeq, forwardStartPos), (reverseSeq, reverseStartPos), transcript.name)
 
def generateSingleEndReadFromTranscript(transcript, readLength, qScoreModel=None):
    startPos = random.randint(0, len(transcript.sequence) - readLength)
    seq = transcript.sequence[startPos : startPos + readLength]
    origSeq = seq
    if qScoreModel != None:
        seq = modifySequenceWithErrors(seq, qScoreModel)

    # TODO REMOVE
    #print "------------------"
    #print "Original/New"
    #print origSeq
    #print seq

    return (seq, startPos, transcript.name)

def simulatePairedEndReads(expressionLevels, transcripts, numReads, readLength, qScoreModel):
    forwardReads = []
    reverseReads = []
    mappings = []
    
    trueExpression = {}
    for transcript in transcripts.values():
        trueExpression[transcript.name] = 0.0 

    print "TRANSCRIPTS: " + str(transcripts)
    print "EXPRESSION LEVELS: " + str(expressionLevels)    

    # Generate reads
    dist = CustomDiscreteDistribution(expressionLevels)
    readId = 0
    for i in range(0, numReads):
        transcript = transcripts[dist.sample()]
        trueExpression[transcript.name] += 1.0
        pairedEndReadResult = generatePairedEndReadFromTranscript(transcript, readLength)
        ((forwardSeq, forwardStartPos), (reverseSeq, reverseStartPos), transcript.name) = generatePairedEndReadFromTranscript(transcript, readLength, qScoreModel)       

        # Unpack generated paired-end reads 
        forwardSeq = pairedEndReadResult[0][0]
        forwardStartPos = pairedEndReadResult[0][1]
        reverseSeq = pairedEndReadResult[1][0]
        reverseStartPos = pairedEndReadResult[1][1]
        transcriptId = pairedEndReadResult[2]
        
        readNameF = str(readId) + FORWARD_SUFFIX
        readNameR = str(readId) + REVERSE_SUFFIX
        readId += 1 

        forwardReads.append(Sequence(readNameF, forwardSeq))
        reverseReads.append(Sequence(readNameR, reverseSeq))

        mappings.append(Mapping(readNameF, transcriptId, forwardStartPos,True))
        mappings.append(Mapping(readNameR, transcriptId, reverseStartPos,False))

    # Calculate true expression by normalizing transcript counts
    sum = 0.0
    for count in trueExpression.values():
        sum += count
    for key, value in trueExpression.iteritems():
        trueExpression[key] = trueExpression[key] / sum

    return ((forwardReads, reverseReads), trueExpression, mappings)

def simulateSingleEndReads(expressionLevels, transcripts, numReads, readLength, qScoreModel):
    """ 
    Simulate single-end reads from a set of transcripts.
        
    Keyword arguments:
    expressionLevels -- dictionary maps transcript name to probability
    transcripts -- dictionary transcript name to sequence object
    numReads -- number of reads
    readLength -- length of each read
    """
    reads = []
    mappings = []

    trueExpression = {}
    for transcript in transcripts.values():
        trueExpression[transcript.name] = 0.0
    
    print "TRANSCRIPTS: " + str(transcripts)
    print "EXPRESSION LEVELS: " + str(expressionLevels)

    # Generate reads
    dist = CustomDiscreteDistribution(expressionLevels)
    for i in range(0, numReads):
        transcript = transcripts[dist.sample()]
        trueExpression[transcript.name] += 1.0
        singleEndReadResult = generateSingleEndReadFromTranscript(transcript, readLength, qScoreModel)
        readSeq = singleEndReadResult[0]
        startPos = singleEndReadResult[1]
        transcriptId = singleEndReadResult[2]

        readName = str(i) + "/1"
        reads.append(Sequence(readName, readSeq))
        mappings.append(Mapping(readName, transcriptId, startPos, True))

    # Calculate true expression by normalize transcript counts
    sum = 0.0
    for count in trueExpression.values():
        sum += count
    for key, value in trueExpression.iteritems():
        trueExpression[key] = trueExpression[key] / sum

    return (reads, trueExpression, mappings)

def readExpressionLevels(filePath):
    """
    Read expression levels from CSV file where first entry is transcript name, and 
    second entry is the expression level.
    """
    expressionLevels = {}
    file = open(filePath, 'r')
    for line in file.readlines():
        expressionLevels[line.split(',')[0] ] = float(line.split(',')[1])
    return expressionLevels

def generateExpressionLevels(transcripts, distribution):
    expressionLevels = {}
    if distribution == UNIFORM_ARG:
        for transcript in transcripts.values():
            expressionLevels[transcript.name] = 1.0 / len(transcripts)
    elif distribution == DIRICHLET_ARG:
        ones = numpy.ones(len(transcripts))
        probabilities = dirichlet(ones, 1)[0]
        for i, transcript in enumerate(transcripts.values()):
            expressionLevels[transcript.name] = probabilities[i] 
    print "Source expression: " + str(expressionLevels)
    return expressionLevels

def writeExpressionFile(expressionFilePath, trueExpression):
    file = open(expressionFilePath, 'w')
    for transcriptId, expression in trueExpression.iteritems():
        file.write(transcriptId + "," + str(expression) + "\n")
    file.close()

def writeMappingsFile(mappingsFilePath, mappings):
    file = open(mappingsFilePath, 'w')
    for mapping in mappings:
        file.write(str(mapping.readId) + "," + mapping.transcriptId + "," + str(mapping.startPosition) + "," + str(mapping.isForward) + "\n")
    file.close()
 
def getOutputFileNames(options):
    """
    Users have the options of explicitly passing in the names of each output file or to pass the name of experiment and have
    this program auto-generate the names of each output file using the experiment name.  This method parses the options and 
    determines the name of the output files.
    """
    readOutputForward = None
    readOutputReverse = None
    readOutput = None
    expressionOutput = None 
    mappingOutput = None 

    if options.simulation_name == None:
        readOutput = options.read_output
        expressionOutput = options.expression_output
        mappingOutput = options.mapping_output
    else:
        if (options.paired_end and options.separate_mates):
            readOutputForward = options.simulation_name + ".reads.forward.fa"
            readOutputReverse = options.simulation_name + ".reads.reverse.fa"
            readOutput = (readOutputForward, readOutputReverse)
        else:
            readOutput = options.simulation_name + ".reads.fa"
        expressionOutput = options.simulation_name + ".expression.txt"
        mappingOutput = options.simulation_name + ".mapping.txt"

    if options.destination != None:
        if (options.paired_end and options.separate_mates):
            readOutput = (join(options.destination, readOutput[0]), join(options.destination, readOutput[1]))
        else:
            readOutput = join(options.destination, readOutput)
        expressionOutput = join(options.destination, expressionOutput)
        mappingOutput = join(options.destination, mappingOutput)

    return (readOutput, expressionOutput, mappingOutput)

def loadQScoreModel(modelPath):
    f = open(modelPath, 'r')
    qScoreModel = pickle.load(f)
    f.close() 
    return qScoreModel

def main():
    parser = OptionParser()
    parser.add_option("-a", "--simulation_name", help="optional name of simulation.  All output files will be autogenerated using this value.")
    parser.add_option("-c", "--expression_file", help="file where custom expression levels are written. only used for custom expression levels")
    parser.add_option("-e", "--expression_level", default=UNIFORM_ARG, help="expression level distribution: uniform, dirichlet, custom (default: dirichlet)")
    parser.add_option("-l", "--read_length", type="int", help="read length")
    parser.add_option("-n", "--num_reads", type="float", help="number of reads")
    parser.add_option("-t", "--transcript_file", help="file where transcripts can be found")
    parser.add_option("-m", "--mapping_output", help="filename to store read to transcript mapping")
    parser.add_option("-p", "--paired_end", action="store_true", help="generate paired end reads")
    parser.add_option("-q", "--read_errors", action="store_true", help="generate reads with errors. Requires error model file path")
    parser.add_option("-r", "--read_output", help="filename to write reads")
    parser.add_option("-s", "--separate_mates", action="store_true", help="separate paired end reads into two files (used only when '-p' is used)")
    parser.add_option("-u", "--error_model_file", help="path to the error model file. Requred for the '-q' argument")
    parser.add_option("-x", "--expression_output", help="filename to write expression levels")
    parser.add_option("-d", "--destination", help="path to directory to write all output")
    (options, args) = parser.parse_args()

    print options

    # Load the Phred Q-Score model if reads are generated with errors
    qScoreModel = None
    if options.read_errors == True:
        qScoreModel = loadQScoreModel(options.error_model_file)

    numReads = int(options.num_reads)
    readLength = options.read_length
    expressionDistribution = options.expression_level
    transcripts = fasta.readFastaFile(options.transcript_file) 
   
    # Generate output paths based on options 
    readOutput, expressionOutput, mappingOutput = getOutputFileNames(options)

    # Read expression distribution
    if expressionDistribution == CUSTOM_ARG:
        expressionLevels = readExpressionLevels(options.expression_file)
    else:    
        expressionLevels = generateExpressionLevels(transcripts, expressionDistribution)

    trueExpression = None
    mappings = None
    if options.paired_end == True:
        reads, trueExpression, mappings = simulatePairedEndReads(expressionLevels, transcripts, numReads, readLength, qScoreModel)
        
        if (options.separate_mates):
            fasta.writeFastaFile(readOutput[0], reads[0])
            fasta.writeFastaFile(readOutput[1], reads[1])
        else:
            fasta.writeFastaFile(readOutput, reads[0] + reads[1])
        #fasta.writeFastaFile(readOutput, reads)
        #fasta.writeFastaFile(forwardReadOutput, reads[0])
        #fasta.writeFastaFile(reverseReadOutput, reads[1])
    else:
        reads, trueExpression, mappings = simulateSingleEndReads(expressionLevels, transcripts, numReads, readLength, qScoreModel)
        fasta.writeFastaFile(readOutput, reads)
    writeMappingsFile(mappingOutput, mappings)
    writeExpressionFile(expressionOutput, trueExpression)

if __name__ == "__main__":
    main()
