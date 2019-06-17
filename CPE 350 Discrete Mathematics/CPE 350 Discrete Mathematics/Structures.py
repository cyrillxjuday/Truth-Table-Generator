from colorama import *
from os import system

class Stack(object):
    def __init__(self):
        self.items = []
        self.size = 0

    def push(self, x):
        self.items.append(x)
        self.size = self.size + 1

    def pop(self):
        self.items.pop(self.size - 1)
        self.size = self.size - 1

    def top(self):
        return self.items[self.size-1]
    
    def isempty(self):
        return self.size == 0

    def print(self):
        print(self.items)

class Deque(object):
    def __init__(self):
        self.items = []
        self.size = 0

    def pushBack(self, x):
        self.items.append(x)
        self.size = self.size + 1

    def popFront(self):
        self.size = self.size - 1
        self.items.pop(0)

    def popBack(self):
        self.items.pop(self.size - 1) # buggy
        self.size = self.size - 1

    def front(self):
        return self.items[0]

    def back(self):
        return self.items[self.size - 1]

    def isempty(self):
        return self.size == 0

    def print(self):
        print(self.items)

class Matrix(object):
    def __init__(self):
        init()
        self.rows = 0                           # matrix rows
        self.cols = 0                           # matix columns
        self.variables = {}                     # stores the variables
        self.items = [[]]                       # here resides the truth table values
        self.output = []                        # the final output of the proposition given the truth table
        self.varcount = 0                       # number of unique variables in the proposition
        self.inputExpression = ''               # holds the input expression. (used at at the final printing of the truth table) referenced only once
              
    def simplify(self, ipt):
        output = ipt
        if ('<->' in ipt):
            output = ipt.replace('<->', '=', len(ipt))
        if ('->' in output):
            output = output.replace('->', '>', len(ipt))
        return output

    def revert(self, ipt):
        output = ipt
        if ('=' in ipt):
            output = ipt.replace('=', '<>', len(ipt))
        if ('>' in output):
            output = output.replace('>', '->', len(ipt))
        return output
    # NOT
    def negate(self,x):
        return 1 if x == 0 else 0

    def isoperator(self, x):
        if str(x) in '-|&>=:':
            return True
        return False

    # function that evaluate binary operators
    def eval(self, op, lhs, rhs):
        if op == ':':                   # XOR
            return 1 if lhs != rhs else 0
        elif op == '|':                 # OR
            return lhs or rhs
        elif op == '&':                 # AND
            return lhs and rhs
        elif op == '>':                 # Implication
            return rhs if lhs != rhs else 1
        elif op == '=':                 # Double Implication
            return 1 if rhs == lhs else 0
        return None

    # evaluates a postfix expression
    # the expression here is already translated with the truth values (p&q) -> (1&1)
    def evaluate(self, expression):
        # expression is a deque of characters that directly translates to a postfix expression
        stack = Stack()

        while not expression.isempty():
            # if the character is an operand, push it to the stack
            char = expression.items[0]
            if str(char) in '10':
                stack.push(expression.front())
            # this is the case for negation,
            # since it only needs a single operand or RHS
            # we must pop one operand from the stack and negate its value.
            # after that, push the negated value to the stack
            elif char == '-':
                negated = self.negate(stack.top())
                stack.pop()
                stack.push(negated)
            # other binary operators will go to this point
            else:
                rhs = stack.top()
                stack.pop()
                lhs = stack.top()
                stack.pop()
                result = self.eval(char, lhs, rhs)
                stack.push(result)
            expression.popFront()
        return 'T' if stack.top() == 1 else 'F'

    # this will convert infix to postfix using Djikstra's Shunting Yard algorithm
    # returns a deque (double ended list in C++) generated from a formatted string
    def infix_to_postfix(self, x):
        precedence = { '-' : 4, '&' : 3, '|' : 2, ':' : 2, '>' : 1, '=' : 1, '(' : 0}
        operatorStack = Stack()
        outputDeque = Deque()
    
        # parse the whole expression characters one by one.
        i = 0
        while i < len(x):
            # ignore the character if its a space
            # skip the current iteration
            if x[i] == ' ':
                i = i + 1
                continue

            # if the character is an opening parenthesis, push it into the operator stack
            # and then continue iteration
            if x[i] == '(':
                operatorStack.push(x[i])
                i = i + 1
                continue
        
            # if the character is an operand, push it into the output deque
            if x[i] in '10':
                outputDeque.pushBack(int(x[i]))
            elif x[i] == 'T':
                outputDeque.pushBack(1) 
            elif x[i] == 'F':
                outputDeque.pushBack(0)
            # if the operator stack is empty, simply push the first operator in it
            elif operatorStack.isempty():
                operatorStack.push(x[i])
            # if the parsed character is a closing parethesis,
            # transfer the operators to the output deque from top to bottom
            elif x[i] == ')':
                #convert the inner expression until an opening parenthesis is encountered
                while operatorStack.top() != '(' and not operatorStack.isempty():
                    outputDeque.pushBack(operatorStack.top())
                    operatorStack.pop()                
                # pop the opening parenthesis
                operatorStack.pop()    
            else: 
                # IMPORTANT.
                # the character is an operator,
                # check the level of precendence of the top operator in the stack (assign to oplev)
                # if (oplev) is greater than the current input operator (x[i]),
                # pop the top operator stack and push the value to the back of output deque
                # push the incoming operator (x[i]) to the stack afterwards
                
                op = operatorStack.top()
                oplev = precedence[op]
                
                if oplev > precedence[x[i]]:
                    # compare the precedence of the incoming operator and the top of the stack
                    # while the top operator in the stack has higher precedence, pop the stack and continue comparing the precedence
                    # until the top operator in the stack has lower precedence or the stack is empty 
                    while not( operatorStack.isempty()) and precedence[x[i]] < precedence[operatorStack.top()] :
                        outputDeque.pushBack(operatorStack.top())
                        operatorStack.pop()

                    operatorStack.push(x[i])
                else:
                # if the top operator in the operator stack has lower precedence,
                # simply push the current (x[i]) to the operator stack
                    operatorStack.push(x[i])

            i = i + 1

        # if there are operators left in the operator stack,
        # transfer them to the output deque one by one from top to bottom
        while not operatorStack.isempty():
            outputDeque.pushBack(operatorStack.top())
            operatorStack.pop()
        return outputDeque

    # initializes the truth table with values
    def createTruthMatrix(self):
        counter = 1
        state = 1
        limit = (2 ** self.varcount)
        interval = limit
        nums = []
        
        self.cols = self.varcount
        self.rows = limit

        # populate the array with the truth table values (1,0)
        i = 0
        while i < (limit * self.varcount):
            nums.append(state)
            if i % limit == 0:
                interval /= 2
            if counter >= interval:
                state = self.negate(state)
                counter = 0
            i += 1
            counter += 1

        # transfer the contents of 1D list to main Matrix
        indexer = i = j = 0
        while i < self.varcount:
            while j < limit:
                self.items[i].append(nums[indexer])
                indexer += 1
                j += 1
            j = 0
            i += 1
            self.items.append([])
    # end createTruthMatrix

    # generates a dictionary of variables and assign an index for the truth table space
    def generateFrom(self, expression):
        operators = 'TF()-=:|&> '
        i = 0
        while i < len(expression):
            if expression[i] not in operators:
                var = ''
                while (expression[i] not in operators):
                    var = var + expression[i]
                    i = i + 1
                    if i == len(expression):
                        break
                if var not in self.variables:
                    self.varcount += 1
                    self.variables[var] = self.varcount
            else:
                i = i + 1
    # end generate from

    # print the truth table
    def print(self): 
        indexer = i = j = 0
        sizes = []
        for key,values in self.variables.items():
            print(Fore.YELLOW + "|",end = '')
            print(Fore.WHITE+str(key).center(len(key)+2,' '),end = '')
            sizes.append(len(key)+2)
        print(Fore.YELLOW+'|',Fore.WHITE+self.inputExpression.center(len(self.inputExpression)+2, ' '), end = Fore.YELLOW+'|\n')
            
        while i < self.rows:
            while j < self.cols:
                value = "F" if self.items[j][i] == 0 else "T"
                print(Fore.YELLOW+"|",end = '')
                print(Fore.WHITE+value.center(sizes[j],' '), end = '')
                j += 1
            print(Fore.YELLOW+'|',Fore.WHITE+self.output[indexer].center(len(self.inputExpression)+2,' '), end = Fore.YELLOW+'|\n')
            indexer += 1
            i += 1
            j = 0
        print()
    # end print

    def printComparison(self, x, y, output1, output2):
        indexer = i = j = 0
        sizes = []
        for key,values in self.variables.items():
            print(Fore.YELLOW + "|",end = '')
            print(Fore.WHITE+str(key).center(len(key)+2,' '),end = '')
            sizes.append(len(key)+2)
        print(Fore.YELLOW+'|',Fore.WHITE+x.center(len(x)+2, ' '), end = '')
        print(Fore.YELLOW+'|',Fore.WHITE+y.center(len(y)+2, ' '), end = Fore.YELLOW+'|\n')
            
        while i < self.rows:
            while j < self.cols:
                value = "F" if self.items[j][i] == 0 else "T"
                print(Fore.YELLOW+"|",end = '')
                print(Fore.WHITE+value.center(sizes[j],' '), end = '')
                j += 1
            print(Fore.YELLOW+'|',Fore.WHITE+output1[indexer].center(len(x)+2,' '), end = Fore.YELLOW+'')
            print(Fore.YELLOW+'|',Fore.WHITE+output2[indexer].center(len(y)+2,' '), end = Fore.YELLOW+'|\n')
            indexer += 1
            i += 1
            j = 0
        print()

    def substitute(self, expression):
        i = j = 0
        while i < self.rows:
            output = expression
            for key, value in self.variables.items():
               output = output.replace(key, str(self.items[value-1][i]),40)
            postOutput = self.infix_to_postfix(output)
            output = self.evaluate(postOutput)
            self.output.append(output)
            i += 1

    def refresh(self):
        self.rows = 0           # matrix rows
        self.cols = 0           # matix columns
        self.variables = {}     # stores the variables
        self.items = [[]]       # here resides the truth table values
        self.varcount = 0       # number of unique variables in the proposition
        self.output = []

    def printOutput(self):
        i = 0
        print('[ ', end = '')
        while i < len(self.output):
            print(self.output[i],',', end = ' ')
            i += 1
        print(']')            
    
    # driver for generator
    def generate(self):
        proposition = self.simplify(input(Fore.WHITE+'enter the proposition: '))
        self.inputExpression = self.revert(proposition)
        self.generateFrom(proposition)
        self.createTruthMatrix()
        self.substitute(proposition)
        self.print()
        self.refresh() 
        system('pause')

    def twoVar(self):
        init()
        print("Available variables to use are [p] and [q]")
        self.generateFrom("p|q")
        proposition = self.simplify(input(Fore.WHITE+'enter the proposition: '))
        self.inputExpression = self.revert(proposition)
        self.createTruthMatrix()
        self.substitute(proposition)
        self.print()
        self.refresh()
        system('pause')
        return

    def threeVar(self):
        init()
        print("Available variables to use are [p], [q] and [r]")
        self.generateFrom("p|q|r")
        proposition = self.simplify(input(Fore.WHITE+'enter the proposition: '))
        self.inputExpression = self.revert(proposition)
        self.createTruthMatrix()
        self.substitute(proposition)
        self.print()
        self.refresh()
        system('pause')
        return

    # driver for comparator
    def compare(self):
        init()
        m1 = Matrix()
        m2 = Matrix()

        m1prop = m1.simplify(input(Fore.WHITE+'enter the First proposition:  '))
        m1.inputExpression = self.revert(m1prop)
        m1.generateFrom(m1prop)
        m1.createTruthMatrix()
        m1.substitute(m1prop)
        proposition1 = m1.output

        m2prop = m2.simplify(input(Fore.WHITE+'enter the Second proposition: '))
        m2.inputExpression = self.revert(m2prop)
        m1.output = []
        m1.substitute(m2prop)
        proposition2 = m1.output

        print()
        print('Generated from the table')
        m1.printComparison(self.revert(m1prop), self.revert(m2prop), proposition1, proposition2)
        print('The two propositions are equal.' if proposition1 == proposition2 else 'The two propositions are inequal.')
        system("pause")

    def compare2(self):
        init()
        m1 = Matrix()
        m2 = Matrix()
        print("Available variables to use are [p] and [q]")
        m1prop = m1.simplify(input(Fore.WHITE+'enter the First proposition:  '))
        m1.inputExpression = self.revert(m1prop)
        m1.generateFrom('p|q')
        m1.createTruthMatrix()
        m1.substitute(m1prop)
        proposition1 = m1.output

        m2prop = m2.simplify(input(Fore.WHITE+'enter the Second proposition: '))
        m2.inputExpression = self.revert(m2prop)
        m1.output = []
        m1.substitute(m2prop)
        proposition2 = m1.output

        print()
        print('Generated from the table')
        m1.printComparison(self.revert(m1prop), self.revert(m2prop), proposition1, proposition2)
        print('The two propositions are equal.' if proposition1 == proposition2 else 'The two propositions are inequal.')
        system("pause")

    def compare3(self):
        init()
        m1 = Matrix()
        m2 = Matrix()
        print("Available variables to use are [p], [q] and [r]")
        
        m1prop = m1.simplify(input(Fore.WHITE+'enter the First proposition:  '))
        m1.inputExpression = self.revert(m1prop)
        m1.generateFrom('p|q|r')
        m1.createTruthMatrix()
        m1.substitute(m1prop)
        proposition1 = m1.output

        m2prop = m2.simplify(input(Fore.WHITE+'enter the Second proposition: '))
        m2.inputExpression = self.revert(m2prop)
        m1.output = []
        m1.substitute(m2prop)
        proposition2 = m1.output

        print()
        print('Generated from the table')
        m1.printComparison(self.revert(m1prop), self.revert(m2prop), proposition1, proposition2)
        print('The two propositions are equal.' if proposition1 == proposition2 else 'The two propositions are inequal.')
        system("pause")

    def prompt(self):
        system('cls')
        print(Fore.WHITE+"Valid Operators:")
        print("\tOperators              Symbols")
        print('\tConjunction               &')
        print('\tDisjunction               |')
        print('\tNegation                  -')
        print('\tBiconditional            <->')
        print('\tImplication               ->')
        print()

    def Start(self):
        while 1:
            system('cls')
            print(Fore.WHITE+'CPE Discrete Mathematics\n')
            print(" [1]  Truth Table Generator.")
            print(" [2]  Proposition Equality Tester.")
            print(" [0]  Exit.\n")
            choice = int(input(" --> Enter your choice: "))
            
            if choice == 1:
                print(Fore.WHITE+'\n\t [1] Two variables [p, q]')
                print('\t [2] Three variables [p, q, r]')
                print('\t [3] Free variables\n')
                choice = int(input("\t --> Enter your choice: "))
                system('cls')
                self.prompt()
                if choice == 1:
                    self.twoVar()
                elif choice == 2:
                    self.threeVar()
                else:
                    self.generate()

            elif choice == 2:
                print(Fore.WHITE+'\n\t [1] Two variables [p, q]')
                print('\t [2] Three variables [p, q, r]')
                print('\t [3] Free variables\n')
                choice = int(input("\t --> Enter your choice: "))
                system('cls')
                self.prompt()
                if choice == 1:
                    self.compare2()
                elif choice == 2:
                    self.compare3()
                else:
                    self.compare()
            elif choice == 0:
                system('cls')
                print("Bye!")
                break
    