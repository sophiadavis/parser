"""
parser.py  
Sophia Davis,  for 11/15/13

to do:
    fix crash if empty line
    no clones
    completer
    should I be storing beta's as a list?
"""
import sys

def main():
    if len(sys.argv) < 3:
        sys.stderr.write('Usage: python ' + sys.argv[0] + ' grammar_file.txt' + ' "sentence to parse" \n')
        sys.exit(1)
    
    sentence = sys.argv[2].split(' ')    
    f = open(sys.argv[1])
    
    branch_rules = {}
    pos_rules = {}
    terminals = {}
    
    for line in f:
        print line
        if line.strip('\n'):
    #         if line:
    #         print line
            if line[0] == '#':
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

def earley(grammar, sentence):
    
    n_bins = len(sentence) + 1
    chart = {}
    for i in range(0, n_bins):
        chart[i] = []
    
    branch_rules = grammar[0]
    pos_rules = grammar[1]
    terminals = grammar[2]
    
    chart[0] = [['gamma', ['.', 'S'], 0, 0]]
    
    for i in range(0, n_bins):
#     for i in range(0, 1):
        
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
    
def add_rule(rule, chart_bin):
    if rule not in chart_bin:
        print 'adding rule: ', rule
        chart_bin.append(rule)
    return chart_bin

def predictor(grammar, chart, index, rule):
    print "in predictor: "
    branch_rules = grammar[0]
    pos_rules = grammar[1]
    
#     if isinstance(rule[2], int ):
#         return chart
        
    dot = rule[1].index('.')
    if dot == (len(rule[1]) - 1):
        return chart
        
    beta_current = rule[1][dot + 1]   
    print rule
    print "looking at: ", beta_current
    
    if beta_current in branch_rules.keys():
        print '      its in branch rules!'
        for beta_next in branch_rules[beta_current]:
            if beta_next[0] is not '.':
                beta_next.insert(0, '.')
            chart[index] = add_rule([beta_current, beta_next, index, index], chart[index])
            # this is already a list so leave the brackets off beta!

    if beta_current in pos_rules.keys():
        print '      its in pos rules!'
        for beta_next in pos_rules[beta_current]:
            chart[index] = add_rule([beta_current, ['.', beta_next], index, index], chart[index])

    print "predictor completed."
    print 'index', index, chart[index]
    print
    return chart
    
def scanner(grammar, chart, index, rule, sentence):
    print "in scanner: "
    branch_rules = grammar[0]
    pos_rules = grammar[1]
    terminals = grammar[2]
    
#     if isinstance(rule[dot + 1], int ):
#         return chart
        
    dot = rule[1].index('.')
    if dot == (len(rule[1]) - 1):
        return chart
        
    beta_current = rule[1][dot + 1]
    print "looking at: ", beta_current
    
#     if rule[dot + 1][0] in pos_rules.keys():
    if beta_current in terminals.keys():
        print '      its in terminals!'
#         print '      its in pos rules!'
#         for beta in pos_rules[rule[dot + 1][0]]:# + terminals.keys():
#         for beta in terminals[rule[dot + 1][0]]:    
        print "looking at the next word: ", sentence[index]
        if sentence[index] in terminals[beta_current]:
            print " ...matching... "
            chart[index + 1] = add_rule([beta_current, [sentence[index], '.'], index, (index + 1)], chart[index + 1])

#     if rule[dot + 1][0] in terminals.keys():
#         print '      its in terminals!'
#         print "looking at the next word: ", sentence[index]
#         if sentence[index] in terminals[rule[dot + 1][0]]:
#             print " ...matching... "
# #             chart[index + 1].append([rule[dot + 1][0], [sentence[index]], '.', index, (index + 1)])
#             chart[index + 1] = add_rule([rule[dot + 1][0], [sentence[index]], '.', index, (index + 1)], chart[index + 1])
    print "scanner completed."
    print 'index', index, chart[index]
    if len(chart.keys()) != index + 1:
        print 'index', index + 1, chart[index + 1]
    return chart

def completer(chart, index, rule):
    print "in completer: "
    
    dot = rule[1].index('.')
    rule_start = rule[2]
#     print rule
    
    if dot == (len(rule[1]) - 1):
        print 'end of rule'
        completed = rule[0]
        
        print "looking for: ", completed

        for rule_prev in chart[rule_start]:
            print 'rule: ', rule_prev
            beta_prev = rule_prev[1]
            dot_prev = beta_prev.index('.')
            print len(beta_prev), dot_prev
            if len(beta_prev) is not (dot_prev + 1):
                print '  item: ', beta_prev[dot_prev + 1]
                if beta_prev[dot_prev + 1] == completed:
                    print '     moving ', rule_prev
                    completed_index = beta_prev.index(completed)
                    rule_prev_start = rule_prev[2]
                    alpha = rule_prev[0]
                    print '     dot at ', dot_prev, '__  completed at ', completed_index, '__ rule start', rule_prev_start
                    # add rule with [alpha, [rule with dot moved], old start, current]
                    processed = beta_prev[0:dot_prev]
                    processed.append(completed)
                    processed.append('.')
                    beta = processed + beta_prev[completed_index + 1:]
                    rule_progress = [alpha, beta, rule_prev_start, index]
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