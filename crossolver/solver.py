import random
from collections import defaultdict

import time

SPACE = 'O'
BLOCK = 'X'


class Constraint:
    """
    Constraint holds information on a binary constraint containing 2 variables and the positions they share.  This
    constraint is represented with 2 tuples in the format (Variable, index), (Variable, index)
    """
    a = (None, 0)
    d = (None, 0)

    def __init__(self, a_tuple, d_tuple):
        self.a = a_tuple
        self.d = d_tuple

    def __eq__(self, other):
        if not isinstance(self, other.__class__):
            return False
        if self.a == other.a and self.d == other.d:
            return True

    def __str__(self):
        return str(self.a[0].num) + self.a[0].ad + '-' + str(self.a[1]) + ' and ' + str(self.d[0].num) + self.d[
            0].ad + '-' + str(self.d[1])

    def satisfied(self):
        """
        Returns True if satisfied, False if not satisfied
        :return: True if satisfied, False if not satisfied
        """
        return self.a[0].value[self.a[1]] == self.d[0].value[self.d[1]]

    def contains(self, var, pos=None):
        """
        Evaluates whether the constraint contains a particular variable
        :param var: Variable to check
        :return: True if var is present, False if it is not
        """
        if pos == None:
            return self.a[0] == var or self.d[0] == var
        elif pos == 'A':
            return self.a[0] == var
        elif pos == 'D':
            return self.d[0] == var

    def flip(self):
        """
        Returns a copy of the Constraint with a and d flipped (for 1-way evaluations)
        :return: Constraint with opposite a and d tuples
        """
        return Constraint(self.d, self.a)


class Variable:
    """
    Variable class holds the information related to each word entry in the puzzle.
    num = Number on the puzzle
    ad = Across or Down
    length = length of
    """

    def __init__(self, num, ad, length, y, x):
        self.num = num
        self.ad = ad
        self.length = length
        self.spaces = []
        if ad == 'A':
            for occupied in range(length):
                self.spaces.append((y, x))
                x += 1
        if ad == 'D':
            for occupied in range(length):
                self.spaces.append((y, x))
                y += 1
        self.domain = []
        self.value = " " * length

    def set_domain(self, dictionary):
        """
        Sets the domain of the variable given a dictionary of possibilities
        :param dictionary:
        :return:
        """
        self.domain = [possible for possible in dictionary if len(possible) == self.length]

    def set_val(self, constraints=None):
        """
        Sets the value to a random value in the domain set
        :return:
        """
        if constraints == None:
            self.value = random.choice(self.domain)
        else:
            possibles = self.domain
            for constraint in constraints:
                possibles = [poss for poss in possibles if constraint.d[0].value[constraint.d[1]] == poss[
                    constraint.a[1]]]  # TODO: Refactor this
            self.value = random.choice(possibles)

    def reset_val(self):
        """
        Removes the current value from the domain and sets a different value
        :return:
        """
        self.set_val()

    def rem_val(self, val):
        """
        Removes a given value from the domain
        :param val:
        :return:
        """
        self.domain.remove(val)

    def __str__(self):
        return str(self.num) + '' + self.ad + ': \t' + str(self.length)  + '  \t Possibles: ' + str(len(self.domain))

    def __eq__(self, other):
        if not isinstance(self, other.__class__):
            return False
        if (self.num == other.num) and (self.ad == other.ad) and (self.length == other.length):
            return True


class Solver:
    """
    Puzzle class serves has the placeholder for all puzzle related data
    """
    puzzle = None
    variables = []

    def __init__(self, puzzle_path='../datafiles/test'):
        with open(puzzle_path, 'r') as puzzle_file:  # Add border around puzzle
            self.puzzle = [list(line.strip()) for line in puzzle_file]
            size = len(self.puzzle[0])
            border = [BLOCK] * size
            self.puzzle.insert(0, border)
            self.puzzle.append(border)
            self.puzzle = [[BLOCK] + line + [BLOCK] for line in self.puzzle]
        self.wordlist = Wordlist()
        self.gen_list()
        self.constraints = self.gen_constraints(self.variables)
        self.constraints += [constraint.flip() for constraint in self.constraints]

    def gen_list(self):
        """
        Read the puzzle and identify all across and down words, loading their properties into Variables
        :return:
        """
        count = 0
        for y in range(1, len(self.puzzle) - 1):
            for x in range(1, len(self.puzzle[0]) - 1):
                a_start = False
                d_start = False
                if self.puzzle[y][x] == SPACE and self.puzzle[y][x + 1] == SPACE and self.puzzle[y][x - 1] != SPACE:
                    a_start = True
                if self.puzzle[y][x] == SPACE and self.puzzle[y + 1][x] == SPACE and self.puzzle[y - 1][x] != SPACE:
                    d_start = True
                if a_start or d_start:
                    count += 1

                if a_start:
                    length = 2
                    while self.puzzle[y][x + length] != BLOCK:
                        length += 1
                    self.variables.append(Variable(count, 'A', length, y, x))
                if d_start:
                    length = 2
                    while self.puzzle[y + length][x] != BLOCK:
                        length += 1
                    self.variables.append(Variable(count, 'D', length, y, x))
        for variable in self.variables:
            variable.set_domain(self.wordlist)

    @staticmethod
    def gen_constraints(variables):
        """
        Generate a list of constraints based on the coordinate intersection of the provided variables
        :param variables: List of variables to be evaluated for intersection
        :return: List of constraints in the form of [((variable, position),(variable, position)), ... ]
        """
        intersections = defaultdict(list)
        for variable in variables:
            for i, space in enumerate(variable.spaces):
                intersections[space].append((variable, i))
        constraints = [Constraint(intsct[0], intsct[1]) for intsct in intersections.values() if len(intsct) > 1]
        return constraints

    def ac3(self):
        """
        Pares all variable domains such that all constraints are arc consistent, or notes that the given variables
        cannot be evaluated with their domains (no solution)
        :return: False if "No Solution:, True if reduced
        """
        for variable in self.variables:
            variable.set_domain(self.wordlist)
        worklist = self.gen_constraints(self.variables)
        worklist = worklist + [flip.flip() for flip in worklist]
        while len(worklist) > 0:
            constraint = worklist.pop(random.randint(0, len(worklist) - 1))
            if self.arc_reduce(constraint):  # if a-value of constraint domain changed
                if len(constraint.a[0].domain) == 0:  # if there are no possible values, there's no solution
                    print("no viable solution")
                    return False
                else:
                    look_again = [reval for reval in self.constraints if reval.contains(constraint.a[0])]
                    worklist += look_again  # TODO: Check for duplicate constraint evaluations?
        return True

    @staticmethod
    def arc_reduce(constraint):
        """
        Reduces the a-variable of the constraint such that the constraint (arc) is consistent
        :param constraint:
        :return:
        """
        change = False  # Tracks whether the domain changes
        for vx in constraint.a[0].domain:
            possibles = [vy for vy in constraint.d[0].domain if vy[constraint.d[1]] == vx[constraint.a[1]]]
            if len(possibles) == 0:
                constraint.a[0].rem_val(vx)
                change = True
        return change

    def solve(self):
        """
        Assigns values to all Variables, providing a solution to the puzzle
        :return:
        """
        for variable in self.variables:
            variable.set_val()
        while len([constraint for constraint in self.constraints if not constraint.satisfied()]):
            for constraint in self.constraints:
                while not constraint.satisfied():
                    constraint.a[0].set_val()
        """
        for variable in self.variables:
            constraints = [constraint for constraint in self.constraints if constraint.contains(variable, pos='A')]
            while any([not constraint.satisfied() for constraint in constraints]):
                variable.set_val(constraints=constraints)
        """


class Wordlist(list):
    """
    Wordlist holds the dictionary to be applied to the puzzle
    """

    def __init__(self, dict_path='../datafiles/dic'):
        with open(dict_path, 'r') as dict_file:
            dictionary = [line.strip() for line in dict_file]
        list.__init__(self, dictionary)


if __name__ == "__main__":
    s = Solver()
    start = time.time()
    #s.ac3()
    stop = time.time()
    print('AC3 Time: ' + str(stop - start))
    start = time.time()
    s.solve()
    stop = time.time()
    print('Solver Time: ' + str(stop - start))
    for var in Solver.variables:
        print(var)
