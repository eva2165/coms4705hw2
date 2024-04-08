# coms4705hw2
This is a homework submission for COMSW4705 Natural Language Processing.

The CKY algorithm is written to `cky.py`, and some logic to verify validity of context-free grammars (in Chomsky normal form) is written to `grammar.py`. There are two data files, `atis3.pcfg`, which contains a probabilistic context-free grammar, and `atis3_test.ptb`, which contains a test corpus of example tree parses.

The parser is evaluated with the command `python evaluate_parser.py atis3.pcfg atis3_test.ptb`.
