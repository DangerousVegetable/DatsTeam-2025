import copy
import random
from model import Model
from words import words

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
    def train(self, words, coeff_range, models=[]):
        models = models
        for _ in range(self.models_per_round - len(models)):
            models.append(Model.random(coeff_range))

        print(models)

        for epoch in range(self.num_epoch):
            scores = [(model.get_score(words), model) for model in models]
            # Массив пар 
            best = sorted(scores, key=lambda score: score[0])
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

            print(f"Epoch: {epoch}, best_model: {best_models[0]}")
            models = best_models

if __name__ == '__main__':
    gen = Genetics(30, 10, 100)
    gen.train([], coeff_range=[(-2, 2), (-2, 2)])

