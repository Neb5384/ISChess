
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
#TODO : PURGER CEUX QUI PUENT
INF = 10_000
nodes = 0

TT = {}
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


piece_values_abs = {
    "p": 1,
    "n": 3,
    "b": 3,
    "r": 5,
    "q": 9,
    "k": 1000
}

TIME_MARGIN = 0.05  # 50 ms de sécurité

class TimeOut(Exception):
    pass

def board_hash(board):
    return tuple(board.flatten())

def ordered_moves(board, x, y, color, base_color):
    piece = board[x, y][0]
    moves = []

    if piece == 'p':
        raw_moves = movePawn(board, x, y, color, base_color)
    elif piece == 'n':
        raw_moves = moveKnight(board, x, y, color)
    elif piece == 'b':
        raw_moves = moveBishop(board, x, y, color)
    elif piece == 'r':
        raw_moves = moveRook(board, x, y, color)
    elif piece == 'q':
        raw_moves = moveQueen(board, x, y, color)
    elif piece == 'k':
        raw_moves = moveKing(board, x, y, color)
    else:
        return []

    for (nx, ny) in raw_moves:
        score = 0
        target = board[nx, ny]

        # captures prioritaires
        if target != "":
            score += piece_values_abs[target[0]] * 10

        # promotion prioritaire
        if piece == 'p' and (nx == 0 or nx == 7):
            score += 20

        moves.append(((nx, ny), score))

    moves.sort(key=lambda m: -m[1])
    return [m[0] for m in moves]


def minimax(board, color, depth, alpha, beta, maximizing,
            base_color, piece_values, start_time, time_budget):
    global nodes

    if time.time() - start_time > time_budget - TIME_MARGIN:
        raise TimeOut()

    key = board_hash(board)

    if key in TT:
        entry = TT[key]
        if entry["depth"] >= depth:
            if entry["flag"] == EXACT:
                return entry["value"]
            elif entry["flag"] == LOWERBOUND:
                alpha = max(alpha, entry["value"])
            elif entry["flag"] == UPPERBOUND:
                beta = min(beta, entry["value"])
            if alpha >= beta:
                return entry["value"]

    nodes += 1

    if depth == 0:
        value = evaluate(board, base_color, piece_values)
    else:
        value = -INF if maximizing else INF

        for x in range(board.shape[0]):
            for y in range(board.shape[1]):
                if board[x, y] == "" or board[x, y][1] != color:
                    continue

                for (nx, ny) in ordered_moves(board, x, y, color, base_color):
                    new_board, _ = simulate_move(board, x, y, nx, ny)

                    score = minimax(
                        new_board,
                        swap(color),
                        depth - 1,
                        alpha,
                        beta,
                        not maximizing,
                        base_color,
                        piece_values,
                        start_time,
                        time_budget
                    )

                    if maximizing:
                        value = max(value, score)
                        alpha = max(alpha, value)
                        if beta <= alpha:
                            break
                    else:
                        value = min(value, score)
                        beta = min(beta, value)
                        if beta <= alpha:
                            break

    flag = EXACT
    if value <= alpha:
        flag = UPPERBOUND
    elif value >= beta:
        flag = LOWERBOUND

    TT[key] = {
        "value": value,
        "depth": depth,
        "flag": flag
    }

    return value



def choose_best_move(board, color, time_budget, piece_values):
    start_time = time.time()
    best_move = None
    depth = 1

    while True:
        try:
            best_value = -INF
            current_best = None

            for x in range(board.shape[0]):
                for y in range(board.shape[1]):
                    if board[x, y] == "" or board[x, y][1] != color:
                        continue

                    for (nx, ny) in ordered_moves(board, x, y, color, color):
                        new_board, _ = simulate_move(board, x, y, nx, ny)

                        value = minimax(
                            new_board,
                            swap(color),
                            depth - 1,
                            -INF,
                            INF,
                            False,
                            color,
                            piece_values,
                            start_time,
                            time_budget
                        )

                        if value > best_value:
                            best_value = value
                            current_best = ((x, y), (nx, ny))

            best_move = current_best
            depth += 1

        except TimeOut:
            break

    elapsed = time.time() - start_time
    nps = nodes / elapsed if elapsed > 0 else 0

    print("===== SEARCH STATS =====")
    print(f"Depth          : {depth}")
    print(f"Nodes searched : {nodes}")
    print(f"Time (s)       : {elapsed:.4f}")
    print(f"Nodes / second : {nps:,.0f}")
    print("========================")

    return best_move

def chess_bot(player_sequence, board, time_budget, **kwargs):
    color = player_sequence[1]

    piece_values = {
        "wp": 1, "bp": -1,
        "wn": 3, "bn": -3,
        "wb": 3, "bb": -3,
        "wr": 5, "br": -5,
        "wq": 9, "bq": -9,
        "wk": 1000, "bk": -1000
    }

    return choose_best_move(board, color, time_budget, piece_values)



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
        promotion = True
    else:
        new_board[nx,ny] = piece
        promotion = False

    return new_board, promotion


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



register_chess_bot("alphaTest", chess_bot)