
def read_file(path):

    fp=open(path, encoding = 'utf8')
    text=fp.read()
    fp.close()

    return text

if __name__=="__main__":

    text=read_file("./Content/news_articles.txt")
    print(text)
