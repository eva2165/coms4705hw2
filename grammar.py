"""
COMS W4705 - Natural Language Processing - Spring 2023
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
# from math import fsum
import math

def rule_to_str(rule):
    return ' -> '.join([rule[0], ' '.join(rule[1])])

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None
        self.verimsg = 'FLAG_UNSET'
        self.read_rules(grammar_file)
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        
        nonterminals = self.lhs_to_rules.keys()
        
        for rules in self.lhs_to_rules.values():
            total_prob = 0.0
            for rule in rules:
                if len(rule[1]) == 2:
                    # First possible form
                    if rule[1][0] not in nonterminals:
                        self.verimsg = rule_to_str(rule) + \
                            " has terminal in RHS: " + rule[1][0]
                        return False
                    if rule[1][1] not in nonterminals:
                        self.verimsg = rule_to_str(rule) + \
                            " has terminal in RHS: " + rule[1][1]
                        return False
                elif len(rule[1]) == 1:
                    # Second possible form
                    if rule[1][0] in nonterminals:
                        self.verimsg = rule_to_str(rule) + \
                            " has nonterminal in RHS: " + rule[1][0]
                        return False
                else:
                    # Not in correct form
                    self.verimsg = rule_to_str(rule) + \
                        " in non-CNF form"
                    return False
                total_prob += rule[2]
            if not math.isclose(total_prob, 1.0):
                self.verimsg = "total probability of all LHS = " + \
                    rules[0][0] + " is " + str(total_prob)
                return False
        
        return True


if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        if grammar.verify_grammar():
            print(f"{sys.argv[1]} is a valid PCFG in CNF")
        else:
            print(f"{sys.argv[1]} is an invalid grammar: {grammar.verimsg}")
        
