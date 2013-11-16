"""
parser.py  
Sophia Davis, for 11/15/13

This program takes a text-file containing a grammar and a sentence (in lower case) 
as commandline arguments, and performs the Earley algorithm to find 
all possible parses of the sentence given that grammar.
This implementation assumes the grammar is in Chomsky Normal Form 
(specifically that grammar rules output no more than two non-terminals) 
to format the correct parses.
"""
import sys

def main():
    if len(sys.argv) < 3:
        sys.stderr.write('Usage: python ' + sys.argv[0] + ' grammar_file.txt' + ' "sentence to parse" \n')
        sys.exit(1)
    
    sentence = sys.argv[2].split(' ')    
    f = open(sys.argv[1])
    
    # use dictionaries to store rules in grammar
    #   {alpha : [list of possible betas] }
    branch_rules = {} # rules with two-argument betas
    pos_rules = {} # unit productions
    terminals = {} # terminals
    
    # read in grammar, store each rule in corresponding dictionary
    for line in f:
        if line.strip('\n'):
            if line[0] == '#':
                continue # ignore comments
            rule = line.split('->')
            alpha = rule[0].strip(' ')
            beta = rule[1].strip(' ').strip('\n')
            if len(beta.split(' ')) > 1:
                if alpha in branch_rules.keys():
                    branch_rules[alpha].append(beta.split(' '))
                else:
                    branch_rules[alpha] = [beta.split(' ')]
            elif beta[0].isupper(	):
                if alpha in pos_rules.keys():
                    pos_rules[alpha].append(beta)
                else:
                    pos_rules[alpha] = [beta]
            else:
                if alpha in terminals.keys():
                    terminals[alpha].append(beta)
                else:
                    terminals[alpha] = [beta]
    f.close()        
    
    grammar = [branch_rules, pos_rules, terminals]
    earley(grammar, sentence)

### implements the Earley algorithm to find all possible parses for given sentence
def earley(grammar, sentence):
    
    n_bins = len(sentence) + 1
    branch_rules = grammar[0]
    pos_rules = grammar[1]
    terminals = grammar[2]
    
    # use dictionary to keep track of progress parsing sentence
    #   { timestep : [all rules that are still possible partial parses at timestep] }  
    chart = {} 
    for i in range(0, n_bins):
        chart[i] = []
    
    # add start symbol to bin 0
    #   each rule is of format: 
    #       [alpha, [beta], starting_index, ending_index, [current completed parse]]
    #   the dot in [beta] signifies how much of beta has been successfully matched to the
    #       input sentence 
    chart[0] = [['gamma', ['.', 'S'], 0, 0, []]]
    
    # for each rule in each bin, pass chart and rule to predictor, scanner, and completer functions
    #   these update the chart according to the rule
    for i in range(0, n_bins):

        for rule in chart[i]:
            chart = predictor(grammar, chart, i, rule)
            chart = scanner(grammar, chart, i, rule, sentence)
            chart = completer(chart, i, rule)

    # after processing final timestep, print all complete possible parses
    last_bin = chart[n_bins - 1]
    done = False
    i = 0
    
    print
    for rule in last_bin: 
        if rule[0] == 'gamma':
            i += 1
            backtrace = rule[4][0]
            done = True
            print "--- parse", i, "---"
            find_tree(backtrace)
            print
    if not done:
        print 'That sentence does not seem possible with this grammar. Please try again later. Good bye!'
    print
    
### prints a formatted parse tree
def find_tree(backtrace):
    i = backtrace[1:].index('(') + 1
    to_print = ''
    left_stack = []
    
    while i < len(backtrace):
        if backtrace[i] is '(':
            left_stack.append('(')
            print to_print
            print ' ' * len(left_stack),
            to_print = backtrace[i]
        else:
            if backtrace[i] is ')':
                if left_stack:
                    left_stack.remove('(')
            to_print = to_print + backtrace[i]
        i += 1
    print to_print

### adds rule to chart bin
#   does not add clones
#   returns updated chart bin
def add_rule(rule, chart_bin):
    if rule not in chart_bin:
        chart_bin.append(rule)
    return chart_bin

### implements the predictor of the Earley algorithm
# if there is a nonterminal to the right of the dot, add a new rule for each 
#   possible expansion of that non-terminal to the current timestep bin 
#   returns updated chart
def predictor(grammar, chart, index, rule):

    branch_rules = grammar[0]
    pos_rules = grammar[1]
      
    dot = rule[1].index('.')
    
    # if the dot is already at the end of beta, there are no possible expansions to process
    if dot == (len(rule[1]) - 1):
        return chart
    
    # beta argument to the right of the dot
    beta_current = rule[1][dot + 1]   
    
    # finds expansions in multi-argument betas
    if beta_current in branch_rules.keys():

        for beta_next in branch_rules[beta_current]:
        
            # add dot marking progress to rule if necessary
            if beta_next[0] is not '.':
                beta_next.insert(0, '.')
            
            chart[index] = add_rule([beta_current, beta_next, index, index, []], chart[index])
    
    # finds expansions in unit productions
    if beta_current in pos_rules.keys():

        for beta_next in pos_rules[beta_current]:
            chart[index] = add_rule([beta_current, ['.', beta_next], index, index, []], chart[index])

    return chart

### implements the scanner of the Earley algorithm
# if there is a POS tag to the right of the dot, check if that POS can generate the next
#   word in the input sentence
#   if so, move dot in the rule, and add the updated rule to the next chart bin
#   returns updated chart
def scanner(grammar, chart, index, rule, sentence):

    branch_rules = grammar[0]
    pos_rules = grammar[1]
    terminals = grammar[2]
        
    dot = rule[1].index('.')
    
    # if the dot is already at the end of beta, there are no possible expansions to process
    if dot == (len(rule[1]) - 1):
        return chart
    
    # beta argument to the right of the dot
    beta_current = rule[1][dot + 1]
    
    # finds associated terminals
    # if the next word in the input sentence can be produced by that beta argument
    #   add that rule to the next chart bin
    if beta_current in terminals.keys():
        if index < len(sentence):
            if sentence[index] in terminals[beta_current]:

                # begin to form the partial parse tree
                partial_parse = ['(' + beta_current + ' ' + sentence[index] +')']
                chart[index + 1] = add_rule([beta_current, [sentence[index], '.'], index, (index + 1), partial_parse], chart[index + 1])
            
    return chart

### implements the completer of the Earley algorithm
# if a rule has been completed, examine all previous rules at the chart bin where the rule was started
#   if a previous rule is still possible given the completion of the current rule
#       generate a new state with that rule in the current index
def completer(chart, index, rule):
    
    dot = rule[1].index('.')
    rule_start = rule[2]
    
    if dot == (len(rule[1]) - 1):
        completed = rule[0]
        
        # iterates over all rules in chart bin corresponding to the starting index of the
        #   completed rule
        for rule_prev in chart[rule_start]:
            
            rule_index = chart[rule_start].index(rule_prev)
            beta_prev = rule_prev[1]
            dot_prev = beta_prev.index('.')
            
            # if the rule hasn't been completed
            if len(beta_prev) is not (dot_prev + 1):
                
                # if the next argument of the beta is the completed tag
                if beta_prev[dot_prev + 1] == completed:
                    
                    completed_index = beta_prev.index(completed)
                    rule_prev_start = rule_prev[2]
                    alpha = rule_prev[0]
                    backtrace = rule[4][0]
                    
                    # add appropriate tags/parentheses to existing partial parse
                    #   relies on assumption of CNF grammar 
                    # if rule is unary 
                    if len(beta_prev) == 2:
                        new_backtrace = ['(' + alpha + ' ' + backtrace + ')']
                    # if first argument of a double-argument beta has been completed
                    elif dot_prev == 0:
                        new_backtrace = ['(' + alpha + ' ' + backtrace]
                    # otherwise, given CNF grammar, the second argument must have been completed
                    else:
                        new_backtrace = [rule_prev[4][0] + ' ' + backtrace + ')']
                    
                    # add rule with [alpha, [beta with dot moved], old start index, current index, [new backtrace]]
                    processed = beta_prev[0:dot_prev]
                    processed.append(completed)
                    processed.append('.')
                    beta = processed + beta_prev[completed_index + 1:]
                    
                    rule_progress = [alpha, beta, rule_prev_start, index, new_backtrace]
                    chart[index] = add_rule(rule_progress, chart[index])
    
    return chart
    
if __name__ == '__main__':
	main()