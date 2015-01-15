#!/usr/bin/python

from markov_chain import MarkovChain
import cPickle as pickle

def main():
    startStateProbabilities = {"A" : 0.25, "B" : 0.4, "C" : 0.35}

    markovChain = MarkovChain()
    
    markovChain.addState("A", {"A" : 0.1, "B" : 0.8, "C" : 0.1})
    markovChain.addState("B", {"A" : 0.1, "B" : 0.1, "C" : 0.8})
    markovChain.addState("C", {"A" : 0.8, "B" : 0.1, "C" : 0.1})
    
    markovChain.setStartStateProbabilities(startStateProbabilities)

    print markovChain

    for i in range(0, 10):
        print markovChain.generateData(30)

    f = open("my_new_pickle.pickle", 'w')
    pickle.dump(markovChain, f)
    f.close()

if __name__ == "__main__":
    main()

