import random
import math
import json
import numpy as np
import copy

from words import words

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

DIRX = np.array([1, 0, 0])
DIRY = np.array([0, 1, 0])
DIRZ = np.array([0, 0, 1])
DIR = [DIRX, DIRY, DIRZ]
ADJX = [-DIRY, DIRY, -DIRZ, DIRZ]
ADJY = [-DIRX, DIRX, -DIRZ, DIRZ]
ADJZ = [-DIRX, DIRX, -DIRY, DIRY]
ADJ = [ADJX, ADJY, ADJZ]

class Word:
    def __init__(self, word: str, word_id = 0, pos = np.array([10, 10, 0]), direction = 0):
        self.dir = direction
        self.id = word_id
        self.pos = pos
        self.word = word

class Game:
    def __init__(self, x = 30, y = 30, z = 100):
        self.x = x
        self.y = y
        self.z = z

        self.board = [[[None for _ in range(self.z)] for _ in range(self.y)] for _ in range(self.x)]
        self.used_words = []

    def in_bounds(self, pos):
        x,y,z = pos
        return x >= 0 and x < self.x and y >= 0 and y < self.y and z >= 0 and z < self.z
    
    def get_letter(self, pos):
        if self.in_bounds(pos):
            x,y,z = pos
            return self.board[x][y][z]
        return None
    
    def can_build(self, word: Word):
        match = False
        total_matches = 0
        # ________TRASH ALERT_________
        pos = copy.copy(word.pos) 
        # ________TRASH ALERT_________
        
        pos -= DIR[word.dir]
        if (self.get_letter(pos)):
            return False
        for letter in word.word:
            pos += DIR[word.dir]
            current_letter = self.get_letter(pos) 
            # Буква совпала
            if (current_letter == letter):
                if match:
                    return False 
                match = True
                total_matches += 1
                continue
            match = False
            # Не None и буква не совпала
            if current_letter:
                return False
            # Проверяем соседние
            else:
                for adj in ADJ[word.dir]:
                    adj_pos = pos + adj
                    if (self.get_letter(adj_pos)):
                        return False

        pos += DIR[word.dir]     
        if self.get_letter(pos):
            return False
        
        # TODO: проверка на 0 этаж
        # TODO: если этаж не 0, то >= 2 пересечения
        return True

    def build_word(self, word: Word):
        if not (self.can_build(word)):
            return False
        pos = word.pos
        #print(pos)
        for letter in word.word:
            x,y,z = pos
            self.board[x][y][z] = letter
            pos += DIR[word.dir]
        return True
        
        
class Model:
    def __init__(self, coeff):
        # Количество связывающих слов (розовые слова) 
        #
        #    |           |
        #    А           О    
        # 1) Б А Л О Б А Ш    -  тут 3 розовых слова    
        #    О           А
        # 2) Б А А А А А Н А Н
        # 3) А Г У Р Е Ц Ы  
        #    |           | 
        # 

        # coeff[0] = розовые слова
        # coeff[1] = длина слова
        self.coeff = coeff
        self.game = Game()

    def __str__(self):
        return str(self.coeff)
    def __repr__(self):
        return str(self.coeff)

    def random(coeff_range):
        coeff = [random.uniform(min_val, max_val) for min_val, max_val in coeff_range]
        return Model(coeff)
        
    # Мутирует модель с определенной силой strength
    def mutate(self, coeff_range, strength):
        coeff = [clamp((c + random.uniform(min_val, max_val) * strength), min_val, max_val) for c, (min_val, max_val) in zip(self.coeff, coeff_range)]
        return Model(coeff)

    # Скрещивает две модели и возвращает новую
    def cross(m1, m2):
        coeff = [random.choice(pair) for pair in zip(m1.coeff, m2.coeff)]
        return Model(coeff)

    # Принимает на вход слова, играет игру и возвращает на вход итоговый score
    def get_score(self, words):
        
        game = []
        return 0.

    def write_map_to_file(self, map_data, file_name):
        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                json.dump(map_data, file, indent=4, ensure_ascii=False)
            print(f"Map data has been written to {file_name}")
        except Exception as e:
            print(f"Error writing map to file: {e}")

    def create_array(self, words):
            map = {}
            
            for id, word in enumerate(words):
                for index, letter in enumerate(word):
                    if not letter in map:
                        map[letter] = {}
                    counter = 2
                    while index + counter < len(word):
                        ending_letter = word[index + counter]
                        if not ending_letter in map[letter]:
                            map[letter][ending_letter] = {}
                        if not (counter - 1) in map[letter][ending_letter]:
                            map[letter][ending_letter][counter - 1] = [id]
                        else:
                            map[letter][ending_letter][counter - 1].append(id)
                        counter += 1
                            
            self.write_map_to_file(map, 'data.json')             
