import os
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo

class pttCrawler:
    
    def __init__(self):
        self._article_dict = dict()
        self._board = None
        self._pages = None
        self._pageURL = None
        self.build_window()

    def build_window(self):
    
        def search_all_pages():
            
            title_list.delete(0, tk.END)
            self._article_dict = dict()
            self._board = search_board_input.get()
            self._pageURL = f"https://www.ptt.cc/bbs/{self._board}/index.html"
            try:
                self._pages = int(search_page_input.get())
                while self._pages:
                    self._pageURL = "https://www.ptt.cc" + article_search(self._pageURL)
                    self._pages -= 1
            except ValueError:
                showinfo("Error", "Invalid page amounts!")
                search_page_input.delete(0, tk.END)
                return
            except TypeError:
                showinfo("Error", "Invalid board name!")
                search_board_input.delete(0, tk.END)
                return
                     
            for idx, title in enumerate(self._article_dict.keys()):
                title_list.insert(idx, title) 
        
    
        def article_search(url):
                
            page = BeautifulSoup(requests.get(url, headers={"cookie": "over18=1"}).text, "html.parser")
            titles = page.find_all("div", class_="title")
            for title in titles[::-1]:
                if title.a is not None:
                    title_name = title.a.string
                    tag = title.find("a")["href"]
                    self._article_dict[title_name] = tag
            lastPage_link = page.find("a", string="‹ 上頁")["href"]
            return lastPage_link
        
        def show_article_content():
            
            content_text.delete(1.0, tk.END)
            article_choice = self._article_dict[title_list.get(tk.ANCHOR)]
            webURL = f"https://www.ptt.cc{article_choice}"
            web = BeautifulSoup(requests.get(webURL, headers={"cookie": "over18=1"}).text, "html.parser")
            title = web.find("title").string
            pre_article = web.find(id="main-container").text.split("--")[0]
            article = "\n".join(pre_article.split("\n")[2:])
            content_text.insert(1.0, title + "\n\n------------------------------\n\n" + article + "\n------------------------------\n")
            
            pushes = web.find_all("div", class_="push")
            for push in pushes:
                sign = push.find("span").string
                userId = push.find("span", class_="f3 hl push-userid").string
                response = push.find("span", class_="f3 push-content")
                time = push.find("span", class_="push-ipdatetime").string.strip()[-11:]
                if sign == "→ ":
                    sign = "回 "
                if response.a != None:
                    response = response.a 
                content_text.insert(tk.END, "{} {:12s} {} {}\n".format(time, userId, sign, response.string))
        
        def save_content():
            file = asksaveasfilename(initialfile='article.txt',
                             defaultextension=".txt",
                             filetypes=[("All Files", "*.*"), ("Text Document", "*.txt")])
            if file is None:
                return
            else:
                try:
                    window.title(os.path.basename(file))
                    file = open(file, 'w')
                    file.write(content_text.get(1.0, tk.END))
                except Exception:
                    showinfo("Error", "Fail to save!")
            
        #----------------------------------------#
        WIDGET_FONT = ("jf open 粉圓 1.1", 16)
        BUTTON_FONT = ("jf open 粉圓 1.1", 12)
        
        window = tk.Tk()
        window.title("pttCrawler")
        window.geometry("1500x800")
        window.config(bg="#B78338")
        left_frame = tk.Frame(window, bg="#B78338")
        right_frame = tk.Frame(window, bg="#B78338")
        
        #----------------------------------------#
        search_frame = tk.Frame(left_frame, bg="#B78338")
        search_board_label = tk.Label(search_frame, text="請輸入看板名稱：", font=WIDGET_FONT, fg="#2F1812", bg="#B78338").grid(row=0, column=0, pady=5)
        search_board_input = tk.Entry(search_frame, font=WIDGET_FONT, width=10)
        search_board_input.grid(row=1, column=0, pady=5)
        
        search_page_frame = tk.Frame(search_frame, bg="#B78338")
        search_page_label = tk.Label(search_page_frame, text="搜尋頁數：", font=WIDGET_FONT, fg="#2F1812", bg="#B78338").grid(row=2, column=0, pady=5) 
        search_page_input = tk.Entry(search_page_frame, font=WIDGET_FONT, width=5)
        search_page_input.insert(0, 1)
        search_page_input.grid(row=2, column=1, pady=5)
        search_page_frame.grid(row=2, column=0, pady=5)
        
        search_board_button = tk.Button(search_frame, text="查詢", font=BUTTON_FONT, command=search_all_pages,  fg="white", bg="#915C4C").grid(row=3, column=0)
        #----------------------------------------#
        title_frame = tk.Frame(left_frame, bg="#B78338")
        title_list = tk.Listbox(title_frame, font=WIDGET_FONT, width=40, height=20, selectmode=tk.SINGLE)
        title_list.grid(row=0, column=0, pady=5)
        search_content_button = tk.Button(title_frame, font=BUTTON_FONT, text="閱讀", command=show_article_content, fg="white", bg="#915C4C").grid(row=1, column=0, padx=5)
        #----------------------------------------#  
        content_frame = tk.Frame(right_frame, bg="#B78338")
        content_scrollbar = tk.Scrollbar(content_frame)
        content_text = tk.Text(content_frame,font=("細明體", 16), width=85, height=35, yscrollcommand=content_scrollbar.set)
        content_scrollbar.config(command=content_text.yview)
        content_text.pack(side=tk.LEFT, fill=tk.BOTH)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        save_button = tk.Button(right_frame, font=BUTTON_FONT, text="儲存", command=save_content, fg="white", bg="#915C4C").grid(row=1, column=0)
        
        
        left_frame.grid(row=0, column=0, padx=10)
        right_frame.grid(row=0, column=1, padx=10)
        search_frame.grid(row=0, column=0, padx=10)
        title_frame.grid(row=1, column=0, padx=10, pady=10)
        content_frame.grid(row=0, column=0, pady=5)
        
        window.mainloop()
        

if __name__ == "__main__":
    pC = pttCrawler()

    