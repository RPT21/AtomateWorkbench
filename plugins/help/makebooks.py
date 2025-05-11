import sys
import os
import time
import shutil
from fnmatch import *
from zipfile import *

_ignoreList = ["CVS", ".*"]

def setIgnore(ignoreList):
    global _ignoreList
    _ignoreList = ignoreList

def makeFromFile(filename):
    print("makeFromFile", filename)
    
    if not os.path.exists(filename):
        print("File '%s' does not exist" % filename)
        return 0
        
    f = open(filename, "r")
    lines = [s.strip() for s in f.readlines()]
    f.close()
    
    #map(make, lines)
    make(lines)


def make(bookList):
    """Make all the books directories passed in as a list"""
    print("make", bookList)
    
    for book in bookList:
        makeBook(book)
        
def matches(filename):
    global _ignoreList
    
    for ig in _ignoreList:
        if fnmatch(filename, ig):
            return True
            
    return False
        
def makeBook(book):
    topDir = os.path.dirname(book)
    #bookDir = os.path.join(topDir, book
    bookBase = os.path.basename(book)
    bookName = "%s.%s"%(bookBase, "zip")
    fullpath = os.path.join(topDir, bookName)
    
    print("top dir:", topDir)
    print("book name:", bookName)
    print("\t", fullpath)
    
    #zf = ZipFile( fullpath, 'w' )
    
    for filename in os.listdir(book):
        print("comp:", filename)
        if matches(filename):
            print("!doh")
            continue
        
    
    #zf.close()
    
    
    


if __name__ == '__main__':
    i = 1
    if len(sys.argv) < 2:
        print("specify filename or list of books with '-books book1,book2,etc' argument")
        sys.exit(13)
    
    
    if sys.argv[i] == "-books":
        if len(sys.argv) < 3:
            print("Error, need to specify book list")
            sys.exit(13)
        
        books = sys.argv[i+1].split(",")
        make(books)
        sys.exit(0)
        
    makeFromFile(sys.argv[i])
    