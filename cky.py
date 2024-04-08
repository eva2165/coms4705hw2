"""
COMS W4705 - Natural Language Processing - Spring 2023
Homework 2 - Parsing with Probabilistic Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg
import copy

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar
        
    
    def parse(self, tokens):
        
        self.tokens = tokens
        self.table = dict()
        self.probs = dict()
        
        # Recursive call that accesses self.table,probs,tokens
        self.__parse__((0, len(self.tokens)))
        
        # assert check_table_format(self.table)
        # assert check_probs_format(self.probs)
        
        table = copy.deepcopy(self.table)
        probs = copy.deepcopy(self.probs)
        
        self.tokens, self.table, self.probs = None, None, None
        
        return table, probs
    
    def __parse__(self, span):
        
        # We can skip table[span]s that have already been parsed, because
        # the table is built from the bottom up
        try:
            self.table[span]
            return
        except KeyError:
            self.table[span] = dict()
            self.probs[span] = dict()
        
        if span[1] - span[0] == 1:
            terminal = self.tokens[span[0]]
            for rule in self.grammar.rhs_to_rules[(terminal,)]:
                self.table[span][rule[0]] = terminal
                self.probs[span][rule[0]] = math.log(rule[2])
            return
        
        for split in range(span[0] + 1, span[1]):
            
            leftspan = (span[0], split)
            rightspan = (split, span[1])
            
            self.__parse__(leftspan)
            self.__parse__(rightspan)
            
            for leftlhs in self.table[leftspan].keys():
                for rightlhs in self.table[rightspan].keys():
                    for rule in self.grammar.rhs_to_rules[(leftlhs, rightlhs)]:
                        prob = math.log(rule[2]) \
                            + self.probs[leftspan][leftlhs] \
                            + self.probs[rightspan][rightlhs]
                        try:
                            if prob > self.probs[span][rule[0]]:
                                # Overwrite backtrace
                                self.table[span][rule[0]] = \
                                    ((leftlhs, leftspan[0], leftspan[1]), \
                                     (rightlhs, rightspan[0], rightspan[1]))
                                self.probs[span][rule[0]] = prob
                        except KeyError:
                            # Write backtrace (no key rule[0] in dict)
                            self.table[span][rule[0]] = \
                                ((leftlhs, leftspan[0], leftspan[1]), \
                                 (rightlhs, rightspan[0], rightspan[1]))
                            self.probs[span][rule[0]] = prob

    def is_in_language(self, tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        table, _ = self.parse(tokens)
        if self.grammar.startsymbol in table[(0, len(tokens))]:
            return True
        else:
            return False
       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        return self.parse(tokens)
    
    # For debugging
    def get_table(self, tokens):
        table, _ = self.parse(tokens)
        return table


def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    if i + 1 == j:
        return (nt, chart[(i,j)][nt])
    
    return (nt, get_tree(chart, chart[(i,j)][nt][0][1], \
                                chart[(i,j)][nt][0][2], \
                                chart[(i,j)][nt][0][0]), \
                get_tree(chart, chart[(i,j)][nt][1][1], \
                                chart[(i,j)][nt][1][2], \
                                chart[(i,j)][nt][1][0]))
 
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        #print(parser.is_in_language(toks))
        #table,probs = parser.parse_with_backpointers(toks)
        #assert check_table_format(chart)
        #assert check_probs_format(probs)
        
