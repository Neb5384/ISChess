
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
#   Simply move the pawns forward and tries to capture as soon as possible
def chess_bot(player_sequence, board, time_budget, **kwargs):
    pieces = ['p', 'n', 'b', 'r', 'q', 'K']
    

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
        "wk" : 1000,
        "bk" : -1000
        }

    ev = evaluate(board,color,piece_values)
    print("evaluation : " + str(ev))

    head =  State(board,color, [],[(),()])
    states = [head]
    n = 0

    while n<2:
        new_states = []
        n += 1
        for state in states:
            all_moves=[]
            board = state.board
            for x in range(board.shape[0]):
                for y in range(board.shape[1]):
                    if board[x,y] != "":
                        piece = board[x,y]
                        #TODO : CAN WE MAKE IT IN SWTICH CASE ? PYTHON IS BAD FOR CONCATENATION + SWITCH CASe
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
                        elif piece.color + piece.type == color + 'k' :
                            moves = moveKing(board, x, y, color)
                        else:
                            continue
                        if len(moves) != 0:
                            for move in moves:
                                all_moves.append([(x,y),move])

            #print(all_moves)
            for move in all_moves:
                #print(move)
                new_board = simulate_move(board, move[0][0], move[0][1], move[1][0], move[1][1])
                #print(new_board)
                new_state = State(new_board,swap(color), [],move)
                state.children.append(new_state)
                new_states.append(new_state)
        states = new_states
        color = swap(color)
    print("number of possibilities calculated: " + str(len(states)))

    color = player_sequence[1]
    nextmove = calldfs(head, piece_values)
    return nextmove


class State:
    def __init__(self, board,color, children = [],move =[(),()]):
        self.board = board
        self.children = children
        self.move = move
        self.color = color



def calldfs(head,piece_values):
    def dfs(state):

        if len(state.children) == 0:
            return evaluate(state.board,state.color,piece_values)
    
        values = []
        for child in state.children:
            values.append(-dfs(child))

        print(state.color,values)
        return max(values)

    maxvalue = -10000
    for child in head.children:
        value = -dfs(child)
        print(value,child.move)
        if value > maxvalue:
            maxvalue = value
            move = child.move
    print(maxvalue,move)
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
                score += piece_values[piece.color + piece.type]
                #print(piece.type + piece.color + str(score))
    if color == 'b': score = -score 
    return score
    
def simulate_move(board, x, y, nx, ny):
    new_board = board.copy()

    piece = board[x,y]
    #print("simulating move on"+str(piece))
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
    moves = [(0,1),(0,-1),(-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1)]
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
            elif board[nx, ny].color != color:
                moveList.append((nx, ny))
                break
            else:  #same color piece blocking the way
                break
            nx += dx
            ny += dy
            #print("Bishop move added : " + str((nx, ny)))
    """
    for i in range(1, 7):
        if x + i <= 7 and y + i <= 7:
            if board[x + i, y + i] == "" or board[x + i, y + i].color != color:
                moveList.append((x + i, y + i))
    """
    return moveList

def moveQueen(board,x,y,color):
    moveList = []
    moveList += moveRook(board,x,y,color)
    moveList += moveBishop(board,x,y,color)
    return moveList



register_chess_bot("A.L.P.H.A", chess_bot)
