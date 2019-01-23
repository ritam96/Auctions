import tkinter as tk
import urllib.request, json

LARGE_FONT= ("Verdana", 12)

class SeaofBTCapp(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (List,NewAuction,MyAuctions,BidHistory):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(List)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

class List(tk.Frame):
    def callback():
        print("BID")

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        menubar = Menu(self)
        menubar.add_command(label="List Current auctions")
        menubar.add_command(label="Create auction", command=newAuction)
        menubar.add_command(label="My auctions")
        menubar.add_command(label="Bid history")
        menubar.add_command(label="Logout")
        self.config(menu=menubar)

        #with urllib.request.urlopen("http://192.168.1.70:8080/list") as url:
        #    data = json.loads(url.read().decode())
        #    print(data)

        data = [{"image": "https://cdn-oppa.meumoveldemadeira.com.br/fotos-moveis/c/o/co_pia-de-cadeira_uma_amarela_1.jpg","desc": "Cadeira amarela" ,"currentPrice":180},
                {"image": "http://www.belleclaire.com.br/colecoes/images/produtos/thumb/CAD19189_695cf48bafaa79fd75399478542a0b2e.jpg","desc": "Cadeira normal" ,"currentPrice":12},
                {"image": "https://i2marabraz-a.akamaihd.net/1800x1800/59/00158762341__2_B_ND.jpg","desc": "Cadeira retro" ,"currentPrice":12}]

        for objeto in data:
            labelframe = LabelFrame(self)
            labelframe.pack(fill="both", expand="yes")


            desc = Label(labelframe, text=objeto['desc']).grid(row=0,column=1)

            currentPrice = Label(labelframe, text=objeto['currentPrice']).grid(row=0,column=10)

            b = Button(labelframe, text="Bid", command=callback).grid(row=0,column=20)

class NewAuction(tk.Frame):
    pass

class MyAuctions(tk.Frame):
    pass

class BidHistory(tk.Frame):
    pass

app = SeaofBTCapp()
app.mainloop()
