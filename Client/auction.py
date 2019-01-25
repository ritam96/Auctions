import urllib.request, json
import requests
from tkinter import *
import datetime
import jwt
from tkinter import messagebox

LARGE_FONT= ("Verdana", 12)

class Main(Tk):
    expiration= None;
    idUtilizador = None;
    sessionToken = None;

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        container = Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (Login, List, NewAuction, MyAuctions, BidHistory, Bid):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Login)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class Login(Frame):
    e=None
    f=None
    e1=None
    f1=None
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Login", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        self.controller = controller
        labelframe = LabelFrame(self,text="Creat Account")
        labelframe.pack()
        a = Label(labelframe ,text="username").grid(row=0,column = 0)
        b = Label(labelframe ,text="password").grid(row=1,column=0)
        Login.e = Entry(labelframe)
        Login.e.grid(row=0,column=1)
        Login.f = Entry(labelframe,show="*")
        Login.f.grid(row=1,column=1)
        Button(labelframe, text="Create account", command=self.newUser).grid(row=2,column=0)

        labelframe1 = LabelFrame(self,text="Login")
        labelframe1.pack()
        a1 = Label(labelframe1 ,text="username").grid(row=1,column = 0)
        b1 = Label(labelframe1 ,text="password").grid(row=2,column=0)
        Login.e1 = Entry(labelframe1)
        Login.e1.grid(row=1,column=1)
        Login.f1 = Entry(labelframe1,show="*")
        Login.f1.grid(row=2,column=1)
        Button(labelframe1, text="LOGIN", command=self.login).grid(row=3,column=0)

    def newUser(self):
        name = Login.e.get()
        pw=Login.f.get()
        #pwhash = crypt(pw)
        j = {"name" : name, "password" : pw}
        headers = {'content-type':'application/json'}
        r = requests.post("http://192.168.1.70:8080/createAccount",data=json.dumps(j),headers=headers)
        print(r.text)


    def login(self):
        name=Login.e1.get()
        pw=Login.f1.get()
        j = {"name" : name, "password" : pw}
        headers = {'content-type':'application/json'}
        r = requests.post("http://192.168.1.70:8080/login",data=json.dumps(j),headers=headers)
        data= json.loads(r.text)
        print(data)
        if data.get('error'):
            messagebox.showerror("Error", data['description'])
        else:
            Main.sessionToken = data['sessionToken'];
            decode = jwt.decode(Main.sessionToken, pw, algorithms=['HS256'])
            Main.expiration=decode['expiration'] ;
            Main.idUtilizador = decode['UserID'];
            print(Main.sessionToken)
            print(Main.expiration)
            print(Main.idUtilizador)
            self.controller.show_frame(List)


class List(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        label = Label(self, text="List Current Auctions ", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        menubar = Menu(self)
        menubar.add_command(label="List Current auctions", command=lambda: controller.show_frame(List))
        menubar.add_command(label="Create auction", command=lambda: controller.show_frame(NewAuction))
        menubar.add_command(label="My auctions", command=lambda: controller.show_frame(MyAuctions))
        menubar.add_command(label="Bid history", command=lambda: controller.show_frame(BidHistory))
        menubar.add_command(label="Logout", command=self.logout)
        controller.config(menu=menubar)

        self.controller = controller

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

            b = Button(labelframe, text="Bid", command=lambda: controller.show_frame(Bid)).grid(row=0,column=20)

    def logout(self):
        Main.expiration= None;
        Main.idUtilizador = None;
        Main.sessionToken = None;
        print("sair")
        self.controller.show_frame(Login)



class NewAuction(Frame):

    hidden = True
    hidden1 = True
    startText = None
    startInput = None
    exposedCheck = None

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Create Auction", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        var1=IntVar()
        var2=IntVar()
        var3=IntVar()

        labelframe = LabelFrame(self)
        labelframe.pack(fill="both", expand="yes")

        englishCheck = Checkbutton(labelframe, text="English Auction", variable=var1, command=self.toggle_entry).grid(row=0, column=0)

        self.startText = Label(labelframe, text="Starting point")
        self.startText.grid(row=0,column=4)
        self.startInput = Entry(labelframe)
        self.startInput.grid(row=0,column=5)
        self.toggle_entry()

        blindCheck = Checkbutton(labelframe, text="Blind Auction", variable=var2, command=self.toggle_entry1).grid(row=1,column=0)
        self.exposedCheck = Checkbutton(labelframe, text="Exposed identity", variable=var3)
        self.exposedCheck.grid(row=1,column=4)
        self.toggle_entry1()

        nbidText = Label(labelframe, text="Maximum number of bids").grid(row=2,column=0)
        nbidInput = Entry(labelframe)
        nbidInput.grid(row=2,column=1)

        nbidersText = Label(labelframe, text="Maximum number of biders").grid(row=3,column=0)
        nbidersInput = Entry(labelframe)
        nbidersInput.grid(row=3,column=1)

        tres=IntVar()
        seis=IntVar()
        doze=IntVar()
        vquatro=IntVar()

        timeText = Label(labelframe, text="Duration").grid(row=4,column=0)
        tresCheck = Checkbutton(labelframe, text="3 hours", variable=tres).grid(row=4,column=1)
        seisCheck = Checkbutton(labelframe, text="6 hours", variable=seis).grid(row=4,column=2)
        dozeCheck = Checkbutton(labelframe, text="12 hours", variable=doze).grid(row=4,column=3)
        vquatroCheck = Checkbutton(labelframe, text="24 hours", variable=vquatro).grid(row=4,column=4)

        descText = Label(labelframe, text="Auction description").grid(row=5,column=0)
        descInput = Entry(labelframe)
        descInput.grid(row=5,column=1)

        imageText = Label(labelframe, text="Image url").grid(row=6,column=0)
        imageInput = Entry(labelframe)
        imageInput.grid(row=6,column=1)

        Button(labelframe, text="Create", command=self.create).grid(row=7,column=4)

    def create(self):
        print("create new auction")

    def toggle_entry(self):

        if NewAuction.hidden:
            self.startText.grid_remove()
            self.startInput.grid_remove()
        else:
            self.startText.grid()
            self.startInput.grid()
        NewAuction.hidden = not NewAuction.hidden

    def toggle_entry1(self):

        if NewAuction.hidden1:
            self.exposedCheck.grid_remove()
        else:
            self.exposedCheck.grid()
        NewAuction.hidden1 = not NewAuction.hidden1



class MyAuctions(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="My Auctions", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        now = datetime.datetime.now()
        data = [{"image": "https://cdn-oppa.meumoveldemadeira.com.br/fotos-moveis/c/o/co_pia-de-cadeira_uma_amarela_1.jpg","desc": "Cadeira amarela" ,"currentPrice":180, "timeStamp": now.strftime("%Y-%m-%d %H:%M")},
                {"image": "http://www.belleclaire.com.br/colecoes/images/produtos/thumb/CAD19189_695cf48bafaa79fd75399478542a0b2e.jpg","desc": "Cadeira normal" ,"currentPrice":12, "timeStamp":now.strftime("%Y-%m-%d %H:%M") },
                {"image": "https://i2marabraz-a.akamaihd.net/1800x1800/59/00158762341__2_B_ND.jpg","desc": "Cadeira retro" ,"currentPrice":12, "timeStamp": now.strftime("%Y-%m-%d %H:%M")}]

        for objeto in data:
            labelframe = LabelFrame(self)
            labelframe.pack(fill="both", expand="yes")

            #image

            desc = Label(labelframe, text=objeto['desc']).grid(row=0,column=1)
            timeStamp = Label(labelframe, text=objeto['timeStamp']).grid(row=0,column=20)
            currentPrice = Label(labelframe, text=objeto['currentPrice']).grid(row=0,column=10)

class BidHistory(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Bid historys", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        data = [{"image": "https://cdn-oppa.meumoveldemadeira.com.br/fotos-moveis/c/o/co_pia-de-cadeira_uma_amarela_1.jpg","desc": "Cadeira amarela" ,"myBid":180,"winingBid":200},
                {"image": "http://www.belleclaire.com.br/colecoes/images/produtos/thumb/CAD19189_695cf48bafaa79fd75399478542a0b2e.jpg","desc": "Cadeira normal" ,"myBid":12,"winingBid":200},
                {"image": "https://i2marabraz-a.akamaihd.net/1800x1800/59/00158762341__2_B_ND.jpg","desc": "Cadeira retro" ,"myBid":12,"winingBid":200}]

        for objeto in data:
            labelframe = LabelFrame(self)
            labelframe.pack(fill="both", expand="yes")

            #image

            desc = Label(labelframe, text=objeto['desc']).grid(row=0,column=1)
            myBid = Label(labelframe, text=objeto['myBid']).grid(row=0,column=10)
            winingBid = Label(labelframe, text=objeto['winingBid']).grid(row=0,column=20)

class Bid(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Bid", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        labelframe = LabelFrame(self)
        labelframe.pack(fill="both", expand="yes")

        bidText = Label(labelframe, text="Bid").grid(row=0,column=0)
        bidInput = Entry(labelframe)
        bidInput.grid(row=0,column=1)

        Nome = Label(labelframe, text="Name").grid(row=2,column=0)
        dataNasc = Label(labelframe, text="Birth date").grid(row=3,column=0)
        morada = Label(labelframe, text="Address").grid(row=4,column=0)
        pinText = Label(labelframe, text="PIN").grid(row=5,column=0)
        pinInput = Entry(labelframe,show="*")
        pinInput.grid(row=5,column=1)

app = Main()
app.mainloop()
