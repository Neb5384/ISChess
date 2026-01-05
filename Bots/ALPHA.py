
#
#   Example function to be implemented for
#       Single important function is next_best
#           color: a single character str indicating the color represented by this bot ('w' for white)
#           board: a 2d matrix containing strings as a descriptors of the board '' means empty location "XC" means a piece represented by X of the color C is present there
#           budget: time budget allowed for this turn, the function must return a pair (xs,ys) --> (xd,yd) to indicate a piece at xs, ys moving to xd, yd
#

#   Be careful with modules to import from the root (don't forget the Bots.)
from Bots.ChessBotList import register_chess_bot
import random
import time
#   Simply move the pawns forward and tries to capture as soon as possible
#TODO : 
# - PURGER CEUX QUI PUENT
# - MOVES DU DEBUT (BEST MOVES)
# - DEUXIEME NOTATION POUR LES CAS D'EGALITE (P.E : AVANCER PIECE = MIEUX, SI RIEN; RANDOM)
# - SELECTION D'UN BON MOVE SI PLUIS DE TEMPS
# - EVITER LES MOVES REPETITIFS
# - TROUVER BEST MOVE EN MEME TEMPS QUE LA CREATION DU GRAPHE ? OU TRIER MIEUX LA LSITE DES MOVES POUR AVOIR LES MEILLEURS EN PREMIER ?
# - TEST SUR PLUSIEURS BOARDS FIXES
# - CLASSIFICATION DE L'ELO
# - POWERPOINT

def chess_bot(player_sequence, board, time_bud, **kwargs):
    global start_time
    start_time = time.time()
    global TIME_MARGIN
    TIME_MARGIN = 0.2
    global time_budget
    time_budget = time_bud

    pieces = ['p', 'n', 'b', 'r', 'q', 'K']
    
    color = player_sequence[1]
    global base_color
    base_color = color
    global piece_values_abs
    piece_values_abs = {
        "p" : 1,
        "n" : 3,
        "b" : 3,
        "r" : 5,
        "q" : 9,
        "k" : 1000,
    }
    global piece_values
    piece_values = {
        "wp" : 1,
        "bp" : -1,
        "wn" : 3,
        "bn" : -3,
        "wb" : 3,
        "bb" : -3,
        "wr" : 5,
        "br" : -5,
        "wq" : 9,
        "bq" : -9,
        "wk" : 1000,
        "bk" : -1000
        }

    ev = evaluate(board,color,piece_values)
    print("evaluation : " + str(ev))

    head =  State(board,color, [],[(),()],0)
    states = [head]

    print(f"Time budget : {time_budget}") 

    color = player_sequence[1]


    depth = 3

    do_bfs(depth)

    print("appelmnigga")
    call_dfs_prune(head,depth)
    print("sortiedefonction")


    nextmove = calldfs(head)

    print(f"Dfs time : {time.time() - start_time}")
    return nextmove











class TimeOut(Exception):
    pass


class State:
    def __init__(self, board,color, children = None,move =[(),()], score=0):
        self.board = board
        self.children = children
        self.move = move
        self.color = color
        self.score = score

def do_bfs(depth):
    n = 0
    while n < depth:
        try:
        
            new_states = []
            for state in states:
                all_moves=[]
                board = state.board
                for x in range(board.shape[0]):
                    if time.time() - start_time > time_budget - TIME_MARGIN:
                            raise TimeOut()
                    for y in range(board.shape[1]):
                        if board[x,y] != "":
                            piece = board[x,y]

                            match piece[1]+piece[0]:
                                case p if p == color + 'p': 
                                    moves = movePawn(board, x, y, color,base_color)
                                case kn if kn == color + 'n':
                                    moves = moveKnight(board, x, y, color)
                                case b if b == color + 'b' :
                                    moves = moveBishop(board, x, y, color)
                                case r if r == color + 'r' :
                                    moves = moveRook(board, x, y, color)
                                case q if q == color + 'q' :
                                    moves = moveQueen(board, x, y, color)
                                case k if k == color + 'k' :
                                    moves = moveKing(board, x, y, color)
                                case _:
                                    continue

                            if len(moves) != 0:
                                for move in moves:
                                    all_moves.append([(x,y),move])
                #print(all_moves)
                for move in all_moves:
                    base_score = state.score
                    if state.board[move[1]] != '' and state.board[move[1]][1] != color:
                        score_diff = piece_values_abs[state.board[move[1]][0]]
                        #print(board_to_string(state.board))
                    else:
                        score_diff = 0
                    if piece[0] == "p" and (move[1][0] == 0 or move[1][0] == 7):
                        score -= (piece_values_abs["q"] - piece_values_abs["p"])

                    score = -base_score - score_diff

                    #print(move)
                    if n != depth:
                        new_board = simulate_move(board, move[0][0], move[0][1], move[1][0], move[1][1])
                        
                        #print(new_board)
                        new_state = State(new_board,swap(color), [],move,score)

                    else:
                        new_state = State(None,swap(color), [],move,score)

                    #print(board_to_string(new_state.board))
                    #print(f"NEW SCORE : {str(score)}")
                    state.children.append(new_state)
                    new_states.append(new_state)


        except TimeOut:
            print("TIMEOUT")
            break

            
        '''
        new_states.sort(key=lambda s: s.score, reverse=True)

        MAX_STATES = 100
        states = new_states[:MAX_STATES]
        '''
        states = new_states
        color = swap(color)
        n += 1

        print(f"depth : {n} - nbr of states : " + str(len(states)) + f"- time : {time.time() - start_time}")

    print("number of possibilities calculated: " + str(len(states)))


def call_dfs_prune(head,depth):
    print("WAITAMINIT")
    def dfs_prune(state,current_depth,depth):
        if current_depth == depth:
            print("ASDGASDGUASDGZGU")
            return state.score < 0
        elif (depth + current_depth) %2 == 1:
            should_prune = True
            for child in state.children:
                prune = dfs_prune(child,current_depth+1,depth)
                if not prune:
                    should_prune = False
            return should_prune
        else:
            should_prune = False
            new_children = []
            for child in state.children:
                prune = dfs_prune(child,current_depth+1,depth)
                if prune:
                    should_prune = True
                    print("pruned this mf")
                else: 
                    new_children.append(child)
            state.children = new_children
            return should_prune

    current_depth = 0
    dfs_prune(head,current_depth,depth)



def calldfs(head, maxdepth):
    def dfs(state,maxdepth):
        if maxdepth > 0:
            values = []
            for child in state.children:
                values.append(-dfs(child,maxdepth-1))

            #print(state[1], values)
            return max(values) 
        else:
            return state.score


    maxvalue = -10000

    for child in head.children:
        value = -dfs(child,maxdepth-1)
        #print(value, child.move)
        if value > maxvalue:
            maxvalue = value
            move = child.move
    #print(maxvalue, move)
    return move


def swap(color):
    if color == "b": return "w"
    else: return "b"
    
def evaluate(board,color,piece_values):
    score = 0
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if board[x,y] != "":
                piece = board[x,y]
                score += piece_values[piece[1] + piece[0]]
                #print(piece[0] + piece[1] + str(score))
    if color == 'b': score = -score 
    return score
    
def simulate_move(board, x, y, nx, ny):
    new_board = board.copy()

    piece = board[x,y]

    #print("simulating move on"+str(piece))
    new_board[x,y] = ""
    if piece[0] == "p" and (nx == 0 or nx == 7):
        new_board[nx,ny] = 'q' + piece[1]
    else:
        new_board[nx,ny] = piece

    return new_board


def board_to_string(board):
    """Return a human-readable string representation of the board.

    Empty squares are shown as '.', pieces as '<type><color>' (e.g. 'pw' pawn white).
    Rows are joined with newlines, columns separated by spaces.
    """
    lines = []
    try:
        rows, cols = board.shape[0], board.shape[1]
    except Exception:
        return str(board)

    for x in range(rows):
        row = []
        for y in range(cols):
            cell = board[x, y]
            if cell == "" or cell is None:
                row.append('.')
            else:
                # piece has attributes [0] and [1]
                row.append(f"{cell[0]}{cell[1]}")
        lines.append(' '.join(row))
    return '\n'.join(lines)

#PIECE VALID MOVEMENT 
def movePawn(board, x, y, color, base_color):
    if color == base_color:
        dir = 1
    else:
        dir = -1
    moveList = []

    if board[x+dir,y] == "":
        moveList.append((x+dir, y))
    if y+1 <= 7 and (board[x+dir,y+1] != "" and board[x+dir,y+1][1] != color):
        moveList.append((x+dir, y+1))
    if y-1 >= 0 and (board[x+dir,y-1] != "" and board[x+dir,y-1][1] != color):
        moveList.append((x+dir, y-1))
    return moveList

def moveKnight(board, x, y, color):
    moveList = []
    moves = [(2,1),(-2,1),(2,-1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
    for move in moves: 
        if 7 >= x + move[0] >= 0 and 7 >= y + move[1] >= 0 :
            nextPlace = board[x + move[0],y + move[1]] #CHANGED PIECE LOGIC, BENNO YOU WERENT CHECKInG LE BON MON REUF -> NOW NEXTPLACE = MOVE DESTINATION
            if nextPlace == "" or nextPlace[1] != color:
                moveList.append((move[0]+x,move[1]+y))
    return moveList

def moveKing(board, x, y, color):
    moveList = []
    moves = [(0,1),(0,-1),(-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1)]
    for move in moves:
        if 7 >= x + move[0] >= 0 and 7 >= y + move[1] >= 0 :
            nextPlace = board[x + move[0],y + move[1]]
            if nextPlace == "" or nextPlace[1] != color:
                moveList.append((move[0] + x, move[1] + y))
    return moveList

def moveRook(board, x, y, color):
    moveList = []
    directions = [(1,0), (-1,0), (0,1), (0,-1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        while 0 <= nx <= 7 and 0 <= ny <= 7:
            if board[nx, ny] == "":
                moveList.append((nx, ny))
            elif board[nx, ny][1] != color:
                moveList.append((nx, ny))
                break
            else:  #same color piece blocking the way
                break

            nx += dx
            ny += dy
            #print("Rook move added : " + str((nx, ny)))
    return moveList

def moveBishop(board, x, y, color):
    moveList = []
    #TODO : HAS TO BE DONE AGAIN - NOT TAKING ALL POSSIBILITIES
    
    directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        while 0 <= nx <= 7 and 0 <= ny <= 7:
            if board[nx, ny] == "":
                moveList.append((nx, ny))
            elif board[nx, ny][1] != color:
                moveList.append((nx, ny))
                break
            else:  #same color piece blocking the way
                break
            nx += dx
            ny += dy
            #print("Bishop move added : " + str((nx, ny)))

    return moveList

def moveQueen(board,x,y,color):
    moveList = []
    moveList += moveRook(board,x,y,color)
    moveList += moveBishop(board,x,y,color)
    return moveList



register_chess_bot("ALPHA", chess_bot)