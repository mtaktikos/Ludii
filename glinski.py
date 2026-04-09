#!/usr/bin/env python3
"""
Glinski Chess coordinate converter between Ludii and Zillions of Games.

Coordinate systems
------------------
Both engines use files a-k (a=1 … k=11) and ranks 1-11, but the axes are
oriented differently on the hexagonal board.

Mapping formulas (1-indexed file numbers):
  Zillions (zf, zr)  →  Ludii (lf, lr):
      lf = zr
      lr = zr - zf + 6

  Ludii (lf, lr)  →  Zillions (zf, zr):
      zr = lf
      zf = lf - lr + 6

Verified against all 36 starting-position piece placements in
Glinski Chess.lud and Glinski-HexChess.zrf.

Move notation
-------------
Both systems use pure coordinate notation: <from><to>, e.g. "a3d4" or "d1f4".
Each square is one letter (a-k) followed by 1-2 digits (1-11).
"""

import re
import sys


# ── coordinate helpers ────────────────────────────────────────────────────────

def _file_num(letter: str) -> int:
    """'a' → 1, 'b' → 2, …, 'k' → 11."""
    return ord(letter.lower()) - ord('a') + 1


def _file_letter(num: int) -> str:
    """1 → 'a', 2 → 'b', …, 11 → 'k'."""
    return chr(ord('a') + num - 1)


def _is_valid(file_num: int, rank: int) -> bool:
    """Check that (file_num, rank) is a legal cell on the Glinski hex board."""
    return (1 <= file_num <= 11
            and 1 <= rank <= 11
            and abs(rank - file_num) <= 5)


def zillions_to_ludii(zf: int, zr: int):
    """
    Convert a Zillions square to a Ludii square.

    Parameters
    ----------
    zf : int  Zillions file number (a=1 … k=11)
    zr : int  Zillions rank (1-11)

    Returns
    -------
    (lf, lr) : (int, int)  Ludii file number and rank, or raises ValueError.
    """
    lf = zr
    lr = zr - zf + 6
    if not _is_valid(lf, lr):
        raise ValueError(f"Zillions square {_file_letter(zf)}{zr} maps to "
                         f"invalid Ludii square {_file_letter(lf)}{lr}")
    return lf, lr


def ludii_to_zillions(lf: int, lr: int):
    """
    Convert a Ludii square to a Zillions square.

    Parameters
    ----------
    lf : int  Ludii file number (a=1 … k=11)
    lr : int  Ludii rank (1-11)

    Returns
    -------
    (zf, zr) : (int, int)  Zillions file number and rank, or raises ValueError.
    """
    zr = lf
    zf = lf - lr + 6
    if not _is_valid(zf, zr):
        raise ValueError(f"Ludii square {_file_letter(lf)}{lr} maps to "
                         f"invalid Zillions square {_file_letter(zf)}{zr}")
    return zf, zr


# ── move parsing ──────────────────────────────────────────────────────────────

# A square is one letter followed by 1-2 digits.
_SQUARE_RE = re.compile(r'([a-kA-K])([1-9][0-9]?)')


def _parse_move(move_str: str):
    """
    Parse a move string such as 'a3d4' or 'g2k11' into two squares.

    Returns
    -------
    ((from_file, from_rank), (to_file, to_rank)) : two (int, int) tuples,
    or None if the string cannot be parsed.
    """
    s = move_str.strip().lower()
    squares = _SQUARE_RE.findall(s)
    if len(squares) < 2:
        return None
    (f1, r1), (f2, r2) = squares[0], squares[1]
    return (_file_num(f1), int(r1)), (_file_num(f2), int(r2))


def _square_str(file_num: int, rank: int) -> str:
    return _file_letter(file_num) + str(rank)


def _convert_move(move_str: str, direction: str) -> str:
    """
    Convert a full move.

    Parameters
    ----------
    move_str  : str   e.g. 'a3d4'
    direction : str   'ludii_to_zillions' or 'zillions_to_ludii'

    Returns
    -------
    Converted move string, e.g. 'd1f4'.
    Raises ValueError on bad input.
    """
    parsed = _parse_move(move_str)
    if parsed is None:
        raise ValueError(f"Cannot parse move '{move_str}'. "
                         "Expected format: <square><square>, e.g. a3d4")
    (f1, r1), (f2, r2) = parsed

    if direction == 'ludii_to_zillions':
        zf1, zr1 = ludii_to_zillions(f1, r1)
        zf2, zr2 = ludii_to_zillions(f2, r2)
        return _square_str(zf1, zr1) + _square_str(zf2, zr2)
    else:  # zillions_to_ludii
        lf1, lr1 = zillions_to_ludii(f1, r1)
        lf2, lr2 = zillions_to_ludii(f2, r2)
        return _square_str(lf1, lr1) + _square_str(lf2, lr2)


# ── interactive loop ──────────────────────────────────────────────────────────

def _prompt_starter() -> str:
    while True:
        answer = input("Who moves first? Enter 'ludii' or 'zillions': ").strip().lower()
        if answer in ('ludii', 'zillions'):
            return answer
        print("Please type 'ludii' or 'zillions'.")


def main() -> None:
    print("Glinski Chess – Ludii / Zillions coordinate converter")
    print("======================================================")
    print("Enter moves in pure coordinate notation, e.g. 'a3d4'.")
    print("Type 'quit' to end the session.\n")

    current = _prompt_starter()
    print()

    while True:
        if current == 'ludii':
            raw = input("Ludii move  : ").strip()
        else:
            raw = input("Zillions move: ").strip()

        if raw.lower() == 'quit':
            print("Game over.")
            break

        try:
            if current == 'ludii':
                converted = _convert_move(raw, 'ludii_to_zillions')
                print(f"Zillions    : {converted}")
                current = 'zillions'
            else:
                converted = _convert_move(raw, 'zillions_to_ludii')
                print(f"Ludii       : {converted}")
                current = 'ludii'
        except ValueError as exc:
            print(f"Error: {exc}")
            # keep current side so the user can retry


if __name__ == '__main__':
    main()
