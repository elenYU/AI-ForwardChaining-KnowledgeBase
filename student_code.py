import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB

        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added

        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)

        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)

            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)


    def kb_assert(self, statement):
        """Assert a fact or rule into the KB

        Args:
            statement (Statement): Statement we're asserting in the format produced by read.py
        """
        printv("Asserting {!r}", 0, verbose, [statement])
        self.kb_add(Fact(statement) if factq(statement) else Rule(statement))

    def kb_ask(self, statement):
        """Ask if a fact is in the KB

        Args:
            statement (Statement) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        printv("Asking {!r}", 0, verbose, [statement])
        if factq(statement):
            f = Fact(statement)
            bindings_lst = ListOfBindings() # now kong
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])
                    # print bindings_lst.list_of_bindings
            return bindings_lst if bindings_lst.list_of_bindings else False

        else:
            print "Invalid ask:", statement
            return False

    def kb_retract(self, statement):
        """Retract a fact from the KB

        Args:
            statement (Statement) - Statement to be asked (will be converted into a Fact)

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [statement])
        ####################################################
        if isinstance(statement,Fact):
            old_fact = statement
            if old_fact in self.facts:
                index = self.facts.index(old_fact)
                dfact = self.facts[index]

            for new_fact in dfact.supports_facts:
                for i, pair in enumerate(new_fact.supported_by):
                    if pair[1].statement == dfact.statement:
                        new_fact.supported_by.pop(i)
                    if len(new_fact.supported_by) == 0 :
                        self.kb_retract(new_fact)
            for new_rule in dfact.supports_rules:
                for i, pair in enumerate(new_rule.supported_by):
                    if pair[1].statement == dfact.statement:
                        new_rule.supported_by.pop(i)
                    if len(new_rule.supported_by) == 0:
                        self.kb_retract(new_rule)
            self.facts.remove(dfact)

        elif isinstance(statement, Rule):
            if statement in self.rules:
                index = self.rules.index(statement)
                drule = self.rules[index]


            for new_fact in drule.supports_facts:
                for i, pair in enumerate(new_fact.supported_by):
                    # print new_fact
                    if drule in pair:
                        new_fact.supported_by.pop(i)
                    if len(new_fact.supported_by) == 0:
                        self.kb_retract(new_fact)

            for new_rule in drule.supports_rules:
                for i, pair in enumerate(new_rule.supported_by):
                    if drule in pair:
                        new_rule.supported_by.pop(i)
                    if len(new_rule.supported_by) == 0:
                        self.kb_retract(new_rule)
            self.rules.remove(drule)

        elif factq(statement):
            old_fact = Fact(statement)
            if old_fact in self.facts:
                index = self.facts.index(old_fact)
                dfact = self.facts[index]


            for new_fact in dfact.supports_facts:
                for i, pair in enumerate(new_fact.supported_by):
                    if pair[1].statement == dfact.statement:
                        new_fact.supported_by.pop(i)
                    if len(new_fact.supported_by) == 0:
                        self.kb_retract(new_fact)

            for new_rule in dfact.supports_rules:
                for i, pair in enumerate(new_rule.supported_by):
                    if pair[1].statement == dfact.statement:
                        new_rule.supported_by.pop(i)
                    if len(new_rule.supported_by) == 0:
                        self.kb_retract(new_rule)

            self.facts.remove(dfact)
class InferenceEngine(object):

    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        bindings = match(rule.lhs[0], fact.statement)
        pair = [[]] * 2
        pair[0] = rule
        pair[1] = fact

        if bindings:
            if len(rule.lhs) == 1:
                new_fact = copy.deepcopy(Fact(instantiate(rule.rhs, bindings)))
                # new_fact = Fact(instantiate(rule.rhs, bindings))
                new_fact.supported_by.append(pair)

                i = kb.facts.index(fact)
                kb.facts[i].supports_facts.append(new_fact)
                j = kb.rules.index(rule)
                kb.rules[j].supports_facts.append(new_fact)

                kb.kb_add(new_fact)
            else:
                lhs = map(lambda x: instantiate(x, bindings), rule.lhs[1:])
                rhs = instantiate(rule.rhs, bindings)
                #new_rule = copy.deepcopy(rule)
                new_rule=Rule([lhs,rhs],[[rule,fact]])

                i = kb.facts.index(fact)
                kb.facts[i].supports_rules.append(new_rule)
                j = kb.rules.index(rule)
                kb.rules[j].supports_rules.append(new_rule)

                kb.kb_add(new_rule)