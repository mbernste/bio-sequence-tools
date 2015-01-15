#!/usr/bin/python

import sys
sys.path.append("../../statistical_modeling/")

import math
import markov_chain
import random
from custom_discrete_distribution import CustomDiscreteDistribution

MAX_Q_SCORE = 93
MIN_ASCII = 32
LOG_BASE = 10.0
FACTOR = -10.0

class QScoreModel:

    def __init__(self, intervalMarkovChains, intervalSize, startIntervalProbabilities):
        self.intervalMarkovChains = intervalMarkovChains
        self.intervalSize = intervalSize
        self.startIntervalDistribution = CustomDiscreteDistribution(startIntervalProbabilities)

    def generateQScoreSequence(self):
        currInterval = self.startIntervalDistribution.sample()
        intervals = [currInterval]

        for markovChain in self.intervalMarkovChains:
            currInterval = markovChain.states[currInterval].sample()
            intervals.append(currInterval)

        scores = []
        for interval in intervals:
            scores.append(random.randint(interval, min(interval + self.intervalSize, MAX_Q_SCORE+1) - 1))

        return scores

    def generateQScoreString(self):
        scoreStr = ""
        scores = self.generateQScoreSequence()
        for score in scores:
            scoreStr += unichr(score + MIN_ASCII)
        return scoreStr

def convertQScoreToProbability(qScore):
    return math.pow(LOG_BASE, qScore / FACTOR)

def convertQScoreToAscii(qScore):
    return unichr(qScore + MIN_ASCII)
