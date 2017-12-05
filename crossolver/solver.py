import random
from collections import defaultdict

SPACE = 'O'
BLOCK = 'X'


def print_list(toPrint):
    for line in toPrint:
        print(line)
    print("---------------------")


class Constraint:
    a = (None, None)
    d = (None, None)

    def __init__(self, a_tuple, d_tuple):
        self.a = a_tuple
        self.d = d_tuple

    def __eq__(self, other):
        if not isinstance(self, other.__class__):
            return False
        if self.a == other.a and self.d == other.d:
            return True

    def satisfied(self):
        if self.a[0].value(self.a[1]) == self.d[0].value(self.d[1]):
            return True
        else:
            return False

    def __str__(self):
        return str(self.a[0].num) + self.a[0].ad + '-' + str(self.a[1]) + ' and ' + str(self.d[0].num) + self.d[0].ad + '-' + str(self.d[1])


class Variable:
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
        self.domain = [possible for possible in dictionary if len(possible) == self.length]

    def __str__(self):
        return str(self.num) + ' ' + self.ad + ': ' + str(self.length) + ' long.  May be: ' + str(self.domain)

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
        with open(puzzle_path, 'r') as puzzle_file:
            self.puzzle = [list(line.strip()) for line in puzzle_file]
            size = len(self.puzzle[0])
            border = [BLOCK] * size
            self.puzzle.insert(0, border)
            self.puzzle.append(border)
            self.puzzle = [[BLOCK] + line + [BLOCK] for line in self.puzzle]
            print_list(self.puzzle)
        self.wordlist = Wordlist()
        self.gen_list()
        self.gen_constraints(self.variables)

    def gen_list(self):
        """
        Read the puzzle and identify all across and down words, loading their properties into variables
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


class Wordlist(list):
    """
    Wordlist holds the dictionary to be applied to the puzzle
    """

    def __init__(self, dict_path='../datafiles/dic'):
        with open(dict_path, 'r') as dict_file:
            dictionary = [line.strip() for line in dict_file]
        list.__init__(self, dictionary)


if __name__ == "__main__":
    Solver()
