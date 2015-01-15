#!/usr/bin/python

import sys
sys.path.append("../fastq_error")

from phred import QScoreModel
import cPickle as pickle

def main():
    f = open("qscore_model.pickle", 'r')
    qScoreModel = pickle.load(f)
    f.close()
    for i in range(0, 10):
        print qScoreModel.generateQScoreString()
        #print qScoreModel.generateQScoreSequence()


if __name__ == "__main__":
    main()

