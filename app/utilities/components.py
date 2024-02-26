from loguru import logger

class MyComponent:
    def __init__(self, logger):
        self.logger = logger

    def do_something(self):
        self.logger.info("Doing something...")
    
    def do_thing(self):
        self.logger.info("something...")

