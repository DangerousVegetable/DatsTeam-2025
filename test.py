import numpy as np
import json
from model import Game, Word

game = Game(5, 5, 5)

game.build_word(Word('абоб', 0, np.array([0,0,0]), 0))
game.build_word(Word('абоб', 1, np.array([0,0,0]), 1))
game.build_word(Word('абоб', 2, np.array([0,0,0]), 2))
game.build_word(Word('овощ', 3, np.array([2,0,0]), 2))
game.build_word(Word('ололо', 4, np.array([0,0,2]), 0))
game.build_word(Word(('балобаш'), 5, np.array([0,1,0]), 0))

# game.build_word(Word('abob', 0, np.array([0,0,0]), 0))
# game.build_word(Word('abob', 1, np.array([0,0,0]), 1))
# game.build_word(Word('abob', 2, np.array([0,0,0]), 2))
# game.build_word(Word('ovos', 3, np.array([2,0,0]), 2))
# game.build_word(Word('ololo', 4, np.array([0,0,2]), 0))
print(game.board)
    
    
def write_map_to_file(map_data, file_name):
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(map_data, file, ensure_ascii=False)
        print(f"Map data has been written to {file_name}")
    except Exception as e:
        print(f"Error writing map to file: {e}")


map = game.board
write_map_to_file(map, 'test2.json')