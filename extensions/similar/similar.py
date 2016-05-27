#!/usr/bin/env python

import sys, os
from extensions.bas_extension import BaseExtension
from utils import Utils
from record import PaperRecord, Category
import cPickle as pickle
import requests
from bs4 import BeautifulSoup

class Similar(BaseExtension):

    papers_dict = {}
    sim_dict = {}
    def __init__(self):
        BaseExtension.__init__(self)
        self.utils = Utils()
        self.category_obj = Category()

    def loadPapers(self):
        if len(self.papers_dict) > 0:
            return
        files = os.listdir('db/eecs/papers/arxiv/')
        for item in files:
            f = open('db/eecs/papers/arxiv/' + item, 'rU')
            lines = f.readlines()
            f.close()
            for line in lines: 
                record = PaperRecord(line)
                self.papers_dict[self.getPid(record.get_url())] = record


    def loadSimDict(self):
        if len(self.sim_dict) == 0:
            self.sim_dict = pickle.load(open("analysis/tfidf/sim_dict.p", "rb"))

    def getPid(self, url):
        return url[url.rfind('/') + 1 : ].replace('.pdf', '').strip()

    def excute(self, form_dict):
        rID = form_dict['rID'].encode('utf-8')
        fileName = form_dict['fileName']
        record = self.utils.getRecord(rID, path=fileName[0 : fileName.rfind('/')])
        if rID.startswith('arxiv'):
            pid = self.getPid(record.get_url())

            self.loadPapers()
            self.loadSimDict()
            #print sim_dict
            if self.papers_dict.has_key(pid) == False:
                return ''
            print 'request:'
            print pid + ' ' + self.papers_dict[pid].get_title()
            if pid in self.sim_dict:
                print 'resutl:'
                for k in self.sim_dict[pid]:
                    print k + ' ' + self.papers_dict[k].get_title()
                return self.genHtml(pid)
        elif self.category_obj.match(record.get_describe(), self.category_obj.website) or self.category_obj.containMatch(rID[0 : rID.find('-')].strip() , self.category_obj.engin):
            return self.genWebsiteHtml(record.get_title().strip())
        return ''

    def genWebsiteHtml(self, key):
        html = '<div class="ref"><ol>'
        count = 0
        cookies = dict(unsafe='True')
        page = ''
        page_num = 6
        page = 'http://www.xmarks.com/topic/' + key
        nextpage = ''
        page_count = 0
        for i in range(0, page_num):
            page_count += 1
            if nextpage != '':
                page = nextpage.replace('2', str(page_count))

            print 'request ' + page
            r = requests.get(page, cookies=cookies)
            if r.status_code != 200:
                break
            soup = BeautifulSoup(r.text)
            #print r.text
            for div in soup.find_all('div', class_='content'):
                count += 1
                html += '<li><span>' + str(count) + '.</span><p><a target="_blank" href="' + div.a['href'] + '">' + div.a.text + "</a></p></li>"
            nextDiv = soup.find('div', class_='site-pagination')
            if nextDiv != None and nextpage == '':
                nextpage = 'http://www.xmarks.com' + nextDiv.a['href']
            if nextDiv == None:
                break
        html += "</ol></div>"
        return html

    def genHtml(self, pid):
        html = '<div class="ref"><ol>'
        records = []
        for k in self.sim_dict[pid]:
            records.append(self.papers_dict[k])
        #self.utils.sortRecords(records)
        #records = records[1 : ]
        count = 0
        for record in records:
            #html += '<li><span>' + record.get_id().strip() + '</span><br/>'
            thumbs = "http://www.arxiv-sanity.com/static/thumbs/" + self.getPid(record.get_url()) + "v1.pdf.jpg"
                    
            authors = record.get_author().split(',')
            categorys = record.get_category().split(' ')
            date_cat =  record.get_published() + "&nbsp;&nbsp; " + self.genListHtml(categorys, "category:")
            count += 1
            html += '<li><span>' + str(count) + '</span>'
            html += '<p><a target="_blank" href="' + record.get_url() + '">' + record.get_title() + '</a><p><div>' + self.genListHtml(authors, "author:") + '</div><div>' + date_cat + '</div><image src="' + thumbs + '"></image><div>' + record.get_summary() + "<div></li><br/>"
        html += "</ol></div>"
        return html

    def genListHtml(self, alist, category):
        html = ''
        for item in alist:
            if item.strip() == "":
                continue
            html += '<a target="_blank" href="http://localhost:5000?db=eecs/papers/arxiv/&filter=' + category + item.strip().replace(' ', '%20') + '">'+ item.strip() + '</a>'
            if item != alist[len(alist) - 1]:
                html += ', '
            else:  
                html += ' '
 
        return html
       

    def check(self, form_dict):
        rID = form_dict['rID'].encode('utf-8')
        fileName = form_dict['fileName']
        record = self.utils.getRecord(rID, path=fileName[0 : fileName.rfind('/')])
        match_website = self.category_obj.match(record.get_describe(), self.category_obj.website) 
        match_engin = self.category_obj.containMatch(rID[0 : rID.find('-')].strip() , self.category_obj.engin)
        return rID.startswith('arxiv') or match_website or match_engin