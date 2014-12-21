#!/usr/bin/env python

#author: wowdd1
#mail: developergf@gmail.com
#data: 2014.12.07

from spider import *

class GithubSpider(Spider):
    lang_list = [
        "C",
        "C++",
        "C#",
        "Clojure",
        "CoffeeScript",
        "Common Lisp",
        "CSS",
        "D",
        "Dart",
        "Emacs Lisp",
        "Erlang",
        "F#",
        "Go",
        "Haskell",
        "Java",
        "JavaScript",
        "Julia",
        "Lua",
        "Matlab",
        "Objective-C",
        "Perl",
        "PHP",
        "Python",
        "R",
        "Ruby",
        "Scala",
        "Scheme",
        "Shell",
        "SQL",
        "Swift"]

    result = ""
    def __init__(self):
        Spider.__init__(self)
        self.school = "github"

    def processGithubData(self, lang, large_than_stars, per_page):
        file_name = self.get_file_name("eecs-" + lang, self.school)
        file_lines = self.countFileLineNum(file_name)
        f = self.open_db(file_name + ".tmp")
        url = "https://api.github.com/search/repositories?page=1&per_page=" + per_page + "&q=stars:>" + large_than_stars +"+language:" +  lang.replace("#","%23").replace("+","%2B") + "&sort=stars&order=desc"
        print "processing " + lang + " " + url
        r = requests.get(url)
        dict_obj = json.loads(r.text)
        self.count = 0
        for (k, v) in dict_obj.items():
            if k =="message":
                self.result += lang + " "
                self.cancel_upgrade(file_name)
                return
            if k == "items":
                for item in v:
                    data = str(item['stargazers_count']) + " " + item["name"] + " " + item['html_url']
                    print data
                    self.write_db(f, str(item["stargazers_count"]) + "-" + str(item['forks_count']), item["name"], item['html_url'])
                    self.count = self.count + 1
 
        self.close_db(f)
        if self.count > 0:
            self.do_upgrade_db(file_name)
            print "before lines: " + str(file_lines) + " after update: " + str(self.count) + " \n\n"
        else:
            self.cancel_upgrade(file_name)
            print "no need upgrade\n"

    def processGithubiUserData(self, location, followers, per_page):
        file_name = self.get_file_name("eecs-" + location, self.school + "-user")
        file_lines = self.countFileLineNum(file_name)
        f = self.open_db(file_name + ".tmp")
        if location == "":
            url = "https://api.github.com/search/users?page=1&per_page=" + per_page + "&q=followers:>" + followers
        else:
            url = "https://api.github.com/search/users?page=1&per_page=" + per_page + "&q=followers:>" + followers + "+location:" + location
            
        print "processing " + url
        r = requests.get(url)
        dict_obj = json.loads(r.text)
        self.count = 0
        for (k, v) in dict_obj.items():    
            if k == "items":
                for item in v:
                    data = str(item["id"]) + " " + item["login"] + " " + item["url"]
                    print data
                    self.write_db(f, item["type"] + "-" + str(item["id"]), item["login"], item["url"])
                    self.count = self.count + 1

        self.close_db(f)
        if self.count > 0:
            self.do_upgrade_db(file_name)
            print "before lines: " + str(file_lines) + " after update: " + str(self.count) + " \n\n"
        else:
            self.cancel_upgrade(file_name)
            print "no need upgrade\n"
    def do_work(self):
        i = 0
        for lang in self.lang_list:
            i += 1
            self.processGithubData(lang, '1000','70')
            if i % 10 == 0:
                print "wait 45s..."
                time.sleep(45)

        if len(self.result) > 1:
            print self.result + " is not be updated"

        print "get user data..."
        self.processGithubiUserData("", '1000', "50")
        self.processGithubiUserData("china", '1000', "50")
        
        
start = GithubSpider()
start.do_work()