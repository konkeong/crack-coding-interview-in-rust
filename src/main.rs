// 2023-03-22 23:17:23.749 || konkeong
// cargo test -- --nocapture

use regex::Regex;
use std::collections::HashMap;

#[derive(Debug, Eq, Hash, PartialEq, Copy, Clone)]
struct Coord {
    x: usize,
    y: usize,
}

impl Coord {
    fn new(x: usize, y: usize) -> Coord {
        Coord { x: x, y: y }
    }

    fn is_adjacent(&self, other: &Coord) -> bool {
        let diff_x = if self.x > other.x {
            self.x - other.x
        } else {
            other.x - self.x
        };
        let diff_y = if self.y > other.y {
            self.y - other.y
        } else {
            other.y - self.y
        };
        if diff_x == 0 && diff_y == 1 {
            return true;
        }
        if diff_x == 1 && diff_y == 0 {
            return true;
        }
        return false;
    }
}

fn path_as_string(path: &Vec<Coord>, 
    map_coord_dar_letter: &HashMap<Coord, String>,
) -> String {
    return path
        .iter()
        .map(|coord| format!("{}", map_coord_dar_letter[coord]))
        .collect::<Vec<String>>()
        .join("");
}

fn trace_letter_of_word(
    word: &str,
    position: usize,
    path: &mut Vec<Coord>,
    map_coord_dar_letter: &HashMap<Coord, String>,
    map_letter_dar_als_coord: &HashMap<String, Vec<Coord>>,
) -> bool {
    if word.len() == 0 {
        return false;
    }
    if path.len() == word.len() {
        return true;
    }
    if position as usize >= word.len() {
        return true;
    }

    eprintln!("position=[{}] :: {:?} :: {:?}", position, path, path_as_string(&path, &map_coord_dar_letter));

    let letter = &word[position..=position];  // single character

    if !map_letter_dar_als_coord.contains_key(letter) {
        return false;
    }

    eprintln!("found the letter=[{}] in coords=[{:?}] :: {:?} :: {:?}", letter, map_letter_dar_als_coord[letter], path, path_as_string(&path, &map_coord_dar_letter));

    // try all the possible locations
    for coord in &map_letter_dar_als_coord[letter] {
        // cannot reuse same position
        if !path.contains(&coord) {
            let mut can_use_coord = false;
            if path.len() == 0 {
                // if first letter, then just use it
                can_use_coord = true;
            } else {
                /*
                 * check that this new letter
                 * can link to previous letter
                 * in 4 cardinal directions
                 */
                let prev_coord = &path[path.len() - 1];
                can_use_coord = coord.is_adjacent(prev_coord);
            }

            // use this coord, as of now
            if can_use_coord {
                // continue this path, until cannot find
                path.push(*coord);

                eprintln!("after joined position=[{}] :: {:?} :: {:?}", position + 1, path, path_as_string(&path, &map_coord_dar_letter));

                // adjust the position for next letter
                if trace_letter_of_word(
                    word,
                    position + 1,
                    path,
                    map_coord_dar_letter,
                    map_letter_dar_als_coord,
                ) {
                    return true;
                }

                // if no usable next letter, then rewind, and try with next sibling position
                path.pop();
            }
        }
    }

    return false;
}

fn check_word_in_block(
    word: &str,
	block: Vec<&str>,
) -> (bool, Vec<Coord>) {
    let mut found = false;
    let mut path: Vec<Coord> = vec![];

    // only uppercase allowed and no spaces
    let re = Regex::new(r"^[A-Z]+$").unwrap();
    if !re.is_match(word) {
        panic!("word=[{}] only uppercase", word);
    }

    /*
     * reconstruct/remap each letter in rectangular block
     * in another data structure
     * for fast lookup
     */
    let mut map_coord_dar_letter: HashMap<Coord, String> = HashMap::new();

    // input block must be rectangular
    let mut num_col_per_row = 0;
    for (nrow, row_v) in block.iter().enumerate() {
        // NOTE: can skip early, if any of the input letter not found inside input block
        let row = row_v.replace(" ", "");

        let re = Regex::new(r"^[A-Z]+$").unwrap();
        if !re.is_match(&row) {
            panic!("rows[{}]=[{}] only uppercase", nrow, row_v);
        }
        if row.len() == 0 {
            panic!("rows[{}]=[{}] in block is empty of elements", nrow, row_v);
        }

        if num_col_per_row == 0 {
            num_col_per_row = row.len();
        } else if num_col_per_row != row.len() {
            panic!("rows[{}]=[{}] in block expect=[{}] elements actual=[{}] elements", nrow, row_v, num_col_per_row, row.len());
        }

        for (ncol, ch) in row.chars().into_iter().enumerate() {
            let coord = Coord::new(nrow, ncol);
            map_coord_dar_letter.insert(coord, ch.to_string());
        }
    }

    /*
     * no reuse allowed, hence if input word
     * is longer than all the letters in the block,
     * then is FALSE
     */
    let num_elem = block.len() * num_col_per_row;
    if word.len() > num_elem {
        panic!("length=[{}] of input word exceeds the number=[{}] of letters in block", word.len(), num_elem);
    }

    /*
     * create a reverse lookup for
     * all the possible locations
     * in which one letter can appear
     */
    let mut map_letter_dar_als_coord: HashMap<String, Vec<Coord>> = HashMap::new();
    for (coord, letter) in map_coord_dar_letter.iter() {
        if !map_letter_dar_als_coord.contains_key(letter) {
            map_letter_dar_als_coord.insert(letter.to_string(), vec![]);
        }
        map_letter_dar_als_coord
            .get_mut(letter)
            .unwrap()
            .push(*coord);
    }

    let position = 0; // starts with 0
    found = trace_letter_of_word(
        word,
        position,
        &mut path,
        &map_coord_dar_letter,
        &map_letter_dar_als_coord,
    );

    return (found, path);
}

#[test]
fn coord_1() {
    let c1 = Coord::new(3, 4);
    let c2 = Coord::new(3, 5);
    assert!(c1.is_adjacent(&c2));
    assert!(c2.is_adjacent(&c1));
    let c3 = Coord::new(2, 4);
    assert!(c1.is_adjacent(&c3));
    let c4 = Coord::new(4, 5);
    assert!(!c1.is_adjacent(&c4));
}

#[test]
fn example_1() {
    let word = "HELLO";
    let board = vec![
        "A B H E J P",
        "F T J L L W",
        "V Y X R O Q",
        "W V U I L W"
    ];
    let (f_ret, path) = check_word_in_block(word, board);
    eprintln!("{} {:?} :: {:?}", if f_ret { "Found" } else { "Not Found" }, word, path);
    assert!(f_ret, "expect TRUE for {:?}", word);
}

#[test]
fn example_2() {
    let word = "WORLD";
    let board = vec![
        "A B H J J P",
        "F T J N D W",
        "V D L R O W",
        "W O R I V W"
    ];
    let (f_ret, path) = check_word_in_block(word, board);
    eprintln!("{} {:?} :: {:?}", if f_ret { "Found" } else { "Not Found" }, word, path);
    assert!(f_ret, "expect TRUE for {:?}", word);
}

#[test]
fn example_3() {
    let word = "RUST";
    let board = vec![
        "A B R U S P",
        "F T J N D T",
        "V D R R G W",
        "W V R I V W"
    ];
    let (f_ret, path) = check_word_in_block(word, board);
    eprintln!("{} {:?} :: {:?}", if f_ret { "Found" } else { "Not Found" }, word, path);
    assert!(f_ret == false, "expect FALSE for {:?}", word);
}

fn main() {
    let word = "QWER";
    check_word_in_block(word, vec!["ABCDEF", "GHIJKL", "MNOPQR", "STUVWX"]);

    let pos = 2;
    let letter = &word[pos..=pos];
    println!("letter=[{}]", letter);

    let c1 = Coord::new(3, 4);
    println!("{:?}", c1);

    let mut path = vec![Coord::new(1, 3), Coord::new(2, 6), Coord::new(3, 9)];
    println!("{:?}", path);

    let mut map_coord_dar_letter: HashMap<Coord, String> = HashMap::new();
    map_coord_dar_letter.insert(Coord { x: 1, y: 3 }, "one".to_string());
    map_coord_dar_letter.insert(Coord { x: 2, y: 6 }, "two".to_string());
    map_coord_dar_letter.insert(Coord { x: 3, y: 9 }, "three".to_string());
    map_coord_dar_letter.insert(Coord { x: 4, y: 12 }, "four".to_string());
    map_coord_dar_letter.insert(Coord { x: 5, y: 15 }, "five".to_string());
    map_coord_dar_letter.insert(Coord { x: 6, y: 18 }, "six".to_string());
    println!("{:?}", map_coord_dar_letter);

    let mut position: usize = 0;
    eprintln!("position=[{}] :: {:?} :: {:?}", position, path, path_as_string(&path, &map_coord_dar_letter));
    path.push(Coord::new(6, 18));
    position = 23;
    eprintln!("position=[{}] :: {:?} :: {:?}", position, path, path_as_string(&path, &map_coord_dar_letter));

    let mut map_letter_dar_als_coord: HashMap<String, Vec<Coord>> = HashMap::new();
    map_letter_dar_als_coord.insert("1".to_string(), vec![Coord::new(1, 1)]);
    println!("found=[{}]", map_letter_dar_als_coord.contains_key("1"));
    println!("not found=[{}]", map_letter_dar_als_coord.contains_key("2"));

    match map_letter_dar_als_coord.get("1") {
        Some(coord) => println!("found=[{:?}]", coord),
        None => println!("not found"),
    }
    println!("{:?}", map_letter_dar_als_coord.get("1").unwrap());

    println!("TAMAT");
}
