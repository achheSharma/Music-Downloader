from __future__ import unicode_literals
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
import youtube_dl
import threading
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from io import StringIO
import sys
import time

no_of_recommended = 5
no_of_links_to_check_if_music = 3
links_watch = []
link_text = []
t1 = threading.Thread()

''' Capture STDOUT '''
# old_stdout = sys.stdout
# result = StringIO()
# sys.stdout = result


def popup(msg, flag, controller):
    if flag == 1 and len(links_watch) >= no_of_recommended:
        popup = tk.Tk()
        def leavemini():
            popup.destroy()

        popup.wm_title("Message")
        label = ttk.Label(popup, text = msg)
        label.pack()
        b1 = ttk.Button(popup, text = "OK", command = lambda: [leavemini(), controller.show_frame("PageOne"), Show_recommended(link_text)])
        b1.pack()
        popup.mainloop()
    else:
        messagebox.showinfo("INFO", message= msg)
        b1 = ttk.Button(popup, text = "OK", command = lambda: [leavemini()] )
        b1.pack()
    # else:
    #     messagebox.showinfo("Downloaded", message= msg)
    #     b1 = ttk.Button(popup, text = "OK", command = lambda: [leavemini()] )
    #     b1.pack()

# def Check_Download(): 
#     for i in range(20):
#         if not t1.is_alive():
#             popup("Download Complete", -1, 0)
#         time.sleep(5)

def DownloadAudio(my_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',    
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([my_url])


def Show_recommended(link_text):
    for i in range(len(links_watch)):
        if(len(link_text[i].get())):
            link_text[i].delete(0,len(link_text[i].get()))
    for i in range(len(links_watch)):
        link_text[i].insert(0,links_watch[i])
    del links_watch[:]
        
def MusicRecommend(my_url):
    uClient = urlopen(my_url)
    page_html = uClient.read()
    uClient.close()
    soup = BeautifulSoup(page_html, "html.parser")
    links_channel = []
    flag = 0
    for link in soup.findAll('a', attrs={'href': re.compile("/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ")}):
        flag = 1
        links_channel.append(link.get('href'))
    if flag == 1:
        global t1
        t1 = threading.Thread(target = DownloadAudio, args = (my_url,))
        t1.start()
        # t2 = threading.Thread(target = Check_Download)
        # t2.start()
        counter = 0
        for link in soup.findAll('span', attrs={'title'}):
            if not link.get('title'):
                temp = link.decode_contents(formatter="html")
                temp = temp.strip()
                links_watch.append(temp)
                counter=counter+1
            if counter >= no_of_recommended:
                break
        return 1
    else:
        return 0
        
def SearchMusic(SearchUrl, controller):
    uClient = urlopen(SearchUrl)
    page_html = uClient.read()
    uClient.close()
    soup = BeautifulSoup(page_html, "html.parser")
    links_watch = []
    counter = 0
    for link in soup.findAll('a', attrs={'href': re.compile("/watch")}):
        links_watch.append(link.get('href'))
        counter = counter+1
        if counter >= no_of_links_to_check_if_music:
            break
    for i in links_watch:
        my_url = "https://www.youtube.com"+str(i)
        flag = MusicRecommend(my_url)
        if flag == 1:
            popup("Downloading", flag, controller)
            break
    if flag == 0:
        popup("Not a valid Music Name", flag, controller)


def link_grab(SearchText, controller):
    SearchQuery = SearchText.get()
    SearchQuery = SearchQuery.strip()
    SearchQuery = SearchQuery.replace(" ","+")
    SearchUrl = "https://www.youtube.com/results?sp=EgIQAQ%253D%253D&search_query="+SearchQuery
    t = threading.Thread(target = SearchMusic, args= (SearchUrl, controller))
    t.start()


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Music Downloader")

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = ttk.Label(self, text="Music Downloader", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        SearchText = ttk.Entry(self)
        SearchText.pack()
        button1 = ttk.Button(self, text="Download",
                             command= lambda: [link_grab(SearchText, controller)])
        button1.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = ttk.Label(self, text="Recommended", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        global link_text
        link_text = []
        bl = []
        for i in range(no_of_recommended):
            link_text.append(ttk.Entry(self))
            link_text[i].pack()
            bl.append(ttk.Button(self, text="Download",
                             command= lambda: [link_grab(link_text[i], controller)]))
            bl[i].pack()

        button = ttk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        
        button.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()

''' Parseing Captured STDOUT '''
''' This can be utilised to display Download Progress Bar '''
# result_string = result.getvalue()

# f = open("log.txt", 'w')
# f.write(result_string)

# sys.stdout = old_stdout
# result_string = result_string.split("\n")
# # print (result_string)
# download_prog = result_string[4].split("\r[download]")
# print (download_prog)
# download_list = []
# for i in range(len(download_prog)-1):
#     temp = []
#     download_prog[i] = download_prog[i].strip()
#     search_obj = re.search( r'([0-9.]+\%) of ([0-9.]+.iB) at ([0-9.]+.iB/s) ETA ([0-9.]+.+[0-9.])', download_prog[i])
#     if search_obj:
#         for j in range(1,5):
#             temp.append(search_obj.group(j))
#     download_list.append(temp)
# search_obj = re.search(r'([0-9.]+\%) of ([0-9.]+.iB) in ([0-9.]+.+[0-9.])', download_prog[-1])
# if search_obj:
#     temp = []
#     for j in range(1,4):
#         temp.append(search_obj.group(j))
#     download_list.append(temp)

# for i in download_list:
#     print (i)
