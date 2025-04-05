import random
import math
import json
import numpy as np
import copy
from solver import Solver
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
        self.words = []

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
        pos = copy.copy(word.pos) 
        
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
        
        return True

    def build_word(self, word: Word):
        if not (self.can_build(word)):
            return False
        pos = word.pos
        for letter in word.word:
            x,y,z = pos
            self.board[x][y][z] = letter
            pos += DIR[word.dir]
        self.words.append(word)
        return True

# Класс для 2д игры (супер-эрудит)
class Game2d:
    def __init__(self, size = (30, 30)):
        self.size = size
        self.words = []
        self.board = [[None for _ in range(self.size[1])] for _ in range(self.size[0])]
    
    def in_bounds(self, pos):
        x,y = pos
        return x >= 0 and x < self.size[0] and y >= 0 and y < self.size[1]
    
    def get_letter(self, pos):
        if self.in_bounds(pos):
            x,y = pos
            return self.board[x][y]
        return None
    
    def can_place(self, word: Word):
        pos = word.pos.copy()
        if not self.in_bounds(pos[:2]) or not self.in_bounds((pos + len(word.word)*DIR[word.dir])[:2]):
            return (False, 0)

        pos -= DIR[word.dir]

        matches = 0
        matched = False

        if self.get_letter(pos[:2]):
            return (False, 0)
        
        for letter in word.word:
            pos += DIR[word.dir]
            cur_letter = self.get_letter(pos[:2])
            if letter == cur_letter:
                if matched:
                    return (False, 0)
                matches += 1
                matched = True
                continue
            elif cur_letter:
                return (False, 0)
            matched = False
            for adj in ADJ[word.dir]:
                adj_pos = pos+adj
                if self.get_letter(adj_pos[:2]):
                    return (False, 0)

        pos += DIR[word.dir]
        if self.get_letter(pos[:2]):
            return (False, 0)
        
        return (True, matches)
    
    def place(self, word: Word):
        result, matches = self.can_place(word)
        if result:
            pos = word.pos.copy()
            for letter in word.word:
                x,y,_ = pos
                self.board[x][y] = letter
                pos += DIR[word.dir]
            self.words.append(word)
            return True
        return False

    def board_str(self):
        s = ""
        for y in reversed(range(self.size[1])):
            for x in range(self.size[0]):
                c = self.get_letter((x, y))
                c = ' ' if not c else c
                s += c + ' '
            s += '\n'
        return s   

    def word_score(self, word: Word, solver: Solver):
        score = 0
        for w in self.words:
            if w.dir == word.dir:
                dir = word.dir
                start = max(word.pos[dir], w.pos[dir])
                stop = min((word.pos + len(word.word)*DIR[dir])[dir], (w.pos + len(w.word)*DIR[dir])[dir])
                shift = w.pos[dir] - word.pos[dir]
                dist = w.pos[1-dir] - word.pos[1-dir]
                for i in range(max(0, shift), min(stop - start, len(word.word))):
                    j = i - shift
                    a = w.word[j]
                    b = word.word[i]
                    # if word is above w
                    if dist < 0:
                        score += len(solver.connections.get(a, {}).get(b, {}).get(-dist-1, []))
                    else:
                        score += len(solver.connections.get(b, {}).get(a, {}).get(dist-1, []))
        return score / len(word.word) / (len(self.words) + 1)
    
    def score(self):
        min_x = self.size[0]
        min_y = self.size[1]
        max_x = max_y = 0

        total_length = 0
        for w in self.words:
            l = len(w.word)
            min_x = min(min_x, w.pos[0])
            min_y = min(min_y, w.pos[1])
            max_x = max(max_x, (w.pos + l*DIR[w.dir])[0])
            max_y = max(max_y, (w.pos + l*DIR[w.dir])[1])
            total_length += l
        dx = max_x - min_x
        dy = max_y - min_y
        return (total_length + len(self.words))*(min(dx, dy) / max(dx, dy))

        
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
        # coeff[2] = количество пересечений
        # coeff[3] = epicness слова 
        # coeff[4] = coolness слова 
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

    # Принимает на вход Solver, играет игру и возвращает на выход итоговый score
    def get_score(self, solver: Solver):
        size_x = 30
        size_y = 30
        game = Game2d((size_x, size_y))
        used = set()
        
        best = None
        place_word = None
        while True:
            print(f"Step {len(used)}")
            for id, word in enumerate(solver.words):
                if id in used:
                    continue
                print(f"word {id}")
                for dir in [0,1]:
                    for x in range(size_x):
                        for y in range(size_y):
                            pword = Word(word, id, np.array([x, y, 0]), dir)
                            res, inter = game.can_place(pword)
                            # Если слово можно поставить, то считаем все параметры с коэффицентами
                            if res and (len(used) == 0 or inter > 0):
                                score = 0
                                score += game.word_score(pword, solver) * self.coeff[0]
                                score += len(word) * self.coeff[1]
                                score += inter * self.coeff[2]
                                score += solver.stats[id][0] * self.coeff[3]
                                score += solver.stats[id][1] * self.coeff[4]

                                if not best or score > best:
                                    best = score
                                    place_word = pword
            if best:
                game.place(place_word)
                used.add(place_word.id)
                best = None
                place_word = None
            else:
                return game
