# coding:utf-8
from urllib import request
import requests
import json
import time
import math
import hashlib
import re
import sys
import importlib
import tkinter as tk
import tkinter.messagebox
import time,threading
from bs4 import BeautifulSoup
from queue import Queue
import os

#全局变量
var = ''
var1 = 0
var2 = 0
var3 = 0
path = './fileout'
Run_flag = False
title_q = Queue()
comment_count_q = Queue()
news_url_q = Queue()
en = ''
num = 0

def get_url(max_behot_time, AS, CP):
    url = 'https://www.toutiao.com/api/pc/feed/?category=news_society&utm_source=toutiao&widen=1' \
          '&max_behot_time={0}' \
          '&max_behot_time_tmp={0}' \
          '&tadrequire=true' \
          '&as={1}' \
          '&cp={2}' \
          '&_signature=pxpB2xAc.VAK8B9apKgvHKcaQa'.format(max_behot_time, AS, CP)
    return url


def get_ASCP():
    t = int(math.floor(time.time()))
    e = hex(t).upper()[2:]
    m = hashlib.md5()
    m.update(str(t).encode(encoding='utf-8'))
    i = m.hexdigest().upper()

    if len(e) != 8:
        AS = '479BB4B7254C150'
        CP = '7E0AC8874BB0985'
        return AS, CP
    n = i[0:5]
    a = i[-5:]
    s = ''
    r = ''
    for o in range(5):
        s += n[o] + e[o]
        r += e[o + 3] + a[o]

    AS = 'AL' + s + e[-3:]
    CP = e[0:3] + r + 'E1'
    print("AS:"+ AS,"CP:" + CP)
    return AS, CP


def download(title,comment_count, news_url):
    print('------------------------------开始下载----------------------------------')
    req = request.urlopen(news_url)
    if req.getcode() != 200:
        print('返回状态有错误,不继续解析')
        return 0
    res = req.read().decode('utf-8')
    pat1 = r'content:(.*?),'
    result = re.findall(pat1, res)
    if len(result) == 0:
        print ("文章无内容!!!")
        return 0
    p = re.compile(r'&lt;p&gt;[\s\S]*?&lt;/p&gt;')
    result = p.findall(str(result))
    title = title.replace(':', '')
    title = title.replace('"', '')
    title = title.replace('|', '')
    title = title.replace('/', '')
    title = title.replace('\\', '')
    title = title.replace('*', '')
    title = title.replace('<', '')
    title = title.replace('>', '')
    title = title.replace('?', '')
    with open(r'./fileout/' + title + '.txt', 'w',encoding='utf-8') as file_object:
        file_object.write('\t\t\t\t')
        file_object.write(title)
        file_object.write('\n')
        file_object.write('\t\t\t\t')
        file_object.write('评论数:')
        file_object.write(str(comment_count))
        file_object.write('\n')
        file_object.write('该新闻地址：')
        file_object.write(news_url)
        file_object.write('\n')
        for i in result:
            i = re.sub('&lt;p&gt;|&lt;/p&gt;','',i)
            i = re.sub('&lt;strong&gt;|&lt;/strong&gt;','',i)
            i = re.sub('&lt;img.*&gt;','',i)
            i = re.sub('&lt;br&gt;','',i)
            i = re.sub('&lt;span&gt;|&lt;/span&gt;','',i)
            file_object.write(i)
            file_object.write('\n')
     #print('正在爬取')


def get_item(url):
    global  var
    header ={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
    cookies = {'tt_webid':'6504211651658139150'}
    wbdata = requests.get(url, cookies=cookies,headers=header)
    wbdata2 = json.loads(wbdata.text)
    print("返回的json:",wbdata2)
    data = wbdata2['data']
    for news in data:
        title = news['title']
        news_url = news['source_url']
        news_url = 'https://www.toutiao.com' + news_url
        print('文章标题:',title," 文章url:",news_url)
        if 'ad_label' in news: #去除广告
            print('ad_label',news['ad_label'])
            continue
        if 'comments_count' in news:
            comments_count = news['comments_count']
            print('评论数:',comments_count)
            if comments_count < var:
                print('评论数不足不向下解析继续执行!!')
                continue
        else:
            print('无评论不向下解析')
            continue
        title_q.put(title)
        comment_count_q.put(comments_count)
        news_url_q.put(news_url)
        download(title_q.get(),comment_count_q.get(),news_url_q.get())
        time.sleep(2)


def thread_it(func):
	t = threading.Thread(target=func)
	t.setDaemon(True)
	t.start()
	
#供开始按钮调用
def show():
    global var
    global Run_flag
    global p
    Run_flag = True
    if var != "":
        print('----------------开始爬取文章-------------------')
        start_spider()
    else:
        tkinter.messagebox.showerror(title='错误',message='请输入要爬取内容的评论数,并点击确认')

#供停止按钮调用
def stop():
    global Run_flag
    Run_flag = False
    print('停止爬取内容')

#开启爬虫
def start_spider():
    print('开始执行爬虫')
    global title_q
    global comment_count
    global news_url_q
    global path
    global var1,var2,var3
    global Run_flag
    toutiao_flag = 0
    x = 0
    weibo_flag = 0
    all_flag = 0
    if var1.get() == 1:
        toutiao_flag = 1
        print('----------------爬取今日头条-------------------')
    else:
        pass
    if var2.get() == 1:
        print('----------------爬取微博----------------------')
        weibo_flag = 1
    else:
        pass
    if var3.get() == 1:
        all_flag = 1
        print('----------------爬取全部----------------------')
    else:
        pass
    while Run_flag:
        x+=1
        if toutiao_flag == 1:
            print('第{0}次：'.format(x))
            max_behot_time = 0
            AS, CP = get_ASCP()
            url = get_url(max_behot_time, AS, CP)
            print('json_url::',url)
            get_item(url)
            time.sleep(1)
    tkinter.messagebox.showinfo(title='完成',message='停止爬取数据，文件存储在'+path+'中,点击\' OK \'退出')
    exit()


#获取输入的爬去评论数
def get_str():
    global var
    va = en.get()
    if va != "" :
        print('要爬取内容的评论数:',va)
        var = int(va)
    else:
        tkinter.messagebox.showerror(title='错误',message='请输入要爬取内容的评论数')

def tkin_show():
    global en
    global var1
    global var2
    global var3
    top = tk.Tk(className='爬虫')
    top.geometry('400x140')
    var1=tk.IntVar()
    tk.Checkbutton(top,text='今日头条',bg='yellow',variable=var1,onvalue=1,offvalue=0,width=10).grid(row=0,sticky='W',column=0)
    var2=tk.IntVar()
    tk.Checkbutton(top,text='微博',bg='red',variable=var2,width=10).grid(row=1,sticky='W',column=0)
    var3=tk.IntVar()
    tk.Checkbutton(top,text='全部',bg='green',variable=var3,width=10).grid(row=2,sticky='W',column=0)

    tk.Label(top,text='输入要爬取内容的评论数量:').grid(row=0,column=2,sticky='E')
    #show='*' 加密方式显示为*
    en = tk.Entry(top,width=9,bg='LightSkyBlue')
    en.grid(row=1,column=2,sticky = 'E')
    tk.Button(top,text='确定',command=get_str,width=7).grid(row=2,column=2,sticky='E')
    tk.Button(top,text='开始',command = lambda:thread_it(show),width = 40,bg='blue').grid(row=4,column=0,columnspan=3,sticky='SE')
    tk.Button(top,text='停止',command = stop,width = 40,bg='blue').grid(row=5,column=0,columnspan=3,sticky='SE')

    top.mainloop()


if __name__ == '__main__':
    '''
    t = threading.Thread(target=tkin_show(),name='tkin_show')
    t.start()
    t.join()
    while True:
        {

        }
    #t1 = threading.Thread(target=start_spider,name='start_spider')
    #t1.start()
    '''
    tkin_show()
