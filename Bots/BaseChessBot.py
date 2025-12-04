
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
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if board[x,y] != "":
                piece = board[x,y]
                if piece.color + piece.type == color + 'p' :
                    print("Call move Pawn")
                    all_moves.append(((x,y),(movePawn(board, x, y).copy())))
                    print("All pawn moves" + str(all_moves))
    return (0,0), (0,0)
    

    
#   Example how to register the function

def movePawn(board, x, y):
    moveList = []
    if board[x+1,y] == "":
        moveList.append((x+1, y))
    if y+1 <= 7 and (board[x+1,y+1] != "" and board[x+1,y+1].color != color):
        moveList.append((x+1, y+1))
    if y-1 >= 0 and (board[x+1,y-1] != "" and board[x+1,y-1].color != color):
        moveList.append((x+1, y-1))
    return moveList


register_chess_bot("A.L.P.H.A", chess_bot)
