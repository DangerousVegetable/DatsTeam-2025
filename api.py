import requests
import datetime
from time import sleep
import json

from secret import TOKEN 
from solver import Solver
from model import Model

class Words:
    def __init__(self, mapSize, nextTurnSec, roundEndsAt, shuffleLeft, turn, usedIndexes, words):
        self.mapSize = mapSize
        self.nextTurnSec = nextTurnSec
        self.roundEndsAt = roundEndsAt
        self.shuffleLeft = shuffleLeft
        self.turn = turn
        self.usedIndexes = usedIndexes
        self.words = words

class API:
    def __init__(self, test=True):
        self.url = 'https://games.datsteam.dev/api'
        if test:
            self.url = 'https://games-test.datsteam.dev/api'
        
        self.headers = {
            "X-Auth-Token": TOKEN
        }

        self.error_number = 0

    def get_request(self, endpoint):
        try:
            response = requests.get(self.url + endpoint, headers=self.headers)
        except Exception as e:
            print('get_request failed with exception: ' + str(e))
            return None
        if not response.ok:
            print(response.json(), self.url)
            save(response.json(), f'errors/error{self.error_number}.txt')
            self.error_number += 1
            return None
            
        return response.json()
    
    def post_request(self, endpoint, dto=None):
        try:
            if dto:   
                response = requests.post(self.url + endpoint, headers=self.headers, json=dto)
            else:
                response = requests.post(self.url + endpoint, headers=self.headers)
        except Exception as e:
            print('post_request failed with exception: ' + str(e))
            return None
        
        if not response.ok:
            print(response.json())
            save(response.json(), f'errors/error{self.error_number}.txt')
            self.error_number += 1
            return None
        return response.json()

    def get_words(self):
        data = self.get_request('/words')
        return data
    
    def get_rounds(self):
        data = self.get_request('/rounds')
        return data
    
    def get_towers(self):
        data = self.get_request('/towers')
        return data
    
    def shuffle(self):
        data = self.post_request('/shuffle')
        return data
    
    def build(self, words, done=True):
        dto = {
            'done': done,
            'words': words
        }
        data = self.post_request('/build', dto)
        return data
    
def dump_board(game):
    for word in game.words:
        print(word.id, word.pos, word.dir)
    with open('tower.json', 'w') as f:
        json.dump(game.board, f, ensure_ascii=False)

class Scheduler:
    def __init__(self, test=True):
        self.api = API(test)
        self.nextTurnSec = 0
        self.test = test
        self.all_words = self.api.get_words()['words']

    def operate(self, tower = 0):
        if tower*100 > len(self.all_words):
            return
        
        # Вызов функции которая выдает нужные слова
        solver = Solver(self.all_words[500:1000])
        model = Model([-0.35653157896755705, 0.012437856571482664, 0.6395248802370185, -0.3339694249653534, 0.40183299512230386])
        #built_limit = 10 if self.test else 10000
        game = model.get_score(solver, 20)
        dump_board(game)
        words = []
        for w in game.words:
            dir = 0
            if w.dir == 0:   # X
                dir = 2
            elif w.dir == 1: # Y
                dir = 3
            else:            # Z
                dir = 1
            pos = [w.pos[0], w.pos[1], w.pos[2]]
            lol = {
                'dir': dir,
                'id': w.id + tower*100,
                'pos': pos,
            }
            words.append(lol)

        data = self.api.build(words)
        while data == None:
            # self.nextTurnSec = self.api.get_words().nextTurnSec
            # sleep(self.nextTurnSec)
            sleep(1)
            data = self.api.build(words)

        self.nextTurnSec = self.api.get_words()['nextTurnSec']
        sleep(self.nextTurnSec)
        self.operate(tower+1)

    def send_request(self):
        data = self.api.get_towers()
        save(data, 'towers')
        print(data)

def save(data, name):
    try:
        with open(f'{name}.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing map to file: {e}")

if __name__ == '__main__':
    app = Scheduler()
    Scheduler(True).operate(2)
# Scheduler(True).send_request()