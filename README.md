for Carleton NLP, Fall 2013

This program takes a text-file containing a grammar and a sentence (in lower case)as commandline arguments, and performs the Earley algorithm to find all possible parses of the sentence given that grammar.

This implementation assumes the grammar is in Chomsky Normal Form (specifically, that grammar rules output no more than two non-terminals) to format the correct parses.
