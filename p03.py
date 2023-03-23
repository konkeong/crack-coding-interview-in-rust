## 2023-03-22 22:10:43.384 || konkeong

import sys
import re
from typing import Dict, List, Tuple


class Coord:

    def __init__(self, x: int, y: int):
        if x < 0:
            raise Exception('x=[{x}] must >= 0')
        if y < 0:
            raise Exception('y=[{y}] must >= 0')
        self.x = x
        self.y = y

    def is_adjacent(self, other: 'Coord') -> bool:
        diff_x = self.x - other.x if self.x > other.x else other.x - self.x
        diff_y = self.y - other.y if self.y > other.y else other.y - self.y
        if diff_x == 0 and diff_y == 1:
            return True
        if diff_x == 1 and diff_y == 0:
            return True
        return False

    @staticmethod
    def from_string(coord: str) -> 'Coord':
        flds = coord.split(',')
        x = int(flds[0])
        y = int(flds[1])
        return Coord(x, y)

    @staticmethod
    def list_as_string(path: List['Coord']) -> str:
        return '{' + ', '.join([f'({p})' for p in path]) + '}'

    def __str__(self) -> str:
        return f'{self.x},{self.y}'


def trace_letter_of_word(
        word: str,
        position: int,
        path: List[Coord],
        map_coord_dar_letter: Dict[Coord, str],
        map_letter_dar_als_coord: Dict[str, List[Coord]],
        f_verbose: bool) -> bool:
    if len(word) == 0:
        return False

    if len(path) == len(word):
        return True

    if position >= len(word):
        return True

    if f_verbose:
        ss = ''.join(map_coord_dar_letter[p] for p in path)
        print(f'position=[{position}] :: {Coord.list_as_string(path)} :: {ss}', file=sys.stderr)

    letter = word[position]

    if letter not in map_letter_dar_als_coord:
        return False

    if f_verbose:
        ss = ''.join(map_coord_dar_letter[p] for p in path)
        print(f'found the letter=[{letter}] in coords={Coord.list_as_string(map_letter_dar_als_coord[letter])} :: {Coord.list_as_string(path)} :: [{ss}]', file=sys.stderr)

    # try all the possible locations
    for coord in map_letter_dar_als_coord[letter]:
        # cannot reuse same position
        if coord not in path:
            can_use_coord = False
            if len(path) == 0:
                # if first letter, then just use it
                can_use_coord = True
            else:
                # check that this new letter
                # can link to previous letter
                # in 4 cardinal directions
                prev_coord = path[-1]
                can_use_coord = coord.is_adjacent(prev_coord)

            # use this coord, as of now
            if can_use_coord:
                # continue this path, until cannot find
                path.append(coord)

                if f_verbose:
                    ss = ''.join(map_coord_dar_letter[p] for p in path)
                    print(f'after joined position=[{(position + 1)}] :: {Coord.list_as_string(path)} :: {ss}')

                # adjust the position for next letter
                if trace_letter_of_word(word,
                                        position + 1,
                                        path,
                                        map_coord_dar_letter,
                                        map_letter_dar_als_coord,
                                        f_verbose):
                    return True

                # if no usable next letter, then rewind, and try with next sibling position
                path.pop()

    return False


def check_word_in_block(word: str,
                        block: List[str],
                        f_verbose: bool) -> Tuple[bool, List[Coord]]:
    found = False
    path: List[Coord] = []  # coordinates "x,y", zero based, origin at TOP-LEFT

    if not re.match('^[A-Z]+$', word):
        raise Exception(f'word=[{word}] only uppercase')

    # reconstruct/remap each letter in rectangular block
    # in another data structure
    # for fast lookup
    map_coord_dar_letter: Dict[Coord, str] = {}

    # input block must be rectangular
    num_col_per_row = 0
    for nrow, row in enumerate(block, 0):
        # NOTE: can skip early, if any of the input letter not found inside input block
        row = row.replace(' ', '')
        if not re.match('^[A-Z]+$', row):
            raise Exception(f'row=[{row}] only uppercase')
        if len(row) == 0:
            raise Exception(f'row=[{nrow + 1}] in block is empty of elements')

        if num_col_per_row == 0:
            num_col_per_row = len(row)
        elif num_col_per_row != len(row):
            raise Exception(f'row=[{nrow + 1}] in block expect=[{num_col_per_row}] elements actual=[{len(row)}] elements')

        for ncol, ch in enumerate(row, 0):
            coord = Coord(nrow, ncol)
            map_coord_dar_letter[coord] = ch

    # no reuse allowed, hence if input word
    # is longer than all the letters in the block,
    # then is FALSE
    num_elem = nrow * num_col_per_row
    if len(word) > num_elem:
        raise Exception(f'length=[{len(word)}] of input word exceeds the number=[{num_elem}] of letters in block')

    # create a reverse lookup for
    # all the possible locations
    # in which one letter can appear
    map_letter_dar_als_coord: Dict[str, List[Coord]] = {}
    for coord, letter in map_coord_dar_letter.items():
        if letter not in map_letter_dar_als_coord:
            map_letter_dar_als_coord[letter] = []
        map_letter_dar_als_coord[letter].append(coord)

    position = 0  # starts with 0
    found = trace_letter_of_word(word,
                                 position,
                                 path,
                                 map_coord_dar_letter,
                                 map_letter_dar_als_coord,
                                 f_verbose)

    return found, path


if __name__ == '__main__':
    f_verbose = False
    for arg in sys.argv:
        if arg == '--verbose':
            f_verbose = True

    # example 1
    word = 'HELLO'
    f_ret, path = check_word_in_block(word, [
        'A B H E J P',
        'F T J L L W',
        'V Y X R O Q',
        'W V U I L W',
    ], f_verbose)
    print(f'{"Found" if f_ret else "Not Found" } "{word}" :: {Coord.list_as_string(path)}', file=sys.stderr)
    assert f_ret == True, f'expect TRUE for "{word}" :: {Coord.list_as_string(path)}'

    # example 2
    word = 'WORLD'
    f_ret, path = check_word_in_block(word, [
        'A B H J J P',
        'F T J N D W',
        'V D L R O W',
        'W O R I V W',
    ], f_verbose)
    print(f'{"Found" if f_ret else "Not Found" } "{word}" :: {Coord.list_as_string(path)}', file=sys.stderr)
    assert f_ret == True, f'expect TRUE for "{word}" :: {Coord.list_as_string(path)}'

    # example 3
    word = 'RUST'
    f_ret, path = check_word_in_block(word, [
        'A B R U S P',
        'F T J N D T',
        'V D R R G W',
        'W V R I V W',
    ], f_verbose)
    print(f'{"Found" if f_ret else "Not Found" } "{word}" :: {Coord.list_as_string(path)}', file=sys.stderr)
    assert f_ret == False, f'expect FALSE for "RUST" :: {Coord.list_as_string(path)}'
