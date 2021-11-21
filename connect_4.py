from collections import Counter
import numpy as np

NUM_COLUMNS = 7
COLUMN_HEIGHT = 6
FOUR = 4

moves_cache = dict()

infinity = 10000000

# Gaussian weight distribution
eval_table = np.array([[3,4,5,5,4,3],
                       [4,6,8,8,6,4],
                       [5,8,11,11,8,5],
                       [7,10,13,13,10,7],
                       [5,8,11,11,8,5],
                       [4,6,8,8,6,4],
                       [3,4,5,5,4,3]])
# Board can be initiatilized with `board = np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype=np.byte)`
# Notez Bien: Connect 4 "columns" are actually NumPy "rows"


def valid_moves(board):
    """Returns columns where a disc may be played"""
    return [n for n in range(NUM_COLUMNS) if board[n, COLUMN_HEIGHT - 1] == 0]


def play(board, column, player):
    """Updates `board` as `player` drops a disc in `column`"""
    (index,) = next((i for i, v in np.ndenumerate(board[column]) if v == 0))
    board[column, index] = player


def take_back(board, column):
    """Updates `board` removing top disc from `column`"""
    if len([i for i, v in np.ndenumerate(board[column]) if v != 0]) is 0:
        return False

    (index,) = [i for i, v in np.ndenumerate(board[column]) if v != 0][-1]
    board[column, index] = 0

    return True


def four_in_a_row(board, player):
    """Checks if `player` has a 4-piece line"""
    return (
        any(
            all(board[c, r] == player)
            for c in range(NUM_COLUMNS)
            for r in (list(range(n, n + FOUR)) for n in range(COLUMN_HEIGHT - FOUR + 1))
        )
        or any(
            all(board[c, r] == player)
            for r in range(COLUMN_HEIGHT)
            for c in (list(range(n, n + FOUR)) for n in range(NUM_COLUMNS - FOUR + 1))
        )
        or any(
            np.all(board[diag] == player)
            for diag in (
                (range(ro, ro + FOUR), range(co, co + FOUR))
                for ro in range(0, NUM_COLUMNS - FOUR + 1)
                for co in range(0, COLUMN_HEIGHT - FOUR + 1)
            )
        )
        or any(
            np.all(board[diag] == player)
            for diag in (
                (range(ro, ro + FOUR), range(co + FOUR - 1, co - 1, -1))
                for ro in range(0, NUM_COLUMNS - FOUR + 1)
                for co in range(0, COLUMN_HEIGHT - FOUR + 1)
            )
        )
    )

def _mc(board, player):
    p = -player
    while valid_moves(board):
        p = -p
        c = np.random.choice(valid_moves(board))
        play(board, c, p)
        if four_in_a_row(board, p):
            return p
    return 0


def montecarlo(board, player):
    montecarlo_samples = 100
    cnt = Counter(_mc(np.copy(board), player) for _ in range(montecarlo_samples))
    return (cnt[1] - cnt[-1]) / montecarlo_samples


def eval_board(board, player):
    if four_in_a_row(board, 1):
        # Alice won
        return 1
    elif four_in_a_row(board, -1):
        # Bob won
        return -1
    else:
        # Not terminal, let's simulate...
        return montecarlo(board, player)


def there_is_a_winner(board):
    global infinity
    
    if four_in_a_row(board, 1):
        # Alice won
        return infinity
    elif four_in_a_row(board, -1):
        # Bob won
        return -infinity
    else:
        return False

def my_eval_board(board):
    # Very local evaluation
    # Not so smart in general

    global eval_table
    global infinity

    if four_in_a_row(board, 1):
        # Alice won
        return infinity
    elif four_in_a_row(board, -1):
        # Bob won
        return -infinity
    else:
        return eval_table[board==1].sum() - eval_table[board==-1].sum()

def show(board):
    print(np.rot90(board))
        
def MSCT(board):
    pass

def is_playable(board, col, player):
    return not len([i for i, v in np.ndenumerate(board[col]) if v == 0]) is 0
        

def is_winning_move(board, col, player):
    play(board, col, player)
    res = four_in_a_row(board, player)
    take_back(board, col)

    return res

def negamax(player, board, alpha, beta, max_step, step, max_play, moves_from_beginning, column_order, position:list=None):
    global moves_cache

    if moves_from_beginning == NUM_COLUMNS * COLUMN_HEIGHT:
        return 0

    for c in range(max_play):
        i = column_order[c]
        if is_playable(board, i, player) and is_winning_move(board, i, player):
            return (NUM_COLUMNS * COLUMN_HEIGHT + 1 - moves_from_beginning)//2

    max_res = (NUM_COLUMNS * COLUMN_HEIGHT - 1 - moves_from_beginning)//2
    if step == 0: games = dict()
    if not position and str(position) in moves_cache:
        max_res = moves_cache[str(position)] +  (-(NUM_COLUMNS*COLUMN_HEIGHT)//2 + 3) - 1

    if beta > max_res:
        beta = max_res
        if alpha >= beta:
            return beta

    for c in range(max_play):
        i = column_order[c]
        if is_playable(board, i, player) and step+1!=max_step:
            play(board, i, player)
            position.append(i)
            res = -negamax(-player,board, -beta, -alpha, max_step, step+1, max_play, moves_from_beginning, column_order, position)
            take_back(board, i)
            position.pop()

            if step == 0: games[res] = i

            if res >= beta:
                if step == 0:
                    play(board, games[res], player)
                    return (max_res, games[res])
                else:
                    return res

            if res > alpha: alpha = res

    moves_cache[str(position)] = alpha - (-(NUM_COLUMNS*COLUMN_HEIGHT)//2 + 3) + 1

    if step == 0 and is_playable(board, games[alpha], player):
        play(board, games[alpha], player)
        position.append(i)
        return (alpha, games[alpha])
    
    return alpha

def minmax(player, board, alpha, beta, max_step, step, max_play, column_order):
    # TREE POST-ORDER TRAVERSAL
    # player_maxer = 1
    # player_minimer = -1

    global infinity
    # Game concluded before arriving to the max depth
    eval = there_is_a_winner(board)
    if eval != False: 
        return eval

    # Exit condition
    if step == max_step:
        return my_eval_board(board)

    if step == 0: games = dict() 

    if player == 1:
        max_res = -infinity

        # 7 possible plays per node
        for c in range(max_play):
            i = column_order[c]
            if is_playable(board, i, player):
                play(board, i, player)
                res = minmax(-player, board, alpha, beta, max_step, step+1, max_play, column_order)
                if step == 0:
                    games[res] = i
                
                max_res = max(max_res, res)

                take_back(board, i)
                
                alpha = max(alpha, res)
                if beta <= alpha:
                    break

        if step == 0:
            play(board, games[max_res], player)
            return (max_res, games[max_res])
        else:
            return max_res
    
    else:
        min_res = infinity
        for c in range(max_play):
            i = column_order[c]
            if is_playable(board, i, player):
                play(board, i, player)
                res = minmax(-player, board, alpha, beta, max_step, step+1, max_play, column_order)
                if step == 0:
                    games[res] = i
                
                min_res = min(min_res, res)

                take_back(board, i)

                beta = min(beta, res)
                if beta <= alpha:
                    break
        
        if step == 0:
            play(board, games[min_res], player)
            return (min_res, games[min_res])
        else:
            return min_res



from random import randint, seed 
from time import time

# MATCH SETTINGS
seed(time())
computer_moves_ahead = 8 # Depth
board = np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype=np.byte)
turn_counter = 0
eval = False
chosen_col = -1
column_order = list()
position_key = list()
player = -1#randint(-1, 1)

for i in range(NUM_COLUMNS):
    column_order.append(NUM_COLUMNS//2 + (1 - 2 * (i%2)) * (i+1)//2)

print("\nConnect 4 game:\tCOMPUTER VS HUMAN")
print("\t\t\tFIGHT")

print("Human player start") if player is 1 else print("Computer start")

while not eval:
    print(f"\nTurn number {turn_counter}")
    
    show(board)

    if player==1:
        print("HUMAN")
        while chosen_col < 0 or chosen_col > NUM_COLUMNS-1:
            print("Chose a column between 1 and 7:")
            chosen_col = int(input()) - 1
            if is_playable(board, chosen_col, player):
                play(board, chosen_col, player)
                position_key.append(chosen_col)
            else:
                print("This column is already full\nReinsert a column")
                chosen_col = -1

    else:
        print("COMPUTER")
        #evaluation, games = negamax(player, board, -1, 1, computer_moves_ahead, 0, NUM_COLUMNS, turn_counter, column_order, position_key)
        evaluation, games = minmax(player, board, -infinity, infinity, computer_moves_ahead, 0, NUM_COLUMNS, column_order)
        print(f"Evaluation of the plays: {evaluation} points\nNext move: Column {games+1}")

    eval = there_is_a_winner(board)

    # Switch player
    player = -player

    turn_counter += 1
    chosen_col = -1

show(board)

if eval == infinity:
    print("\n\t\tHUMAN WINS")
else:
    print("\n\t\tCOMPUTER WINS\n\t\tPC MASTER RACE!!!!")
