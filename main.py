import copy
import random
import json
from model import Model
from solver import Solver
from words import words as WORDS

class Genetics:
    def __init__(self, models_per_round, top_models, num_epoch):
        # Количество моделей в одном раунде
        self.models_per_round = models_per_round
        # Количество моделей которые переходят в следующий раунд
        self.top_models = top_models
        # Количество эпох
        self.num_epoch = num_epoch

    # coeff_range - рэнджи коэффицентов (откуда до куда меняются, например -2 < x < 2)
    # models - стартовые модели
    def train(self, solver, coeff_range, models=[]):
        models = models
        for _ in range(self.models_per_round - len(models)):
            models.append(Model.random(coeff_range))

        print(models)

        for epoch in range(self.num_epoch):
            scores = [(model.get_score(solver).score(), model) for model in models]
            # Массив пар 
            best = sorted(scores, key=lambda score: score[0], reverse=True)
            best_models = [model[1] for model in best[:self.top_models]]
            # Количество мутированных моделей
            mutated_models_num = (self.models_per_round - self.top_models)//2
            # Количество скрещенных моделей
            crossed_models_num = self.models_per_round - self.top_models - mutated_models_num

            mutated_models = [copy.deepcopy(model).mutate(coeff_range, 0.2) for model in best_models][:mutated_models_num]
            crossed_models = []
            for _ in range(crossed_models_num):
                i = random.randint(0, len(best_models)-1)
                j = random.randint(0, len(best_models)-1)
                crossed = Model.cross(best_models[i], best_models[j])
                crossed_models.append(crossed)

            best_models.extend(mutated_models)
            best_models.extend(crossed_models)

            print(f"Epoch: {epoch}, best_model: {best_models[0]}, best_score: {scores[0][0]}")
            models = best_models
        
        return models[:self.top_models]

def train(words, models=[]):
    solver = Solver(words)
    gen = Genetics(10, 3, 4)
    best = gen.train(solver, coeff_range=[(-1, 1), (-1, 1), (-1, 1), (-0.5, 0.5), (-0.5, 0.5)], models=models)[0]
    return best

def play_and_save(model, solver):
    game = model.get_score(solver)
    board = game.board_str()
    with open("board.txt", 'w') as f:
        f.write(board)
        f.write(str(best))
    return game

if __name__ == '__main__':
    solver = Solver(WORDS[0:500])
    models = [
        Model([-0.35653157896755705, 0.012437856571482664, 0.6395248802370185, -0.3339694249653534, 0.40183299512230386]),
        Model([-0.35653157896755705, 0.13024319608070142, 0.6395248802370185, -0.3339694249653534, 0.5]),
        Model([0.5, 0., 1, 0.2, 0.2])]
    best = models[0]
    #game = play_and_save(best, solver)
    game = best.get_score(solver)
    for word in game.words:
        print(word.id, word.pos, word.dir)
    with open('tower.json', 'w') as f:
        json.dump(game.board, f, ensure_ascii=False)
    # id    pos      dir
    # 8  [0, 0, 5]  X 2
    # 9  [4, 0, 11] Z 1
    # 36 [6, 0, 7] Z 1
    # 30 [3, 0, 0] X 2

    #play_and_save(best, solver)
    #best = train(WORDS[500:550], models)

