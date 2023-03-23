## 2023-03-22 17:06:05.285 || konkeong

import sys
import re
from typing import Dict, List, Tuple


def is_coord_adjacent(curr_coord: str, prev_coord: str) -> bool:
    print(f'curr={curr_coord} prev={prev_coord}', end='', file=sys.stderr)

    # no validation here
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
        print(f'  can join', file=sys.stderr)
        return True

    if diff_x == 1 and diff_y == 0:
        print(f'  can join', file=sys.stderr)
        return True

    print(f'  cannot join', file=sys.stderr)
    return False


def find_letter_of_word_in_rectangle(word: str, path: List[str], map_coord_dar_letter: Dict[str, str], map_letter_dar_als_coord: Dict[str, List[str]]) -> bool:
    # cut the word into 2 parts:
    #   head = first letter and work with this
    #   tail = remaining letters (if any)

    if len(word) == 0:
        return True  # done, no more

    head = word[0:1]
    tail = word[1:]

    if head not in map_letter_dar_als_coord:
        return False  # cannot find, stop

    ss = ''
    for p in path:
        ss += map_coord_dar_letter[p]
    print(f'found the letter=[{head}] in coords={map_letter_dar_als_coord[head]} :: [{path}] :: [{ss}]', file=sys.stderr)

    if len(path) == 0:
        # different heads/branches
        for coord in map_letter_dar_als_coord[head]:
            path2: List[str] = [coord]
            found2 = find_letter_of_word_in_rectangle(tail, path2, map_coord_dar_letter, map_letter_dar_als_coord)
            if found2:
                path = path2.copy()
                return True
        return False
    else:
        found_coord = ''
        for coord in map_letter_dar_als_coord[head]:
            if coord in path:
                # cannot reuse
                found_coord = ''
            else:
                # check that this new letter
                # can link to previous letter
                # in 4 cardinal directions
                prev_coord = path[-1]
                if is_coord_adjacent(coord, prev_coord):
                    found_coord = coord
                    break
        if found_coord == '':
            # no usable leter found in any position / coordinates
            return False

        path.append(found_coord)

        # recursive call with tail
        return find_letter_of_word_in_rectangle(tail, path, map_coord_dar_letter, map_letter_dar_als_coord)


def check_word_in_rectangle(word: str, rectangle: List[str]) -> Tuple[bool, List[str]]:
    found = False
    path: List[str] = []  # coordinates "x,y", zero based, origin at TOP-LEFT

    if not re.match('^[A-Z]+$', word):
        raise Exception(f'word=[{word}] only uppercase')

    # reconstruct/remap each letter in rectangle in another data structure
    map_coord_dar_letter: Dict[str, str] = {}

    # input rectangle must be rectangle
    nrow = 0
    num_col_per_row = 0
    for row in rectangle:
        row = row.replace(' ', '')
        if not re.match('^[A-Z]+$', row):
            raise Exception(f'word=[{word}] only uppercase')
        if len(row) == 0:
            raise Exception(f'row=[{nrow + 1}] in rectangle is empty of elements')
        if num_col_per_row == 0:
            num_col_per_row = len(row)
        elif num_col_per_row != len(row):
            raise Exception(f'row=[{nrow + 1}] in rectangle expect=[{num_col_per_row}] elements actual=[{len(row)}] elements')

        ncol = 0
        for ch in row:
            coord = f'{nrow},{ncol}'
            map_coord_dar_letter[coord] = ch
            ncol += 1
        nrow += 1

    # no reuse allowed, hence if input word
    # is longer than whatever in the rectangle,
    # then is FALSE
    num_elem = nrow * num_col_per_row
    if len(word) > num_elem:
        raise Exception(f'input word, length=[{len(word)}] exceeds the number=[{num_elem}] of letters in rectangle')

    # create a reverse lookup
    map_letter_dar_als_coord: Dict[str, List[str]] = {}
    for coord, letter in map_coord_dar_letter.items():
        if letter not in map_letter_dar_als_coord:
            map_letter_dar_als_coord[letter] = []
        map_letter_dar_als_coord[letter].append(coord)

    found = find_letter_of_word_in_rectangle(word, path, map_coord_dar_letter, map_letter_dar_als_coord)

    return found, path


if __name__ == '__main__':
    # example 1
    f_ret, path = check_word_in_rectangle('HELLO', [
        'A B H E J P',
        'F T J L L W',
        'V Y X R O Q',
        'W V U I L W',
    ])
    assert f_ret == True, f'expect TRUE for "HELLO" :: {path}'

    # example 2
    f_ret, path = check_word_in_rectangle('WORLD', [
        'A B H J J P',
        'F T J N D W',
        'V D L R O W',
        'W V R I V W',
    ])
    assert f_ret == True, f'expect TRUE for "WORLD" :: {path}'

    # example 3
    f_ret, path = check_word_in_rectangle('RUST', [
        'A B R U S P',
        'F T J N D T',
        'V D R R G W',
        'W V R I V W',
    ])
    assert f_ret == False, f'expect FALSE for "RUST" :: {path}'
