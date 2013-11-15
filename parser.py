"""
parser.py  
Sophia Davis,  for 11/15/13

This program implements the Earley algorthim to find all possible parses of a sentence.
This implementation assumes the given grammar is in CNF when forming the correct parse.
"""
import sys

def main():
    if len(sys.argv) < 3:
        sys.stderr.write('Usage: python ' + sys.argv[0] + ' grammar_file.txt' + ' "sentence to parse" \n')
        sys.exit(1)
    
    sentence = sys.argv[2].split(' ')    
    f = open(sys.argv[1])
    
    # use dictionaries to store grammar rules
    #   {alpha : [list of possible betas] }
    branch_rules = {} # rules with two-argument betas
    pos_rules = {} # unit productions
    terminals = {} # terminals
    
    # read in grammar, store each rule in corresponding dictionary
    for line in f:
        if line.strip('\n'):
            if line[0] == '#': # ignore comments
                continue
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
    print
    print
    print 'branch rules: '
    print branch_rules
    print 'pos rules: '
    print pos_rules
    print 'terminals: '
    print terminals        
    
    grammar = [branch_rules, pos_rules, terminals]
    earley(grammar, sentence)

### implements the Earley algorithm to find all possible parses for given sentence
def earley(grammar, sentence):
    
    n_bins = len(sentence) + 1
    chart = {}
    
    # create a dictionary with one key per time step
    #   store a list of all rules that are still possible partial parses for the given sentence
    #   as of that time step 
    for i in range(0, n_bins):
        chart[i] = []
    
    branch_rules = grammar[0]
    pos_rules = grammar[1]
    terminals = grammar[2]
    
    # add start symbol to bin 0
    #   each rule is of this format: 
    #       [alpha, [beta], starting_index, ending_index, [current completed parse]]
    #   the dot in [beta] signifies how much of the beta has been successfully matched to the
    #       input sentence 
    chart[0] = [['gamma', ['.', 'S'], 0, 0, []]]
    
    # for each rule in each bin, pass chart and rule to predictor, scanner, and completer functions
    # these update the chart according to the rule
    for i in range(0, n_bins):
        
        print
        print
        print " ##################### bin number ", i, "#####################"

        for rule in chart[i]:
            print
            print '******'
            print "processing rule: ", rule 
            print
            chart = predictor(grammar, chart, i, rule)
            chart = scanner(grammar, chart, i, rule, sentence)
            chart = completer(chart, i, rule)
    print
    print '~~~~~~~~~~~ results ~~~~~~~~~~~'
    for i in range(0, n_bins):
        print
        print ' ~~~~~~~ bin number', i, '~~~~~~~ '
        for rule in chart[i]:
            print rule
    print
    last_bin = chart[n_bins - 1]
    done = False
    
    # after processing final timestep, print all complete possible parses
    for rule in last_bin:
        if rule[0] == 'gamma':
            backtrace = rule[4][0]
            done = True
            print backtrace
            print
            find_tree(backtrace)
            print
    if not done:
        print 'That sentence does not seem possible with this grammar. Please try again later. Good bye!'

### prints a formatted parse tree
def find_tree(backtrace):
    i = backtrace[1:].index('(') + 1
    to_print = ''
    
    left_stack = []
    margin = 0
    while i < len(backtrace):
        if backtrace[i] is '(':
            left_stack.append('(')
            print to_print
            print ' ' * len(left_stack),
            to_print = backtrace[i]
            i += 1
        else:
            if backtrace[i] is ')':
                if left_stack:
                    left_stack.remove('(')
            to_print = to_print + backtrace[i]
            i += 1
    print to_print

### adds rules to chart bin
# does not add duplicates
# returns updated chart bin
def add_rule(rule, chart_bin):
    if rule not in chart_bin:
        print '      adding rule: ', rule
        chart_bin.append(rule)
    return chart_bin

### implements the predictor of the Earley algorithm
# if there is a nonterminal to the right of the dot, adds a new rule for each 
#   possible expansion of that non-terminal to the current timestep bin 
def predictor(grammar, chart, index, rule):
    print "in predictor: "
    branch_rules = grammar[0]
    pos_rules = grammar[1]
      
    dot = rule[1].index('.')
    
    # if the dot is already at the end of beta, there are no possible expansions for 
    #   predictor to process
    if dot == (len(rule[1]) - 1):
        return chart
    
    # the beta argument to the right of the dot
    beta_current = rule[1][dot + 1]   
    print rule
    print "looking at: ", beta_current
    
    # finds expansions in multi-argument betas
    if beta_current in branch_rules.keys():
        print '      its in branch rules!'
        for beta_next in branch_rules[beta_current]:
        
            # add dot marking progress to rule if necessary
            if beta_next[0] is not '.':
                beta_next.insert(0, '.')
            
            chart[index] = add_rule([beta_current, beta_next, index, index, []], chart[index])
    
    # finds expansions in unit productions
    if beta_current in pos_rules.keys():
        print '      its in pos rules!'
        for beta_next in pos_rules[beta_current]:
            chart[index] = add_rule([beta_current, ['.', beta_next], index, index, []], chart[index])

    print "predictor completed."
    print 'index', index, chart[index]
    print
    return chart

### implements the scanner of the Earley algorithm
# if there is a POS tag to the right of the dot, check if that POS can generate the next
#   word in the input sentence
#   if so, move dot in the rule, and add the rule to the next chart bin
def scanner(grammar, chart, index, rule, sentence):
    print "in scanner: "
    branch_rules = grammar[0]
    pos_rules = grammar[1]
    terminals = grammar[2]
        
    dot = rule[1].index('.')
    
    # if the dot is already at the end of beta, there are no possible expansions for 
    #   predictor to process
    if dot == (len(rule[1]) - 1):
        return chart
    
    # the beta argument to the right of the dot
    beta_current = rule[1][dot + 1]
    print "looking at: ", beta_current
    
    # finds associated terminals
    # if the next word in the input sentence can be produced by that beta argument
    #   add that rule to the next chart bin
    if beta_current in terminals.keys():
        if index < len(sentence):
            print '      its in terminals!'  
            print "      looking at the next word: ", sentence[index]
            if sentence[index] in terminals[beta_current]:
                print "      ...matching... "
                # begin to form the partial parse tree
                chart[index + 1] = add_rule([beta_current, [sentence[index], '.'], index, (index + 1), ['(' + beta_current + ' ' + sentence[index] +')']], chart[index + 1])
            
    print "scanner completed."
    print 'index', index, chart[index]
    if len(chart.keys()) != index + 1:
        print 'index', index + 1, chart[index + 1]
    print
    return chart

### implements the completer of the Earley algorithm
# if a rule has been completed, examine all previous rules at the index where the rule was started
#   if a previous rule is still possible given the completion of the current rule
#       generate a new state with that rule in the current index
def completer(chart, index, rule):
    print "in completer: "
    
    dot = rule[1].index('.')
    rule_start = rule[2]
    
    if dot == (len(rule[1]) - 1):
        print '     end of rule'
        completed = rule[0]
        
        print "looking for: ", completed
        
        # iterates over all rules in chart bin corresponding to the starting index of the
        #   completed rule
        for rule_prev in chart[rule_start]:
            
            rule_index = chart[rule_start].index(rule_prev)
            print '     rule: ', rule_prev, rule_index
            beta_prev = rule_prev[1]
            dot_prev = beta_prev.index('.')
            if len(beta_prev) is not (dot_prev + 1):
                print '     item: ', beta_prev[dot_prev + 1]
                if beta_prev[dot_prev + 1] == completed:
                    print '       moving ', rule_prev
                    completed_index = beta_prev.index(completed)
                    rule_prev_start = rule_prev[2]
                    alpha = rule_prev[0]
                    backtrace = rule[4][0]
                    print backtrace
                    
                    # add appropriate tags/parentheses to existing partial parse
                    # relies on assumption of CNF grammar 
                    # if rule is unary 
                    if len(beta_prev) == 2:
                        new_backtrace = ['(' + alpha + ' ' + backtrace + ')']
                        print 'len = 2'
                    # if first argument of a double-argument beta has been completed
                    elif dot_prev == 0:
                        new_backtrace = ['(' + alpha + ' ' + backtrace]
                        print 'dot at 0'
                    # otherwise, given CNF grammar, the second argument must have been completed
                    else:
                        new_backtrace = [rule_prev[4][0] + ' ' + backtrace + ')']
                        print 'dot at 3'
                    print new_backtrace
                    
                    # add rule with [alpha, [rule with dot moved], old start index, current index, [new backtrace]]
                    processed = beta_prev[0:dot_prev]
                    processed.append(completed)
                    processed.append('.')
                    beta = processed + beta_prev[completed_index + 1:]
                    rule_progress = [alpha, beta, rule_prev_start, index, new_backtrace]
                    print '     ', rule_progress
                    chart[index] = add_rule(rule_progress, chart[index])
    
    print "completer completed."
    print 'index', index, chart[index]
    if len(chart.keys()) != index + 1:
        print 'index', index + 1, chart[index + 1]
    print
    return chart
    
if __name__ == '__main__':
	main()