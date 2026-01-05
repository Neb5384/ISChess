#!/usr/bin/env python3
import sys
import os
import argparse
import numpy as np
import chess

import pkgutil
import importlib
# IMPORTANT: Import bot registry (functions)
from Bots.ChessBotList import CHESS_BOT_LIST

def load_all_bots():
    # Import every module in Bots/ so their register_chess_bot() runs
    import Bots  # package
    for _, module_name, _ in pkgutil.iter_modules(Bots.__path__):
        importlib.import_module(f"Bots.{module_name}")

load_all_bots()


# =========================
# UCI helpers
# =========================
def send(msg: str):
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


# =========================
# Board conversion
# Your engine expects:
# - board[x, y] with x forward (+1)
# - pieces like "pw", "kb", ""
# - side-to-move always plays "up"
# =========================
PIECE_MAP = {
    chess.PAWN: "p",
    chess.ROOK: "r",
    chess.KNIGHT: "n",
    chess.BISHOP: "b",
    chess.QUEEN: "q",
    chess.KING: "k",
}

def chess_to_ischess(board: chess.Board) -> np.ndarray:
    arr = np.full((8, 8), "", dtype=object)
    white_to_move = board.turn == chess.WHITE

    for sq, piece in board.piece_map().items():
        file_ = chess.square_file(sq)
        rank_ = chess.square_rank(sq)

        # rotate so side-to-move always plays "up"
        if white_to_move:
            x, y = rank_, file_
        else:
            x, y = 7 - rank_, 7 - file_

        color = "w" if piece.color == chess.WHITE else "b"
        arr[x, y] = PIECE_MAP[piece.piece_type] + color

    return arr


def ischess_move_to_uci(board: chess.Board, move_xy):
    (xs, ys), (xd, yd) = move_xy
    white_to_move = board.turn == chess.WHITE

    if white_to_move:
        fs, fr = ys, xs
        ts, tr = yd, xd
    else:
        fs, fr = 7 - ys, 7 - xs
        ts, tr = 7 - yd, 7 - xd

    from_sq = chess.square(fs, fr)
    to_sq = chess.square(ts, tr)

    # promotion handling (default queen)
    promotion = None
    piece = board.piece_at(from_sq)
    if piece and piece.piece_type == chess.PAWN:
        if (piece.color == chess.WHITE and tr == 7) or (piece.color == chess.BLACK and tr == 0):
            promotion = chess.QUEEN

    return chess.Move(from_sq, to_sq, promotion=promotion)


# =========================
# Time handling
# =========================
def get_movetime_ms(parts, board):
    if "movetime" in parts:
        return max(50, int(parts[parts.index("movetime") + 1]))

    if board.turn == chess.WHITE and "wtime" in parts:
        t = int(parts[parts.index("wtime") + 1])
        inc = int(parts[parts.index("winc") + 1]) if "winc" in parts else 0
    elif board.turn == chess.BLACK and "btime" in parts:
        t = int(parts[parts.index("btime") + 1])
        inc = int(parts[parts.index("binc") + 1]) if "binc" in parts else 0
    else:
        return 500

    # simple heuristic: allocate a fraction of remaining time + some increment
    return max(50, min(2000, t // 35 + inc // 2))


# =========================
# Bot selection
# =========================
def pick_bot(bot_name: str):
    if not bot_name:
        raise RuntimeError("No bot specified. Use --bot <name> or set ISCHESS_BOT.")

    if bot_name not in CHESS_BOT_LIST:
        available = ", ".join(sorted(CHESS_BOT_LIST.keys()))
        send(f"info string ERROR: Bot '{bot_name}' not found.")
        send(f"info string Available bots: {available}")
        raise RuntimeError(f"Bot '{bot_name}' not registered.")

    return bot_name, CHESS_BOT_LIST[bot_name]


# =========================
# UCI loop
# =========================
def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--bot", type=str, default=None)
    args, _ = parser.parse_known_args()

    desired_bot = args.bot or os.environ.get("ISCHESS_BOT")
    bot_name, bot_fn = pick_bot(desired_bot)

    board = chess.Board()

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        line = line.strip()

        if line == "uci":
            send(f"id name ISChess ({bot_name})")
            send("id author ISChess")
            send("uciok")

        elif line == "isready":
            send("readyok")

        elif line == "ucinewgame":
            board.reset()

        elif line.startswith("position"):
            parts = line.split()
            i = 1

            if i < len(parts) and parts[i] == "startpos":
                board = chess.Board()
                i += 1
            elif i < len(parts) and parts[i] == "fen":
                fen = " ".join(parts[i + 1:i + 7])
                board = chess.Board(fen)
                i += 7

            if i < len(parts) and parts[i] == "moves":
                for u in parts[i + 1:]:
                    mv = chess.Move.from_uci(u)
                    if mv in board.legal_moves:
                        board.push(mv)

        elif line.startswith("go"):
            parts = line.split()
            movetime_ms = get_movetime_ms(parts, board)

            ischess_board = chess_to_ischess(board)
            color = "w" if board.turn == chess.WHITE else "b"
            player_sequence = f"0{color}0"

            move_xy = bot_fn(player_sequence, ischess_board, movetime_ms / 1000.0)

            mv = ischess_move_to_uci(board, move_xy)
            if mv not in board.legal_moves:
                mv = next(iter(board.legal_moves))

            send(f"bestmove {mv.uci()}")

        elif line == "quit":
            break


if __name__ == "__main__":
    main()
