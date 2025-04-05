import json

class Solver:
    def __init__(self, words):
        self.words = words
        # Init connections
        self.init_connections(words)
        self.init_stats(words)

    def calculate_common(self, w1, w2):
        # w1: __АБОБА__
        # w2: _ШАЛОПАЙ_
        total = 0
        for shift in range(-len(w2), len(w1)):
            common = {}
            for i in range(len(w2)):
                j = shift + i
                if j < 0 or j >= len(w1):
                    continue
                a = w1[j]
                b = w2[i]
                for l, _ in self.connections.get(a, {}).get(b, {}).items():
                    common[l] = common.get(l, 0) + 1
            max_num = 0
            for _, num in common.items():
                max_num = max(max_num, num-1)
            total += max_num
            #print(shift, common)
        return total


    def init_stats(self, words):
        stats = [(0,0) for _ in words]
        max_a = 0
        max_b = 0
        for id, word in enumerate(words):
            print(f"__ {id} __")
            a = 0
            b = 0
            for id2, w in enumerate(words):
                if id == id2:
                    continue
                a += self.calculate_common(word, w)
                b += self.calculate_common(w, word)
            stats[id] = (a, b)
            max_a = max(a, max_a)
            max_b = max(b, max_b)
        self.stats = [(a / max_a, b / max_b) for (a,b) in stats]


    def init_connections(self, words):
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
                            
            self.connections = map 
    
    def load(words):
        solver = Solver([])
        solver.words = words
        solver.init_connections(words)
        with open('solver.json', 'r', encoding='utf-8') as file:
            stats = json.load(file)
            solver.stats = stats
            return solver
        
    def save(self):
        try:
            with open('solver.json', 'w', encoding='utf-8') as file:
                json.dump(self.stats, file, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing map to file: {e}")

if __name__ == "__main__":
    from words import words as WORDS
    #solver = Solver(WORDS)
    #w1 = WORDS[0]
    #w2 = WORDS[1]
    #print(w1, w2, solver.calculate_common(w1, w2))
    #print(solver.stats)
    #solver.save()

    solver2 = Solver.load(WORDS)
    print(solver2.stats)
    assert(len(solver2.stats) == len(WORDS))