## 2023-03-22 19:40:52.823 || konkeong

import sys
import re
from typing import Dict, List, Tuple


def is_coord_adjacent(curr_coord: str, prev_coord: str) -> bool:
    # FIXME: no validation here, use this function with care

    # print(f'curr={curr_coord} prev={prev_coord}', end='', file=sys.stderr)

    curr_flds = curr_coord.split(',')
    curr_x = int(curr_flds[0])
    curr_y = int(curr_flds[1])

    prev_flds = prev_coord.split(',')
    prev_x = int(prev_flds[0])
    prev_y = int(prev_flds[1])

    diff_x = curr_x - prev_x
    if diff_x < 0:
        diff_x = -1 * diff_x

    diff_y = curr_y - prev_y
    if diff_y < 0:
        diff_y = -1 * diff_y

    if diff_x == 0 and diff_y == 1:
        # print(f'  can join', file=sys.stderr)
        return True

    if diff_x == 1 and diff_y == 0:
        # print(f'  can join', file=sys.stderr)
        return True

    # print(f'  cannot join', file=sys.stderr)
    return False


def trace_letter_of_word(
        word: str,
        position: int,
        path: List[str],
        map_coord_dar_letter: Dict[str, str],
        map_letter_dar_als_coord: Dict[str, List[str]]) -> bool:
    if len(word) == 0:
        return False

    if len(path) == len(word):
        return True

    if position >= len(word):
        return True

    # ss = ''.join(map_coord_dar_letter[p] for p in path)
    # print(f'position=[{position}] :: {path} :: {ss}', file=sys.stderr)

    letter = word[position]

    if letter not in map_letter_dar_als_coord:
        return False

    # ss = ''.join(map_coord_dar_letter[p] for p in path)
    # print(f'found the letter=[{letter}] in coords={map_letter_dar_als_coord[letter]} :: [{path}] :: [{ss}]', file=sys.stderr)

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
                can_use_coord = is_coord_adjacent(coord, prev_coord)

            # use this coord, as of now
            if can_use_coord:
                # continue this path, until cannot find
                path.append(coord)

                # ss = ''.join(map_coord_dar_letter[p] for p in path)
                # print(f'after joined pos=[{(position + 1)}] :: {path} :: {ss}')

                # adjust the position for next letter
                if trace_letter_of_word(word,
                                        position + 1,
                                        path,
                                        map_coord_dar_letter,
                                        map_letter_dar_als_coord):
                    return True

                # if no usable next letter, then rewind, and try with next sibling position
                path.pop()

    return False


def check_word_in_block(word: str, block: List[str]) -> Tuple[bool, List[str]]:
    found = False
    path: List[str] = []  # coordinates "x,y", zero based, origin at TOP-LEFT

    if not re.match('^[A-Z]+$', word):
        raise Exception(f'word=[{word}] only uppercase')

    # reconstruct/remap each letter in rectangular block
    # in another data structure
    # for fast lookup
    map_coord_dar_letter: Dict[str, str] = {}

    # input block must be rectangular
    nrow = 0
    num_col_per_row = 0
    for row in block:
        row = row.replace(' ', '')
        if not re.match('^[A-Z]+$', row):
            raise Exception(f'word=[{word}] only uppercase')
        if len(row) == 0:
            raise Exception(f'row=[{nrow + 1}] in block is empty of elements')

        if num_col_per_row == 0:
            num_col_per_row = len(row)
        elif num_col_per_row != len(row):
            raise Exception(f'row=[{nrow + 1}] in block expect=[{num_col_per_row}] elements actual=[{len(row)}] elements')

        ncol = 0
        for ch in row:
            coord = f'{nrow},{ncol}'
            map_coord_dar_letter[coord] = ch
            ncol += 1
        nrow += 1

    # no reuse allowed, hence if input word
    # is longer than all the letters in the block,
    # then is FALSE
    num_elem = nrow * num_col_per_row
    if len(word) > num_elem:
        raise Exception(f'length=[{len(word)}] of input word exceeds the number=[{num_elem}] of letters in block')

    # create a reverse lookup for
    # all the possible locations in which one letter can appear
    map_letter_dar_als_coord: Dict[str, List[str]] = {}
    for coord, letter in map_coord_dar_letter.items():
        if letter not in map_letter_dar_als_coord:
            map_letter_dar_als_coord[letter] = []
        map_letter_dar_als_coord[letter].append(coord)

    position = 0  # starts with 0
    found = trace_letter_of_word(word,
                                 position,
                                 path,
                                 map_coord_dar_letter,
                                 map_letter_dar_als_coord)

    return found, path


if __name__ == '__main__':
    # example 1
    word = 'HELLO'
    f_ret, path = check_word_in_block(word, [
        'A B H E J P',
        'F T J L L W',
        'V Y X R O Q',
        'W V U I L W',
    ])
    assert f_ret == True, f'expect TRUE for "{word}" :: {path}'
    print(f'{"Found" if f_ret else "Not Found" } "{word}" :: {path}')

    # example 2
    word = 'WORLD'
    f_ret, path = check_word_in_block(word, [
        'A B H J J P',
        'F T J N D W',
        'V D L R O W',
        'W O R I V W',
    ])
    assert f_ret == True, f'expect TRUE for "{word}" :: {path}'
    print(f'{"Found" if f_ret else "Not Found" } "{word}" :: {path}')

    # example 3
    word = 'RUST'
    f_ret, path = check_word_in_block(word, [
        'A B R U S P',
        'F T J N D T',
        'V D R R G W',
        'W V R I V W',
    ])
    assert f_ret == False, f'expect FALSE for "RUST" :: {path}'
    print(f'{"Found" if f_ret else "Not Found" } "{word}" :: {path}')
