from collections.abc import Sequence

class MyList(Sequence):
    
    def __init__(self):
        self._data = {}
        self._index = 0
        self._next_index = 0

    def append(self, *values):
        for value in values:
            self._data[self._index] = value
            self._index += 1
        
    def __len__(self):
        return self._index
    
    def __getitem__(self, item):
        return self._data[item]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._next_index >= self._index:
            raise StopIteration
    
        value = self._data[self._next_index]
        self._next_index += 1
        return value
        


if __name__ == '__main__':
    list = MyList()
    list.append('Maria', 'Lucas', "Carlos")
    list.append('João')
    print(list._data)
    print(list[0])
    print(len(list))
    for item in list:
        print(item)
