# encoding: utf-8
"""
Created on Thu Sep  1 10:46:48 2022

@author: User
"""
import time
import sys
import shutil
import configparser
from functools import partial
import os
from multiprocessing import Pool, freeze_support
import urllib.request
import requests
import urllib.parse
import re
from bs4 import BeautifulSoup

# read config
cp = configparser.RawConfigParser()
cp.read("foo_config.txt")
ext = cp['extensions']['ext']
addr = cp['address']['addr']
filedate = int(cp['filename']['date'])
postname = int(cp['filename']['postname'])
username = int(cp['filename']['username'])
foo = "https://foo.net"
boo = "https://boo.net"
def finditems(link, switch, parentdir, domain, username):

    # set variables
    count = 0
    itemlist = []

    # parse url
    fullurl = link
    itempages = urllib.request.urlopen(fullurl)
    itemsoup = BeautifulSoup(itempages, 'html.parser')

    #parse post information
    post_title = itemsoup.select("h1.post__title")[0].text.strip()
    post_date = "[" + re.split(' ', itemsoup.select("time")[0].text.strip())[0] + "]"
    folder_title = post_date + post_title
    folder_title = re.sub('[\?\\\/\:\|\<\>\*\"\\n\\t\\0]', '', folder_title)

    # post download mode
    if not switch:
        username = itemsoup.select("a.post__user-name")[0].text.strip().replace(" ","")
        if addr == '':
            finaldir = os.path.dirname(os.getcwd())
        else:
            try:
                finaldir = addr
            except FileNotFoundError:
                finaldir = os.path.dirname(os.getcwd())
        # finaldir = os.path.dirname(finaldir, folder_title)
        itemhref = [i['href'] for i in itemsoup.find_all('a', href=True)]
        newitemlist = []
        newtemplist = list(filter(re.compile('^.*data.*$').match, itemhref))
        newtemplist = list(set(newtemplist))
        longest_first = sorted(ext, key=len, reverse=True)
        r = re.compile(r'(?:{})'.format('|'.join(map(re.escape, longest_first))))
        newtemplist = list(filter(r.search, newtemplist))
        for j in newtemplist:
            count += 1
            item_fullurl = urllib.parse.urljoin(domain, j)
            newitemlist.append(item_fullurl)
        itemlist.extend(newitemlist)
        return([folder_title,itemlist,count],count, finaldir, username)

    # user download mode
    else:
        finaldir = os.path.join(parentdir, folder_title)


        itemhref = [i['href'] for i in itemsoup.find_all('a', href=True)]
        newitemlist = []
        newtemplist = list(filter(re.compile('^.*data.*$').match, itemhref))
        newtemplist = list(set(newtemplist))
        longest_first = sorted(ext, key=len, reverse=True)
        r = re.compile(r'(?:{})'.format('|'.join(map(re.escape, longest_first))))
        newtemplist = list(filter(r.search, newtemplist))
        for j in newtemplist:
            count += 1
            item_fullurl = urllib.parse.urljoin(domain, j)
            newitemlist.append(item_fullurl)
        itemlist.extend(newitemlist)
        return([folder_title,itemlist,count],count)

def download(link, path, user, totalcount, postswitch):
    count = 0
    if postswitch:
        if not os.path.exists(path):
            os.makedirs(path)
    key = link[0]
    postpath = os.path.join(path, key)
    if not os.path.exists(postpath):
        os.makedirs(postpath)
    date = key.split(']')[0]+']'
    post_title = '[%s]' % key.split(']')[1]
    for j in link[1]:
        count += 1
        item_name = str(count) + '.' + os.path.basename(j).split('?')[-1].split('.')[-1]
        if postname == 1:
            item_name = (post_title) + item_name
        if username == 1:
            item_name = ("[%s]" % user) + item_name
        if filedate == 1:
            item_name = date + item_name
        itempath = os.path.join(postpath, item_name).encode('utf-8')
        with requests.get(j, stream = True) as r:
            with open(itempath.decode('utf-8'), mode = "wb+") as f:
                shutil.copyfileobj(r.raw, f)
        print(str(count)+'/'+str(link[2]), flush=True)
    return(count, postpath)

def handler2(path, links, user, totalcount):
    print('downloading to: '+path)
    if not os.path.exists(path):
        os.makedirs(path)
    with Pool(4) as pool:
        dl = partial(download, path = path, user = user, totalcount = totalcount, postswitch = False)
        for result in pool.map(dl, links):
            pass
        pool.close()
        pool.join()

def findposts():
    theurl = input("input link:")
    if re.match('^(?!.*(foo.net|boo.net)).*$', theurl):
        return(False)
    else:
        if re.match('^.*\?o=.*$', theurl):
            theurl = theurl.split('?')[0]
        else:
            if re.match('^.*post.*$', theurl):
                if re.match('^.*foo.net.*$', theurl):
                    domain = foo
                    return(theurl,domain)
                else:
                    if re.match('^.*boo.net.*$', theurl):
                        domain = boo
                        return(theurl,domain)
    if re.match('^.*foo.net.*$', theurl):
        domain = foo
    else:
        if re.match('^.*boo.net.*$', theurl):
            domain = boo
        else:
            return(False)
    start1 = time.time()
    thepage = urllib.request.urlopen(theurl)
    soup = BeautifulSoup(thepage, 'html.parser')
    username = soup.find("span", itemprop = 'name').text
    project_href = [i['href'] for i in soup.find_all('a', href=True)]
    try:
        lastpagestart = int(re.split('=', project_href[-8])[1])
        nop = int(lastpagestart/25+1)
    except IndexError:
        lastpagestart = 0
        nop = 1

    startindex = 0
    itemlist = []
    for i in range(nop):
        pageindex = "?o=" + str(startindex)
        fullurl = urllib.parse.urljoin(theurl, pageindex)
        startindex += 25
        itempage = urllib.request.urlopen(fullurl)
        itemsoup = BeautifulSoup(itempage, 'html.parser')
        itemhref = [i['href'] for i in itemsoup.find_all('a', href=True)]
        templist = itemhref[14:-6]
        newitemlist = []
        newtemplist = list(filter(re.compile('^(?!.*\?o=).*$').match, templist))
        for j in newtemplist:
            if re.match('^.*user.*post.*$', j):
                newitemlist.append(urllib.parse.urljoin(domain, j))
        itemlist.extend(newitemlist)
    itemlist = list(set(itemlist))
    end1 = time.time()
    print('posts scrape elapsed: '+str(end1-start1))
    print('number of posts: '+str(len(itemlist)))
    return(itemlist, username, domain)

def handler(ilist, username, domain):
    totallist = []
    if addr == '':
        current_directory = os.path.dirname(os.getcwd())
        userdir = os.path.join(current_directory, username)
    else:
        try:
            userdir = os.path.join(addr, username)
        except FileNotFoundError:
            current_directory = os.path.dirname(os.getcwd())
            userdir = os.path.join(current_directory, username)
    if not os.path.exists(userdir):
        os.makedirs(userdir)
    with Pool(4) as pool:
        count = 0
        fi = partial(finditems, parentdir = userdir, switch = True, domain = domain, username = username)

        # call the same function with different data in parallel
        for result in pool.map(fi, ilist):
            if result[1] != 0:
                totallist.append(result[0])
                count += result[1]

        pool.close()
        pool.join()
        return(totallist, count, userdir)

def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total

if __name__ == '__main__':
    freeze_support()
    exit_switch = False
    while exit_switch is False:
        ilist = findposts()
        if ilist is False:
            print('link not supported')
        else:
            scrape_switch = input('scrape all files?(Y/N)')
            if scrape_switch == 'y' or scrape_switch == 'Y':
                # post download
                if isinstance(ilist[0], str):
                    start = time.time()
                    final = finditems(ilist[0], False, "", ilist[1], "")
                    finallist = final[0]
                    filecount = final[1]
                    postpath = final[2]
                    postuser = final[3]
                    end = time.time()
                    print('number of files: '+str(filecount))
                    print('item scrape elapsed: '+str(end-start))
                    if filecount != 0:
                        download_switch = input('download files?(Y/N)')
                        if download_switch == 'y' or download_switch == 'Y':
                            dlstart = time.time()
                            postpath = download(finallist, postpath, postuser, filecount, True)[1]
                            dlend = time.time()
                            print(str(round((get_dir_size(postpath)/1024/1024),2))+'MB downloaded')
                            print('download elapsed: '+str(dlend-dlstart))
                # user download
                else:
                    start = time.time()
                    final = handler(ilist[0], ilist[1], ilist[2])
                    finallist = final[0]
                    filecount = final[1]
                    userpath = final[2]
                    end = time.time()
                    print('number of non-fileless posts: '+str(len(finallist)))
                    print('number of files: '+str(filecount))
                    print('item scrape elapsed: '+str(end-start))
                    download_switch = input('download files?(Y/N)')
                    if download_switch == 'y' or download_switch == 'Y':
                        dlstart = time.time()
                        handler2(userpath, finallist, ilist[1], filecount)
                        dlend = time.time()
                        time.sleep(1)
                        print(str(round((get_dir_size(userpath)/1024/1024),2))+'MB downloaded')
                        print('download elapsed: '+str(dlend-dlstart))

                exit_input = input("exit?(Y/N)")
                if exit_input == 'y' or exit_input == 'Y':
                    exit_switch = True
            else:
                exit_input = input("exit?(Y/N)")
                if exit_input == 'y' or exit_input == 'Y':
                    exit_switch = True
    print('exited program')
