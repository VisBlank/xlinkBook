#!/usr/bin/env python

# -*- coding: utf-8-*-  

import getopt
import time
import re
import os,sys
reload(sys)
sys.setdefaultencoding('utf-8')
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from bs4 import BeautifulSoup
import requests
import webbrowser

def getToc(pdfPath):
    infile = open(pdfPath, 'rb')
    parser = PDFParser(infile)
    document = PDFDocument(parser)

    toc = list()
    for (level,title,dest,a,structelem) in document.get_outlines():
        toc.append((level, title))

    return toc

def toOutline(source):
    if source.endswith('.pdf') and source.startswith('http') == False:
       for item in getToc(source):
           print item[1]
    elif source.startswith('http'):
        url = 'https://gsnedders.html5.org/outliner/process.py?url=' + source
        webbrowser.open(url)
        #r = requests.get('https://gsnedders.html5.org/outliner/process.py?url=' + source) 
        #soup = BeautifulSoup(r.text)
        #for li in soup.find_all('li'):
        #    print li.text.strip()
        

def main(argv):
    source = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:],'i:', ['input'])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)


    for o, a in opts:
        if o in ('-i', '--input'):
            source = a

    toOutline(source)

if __name__ == '__main__':
    main(sys.argv)
