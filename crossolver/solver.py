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

    def __init__(self, a_word, a_pos, d_word, d_pos):
        a = (a_word, a_pos)
        d = (d_word, d_pos)

    def satisfied(self):
        if self.a[0].value(self.a[1]) == self.b[0].value(self.b[1]):
            return True
        else:
            return False

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
        for poss in dictionary:
            if len(poss) == self.length:
                self.domain.append(poss)


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
        self.gen_constraints()

    def gen_list(self):
        """
        Read the puzzle and identify all across and down words, loading their properties into variables
        :return:
        """
        count = 0
        for y in range(1, len(self.puzzle)-1):
            for x in range(1, len(self.puzzle[0])-1):
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
            pass
            # variable.set_domain(self.wordlist)

    def gen_constraints(self):
        """
        Generate list of constraints for the variables
        :return:
        """
        intersections = defaultdict(list)
        for variable in self.variables:
            for i, space in enumerate(variable.spaces):
                intersections[space].append((variable,i))
        constraints = [occurances for occurances in intersections.values() if len(occurances) > 1]
        return constraints



class Wordlist:
    """
    Wordlist holds the dictionary to be applied to the puzzle
    """

    def __init__(self, dict_path='../datafiles/dictionary'):
        with open(dict_path, 'r') as dict_file:
            dictionary = [line.strip() for line in dict_file]
        print(dictionary)


if __name__ == "__main__":
    Solver()
