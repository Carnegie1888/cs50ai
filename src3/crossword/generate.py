import sys
import random

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            for word in self.domains[var]:
                if len(word) != var.length:
                    self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        i, j  = self.crossword.overlaps[x, y]

        for x_word in self.domains[x].copy():
            ok = False
            for y_word in self.domains[y]:
                if x_word[i] == y_word[j]:
                    ok = True
                    break
            if not ok:
                self.domains[x].remove(x_word)
                revised = True
        return revised
            


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            queue = self.crossword.overlaps
        else:
            queue = arcs
        queue_copy = queue.copy()
        while queue:
            key, = queue.popitem()
            x, y = key
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for var in self.crossword.neighbors(x).difference(set(y)):
                    queue[var, x] = queue_copy[var, x]
        return True



    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.crossword.variables):
            return True
        return False


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var in assignment:
            word_x = assignment[var]
            if len(word_x) != var.length:
                return False
            for neighbor in self.crossword.neighbors(var):
                i, j = self.crossword.overlaps[neighbor, var]
                word_y = assignment[neighbor]
                if word_x[i] != word_y[j]:
                    return False
        return True




    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        rule_out = {}

        for word1 in self.domains[var]:
            cnt = 0
            for neighbor in self.crossword.neighbors(var).difference(set(assignment.keys())):
                i, j = self.crossword.overlaps[neighbor, var]
                for word2 in self.domains[neighbor]:
                    if word1[i] != word2[j]:
                        cnt += 1
            rule_out[word1] = cnt
        
        rule_out = dict(sorted(rule_out.items(), key=lambda item: item[1]))


        return list(rule_out.keys())



    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        data = {}
        for var in self.crossword.variables.difference(set(assignment.keys())):
            remain = len(self.domains[var])
            degree = len(self.crossword.neighbors(var))
            data[var] = (remain, degree)
        
        def tuple_compare(item):
            return (item[1][0], -item[1][1])


        data = sorted(data.items(), key=tuple_compare)

        choices = [data[0]]

        for key, value in data[1:]:
            if value == choices[0][1]:
                choices.append((key, value))
        
        return random.choice(choices)[0]
    

    def inference(self, var):
        arcs = {}
        keys = self.crossword.overlaps.keys()
        self.domains_copy = self.domains


        for neighbor in self.crossword.neighbors(var):
            if (neighbor, var) in keys:
                arcs[neighbor, var] = self.crossword.overlaps[neighbor, var]

        return self.ac3(arcs)

        


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment_copy = assignment.copy()
            assignment[var] = value
            
            if self.consistent(assignment):
                infer = self.inference()
                if not infer:
                    self.domain = self.domains_copy
                result = self.backtrack(assignment)
                if result:
                    return result
                
            self.domain = self.domains_copy
            assignment = assignment_copy
        return False
                




def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
