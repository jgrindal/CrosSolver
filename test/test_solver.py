import pytest
import unittest
from crossolver.solver import Variable, Solver, Constraint


class MyTestCase(unittest.TestCase):
    @pytest.fixture
    def test_setup(self):
        one_a = Variable(num=1, ad='A', length=3, x=1, y=1)
        one_d = Variable(num=1, ad='D', length=3, x=1, y=1)
        two_d = Variable(num=2, ad='D', length=2, x=2, y=1)
        one_a2 = Variable(num=1, ad='A', length=3, x=1, y=1)

    def test_constraint_eq(self):
        one_a = Variable(num=1, ad='A', length=3, x=1, y=1)
        one_d = Variable(num=1, ad='D', length=3, x=1, y=1)
        two_d = Variable(num=2, ad='D', length=2, x=2, y=1)
        one_a2 = Variable(num=1, ad='A', length=3, x=1, y=1)
        cons_1 = Constraint((one_a, 0), (one_d, 0))
        cons_2 = Constraint((one_a, 0), (one_d, 0))  # Identical to cons_1
        cons_3 = Constraint((one_d, 0), (one_a, 0))  # Backwards constraint
        cons_4 = Constraint((one_a, 1), (two_d, 0))  # Valid Constraint
        cons_5 = Constraint((one_a2, 0), (one_d, 0))  # Identical to cons_1, but with different one_a
        self.assertTrue(cons_1 == cons_2)  # Equivalent constraints should evaluate the same
        self.assertTrue(cons_1 == cons_5)  # Equivalent constraints should evaluate the same
        self.assertFalse(cons_1 == cons_3)  # Backwards constraints should fail
        self.assertFalse(cons_1 == cons_4)  # Different constraints should fail
        self.assertTrue(cons_1 != cons_4)  # Different constraints should not equal

    def test_gen_constraints(self):
        """
        Test case:
             1D 2D
              | |
              v v
        1A -> O O O
        3A -> O O
              O
        """
        cons = []
        one_a = Variable(num=1, ad='A', length=3, x=1, y=1)
        one_d = Variable(num=1, ad='D', length=3, x=1, y=1)
        two_d = Variable(num=2, ad='D', length=2, x=2, y=1)
        three_a = Variable(num=3, ad='A', length=2, x=2, y=2)
        vars = [one_a, one_d, two_d, three_a]
        self.assertNotEquals(False, True)


if __name__ == '__main__':
    unittest.main()
