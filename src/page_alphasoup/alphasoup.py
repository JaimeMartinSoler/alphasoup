import copy
import logging
import random

from page_alphasoup.position import Position
from page_alphasoup.way import Way

logger = logging.getLogger()


class AlphaSoup:

    def __init__(self, rows, cols, letters, letters_weights_map, words, ways):

        # args
        self.rows = rows
        self.cols = cols
        self.letters = [letter.upper() for letter in letters]  # case-insensitive (only upper letters)
        self.letters_weights_map = self._build_letters_weights_map(letters_weights_map)  # case-insensitive (only upper letters)
        self.words = [word.upper() for word in words]  # case-insensitive (only upper letters)
        self.ways = self._build_ways(ways)

        # init
        self.words_data = self._init_words_data()
        self.soup = self._init_soup()

        # validate
        self._validate()

    def build_alphasoup(self, only_solution=False):
        logger.info(f"build_alphasoup(only_solution={only_solution})"
                    f", (rows, cols) = ({self.rows}, {self.cols}), ways={self.ways}, words={self.words}")
        self._build_words_data()
        self._build_soup(only_solution)

    def _validate(self):
        words_bigger_than_soup = [word for word in self.words if len(word) > self.rows and len(word) > self.cols]
        if len(words_bigger_than_soup) > 0:
            raise ValueError(f"there are words ({words_bigger_than_soup})"
                             f" that doesn't fit in soup with dimensions ({self.rows}, {self.cols})")
        return True

    # ------------------------------------------------------------------------------------------------------------------
    # words_data

    def _build_letters_weights_map(self, letters_weights_map):
        self.letters_weights_map = {letter: 1.0 for letter in self.letters}
        if letters_weights_map is not None and len(letters_weights_map) > 0:
            for letter, weight in letters_weights_map.items():
                self.letters_weights_map[letter.upper()] = weight  # case-insensitive (only upper letters)
        return self.letters_weights_map

    def _build_words_data(self):

        self._init_words_data()

        words_attempts = [self.words, self.words[::-1]]

        all_words_inserted = False
        for words in words_attempts:

            for word_idx, word in enumerate(words):

                word_inserted = False

                # way
                ways_valid = self._get_ways_valid(word)
                while not word_inserted and len(ways_valid) > 0:
                    way_idx = random.randrange(0, len(ways_valid))
                    way = ways_valid.pop(way_idx)

                    self.words_data[word]['way'] = way

                    # position0
                    positions_valid = self._get_positions_valid(word, way)
                    while not word_inserted and len(positions_valid) > 0:
                        self.words_data[word]['positions'] = []
                        position_idx = random.randrange(0, len(positions_valid))
                        position0 = positions_valid.pop(position_idx)

                        # try to insert word from position0, but if invalid cross then break
                        positions_with_word_current = []
                        word_validated = True
                        for idx, letter in enumerate(word):

                            # position
                            position = Position(position0.row, position0.col)
                            # row
                            if way.is_south_half():
                                position.row += idx
                            elif way.is_north_half():
                                position.row -= idx
                            # col
                            if way.is_east_half():
                                position.col += idx
                            elif way.is_west_half():
                                position.col -= idx

                            position_letter_dict = self._get_position_letter_dict()

                            self.words_data[word]['positions'].append(position)

                            # validate word cross
                            if position.is_in(list(position_letter_dict.keys())):
                                if position_letter_dict[position] == letter:
                                    logger.debug(f"word cross OK, in {position} for letter '{letter}')")
                                else:
                                    word_validated = False
                                    self.words_data[word]['positions'] = []
                                    break

                        if not word_validated:
                            logger.debug(f"word '{word}' not valid from position {position0}, way {way}")
                            # redundant, but clearer
                            word_inserted = False
                            self.words_data[word]['positions'] = []
                            continue
                        else:
                            word_inserted = True
                            logger.info(f"word '{word}' from {position0}, way: {way}")

                # for word_idx, word in enumerate(words):

                if not word_inserted:
                    logger.debug(f"word '{word}' couldn't be assigned, trying another words_attempt")
                    self._init_words_data()
                    break

                if word_idx == len(words) - 1:
                    all_words_inserted = True

            # for words in words_attempts:
            if all_words_inserted:
                break

        if not all_words_inserted:
            self._init_words_data()
            raise RuntimeError(f"Couldn't assign word '{word}'!")
        else:
            logger.info(f"all words_data assigned, OK!")

        return self.soup

    def _init_words_data(self):
        self.words_data = {word: {'positions': [], 'way': None} for word in self.words}
        return self.words_data

    def _get_position_letter_dict(self):
        position_letter_dict = {p: letter for word, word_data in self.words_data.items()
                                for p, letter in zip(word_data['positions'], word)}
        return position_letter_dict

    def _build_ways(self, ways):
        self.ways = [way if isinstance(way, Way) else Way(way) for way in ways]
        return self.ways

    def _get_ways_valid(self, word):
        ways_valid = copy.deepcopy(self.ways)
        if len(word) > self.rows:
            ways_valid = [way for way in ways_valid if way.is_horizontal()]
        if len(word) > self.cols:
            ways_valid = [way for way in ways_valid if way.is_vertical()]
        if len(ways_valid) == 0:
            raise ValueError(f"word '{word}' doesn't fit in soup (rows={self.rows}, cols={self.cols})")
        return ways_valid
    
    def _get_positions_valid(self, word, way):
        
        # rows min max
        if way.is_south_half():
            row_min = 0
            row_max = self.rows - len(word)
        elif way.is_north_half():
            row_min = len(word) - 1
            row_max = self.rows - 1
        else:
            row_min = 0
            row_max = self.rows - 1
            
        # cols min max
        if way.is_east_half():
            col_min = 0
            col_max = self.cols - len(word)
        elif way.is_west_half():
            col_min = len(word) - 1
            col_max = self.cols - 1
        else:
            col_min = 0
            col_max = self.cols - 1

        # positions_valid
        positions_valid = []
        for row in range(row_min, row_max + 1):
            for col in range(col_min, col_max + 1):
                positions_valid.append(Position(row, col))

        return positions_valid

    # ------------------------------------------------------------------------------------------------------------------
    # soup

    def _build_soup(self, only_solution=False):
        self._init_soup()
        self._insert_words_data_into_soup()
        if not only_solution:
            self.build_soup_background()
        return self.soup

    def _init_soup(self):
        self.soup = [['' for _ in range(self.cols)] for _ in range(self.rows)]
        return self.soup

    def _insert_words_data_into_soup(self):
        for word, word_data in self.words_data.items():
            for p, letter in zip(word_data['positions'], word):
                self.soup[p.row][p.col] = letter

    def build_soup_background(self):

        logger.info(f"build_soup_background")

        for row in range(self.rows):
            for col in range(self.cols):

                letter_soup = self.soup[row][col]
                if letter_soup is not None and len(letter_soup) > 0:
                    continue

                surrounding_letters = self._get_surrounding_letters(row, col)

                letters_weights_map_copy = copy.deepcopy(self.letters_weights_map)
                for surr_letter in surrounding_letters:
                    letters_weights_map_copy[surr_letter] = 0.0

                letter = random.choices(self.letters, weights=list(letters_weights_map_copy.values()), k=1)[0]

                self.soup[row][col] = letter

        return self.soup

    def _get_surrounding_letters(self, row, col):

        surrounding_letters = []

        for r in range(max(0, row-1), min(self.rows, row+2)):
            for c in range(max(0, col-1), min(self.cols, col+2)):
                letter_soup = self.soup[r][c]
                if letter_soup is None or len(letter_soup) == 0:
                    continue
                surrounding_letters.append(letter_soup)

        return surrounding_letters


