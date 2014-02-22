#!/usr/bin/env python2

import math

class AwesomeDict:

    def __init__(self, size=8):
        self.size = size
        self.keys = [None] * size
        self.values = [None] * size
        

    def add_key_value_pair(self, key, value):
        # check if key exists already
        index = self.choose_index(key)
        self.keys[index] = key
        self.values[index] = value    
        print self.keys
        print self.values    

    def dumbhash(self,key):
        if key == 'maja':
            return math.factorial(8)
        else:
            return math.factorial(9)

    def choose_index(self, key):
        i = 0
        while i < self.size:
            index = (self.dumbhash(key) % (self.size - i) + (self.dumbhash(key)+ 1) % \
             (self.size - i)) % self.size
            if not self.keys[index]:
                return index
            elif self.keys[index] == key:
                return index
            else:
                i += 1

        raise Exception("Ran out of slots :(")

# Keep only last three digits/bits? of hash? why?


    def get_value(self, key):
        index = 0#self.hashes.index(hash(key))
        return self.values[index]

    def remove_key(self, key):
        pass

    def __str__(self):
        return "\nvalues " + str(self.values) + \
            "\nkeys " + str(self.keys)

def main():
    names = AwesomeDict()
    for i in range(1):
        print i
        names.add_key_value_pair('maja', 100+i)
        names.add_key_value_pair('amy', 1200+i)
    

    print str(names)

if __name__ == '__main__':
    main()