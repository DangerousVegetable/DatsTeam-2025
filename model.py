import random
import math
import json
import copy
from solver import Solver
from words import words

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

class Vec:
    def __init__(self, *components):
        self.components = list(components)
    
    def __add__(self, other):
        if len(self) != len(other):
            raise ValueError("Vectors must be of the same length to add")
        return Vec(*[a + b for a, b in zip(self.components, other.components)])
    
    def __sub__(self, other):
        if len(self) != len(other):
            raise ValueError("Vectors must be of the same length to subtract")
        return Vec(*[a - b for a, b in zip(self.components, other.components)])
    
    def __neg__(self):
        return Vec(*[-a for a in self.components])

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            raise TypeError("Can only multiply by a scalar (int or float)")
        return Vec(*[a * scalar for a in self.components])
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __iter__(self):
        return iter(self.components)
    
    def __len__(self):
        return len(self.components)
    
    def __repr__(self):
        return f"Vec({', '.join(map(str, self.components))})"
    
    def __eq__(self, other):
        return self.components == other.components
    
    def __getitem__(self, index):
        return self.components[index]

    def __setitem__(self, index, value):
        self.components[index] = value
        
    def copy(self):
        return Vec(*self.components)

DIRX = Vec(1, 0, 0)
DIRY = Vec(0, 1, 0)
DIRZ = Vec(0, 0, -1)
DIR = [DIRX, DIRY, DIRZ]
ADJX = [-DIRY, DIRY, -DIRZ, DIRZ]
ADJY = [-DIRX, DIRX, -DIRZ, DIRZ]
ADJZ = [-DIRX, DIRX, -DIRY, DIRY]
ADJ = [ADJX, ADJY, ADJZ]

class Word:
    def __init__(self, word: str, word_id = 0, pos = Vec(10, 10, 0), direction = 0):
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
        
        if not self.in_bounds(word.pos) or not self.in_bounds((word.pos + (len(word.word)-1)*DIR[word.dir])):
            return False

        pos = word.pos.copy() 
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
        pos = word.pos.copy()
        for letter in word.word:
            x,y,z = pos
            self.board[x][y][z] = letter
            pos += DIR[word.dir]
        self.words.append(word)
        return True
    
    def forced_place(self, word: Word):
        pos = word.pos
        for letter in word.word:
            x,y,z = pos
            self.board[x][y][z] = letter
            pos += DIR[word.dir]
        self.words.append(word)

class Floors:
    def __init__(self, size = (30, 30, 100)):
        self.game = Game(size[0], size[1], size[2])
        self.prev_level = -1

    def can_place(self, word: Word, solver: Solver):
        if self.prev_level < 0:
            return (True, [])
        #pos = word.pos[:2]
        dist = word.pos[2] - self.prev_level

        ids = set()
        vert = []
        i = 0
        while i < len(word.word):
            b = word.word[i]
            pos_2d = word.pos + i*DIR[word.dir]
            a = self.game.get_letter(Vec(pos_2d[0], pos_2d[1], self.prev_level))
            if not a:
                i += 1
                continue
            con = solver.connections.get(b, {}).get(a, {}).get(dist-1, [])
            for id, shift in con:
                if id in ids:
                    continue
                v = Word(solver.words[id], id, Vec(pos_2d[0], pos_2d[1], word.pos[2]+shift), 2)
                res = self.game.can_build(v)
                if res:
                    vert.append(v)
                    ids.add(id)
                    i += 1
                    break
            i += 1
        if len(vert) > 1:
            return (True, vert[:2])
        return (False, [])
    
    def place(self, word: Word, solver: Solver):
        res, vert = self.can_place(word, solver)

        used = set()
        if res:
            for v in vert:
                res = self.game.build_word(v)
                assert(res)
                used.add(v.id)
            self.game.forced_place(word)
            used.add(word.id)
        return used
        

# Какую-то ?#!.@ пишу
# че то придумал? лайк

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
        if not self.in_bounds(pos[:2]) or not self.in_bounds((pos + (len(word.word)-1)*DIR[word.dir])[:2]):
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

    def build_floor(self, used, solver: Solver, floors: Floors, floor_num):
        best = None
        place_word = None
        floor = Game2d((floors.game.x, floors.game.y))

        built = 0
        while True:
            print(f"Step {len(used)}")
            for id, word in enumerate(solver.words):
                if id in used:
                    continue
                for dir in [0,1]:
                    for x in range(floors.game.x):
                        for y in range(floors.game.y):
                            pword = Word(word, id, Vec(x, y, floor_num), dir)
                            res, inter = floor.can_place(pword)
                            # Если слово можно поставить, то считаем все параметры с коэффицентами
                            if res:
                                res, vert = floors.can_place(pword, solver)
                                if res:
                                    score = 0
                                    score += floor.word_score(pword, solver) * self.coeff[0]
                                    score += len(word) * self.coeff[1]
                                    score += inter * self.coeff[2]
                                    score += solver.stats[id][0] * self.coeff[3]
                                    score += solver.stats[id][1] * self.coeff[4]

                                    if not best or score > best:
                                        best = score
                                        place_word = pword
            if best and built < 10:
                res = floor.place(place_word)
                used.add(place_word.id)
                assert(res)
                ids = floors.place(place_word, solver)
                for id in ids:
                    used.add(id)

                best = None
                place_word = None
                built += 1
                print(floor.board_str())
                #print(floors.game.words)
            else:
                if built != 0:
                    floors.prev_level = floor_num
                return built

    # Принимает на вход Solver, играет игру и возвращает на выход итоговый score
    def get_score(self, solver: Solver):
        size_x = 30
        size_y = 30
        size_z = 30

        used = set()
        floors = Floors((size_x, size_y, size_z))
        for floor_num in range(0, size_z):
            print(f"Building floor {floor_num}")
            self.build_floor(used, solver, floors, floor_num)
        return floors.game
        
