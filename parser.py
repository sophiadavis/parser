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
        elif beta.isupper(	):
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
    print branch_rules
    print pos_rules
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
    
    chart[0] = [['gamma', '.', ['S'], 0, 0]]
    
#     for i in range(0, n_bins):
    for i in range(0, n_bins):
        
        print
        print
        print "bin number ", i

        for rule in chart[i]:
            print
            print '******'
            print "processing rule: ", rule 
            print
            chart = predictor(grammar, chart, i, rule)
            chart = scanner(grammar, chart, i, rule, sentence)
            chart = completer(chart, i, rule)


def predictor(grammar, chart, index, rule):
    print "in predictor: "
    branch_rules = grammar[0]
    pos_rules = grammar[1]
    
    dot = rule.index('.')
    if isinstance(rule[dot + 1], int ):
        print 'int'
        return chart
        
    print rule
    print "looking at: ", rule[dot + 1][0]
    
    if rule[dot + 1][0] in branch_rules.keys():
        print '      its in branch rules!'
        for beta in branch_rules[rule[dot + 1][0]]:
            print 'appending ', beta
            chart[index].append([rule[dot + 1][0], '.', beta, index, index])
    if rule[dot + 1][0] in pos_rules.keys():
        print '      its in pos rules!'
        for beta in pos_rules[rule[dot + 1][0]]:
            print 'appending ', [beta]
            print 'rule', rule[dot + 1][0]
            print 'index', index
            print [rule[dot + 1][0], '.', [beta], index, index]
            print chart[index]
            chart[index].append([rule[dot + 1][0], '.', [beta], index, index])
    print "predictor completed: "
    print chart[index]
    print
    return chart
    
def scanner(grammar, chart, index, rule, sentence):
    print "in scanner: "
    branch_rules = grammar[0]
    pos_rules = grammar[1]
    terminals = grammar[2]
    
    dot = rule.index('.')
    if isinstance(rule[dot + 1], int ):
        return chart
        
    print rule
    print "looking at: ", rule[dot + 1][0]
    
    if rule[dot + 1][0] in pos_rules.keys():
        print '      its in pos rules!'
        for beta in pos_rules[rule[dot + 1][0]]:# + terminals.keys():
            print "looking at: ", beta
            if beta in terminals.keys():
                print '      its in terminals!'
                print "looking at the next word: ", sentence[index]
                if sentence[index] in terminals[beta]:
                    print " ...matching... "
                    chart[index + 1].append([beta, [sentence[index]], '.', index, (index + 1)])
    if rule[dot + 1][0] in terminals.keys():
        print '      its in terminals!'
        print "looking at the next word: ", sentence[index]
        if sentence[index] in terminals[rule[dot + 1][0]]:
            print " ...matching... "
            chart[index + 1].append([rule[dot + 1][0], [sentence[index]], '.', index, (index + 1)])
        
    print "scanner completed: "
    print chart[index]
    print chart[index + 1]
    print
    return chart

def completer(chart, index, rule):
    print "in completer: "
    
    dot = rule.index('.')
    print rule
    
    if isinstance(rule[dot + 1], int ):
        print 'end of rule'
        completed = rule[0]
        print "looking for: ", completed
        for i in range(0, index):
            for rule in chart[i]:
                if [completed] in rule:
                    at = rule.index([completed])
                    if rule[at - 1] == '.':
                        start = rule[3]
                        chart[index].append(rule[0], )         
    return chart
    
if __name__ == '__main__':
	main()