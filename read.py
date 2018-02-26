# -*- coding: utf-8 -*-
# @Author: Kristian Hammond
# @Date: 2017-10-19
# @Last Modified by:   Sam Hill
# @Last Modified time: 2017-11-01 21:49:01
# Modified comment structure, and some minor edits to most functions

# labels for input (essentially an enum)
FACT = 0
RULE = 1
COMMENT = 2
BLANK = 3

# read_tokenize takes the name of a file, reads it in and tokenizes the
# statements and rules in that file.
def read_tokenize(file):
    """Reads in a file and processes contents into lists of facts and rules.

    Args:
        file (file): A txt file with facts of the form (predicate subject
        object) such as "fact: (isa cube block)". As well, there are rules with
        a right and left hand side that are essentially (fact1 and fact2) ->
        (fact3) such as "rule: ((inst ?x ?y) (isa ?y ?z)) -> (inst ?x ?z)".
        These facts and rules each go on a new line in the file and are looped
        over to build the two seperate lists of facts and rules.

    Returns:
        Tuple: tokenized_facts, tokenized_rules. Lists of facts and rules.
    """
    tokenized_facts = []
    tokenized_rules = []
    file = open(file, "r")
    elements = []
    current = ""
    for line in file:
        if line[0:5] in ("fact:", "rule:"):
            elements.append(current)
            current = line.rstrip()
        else:
            current = current + " " + line.rstrip()
    elements.append(current)
    output = []
    for e in elements:
        parsed = parse_input(e)
        output.append(parsed)
        # if parsed[0] == FACT:
        #     tokenized_facts.append(parsed[1])
        # elif parsed[0] == RULE:
        #     tokenized_rules.append((parsed[1][0], parsed[1][1]))
    file.close()
    # return tokenized_facts, tokenized_rules
    return output


def read_from_input(message):
    """Collects user input from the command line.

    Args:
        message (string): Message to present to user specifying input.

    Returns:
        str: input from user
    """
    return raw_input(message + " ")


def parse_input(e):
    """Parses input, assigning labels and splitting rules into LHS & RHS

    Args:
        e (string): Input string to parse

    Returns:
        (number, string | listof string): label, then parsed input
    """
    if len(e) == 0:
        return (BLANK, None)
    elif e[0] == '#':
        return (COMMENT, e)
    elif e[0:5] == "fact:":
        e = e[5:].replace(")", "").replace("(", "").rstrip().strip().split()
        return (FACT, e)
    elif e[0:5] == "rule:":
        e = e[5:].split("->")
        rhs = e[1].replace(")", "").replace("(", "").rstrip().strip().split()
        lhs = e[0].rstrip(") ").strip("( ").replace("(", "").split(")")
        lhs = map(lambda x: x.rstrip().strip().split(), lhs)
        return (RULE, [lhs, rhs])
    else:
        print "PARSE ERROR: input header", e[0:5], "not recognized."

def get_new_fact_or_rule():
    """Creates a new fact or rule. (instead of args, we use command line input
    via the read_from_input() function)

    Returns:
        list: fact list or list of the left and right hand sides of a rule
    """
    msg = "Please type in a new fact or rule you want to add to the KB:\n"
    e = read_from_input(msg)
    return parse_input(e)

def get_new_statements():
    """Gets statements from user via the command line.  Statments are expected
     in the form predicate followed by terms with spaces between (e.g. "isa
     cube block").  Changed from -
        map(lambda x: filter(str.isalnum, x), e.split(" "))
    because I wanted to allow for statements to have non-alphanumeric
    characters, namely "?".  This way, the method can be used any time that the
    user is creating a statement, not just when the statement is all constants.

    Returns:
        list: statement filtered for strings of the form `pred x1 x2 ... :`
    """
    e = read_from_input("Please type in a statement of the form " +
            "\"pred x1 x2 ...\":\n")
    return e.split()