import numpy as np
import json
from model import Game, Word, Game2d, Model
from solver import Solver
from words import words as WORDS

def test_game():
    game = Game(5, 5, 5)
    game.build_word(Word('абоб', 0, np.array([0,0,0]), 0))
    game.build_word(Word('абоб', 1, np.array([0,0,0]), 1))
    game.build_word(Word('абоб', 2, np.array([0,0,0]), 2))
    game.build_word(Word('овощ', 3, np.array([2,0,0]), 2))
    game.build_word(Word('ололо', 4, np.array([0,0,2]), 0))
    game.build_word(Word(('балобаш'), 5, np.array([0,1,0]), 0))
        
        
    def write_map_to_file(map_data, file_name):
        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                json.dump(map_data, file, ensure_ascii=False)
            print(f"Map data has been written to {file_name}")
        except Exception as e:
            print(f"Error writing map to file: {e}")


    map = game.board
    write_map_to_file(map, 'test2.json')

def test_game2d():
    game = Game2d((5,5))
    game.place(Word('абоба', 0, np.array([0, 0, 0]), 0))
    game.place(Word('абоба', 0, np.array([0, 0, 0]), 1))
    game.place(Word('опера', 0, np.array([2, 0, 0]), 1))
    game.place(Word('опера', 0, np.array([0, 2, 0]), 0))
    print(game.board_str())
    #solver = Solver(WORDS)
    #solver.save()

if __name__ == '__main__':
    solver = Solver(WORDS[:50])
    model = Model([1., 0., 0.5, 0.2, 0.2])
    game = model.get_score(solver)
    print(game.board_str())

    #solver = Solver(['абоба', 'опера', 'абоба', 'опера'])
    #score, words = model.get_score(solver)
    #print(score)
    #for w  in words:
    #    print(w.pos, w.dir, w.word)
    #print(solver.connections)
    #game = Game2d((6,6))
    #game.place(Word('абоба', 0, np.array([0, 0, 0]), 0))
    #game.place(Word('абоба', 0, np.array([0, 0, 0]), 1))
    #game.place(Word('опера', 0, np.array([2, 0, 0]), 1))
    #game.place(Word('опера', 0, np.array([0, 2, 0]), 0))
    #print(game.score())