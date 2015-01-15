#!/usr/bin/python

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

    def __repr__(self):
        reprStr = "[Start Distribution]"
        

