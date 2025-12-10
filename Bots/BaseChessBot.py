
#
#   Example function to be implemented for
#       Single important function is next_best
#           color: a single character str indicating the color represented by this bot ('w' for white)
#           board: a 2d matrix containing strings as a descriptors of the board '' means empty location "XC" means a piece represented by X of the color C is present there
#           budget: time budget allowed for this turn, the function must return a pair (xs,ys) --> (xd,yd) to indicate a piece at xs, ys moving to xd, yd
#

#   Be careful with modules to import from the root (don't forget the Bots.)
from Bots.ChessBotList import register_chess_bot

#   Simply move the pawns forward and tries to capture as soon as possible
def chess_bot(player_sequence, board, time_budget, **kwargs):
    pieces = ['p', 'n', 'b', 'r', 'q', 'K']
    
    all_moves=[]

    color = player_sequence[1]
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
        "wk" : 0,
        "bk" : 0
        }
    ev = evaluate(board,color,piece_values)
    print("evaluation : " + str(ev))

    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if board[x,y] != "":
                piece = board[x,y]
                #TODO : CAN WE MAKE IT IN SWTICH CASE ? PYTHON IS BAD FOR CONCATENATION + SWITCH CASe
                #CHANGES : ADDED EVALUATION IN ALL THE POSSIBLE MOVES -> EASIER TO DO GREED DEPTH SEARCH AFTER
                if piece.color + piece.type == color + 'p' :
                    moves = movePawn(board, x, y, color)
                elif piece.color + piece.type == color + 'n' :
                    moves = moveKnight(board, x, y, color)
                elif piece.color + piece.type == color + 'b' :
                    moves = moveBishop(board, x, y, color)
                elif piece.color + piece.type == color + 'r' :
                    moves = moveRook(board, x, y, color)
                elif piece.color + piece.type == color + 'q' :
                    moves = moveQueen(board, x, y, color)
                elif piece.color + piece.type == color + 'K' :
                    moves = moveKing(board, x, y, color)
                else:
                    continue

                try:
                    for move in moves:
                        new_board = simulate_move(board, x, y, move[0], move[1])
                        new_ev = evaluate(new_board, color, piece_values)
                        all_moves.append(((x,y),moves, new_ev))
                except:
                    continue
                

    print("All moves : " + str(all_moves))
    return (0,0), (0,0)

    #CREATE ALL POSSIBLE MOVES
    

def evaluate(board,color,piece_values):
    score = 0
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if board[x,y] != "":
                piece = board[x,y]
                score += piece_values[piece.color + piece.type]
                #print(piece.type + piece.color + str(score))
    if color == 'b': score = -score 
    return score
    
def simulate_move(board, x, y, nx, ny):
    new_board = board.copy()

    piece = new_board[x,y]
    new_board[x,y] = ""
    new_board[nx,ny] = piece

    return new_board

#PIECE VALID MOVEMENT 
def movePawn(board, x, y, color):
    moveList = []
    if board[x+1,y] == "":
        moveList.append((x+1, y))
    if y+1 <= 7 and (board[x+1,y+1] != "" and board[x+1,y+1].color != color):
        moveList.append((x+1, y+1))
    if y-1 >= 0 and (board[x+1,y-1] != "" and board[x+1,y-1].color != color):
        moveList.append((x+1, y-1))
    return moveList

def moveKnight(board, x, y, color):
    moveList = []
    moves = [(2,1),(-2,1),(2,-1),(-2,1),(1,2),(-1,2),(1,-2),(-1,-2)]
    for move in moves: 
        if 7 >= x + move[0] >= 0 and 7 >= y + move[1] >= 0 :
            nextPlace = board[x + move[0],y + move[1]] #CHANGED PIECE LOGIC, BENNO YOU WERENT CHECKInG LE BON MON REUF -> NOW NEXTPLACE = MOVE DESTINATION
            if nextPlace == "" or nextPlace.color != color:
                moveList.append((move[0]+x,move[1]+y))
    return moveList

def moveKing(board, x, y, color):
    moveList = []
    moves = [(0,1),(0,-1),(-1,-1),(-1,0),(-1,1),(1,-1),(1,0)(1,1)]
    for move in moves:
        if 7 >= x + move[0] >= 0 and 7 >= y + move[1] >= 0 :
            nextPlace = board[x + move[0],y + move[1]]
            if nextPlace == "" or nextPlace.color != color:
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
            elif board[nx, ny].color != color:
                moveList.append((nx, ny))
                break
            else:  #same color piece blocking the way
                break
            nx += dx
            ny += dy
    return moveList

def moveBishop(board, x, y, color):
    moveList = []
    directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        while 0 <= nx <= 7 and 0 <= ny <= 7:
            if board[nx, ny] == "":
                moveList.append((nx, ny))
            elif board[nx, ny].color != color:
                moveList.append((nx, ny))
                break
            else:  #same color piece blocking the way
                break
            nx += dx
            ny += dy
    return moveList

def moveQueen(board,x,y,color):
    moveList = []
    moveList.append(moveRook(board,x,y,color))
    moveList.append(moveBishop(board,x,y,color))
    return moveList


register_chess_bot("A.L.P.H.A", chess_bot)
