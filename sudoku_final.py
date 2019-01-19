import time, random, os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

digits   = '123456789'
rows     = 'ABCDEFGHI'
cols     = digits
squares  = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))
             for s in squares)
global results, times
def test():
    "A set of unit tests."
    assert len(squares) == 81
    assert len(unitlist) == 27
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 20 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
                           ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
                           ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
    assert peers['C2'] == set(['A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
                               'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                               'A1', 'A3', 'B1', 'B3'])
    print('All tests pass.')


def parse_board(board):
    """Convert board to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the board.
    values = dict((s, digits) for s in squares)
    for s,d in board_values(board).items():
        if d in digits and not assign(values, s, d):
            return False ## (Fail if we can't assign d to square s.)
    return values

def board_values(board):
    "Convert board into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in board if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))


def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False

def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if d not in values[s]:
        return values
    values[s] = values[s].replace(d, '')
    if len(values[s]) == 0:
        return False
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False
        elif len(dplaces) == 1:
            if not assign(values, dplaces[0], d):
                return False
    return values

def drawboard(board):

    i = 0
    for val in board:
        if val == '.':
            print('.', end = ' ')
        elif val == '\n':
            return
        elif int(val) < 10:
            print(str(val), end =' ')
        else:
            print('Something wrong happened')
        i +=1

        if i in [(x*9)+3 for x in range(81)] + [(x*9)+6 for x in range(81)] + [(x*9)+9 for x in range(81)]:
            print('|', end =' ')
        if i in [27, 54, 81]:
            print('\n------+-------+-------+')
        elif i in [(x*9) for x in range(81)]:
            print('\n')



def solve(board): return search(parse_board(board))

def search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!
    ## Chose the unfilled square s with the fewest possibilities
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d))
		for d in values[s])

def some(seq):
    "Return some element of seq that is true."
    for e in seq:
        if e: return e
    return False

onetonine = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def solve_all(boards, name='', showif=0.0):
    """Attempt to solve a sequence of boards. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""

    def time_solve(board):
        start = time.time()
        values = solve(board)
        t = time.time() - start
        ## Display puzzles that take long enough
        print(board)
        #drawboard(board)
        if showif is not None and t > showif:
            try:
                drawboard(solve(board).values())
            except AttributeError:
                print('Sorry!!! This sudoku Failed')
                return False
            print(bcolors.BOLD + bcolors.OKGREEN + '('+str(round(t,2))+ ' seconds)\n' + bcolors.ENDC)
            ls1 = solve(board).values()
        print(''.join(ls1) + '\n')

        print('\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')
        return (t, solved(values))

    try:
        times, results = zip(*[time_solve(board) for board in boards])
    except TypeError:
        print('Sorry!! Could not solve this sudoku')
    N = len(boards)
    if N > 1:
        try:
            print(bcolors.BOLD + bcolors.OKGREEN + 'Solved '+str(sum(results)) +' of '+ str(N) + ' '+ name +' puzzles (total '+str(sum(times).__round__(3)) +' avg '+ str((sum(times)/N).__round__(3))+ ' secs ('+str((N/sum(times)).__round__(3))+' Hz), max '+str(float(max(times)).__round__(3))+' secs).' + bcolors.ENDC)
        except UnboundLocalError:
            print('Something bad happened. Sorry!!')

def solved(values):
    "A puzzle is solved if each unit is a permutation of the digits 1 to 9."

    def unitsolved(unit):
        return set(values[s] for s in unit) == set(digits)

    return values is not False and all(unitsolved(unit) for unit in unitlist)


def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return list(open(filename, 'r'))


def random_puzzle(N=17):
    """Make a random puzzle with N or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s]) == 1 else '.' for s in squares)
    return random_puzzle(N)  ## Give up and make a new puzzle


def playagain():
    asking = True
    while asking:
        userchoice = input('Do you want to play again?(Y/N)').lower()
        if userchoice == 'y':
            return True
        elif userchoice == 'n':
            return False
        else:
            continue


def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq


board = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
board1 = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
board2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
hard1 = '.....6....59.....82....8....45........3........6..3.54...325..6..................'
hardest_sudoku = '...2....53................7..7..........3.81.4.6...7.....5.....6......3.8...4..7.'
some_harder = '.79...4.....4.5.......8......2....41..3.................724.......5..3...2..1....'

problems = [board, board1, board2, hard1, hardest_sudoku, some_harder]
print('Welcome to SUDOKU')
mega = True
while mega:
    choice = input('Choose any option\n=>1. Enter sudoku via keyboard\n=>2. Sudoku problem is in a file\n=>3. Show some random Sudokues\n=>4. Exit\n==> ')
    if choice == '1':
        print('Here is example of sudoku problem.')
        example = random.randrange(0,5)
        print(problems[int(example)])
        drawboard(problems[int(example)])
        choice1 = input('=>1. Enter sudoku as shown in sample\n=>2. Go Back\n==> ')

        if choice1 == '1':
            option1 = True
            more_break, more_break1 = False, False
            while option1:
                userboard = input('Enter your sudoku problem here.\n+=> ')
                userboard1 = list(userboard)
                for i in range(len(userboard1)):
                    if userboard1[i] not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '.','0']:
                        print('Something wrong happened. We are sorry for that. Would you like to enter problem again?(Y/N)')
                        again = input()
                        if again.lower() == 'y':
                            more_break = True
                            break
                        elif again.lower() == 'n':
                            more_break1 = True
                            mega = False
                            break
                        else:
                            print('Wrong input!!')
                            continue
                if more_break:
                    continue
                if more_break1:
                    break
                open('temp.txt', 'x')
                temp = open('temp.txt', 'w')
                temp.write(userboard)
                temp.close()
                solve_all(from_file('temp.txt'))
                os.remove('temp.txt')
                play = playagain()
                if play:
                    continue
                else:
                    break

        elif choice1 == '2':
            continue
        else:
            print('Incorrect input!!')
            continue
    elif choice == '2':
        file = True
        while file:
            filepath = input('Enter path for file(back to back): ')
            if filepath.lower() == 'back':
                break
            try:
                open(filepath, 'r')
            except IOError:
                print('File or path does not exist. Please check again')
                continue
            file = False
            solve_all(from_file(filepath))
            play = playagain()
            if play:
                continue
            else:
                break
    elif choice == '3':
        ran = True
        while ran:
            print('Sometimes random problem in sudoku might not be solvable so code might crash. Sorry in advance !!!')
            number = input('How many random sudokus do you want to see??(back to back)\n==> ')
            if number.lower == 'back':
                break
            elif not number.isdigit():
                print('Incorrect input!! Try again')
                continue
            test()
            solve_all([random_puzzle() for _ in range(int(number))], "random")
            play = playagain()
            if play:
                continue
            else:
                break
    elif choice == '4':
        mega = False
        break
    else:
        print('Incorrect input try again!!')
        continue

#test()

#solve_all(from_file("files/hard.txt"), "hard", 0.0)

#solve_all([random_puzzle() for _ in range(99)], "random", 1.0)

