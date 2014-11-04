#!/usr/bin/python

compliments = {'A':'T', 'T':'A', 'G':'C', 'C':'G'}

class Sequence:
    def __init__(self, name=None, sequence=None):
        self.name = name
        self.sequence = sequence

    def __repr__(self):
        return "name:" + self.name + "\n" + "sequence:" + self.sequence

def complimentBase(base):
    base = base.upper()
    return compliments[base]
   

def reverseCompliment(seq):
    reverseComp = ""
    for base in seq[::-1]:
        reverseComp += complimentBase(base)
    return reverseComp
