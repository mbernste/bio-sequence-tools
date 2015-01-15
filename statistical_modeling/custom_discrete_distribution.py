#!/usr/bin/python

import random
import cPickle as pickle

class Interval:
    """
    An interval within [0,1] and a corresponding value that is sampled when
    the uniform random variable falls within this range.
    """
    def __init__(self, value, bounds):
        self.bounds = bounds
        self.value = value
    
    def __repr__(self):
        return "{" + self.value + ": Bounds=" + str(self.bounds) + "}" 

class CustomDiscreteDistribution:
    """ 
    A custom discrete probability distribution in which values are associated
    with probabilities.  Values can then be sampled according to theses 
    probabilities. 
    """
    def __init__(self, probabilities={}):
        """ 
        Arguments:
        probabilites -- dictionary of values with associated probabilities
        """ 
        self.probabilities = probabilities;
        self.intervals = []
        lowerBound = 0.0
        for key, val in probabilities.iteritems():
            bounds = (lowerBound, lowerBound + val)
            lowerBound = lowerBound + val
            self.intervals.append(Interval(key, bounds))

    def sample(self):
        """
        Sample a value from this probability distribution.
        """
        rand = random.random()
        for interval in self.intervals:
            if rand >= interval.bounds[0] and rand < interval.bounds[1]:
                return interval.value
        if rand == 1:
            return self.intervals[-1].value 

def main():
    probabilities = {"A":0.25, "B":0.4, "C":0.35}
    c = CustomDiscreteDistribution(probabilities)
    print c.sample() 

if __name__ == "__main__":
    main()

