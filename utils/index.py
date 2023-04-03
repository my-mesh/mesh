def get_index(data, id, search):
    for index, element in enumerate(data):
        if (element[search] == id):
            return index
    
    return -1