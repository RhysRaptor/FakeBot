import json
import os

class JsonStorage:
    def __init__(self, path):
        path = os.path.abspath(path)
        try:
            with open(path) as json_file:
                self.json = json.load(json_file)
        except:
            self.json = {}

        self.path = path

    def __getitem__(self, x):
        if x not in self.json:
            self.json[x] = {}

        return self.json[x]
    
    def __setitem__(self, key, value):
        self.json[key] = value

    def writeFile(self):
        with open(self.path, 'w') as fp:
            json.dump(self.json, fp)


GlobalJsonStorage = None

class JsonInteractor:
    global GlobalJsonStorage

    def __init__(self, section):
        self.section = section
        self.storage = None
        self.update()

    def __getitem__(self, x):
        if x not in self.storage:
            self.storage[x] = {}
            
        return self.storage[x]
    
    def __setitem__(self, key, value):
        self.storage[key] = value

    def update(self):
        self.storage = GlobalJsonStorage[self.section]
        if (self.storage is None):
            raise Exception("Invalid section!")

    def read(self, target: list):
        ret = self.storage
        for x in target:
            ret = ret[x]
         #get re(k)t nerd
        
        return ret

    def write(self, target: list, insert):
        edit = self.storage
        for x in target[0:-1]:
            edit = edit[x]

        edit[target[-1]] = insert
    
    def save(self):
        GlobalJsonStorage[self.section] = self.storage
        GlobalJsonStorage.writeFile()