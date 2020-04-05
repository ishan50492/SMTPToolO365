import markovify
import io
import time
from multiprocessing import Pool, TimeoutError
import timeit
import reading_file
import random

class TextGenerator(object):
    text_model = None
    text_model_file_path = "./Content/news_articles.txt"

    def __init__(self, text_model_file_path=None):
        self.text_model_file_path = text_model_file_path or self.text_model_file_path
        #load file into memory
        text=reading_file.read_file(self.text_model_file_path)
        
        self.text_model = markovify.Text(text)

    # generate_text(num_strs, length) - generates number of sentences at variable length
    # params: 
    #   num_strs - number of strings to generate per paragraph
    #       defaults: 1
    #   length - limit strings to a specific length 
    #       defaults: 0 = infinite
    # returns:
    #   list of strings
    def generate_text(self, num_strs=1, length=0):
        strings = list()

        for i in range(num_strs):
            if(length == 0):
                strings.append(self.text_model.make_sentence())
            else:
                strings.append(self.text_model.make_short_sentence(length))
        
        return strings

#wrapper and diagprint for diagnostics for test text generation
def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

def diagprint(func, *args, **kwargs):
    wrapped = wrapper(func, *args, **kwargs)
    #t1 = timeit.timeit(wrapped, number=1)
    print(wrapped())
    #return t1

if __name__ == "__main__":
    tg = TextGenerator()
    total_time = 0
    # total_time += diagprint(tg.generate_text, num_strs=1,length=0)
    # total_time += diagprint(tg.generate_text, num_strs=15,length=0)
    # total_time += diagprint(tg.generate_text, num_strs=3,length=0)
    # total_time += diagprint(tg.generate_text, num_strs=5,length=0)
    # total_time += diagprint(tg.generate_text, num_strs=1,length=65)

    for i in range(50):
        diagprint(tg.generate_text, num_strs=random.randrange(1, 20), length=0)

