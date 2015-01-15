#!/usr/bin/python

import sys
import math

def mean(vals):
    sum = 0.0
    for x in vals:
        sum += x
    return sum / len(vals)

def standardDeviation(vals):
    if (len(vals) < 1):
        return 0.0

    avg = mean(vals)
    sum = 0.0
    for x in vals:
        sum += math.pow(x - avg, 2)
    return math.sqrt(sum / len(vals))

    
def main():
    vals = [1, 2, 3, 4]
    print str(standardDeviation(vals))

if __name__ == "__main__":
    main()

