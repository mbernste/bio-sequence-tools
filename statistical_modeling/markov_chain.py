#!/usr/bin/python

from custom_discrete_distribution import CustomDiscreteDistribution

class MarkovChain:

    def __init__(self, statesToTransitionProbabilites={}, startStateProbabilities={}):
        """
        Arguments:
        statesToTransitionProbabilites -- A dictionary mapping a state to a dictionary storing the transition probabilities.
            The mapped dictionary maps a state to a probability of transition to from the outer dictionary's key to the 
            inner dictionary's key.
        startStateProbabilities -- A dictionary mapping a state to a probability that the chain begins at that state.
        """
        self.states = {}
        
        if not statesToTransitionProbabilites == None:
            for state, transitionProbabilities in statesToTransitionProbabilites.iteritems():
                self.states[state] = CustomDiscreteDistribution(transitionProbabilities)
        
        self.startStateDistribution = CustomDiscreteDistribution(startStateProbabilities)

    def __repr__(self):
        strRep = ""
        for state, transitionDistribution  in self.states.iteritems():
            strRep += "[" + str(state) + "]\n"
            for toState, p in transitionDistribution.probabilities.iteritems():
                strRep += str(p) + " --> [" + str(toState) + "]\n" 
            strRep += "\n"
        return strRep

    def setStartStateProbabilities(self, startStateProbabilities):
        """
        Arguments:
        startStateProbabilities -- A dictionary mapping a state to a probability that the chain begins at that state.
        """
        self.startStateDistribution = CustomDiscreteDistribution(startStateProbabilities)

    def addState(self, state, transitionProbabilities):
        """
        Add a state to the model.

        Arguments:
        state -- the new state
        transitionProbabilities -- A dictionary that maps other states in the model to probabilities of transition to 
            that state.
        """
        self.states[state] = CustomDiscreteDistribution(transitionProbabilities)

    def generateData(self, outputLength, startState=None):
        """
        Generate data from the Markov chain.

        Arguments:
        outputLength -- number of states to traverse in the model
        startState -- state to begin generation.  If not specified, this method will sample from the start state distribution.
        """    
        if startState == None:
            startState = self.startStateDistribution.sample()
        
        output = [startState]

        currState = startState
        for i in range(0, outputLength):
            currState = self.states[currState].sample()
            output.append(currState)

        return output
        
        
