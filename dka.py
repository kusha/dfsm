#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#DKA:xbirge00

"""
IPP: Finite State Machine determinization
Mark Birger (xbirge00) 5.4.2014-22.4.2014
Finite State Machine processing module
use-case:
    Automata(data)
    automata.remove_empty
    automata.determinize
    print(automata)
"""

__author__ = "Mark Birger"
__email__ = "xbirge00@stud.fit.vutbr.cz"
__license__ = "MIT"
__status__ = "Development" 

import sys
import re

IDENTIF = re.compile("^[A-Za-z0-9]([A-Za-z0-9_]*[A-Za-z0-9])?$")

class Aumomata(object):
    """
    Final State Machine object
    represent structured description of FSM
    provide set of FSM operations
    """

    def __init__(self, desc):
        """
        Class constructor. Parameter desc is string with
        FSM description in special format.
        """
        self.Q = None
        self.E = None
        self.R = None
        self.s = None
        self.F = None
        self.desc = desc
        self.__parse_desc()

    def __parse_desc(self):
        """
        Parse description module. Used for modularity.
        Called by __init__ method.
        """
        self.desc = re.sub(r"#([^\'].*)?(\r|\n|$)", "", self.desc)
        self.desc = re.sub(r"([^\'])[\r|\n| |\t]*", r"\1", self.desc)
        self.desc = re.sub(r"[\r|\n| |\t]*([^\'])", r"\1", self.desc)
        self.desc = re.sub(r"([^\'])[\r|\n| |\t]*([^\'])", r"\1\2", self.desc)
        self.desc = re.sub(r"(^[\r\n \t])|([\r\n \t]$)", "", self.desc)
        if not self.desc.startswith('({') and self.desc.endswith('})'):
            halt(40, "ERR: can't parse braces of fsm")
        self.desc = self.desc[2:-2]
        self.desc = re.sub(r'},([^{}]*),{', r'},{\1},{', self.desc)
        parts = re.split("},{", self.desc)
        if not len(parts) == 5:
            halt(40, "ERR: can't parse subsets of fsm")
        self.__parse_states(parts[0])
        self.__parse_alphabet(parts[1])
        self.__parse_rules(parts[2])
        self.__parse_initial(parts[3])
        self.__parse_final(parts[4])
        self.__check_semantic()

    def __parse_states(self, states):
        """
        Method spilts and parse set of states from provided string.
        """
        if not states:
            halt(40, "ERR: empty states set")
        states = states.split(",")
        if not all(IDENTIF.match(state) for state in states):
            halt(40, "ERR: wrong state name")
        self.Q = set(states)

    @staticmethod
    def __prepare_symbol(symbol, fully=True):
        """
        Helper static methos, used to parse special symbols.
        Parameter fully define, is symbol wrapped in \'\'.
        """
        caller = "alphabet definition" if fully else "rules definition"
        if fully:
            if not symbol[0] == '\'' and symbol[-1] == '\'':
                halt(40, "ERR: wrong alphabet char %s @ %s" % (symbol, caller))
            symbol = symbol[1:-1]
        if symbol == '\'\'':
            symbol = '\''
        if len(symbol) > 1:
            halt(40, "ERR: wrong len alphabet char %s @ %s" % (symbol, caller))
        return symbol

    def __parse_alphabet(self, alphabet):
        """
        Method spilts and parse set of symbols from provided string.
        Uses heleper __prepare_symbol static method.
        """
        alphabet = alphabet.split(",")
        self.E = set([self.__prepare_symbol(symbol) for symbol in alphabet])

    def __parse_rules(self, rules):
        """
        Method splits and parse rules from stirng.
        Uses global regular expression IDENTIF.
        """
        self.R = list() #list(tuple(tuple(string, string), string), ...)
        if rules == "": return
        rules = rules.split(",")
        for rule in rules:
            rule = rule.split("'->", 1)
            if not len(rule) == 2:
                halt(40, "ERR: rule -> troubles")
            if not IDENTIF.match(rule[1]):
                halt(40, "ERR: right side of a rule, non-valid identificator")
            rule[0] = rule[0].split("'", 1)
            if not len(rule[0]) == 2:
                halt(40, "ERR: rule comma before -> troubles")
            if not IDENTIF.match(rule[0][0]):
                halt(40, "ERR: left side of a rule, non-valid identificator")
            rule[0][1] = self.__prepare_symbol(rule[0][1], False)
            self.R.append(((rule[0][0], rule[0][1]), rule[1]))
        self.R = list(set(self.R))


    def __parse_initial(self, state):
        """
        Method parse initial state. It's only needed to check with regex.
        """
        if not IDENTIF.match(state):
            halt(40, "ERR: initial state non-valid identificator")
        self.s = state

    def __parse_final(self, states):
        """
        Method parse final states set. Similat as a first states Method,
        except final states set can be empty.
        """
        self.F = set()
        if states == "": return
        states = states.split(",")
        if not all(IDENTIF.match(state) for state in states):
            halt(40, "ERR: wrong state name in final set")
        self.F = set(states)

    def __check_semantic(self):
        """
        Checks semantic of parsed final states machine. Check following rules:
            - empty alphabet
            - rules with wrong symbol/states
            - wrong inital state
            - final states set not inside states set
        """
        if not self.E:
            halt(41, "ERR: empty automata alphabet")
        for r in self.R:
            if r[0][0] not in self.Q:
                halt(41, "ERR: rule origin %s not in states set" % r[0][0])
            if r[0][1] not in self.E | set([""]):
                halt(41, "ERR: rule symbol %s not in alphabet set" % r[0][1])
            if r[1] not in self.Q:
                halt(41, "ERR: rule target %s not in states set" % r[1])
        if self.s not in self.Q:
            halt(41, "ERR: initial state %s not in states set"  % self.s)
        if not self.F.issubset(self.Q):
            halt(41, "ERR: final states set isn't subset of states")

    def __str__(self):
    
        states = sorted(list(self.Q))
        alphabet = sorted(list(self.E))
        rules = sorted(self.R, key=lambda x: (x[0][0], x[0][1], x[1]))
        #initial skipped
        final = sorted(list(self.F))

        output = "(\n"

        output += "{"
        if states:
            for state in states[:-1]:
                output += "%s, " % state
            output += "%s},\n" % states[-1]
        else:
            output += "},\n"

        output += "{"
        if alphabet:
            for symbol in alphabet[:-1]:
                symbol = symbol if symbol != '\'' else '\'\''
                output += "\'%s\', " % symbol
            output += "\'%s\'},\n" % alphabet[-1]
        else:
            output += "},\n"

        output += "{\n"
        if rules:
            for rule in rules[:-1]:
                symbol = rule[0][1] if rule[0][1] != '\'' else '\'\''
                output += "%s \'%s\' -> %s,\n" % (rule[0][0], symbol, rule[1])
            rule = rules[-1]
            symbol = rule[0][1] if rule[0][1] != '\'' else '\'\''
            output += "%s \'%s\' -> %s\n},\n" % (rule[0][0], symbol, rule[1])
        else:
            output += "},\n"

        output += "%s,\n" % self.s
        
        output += "{"
        if final:
            for state in final[:-1]:
                output += "%s, " % state
            output += "%s}\n" % final[-1]
        else:
            output += "}\n"

        output += ")"

        return output

    def __empty_closure(self, p):
        """
        Method provide set of states, which are in empty closure of this state.
        Warning, this set includes provided state.
        """
        if p not in self.Q:
            halt(40, "ERR: empty closure, rule not in states set")
        Q = list()
        Q.append(set([p]))
        while True:
            p1 = set()
            for rule in self.R:
                if (rule[0][0] in Q[-1]) and (rule[0][1] == ''):
                    p1.add(rule[1])
            Q.append(Q[-1]|p1)
            if Q[-1] == Q[-2]:
                return Q[-1]

    def remove_empty(self):
        """
        Method removes rules with empty symbols. Uses empty_closure method.
        Called outside of the class.
        """
        R1 = list()
        for p in self.Q:
            closure = self.__empty_closure(p)
            for r in self.R:
                if r[0][0] in closure and r[0][1] in self.E:
                    new = ((p,r[0][1]),r[1])
                    R1.append(new)
        R1 = list(set(R1))
        F1 = set()
        for p in self.Q:
            if self.__empty_closure(p) & self.F:
                F1.add(p)
        self.R = R1
        self.F = F1

    @staticmethod
    def __new_state(states_set):
        """
        Create new state name.
        Independent of provided varable state (set, frozenset, tuple, list).
        """
        states_set = list(states_set)
        states_set = sorted(states_set)
        name = "_".join(states_set)
        return name

    def determinize(self):
        """
        Determinization method
        Uses algorithm from IFJ presentation. Uses sets(frozensets(states,..)).
        """
        sd = frozenset([self.s])
        Qn = set([sd])
        Rd = list(); Qd = set(); Fd = set()
        while True:
            Q1 = None #Q1 can be empty, it's safe; statement only for pylint
            for Q1 in Qn: break #get element from set
            Qn.discard(Q1)
            Qd.add(self.__new_state(Q1)) 
            for a in self.E:
                Q2 = set()
                for r in self.R:
                    if r[0][0] in Q1 and r[0][1] == a: Q2.add(r[1])
                if Q2: 
                    nQ1 = self.__new_state(Q1)
                    nQ2 = self.__new_state(Q2)
                    Rd.append(((nQ1,a),nQ2))
                Q2 = frozenset(Q2)
                if (not self.__new_state(Q2) in Qd) and bool(Q2): Qn.add(Q2)
            if set(Q1) & self.F: Fd.add(self.__new_state(Q1))
            if not Qn: break
        self.Q = Qd
        self.R = Rd
        self.F = Fd

    def analyze(self, string, state=None):
        """
        Final state machine string processing method.
        Warning, it's recursive.
        """
        if state == None:
            state = self.s
        if string:
            symbol = string[0]
            string = string[1:]
            if not symbol in self.E:
                halt(1, "ERR: string contains not-acceptable symbol")
            for rule in self.R:
                if rule[0][0] == state and rule[0][1] == symbol:
                    return self.analyze(string, state=rule[1])
        else:
            if state in self.F:
                return 1
            else:
                return 0


def halt(code, message=None):
    """
    Halt function, prints error messages, close process.
    """
    if message:
        print(message, file=sys.stderr) # 
    sys.exit(code)

def main():
    #Parse input arguments
    source = output = None
    no_epsilon_rules = determinization = case_insensitive = False
    analyze = None
    for attr in sys.argv[1:]:
        if attr == "--help":
            if len(sys.argv[1:]) == 1:
                print(
                    "Finite State Machine processing module."
                    "\nTask DKA from IPP 2013/2014."
                    "\nAuthor: Mark Birger (xbirge00) 22.04.2014"
                    "\n"
                    "\nThis script provides can operate with FSM."
                    "\nProvide operations like removing e-states, "
                    "\ndeterminization of string processing."
                    "\n"
                    "\nUsage:"
                    "\n\t--help"
                    "\n\t\tprints help, script terminates"
                    "\n\t--input=filename"
                    "\n\t\tspecify input file, default is stdin"
                    "\n\t--output=filename"
                    "\n\t\tspecify output file, default is stdout"
                    "\n\t-e or --no-epsilon-rules"
                    "\n\t\tscript will remove all epsilon rules"
                    "\n\t-d or --determinization"
                    "\n\t\tscript will determinize provided FSM"
                    "\n\t\tremoving of empty rules included"
                    "\n\t-i or --case-insensitive"
                    "\n\t\tscript will be case insensitive"
                    "\n\t\teven for string processing"
                    "\n\t--analyze-string=\"string\""
                    "\n\t\tscript will check is string acceptable"
                    "\n\t\tfor provided FSM, if yes output is 1, else 0"
                    "\n"
                    "\nScript can be used like an external module:"
                    "\n\tautomata = Automata(data)"
                    "\n\tautomata.remove_empty"
                    "\n\tautomata.determinize"
                    "\n\tprint(automata)"
                )
                halt(0)
            else:
                halt(1, "ERR: --help argument should be alone")
        elif attr.startswith("--input="):
            if source == None:
                source = attr[len("--input="):]
                if source == "":
                    halt(1, "ERR: --input argument with empty filename")
            else:
                halt(1, "ERR: --input argument used twice")
        elif attr.startswith("--output="):
            if output == None:
                output = attr[len("--output="):]
                if output == "":
                    halt(1, "ERR: --output argument with empty filename")
            else:
                halt(1, "ERR: --output argument used twice")
        elif attr in ["-e", "--no-epsilon-rules"]:
            if no_epsilon_rules == False:
                if determinization == False and analyze == None:
                    no_epsilon_rules = True
                else:
                    halt(1, "ERR: -e used with -d or --analyze argument")
            else:
                halt(1, "ERR: --no-epsilon-rules used twice")
        elif attr in ["-d", "--determinization"]:
            if determinization == False:
                if no_epsilon_rules == False and analyze == None:
                    determinization = True
                else:
                    halt(1, "ERR: -d used with -e or --analyze argument")
            else:
                halt(1, "ERR: --determinization used twice")
        elif attr in ["-i", "--insensitive"]:
            if case_insensitive == False:
                case_insensitive = True
            else:
                halt(1, "ERR: --insensitive used twice")
        elif attr.startswith("--analyze-string="):
            if analyze == None:
                if determinization == False and no_epsilon_rules == False:
                    analyze = attr[len("--analyze-string="):]
                    # print(analyze)
                    # if analyze.startswith('"') and analyze.endswith('"'):
                    #     analyze = analyze[1:-1]
                    # else:
                    #     halt(1, "ERR: --analyze string not in \"\"")
                else:
                    halt(1, "ERR: --analyze used with -d or -e argument")
            else:
                halt(1, "ERR: --analyze-string used twice")
        else:
            halt(1, "ERR: unrecognized argument")

    #Input file section
    if source:
        try:
            with open(source, "r") as src:
                data = src.read()
        except EnvironmentError: #IOError OSError parent
            halt(2, "ERR: can't open input file")
    else:
        data = sys.stdin.read()

    #Check case sensitivity
    if case_insensitive:
        data = data.lower()
        if analyze:
            analyze = analyze.lower()
    
    #Create finite state machine
    fsm = Aumomata(data)

    #Process task
    if no_epsilon_rules:
        fsm.remove_empty()
        result = str(fsm)
    elif determinization:
        fsm.remove_empty()
        fsm.determinize()
        result = str(fsm)
    elif analyze:
        fsm.remove_empty()
        fsm.determinize()
        result = str(fsm.analyze(analyze))
    else:
        result = str(fsm)

    #Output file section
    if output:
        try:
            with open(output, "w") as out:
                print(result, file=out, end="") #pass#TODO 
        except EnvironmentError: #IOError OSError parent
            halt(3, "ERR: can't open input file")
    else:
        print(fsm)

if __name__ == '__main__':
    main()
