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
import math
#   Simply move the pawns forward and tries to capture as soon as possible
#TODO : 
# - MOVES DU DEBUT (BEST MOVES)
# - EVITER LES MOVES REPETITIFS
# - TRANSPOSITION TABLE -> GARDER EN CACHE LES COUPS ET LEUR EVALUATION
# - TEST SUR PLUSIEURS BOARDS FIXES
# - CLASSIFICATION DE L'ELO
# - POWERPOINT

pieces = ['p', 'n', 'b', 'r', 'q', 'K']


piece_values_abs = {
    "p" : 1,
    "n" : 3,
    "b" : 3,
    "r" : 5,
    "q" : 9,
    "k" : 1000,
}

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

def chess_bot(player_sequence, board, time_bud, **kwargs):


    print("ALPHA_V4-BASE =====")
    start_time = time.time()
    global time_margin
    time_margin = 0.15
    depth = 10
    max_depth = depth
    time_budget = time_bud

    global color
    color = player_sequence[1]
    base_color = color

    color = player_sequence[1]

    base_color = color
    best_move = None

    try:
        for depth in range(1, max_depth + 1):
            _, best_move = negamax(
                board,
                depth,
                depth,
                -math.inf,
                math.inf,
                color,
                base_color,
                start_time,
                time_bud,
                current_eval=0
            )
                
            print(f"Total time : {time.time() - start_time}, depth : {depth}")
            print(best_move)
    except TimeOut:
        pass


    return best_move

class TimeOut(Exception):
    pass

def negamax(board, depth, max_depth, alpha, beta, color, base_color, start_time, time_budget, current_eval):
    if time.time() - start_time > time_budget - time_margin:
        print("TIMEOUT")
        raise TimeOut()

    
    alpha_orig = alpha
    

    if depth == 0:
        return current_eval, None

    best_score = -math.inf
    best_move = None
    moves = generate_moves(board, color, base_color)

    #move ordering 
    def move_score(move):
        src, dst = move
        piece = board[src]
        score = 0

        if board[dst] != "":
            captured = board[dst][0]

            score = piece_values_abs[captured]
        #promotion
        if piece[0] == "p" and (dst[0] == 0 or dst[0] == 7):
            score += piece_values_abs["q"] - piece_values_abs["p"]

        
        return score
    
    def is_kingcapture(move):
        src, dst = move
        if board[dst] != "":
            captured = board[dst][0]
            kingcapture = (captured == "k")
        else:
            kingcapture = False
        return kingcapture
    

    moves.sort(key=move_score, reverse=True)

    for move in moves:
        move_eval = move_score(move)
        kingcapture = is_kingcapture(move)
        next_eval = -current_eval - move_eval
        if kingcapture:
            score = 1000
        else:
            new_board = simulate_move(board, *move[0], *move[1])
            score,_ = negamax(
                new_board,
                depth - 1,
                max_depth,
                -beta,
                -alpha,
                swap(color),
                base_color,
                start_time,
                time_budget,
                next_eval
            )
            score = -score

        if score > best_score:
            best_score = score
            if depth == max_depth:
                best_move = move


        alpha = max(alpha, score)
        if alpha > beta:
            break
        if alpha == beta:
            break
    

    return best_score, best_move


def best_centimove(board,moveList,base_color):
    return moveList[0] 

def generate_moves(board, color, base_color):
    moves = []
    for x in range(8):
        for y in range(8):
            if board[x, y] == "":
                continue
            piece = board[x, y]
            if piece[1] != color:
                continue

            match piece[0]:
                case "p":
                    dests = movePawn(board, x, y, color, base_color)
                case "n":
                    dests = moveKnight(board, x, y, color)
                case "b":
                    dests = moveBishop(board, x, y, color)
                case "r":
                    dests = moveRook(board, x, y, color)
                case "q":
                    dests = moveQueen(board, x, y, color)
                case "k":
                    dests = moveKing(board, x, y, color)
                case _:
                    dests = []

            for d in dests:
                moves.append(((x, y), d))
    return moves


def evaluate(board, color):
    score = 0
    for x in range(8):
        for y in range(8):
            if board[x, y] != "":
                p = board[x, y]
                score += piece_values[p[1] + p[0]]
    return score if color == "w" else -score


def swap(color):
    return "b" if color == "w" else "w"


def simulate_move(board, x, y, nx, ny):
    new_board = board.copy()
    piece = board[x, y]
    new_board[x, y] = ""
    if piece[0] == "p" and (nx == 0 or nx == 7):
        new_board[nx, ny] = "q" + piece[1]
    else:
        new_board[nx, ny] = piece
    return new_board

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



register_chess_bot("ALPHA_V4-Base", chess_bot)