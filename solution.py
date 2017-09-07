assignments = []

def cross(a, b):
    """
    Cross product of elements in A and elements in B.
    Args:
        any two strings or lists
    Returns:
        a list of all the possible combinations using each index of a with each of b
    """
    return [s+t for s in a for t in b]
# diagonal_sudoku is a global variable to switch type of sudoku puzzle between regular and diagonal
diagonal_sudoku = True
# rows and cols are constants to name the sudoku board
rows = 'ABCDEFGHI'
cols = '123456789'
# boxes lists the names of all 81 boxes on the sudoku board
boxes = cross(rows, cols)
# Element example:
# row_units[0] = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9']
# This is the top most row.
row_units = [cross(r, cols) for r in rows]
# Element example:
# column_units[0] = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1']
# This is the left most column.
column_units = [cross(rows, c) for c in cols]
# Element example:
# square_units[0] = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
# This is the top left square.
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Element example:
# diagonal_units[0] = ['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9']
# This is the top left to bottom right diagonal
diagonal_units = [list(''.join(i) for i in zip(rows, cols)), list(''.join(i) for i in zip(rows, cols[::-1]))]
# a conditional statement to define the different units in each type of sudoku inside unitlist
if diagonal_sudoku is True:
    unitlist = row_units + column_units + square_units + diagonal_units
else:
    unitlist = row_units + column_units + square_units
# units is a dictionary of each box with a list of units each are contained in
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
# peers is a dictionary of each box and a list of its peers
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)




def assign_value(values, box, value):
    """
    Assigns a value to a given box. If it updates the board record it.
    Use this function to update values dictionary in order for pygame to work!
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
        box: the location on the sudoku board to change
        value: the value to append to the values dictionary for the particular box
    Returns:
        the updated values dictionary
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """
    Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    # List boxes with two possible answers left in format ['A1','A2',...]
    unsolved = [box for box in values.keys() if len(values[box]) == 2]
    # Collect boxes that have the same answers if also are peers
    twins = [[twin1, twin2] for twin1 in unsolved \
                    for twin2 in peers[twin1] \
                    if values[twin1] == values[twin2]]

    if len(twins) > 0:
    # For each pair of naked twins,
        for i in range(len(twins)):
            # find intersection of peers
            twins_peers = peers[twins[i][0]] & peers[twins[i][1]]
            # Delete the naked twin values from intersecting peers.
            for twins_peer in twins_peers:
                if len(values[twins_peer])>1:
                    for numb in values[twins[i][0]]:
                        #values[twins_peer] = values[twins_peer].replace(numb,'')
                        assign_value(values, twins_peer, values[twins_peer].replace(numb,''))
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    for numb in grid:
        if numb == '.':
            values.append(all_digits)
        elif numb in all_digits:
            values.append(numb)
    assert len(values) == 81
    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Performs the elimination strategy by eliminating the possible answers in the values dixtionary given by the peers of each box
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the updated values dictionary with peer values eliminated
    """
    solved_box = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_box:
        eliminate_value = values[box]
        for affected_peer in peers[box]:
            #values[affected_peer] = values[affected_peer].replace(eliminate_value,'')
            assign_value(values, affected_peer, values[affected_peer].replace(eliminate_value,''))
    return values

def only_choice(values):
    """
    Peforms the only choice strategy by searching each unit for a box that contains a possible answer no other box in the unit contains
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the updated values dictionary with the only possible answer chosen for each unit
    """
    for unit in unitlist:
        for num in cols:
            only_value = [box for box in unit if num in values[box]]
            if len(only_value) == 1:
                #values[only_value[0]] = num
                assign_value(values, only_value[0], num)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Args:
        A sudoku in dictionary form.
    Returns:
        The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.
    Args:
        A sudoku in dictionary form.
    Returns:
        The resulting sudoku in dictionary form.
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## contstraint propagation failed in this iteration
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(reduce_puzzle(grid_values(grid)))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
