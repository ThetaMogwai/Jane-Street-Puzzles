import numpy as np

# ====================================================================================
# Step 1 : Generate the list of operations creating a path to all the pre-filled cells

# From a starting score and turn, generate all combinations of operations (+ * /), compute the score of each sequence,
# then see if it matches one of the pre-filled cell and returns the sequence of operations and scores leading to this cell.
# Then remove this cell from the list, set it as the starting point and run the function again

# Repeat this operation until a sequence linking all pre-filled cells is found

# List of pre-filled scores (0 is removed as it's the starting point)
targets = [1,16,23,37,88,138,272,449,528,750,1100] # targets will be reused much later

def complete_sequence(targets):
    
    def next_sequence(start, targets, turn):
        sequences = [[[start], ""]]
    
        if turn < 18 : steps = 3       # the first 6 sequences contain 3 turns
        else : steps = 7               # the last 5 sequences contain 7 turns (found using a while loop)
        
        # for each turn try all operations on all previous sequences until they reach the correct length (3 or 7)
        # creating a tree-like structure of operations and scores
        
        for n in range(turn, turn + steps):
            new_sequences = []
            
            for sequence in sequences:
                scores, operators = sequence
    
                new_sequences.append([scores + [scores[-1] + n], operators + "+"])
                new_sequences.append([scores + [scores[-1] * n], operators + "*"])
    
                if scores[-1] % n == 0:     # check if the score is divisble by n (turn)
                    new_sequences.append([scores + [int(scores[-1] / n)], operators + "/"])
    
            sequences = new_sequences.copy()
        
        
        # for all the sequences generated, try to find one with a score equal to a pre-filled cell
        # the function always returns a single sequence
        
        for sequence in sequences:
            if sequence[0][-1] in targets:
                sequence[0].pop(0)                  # remove the first score (the starting point)
                return sequence, turn + steps       # saved at the end of the previous sequence
    
    
    # Run this function from the starting point 0 
    # Repeat from the end point until a path to all pre-filled cell is found
    
    start, turn = 0, 1
    sequences = []
    
    while len(targets) > 0:
        sequence, turn = next_sequence(start, targets, turn)
        last_target = sequence[0][-1]
        
        start = last_target
        targets.remove(last_target)
        sequences.append(sequence)
    
    return sequences


# ====================================================================================
# Step 2 : Reasoning on the operator sequence and introducting towers

# Using the full operator sequence generated earlier we can deduct the "height" of each score :
    # * and the following + have a height of 1 and thus need to be on a tower
    # / and the following + have a height of 0 and thus the previous operators have a height of 1
    
# Operator sequence = ++/+++*/+++*++/+++++*++/+++++*/+*/+++++++++++++++++++*
# The first special operator is a /, so the previous operators have a height of 1 and are placed on towers
# From this we deduct that the bottom left cell is a tower

def sequence_height(sequences):
    # assign a height to each operation/score : "+" height unchanged, "*" height increased, "/" height reduced
    # the height is then stored as a sublist of each sequence
    
    current_height = 1
    for sequence in sequences:
        height = []
        
        for operator in sequence[1]:
            if operator == "*" : current_height += 1
            elif operator == "/" : current_height -= 1
            height.append(current_height)
        
        sequence.append(height)
    return sequences

# By looking at the sequence we generated we only need 12 towers (out of 13) to all the pre-filled cells,
# So we know that we will have to make additionnal moves to add the last tower.

""" Full sequences of scores, operators and heights
sequences = [[[1, 3, 1], '++/', [1, 1, 0]],
             [[5, 10, 16], '+++', [0, 0, 0]],
             [[112, 14, 23], '*/+', [1, 0, 0]],
             [[33, 44, 528], '++*', [0, 0, 1]],
             [[541, 555, 37], '++/', [1, 1, 0]],
             [[53, 70, 88], '+++', [0, 0, 0]],
             [[107, 127, 2667, 2689, 2712, 113, 138], '++*++/+', [0, 0, 1, 1, 1, 0, 0]],
             [[164, 191, 219, 248, 7440, 240, 272], '++++*/+', [0, 0, 0, 0, 1, 0, 0]],
             [[8976, 264, 299, 335, 372, 410, 449], '*/+++++', [1, 0, 0, 0, 0, 0, 0]],
             [[489, 530, 572, 615, 659, 704, 750], '+++++++', [0, 0, 0, 0, 0, 0, 0]],
             [[797, 845, 894, 944, 995, 1047, 1100], '+++++++', [0, 0, 0, 0, 0, 0, 0]]]
"""


# ====================================================================================
# Step 3 : Creating the variables described in the puzzle

# Starting board with all the pre-filled scores
board = np.array([[None, None, None, None, None, 37,   None, 1100],
                  [None, None, None, None, None, None, None, None],
                  [None, None, None, 23,   None, 138,  None, None],
                  [528,  None, None, None, None, None, None, None],
                  [None, 449,  None, None, 16,   None, None, None],
                  [None, 750,  None, 88,   None, 272,  1,    None],
                  [None, None, None, None, None, None, None, None],
                  [0,    None, None, None, None, None, None, None]])

# Map of the board divided in regions, each cell contain the id of the zone it belongs to
regions_map = np.array([[ 0,  0,  0,  0,  0,  1,  1,  1],
                        [ 2,  2,  2,  3,  3,  4,  4,  1],
                        [ 2,  5,  2,  3,  3,  3,  4,  1],
                        [ 6,  5,  5,  7,  7,  8,  4,  4],
                        [ 6,  6,  5,  7,  7,  8,  8,  9],
                        [ 6, 10,  5, 11,  8,  8, 12,  9],
                        [ 6, 10, 11, 11, 11, 12, 12,  9],
                        [10, 10, 10, 11, 12, 12,  9,  9]])

regions = [0]*13    # Contain the state of each region : 0 = no tower, 1 = already a tower
regions[10] = 1     # we know that the bottom lef cell in zone 10 has a tower

# Possible moves for each operator, we already analyzed the height so all moves are 2D moves and "*" = "/"
movesets = {"+": [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)],
            "*": [(2,0),(-2,0),(0,2), (0,-2)],
            "/": [(2,0),(-2,0),(0,2), (0,-2)]}


# ====================================================================================
# Step 4 : Filling boards until we find the correct one

# Generate all the possible boards unsing a sequence of operations considering the current state of the board
# First there will be a growing number of possible boards (especially as the length of a sequence goes to 7)
# Up to several thousands possible boards, before a drastic reduction as we won't be able to complete the last sequences

def all_boards(board,regions,start,target,sequence):
    boards = []
    regions_list = []
    
    def next_move(position,board,regions,step):
        
        # A move is possible if all the following conditions are met :
            # - the destination is on the board
            # - the total height of the region (after the move) is inferior to 2
            # - the cell is empty if it's not the last move of the sequence
            # - the cell is equal to the sequence's target if it's the last move
        
        def move_available(position,board,target):
            x,y = position
            if 0 <= x < 8 and 0 <= y < 8:
                if regions[regions_map[x,y]] + height < 2:
                    if (step + 1 < len(sequence[1]) and board[x,y] == None) or (step + 1 == len(sequence[1]) and board[x,y] == target):
                        return True
            return False
        
        
        score, move_type, height = [sublist[step] for sublist in sequence]
        x,y = position
        
        for dx,dy in movesets[move_type]:
            new_position = (x+dx,y+dy)
            
            # if a move is possible, we update the board and the regions values, then :
                # - if we completed the sequence then the board is good and saved
                # - if there are moves left we run the function again 
            # then we backtrack restoring the old board and regions before exploring other moves
            
            if move_available(new_position,board,target):
                X,Y = new_position
                region_id = regions_map[X,Y]
                
                old_board = board[X,Y]
                board[X,Y] = sequence[0][step]
                regions[region_id] += height
                
                if step + 1 < len(sequence[1]):
                    next_move(new_position,board,regions, step+1)
                else:
                    boards.append(board.copy())
                    regions_list.append(regions.copy())
                
                board[X,Y] = old_board          # backtracking board
                regions[region_id] -= height    # backtracking regions values
            
    next_move(start,board,regions,0)
    return boards, regions_list


# Iterate through sequences using boards generated by previous sequences until it finds boards
# with a path through all the pre filled cells 

def chained_boards(sequences,board,regions):   
    targets = [1,16,23,528,37,88,138,272,449,750,1100]
    starts=[[7,0],[5,6],[4,4],[2,3],[3,0],[0,5],[5,3],[2,5],[5,5],[4,1],[5,1]]
    
    boards=[board]
    list_regions = [regions]
    
    for i,sequence in enumerate(sequences):
        next_boards = []
        next_regions = []

        for board,regions in zip(boards,list_regions):    
            new_boards, new_regions = all_boards(board,regions, starts[i], targets[i], sequence)
            
            next_boards.extend(new_boards.copy())
            next_regions.extend(new_regions.copy())
        
        boards = next_boards.copy()
        list_regions = next_regions.copy()      
    
    return boards, list_regions


# ====================================================================================
# Step 5 : Filtering boards and placing the last tower

# The previous function returns 35 different boards going through all the pre-filled cells
# All these boards are missing a tower in the top right region (regions[1])
# The knight ended it's last turn (n=53) on the top righ cell with a score of 1100

# In this region, 2 cells are pre-filled, so there are only 3 cells where we can put a tower :
    # - [2,7] accessible through a direct "*" move and a final score of 54 * 1100 = 59400
    # - [0,6] and [1,7] accessible with "+*" or "++*" if [2,6] and/or [1,5] is unvisited

# We filter the 35 boards to find boards fitting on of these conditions
    
def board_filter(final_boards):
    boards1, boards2 = [],[]
    
    for board in final_boards:
        if board[2,7] == None: # boards with a direct move to a tower
            board[2,7] = 54*1100
            boards1.append(board)
        
        if (board[0,6] == None and board[1,7] == None) and (board[1,5] == None or board[2,6] == None): # boards with a move available and a place left for a tower
            # more code would be needed to finish these boards...
            boards2.append(board)
    
    return boards1, boards2

# There only 1 board of type 1 and no type 2 board,


# ====================================================================================
# Step 6 : Computing the score of visited cell adjacent to unvisited cells
# calculating the sum using a vectorized approach

def unvisited_sum(board):
    mask = (board == None).astype(int)
    board = np.pad(board,1)
    board = np.where(board == None, 0, board).astype(int)

    down = board[2:,1:-1] * mask
    up = board[0:-2,1:-1] * mask
    left = board[1:-1,0:-2] * mask
    right = board[1:-1,2:] * mask

    unvisited_sum = down+up+left+right
    unvisited_sum = np.sum(unvisited_sum)
    return unvisited_sum


# ====================================================================================
# Step 7 : Running the whole program

sequences = complete_sequence(targets)      # generate the sequences of scores and operations
sequences = sequence_height(sequences)      # complete with the hight of each sequence


final_boards, final_regions = chained_boards(sequences, board, regions)
boards1,boards2 = board_filter(final_boards)

result = unvisited_sum(boards1[0])
print(f"The result is : {result}")
