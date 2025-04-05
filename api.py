import requests
import datetime
from time import sleep

from secret import TOKEN 

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

    def get_request(self, endpoint):
        try:
            response = requests.get(self.url + endpoint, headers=self.headers)
        except Exception as e:
            print('get_request failed with exception: ' + str(e))
            return None
        if not response.ok:
            print(response.json(), self.url, self.headers)
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
    
class Scheduler:
    def __init__(self, test=True):
        self.api = API(test)
        self.nextTurnSec = 0

    def operate(self):
        # Вызов функции которая выдает нужные слова
        # words = create_board()
        words = [{}]
        data = self.api.build(words)
        while data == None:
            self.nextTurnSec = self.api.get_words().nextTurnSec
            sleep(self.nextTurnSec)
            data = self.api.build(words)

        self.nextTurnSec = self.api.get_words().nextTurnSec
        sleep(self.nextTurnSec)
        self.operate()

    def send_request(self):
        data = self.api.get_words()
        print(data)

app = Scheduler()

Scheduler(test=True).send_request()