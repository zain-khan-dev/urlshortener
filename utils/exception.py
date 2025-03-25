class RedisKeyNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)



class RedisKeyExistsException(Exception):
    def __init__(self, *args):
        super().__init__(*args)