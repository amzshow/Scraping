import threading
import requests
import urllib
import bs4
import sys
import os
import re

MAX_THREADS = 100

def isFolderNameValid(name):
    return True if re.search('^(\w+\.?)*\w+$', '.hello') else False

def getNameAndImageURL(html):
    soup = bs4.BeautifulSoup(html, 'lxml')
    folderName = soup.find('div', {'id': 'info'}).find('h1').get_text()
    if not isFolderNameValid(folderName):
        folderName = re.sub('[\*\\|/"?<>.^.$\.{2,}]+', '', folderName)
        folderName = re.sub('\.+$', '', folderName)
    urls = [x.find('img')['data-src'].replace('t.n', 'i.n').replace('t.', '.') for x in soup.find_all('div', 'thumb-container')]
    files = [x.split('/')[-1] for x in urls]
    return folderName, urls, files
    
def downloadImage(url, folder, name):
    while True:
        try:
            urllib.request.urlretrieve(url, folder + '\\' + name)
            break
        except:
            pass
    
def downloadImages(urls, folder, names):
    threads = []
    count = 0
    for count in range(len(urls)):
        if names[count] not in os.listdir(folder):
            thread = threading.Thread(target = downloadImage, args = (urls[count], folder, names[count]))
            threads.append(thread)
    runningThreads = []
    downloaded = 0
    if(len(threads) == 0):
        print('\nImages already exist... Skipping...')
        return
    print('Downloading ' + folder + '\n')
    while True:
        if len(runningThreads) >= MAX_THREADS:
            continue
        if len(threads) > 0:
            thread = threads[0]
            threads.remove(thread)
            thread.start()
            runningThreads.append(thread)
        for thread in runningThreads:
            if not thread.isAlive():
                runningThreads.remove(thread)
                downloaded += 1
                print('\rCompleted:\t' + str(downloaded) + '\t/\t' + str(len(urls)), end = '')
        if len(runningThreads) == 0 and len(threads) == 0:
            break
    print('\n\nDownload Complete')

def nHentai(source):
    try:
        urlCheck = re.search('nhentai[a-zA-Z\./]+([0-9]+)', source, re.IGNORECASE)
        if(urlCheck):
            source = urlCheck.group(1)
        while True:
            try:
                r = requests.get('https://nhentai.net/g/' + source, timeout = 4)
                break
            except:
                pass
        folderName, imageURLs, imageFiles = getNameAndImageURL(r.text)
        if folderName not in os.listdir():
            os.mkdir(folderName)    
        downloadImages(imageURLs, folderName, imageFiles)
    except:
        print("\n\nError while downloading " + source)
        pass
    
args = sys.argv

if len(args) > 1:
    for arg in args[1:]:
        nHentai(arg)
    sys.exit(1)
    
if 'input.txt' in os.listdir():
    f = open('input.txt', 'r')
    data = []
    for line in f:
        data.append(line.strip())
    f.close()
    for d in data:
        nHentai(d)
    

#nHentai('https://nhentai.net/g/203371/')