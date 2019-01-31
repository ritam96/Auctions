import urllib.request, json
import requests
from tkinter import *
import datetime
import jwt
from tkinter import messagebox
import PyKCS11
from PyKCS11 import *
import os
import binascii
import getpass
import OpenSSL
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography.hazmat._oid import ObjectIdentifier
from cryptography.hazmat.primitives import hashes
import hashlib
import pem
import random
import itertools
import math
from random import randint
import x5092json


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
        for F in (Login, List, NewAuction, MyAuctions, BidHistory, Bid, Auction):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Login)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class Security(object):
    def encryptWithRandomKey(data):
        ret = {}
        key = os.urandom(32)
        ret['key'] = key
        iv = os.urandom(16)
        ret['iv'] = iv
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(data) + encryptor.finalize()
        ret['cipheredData'] = ct

        return ret

    def encryptWithDH(data, key):
        ret = {}
        nonce = os.urandom(16)
        ret['nonce'] = nonce
        algorithm = algorithms.ChaCha20(key, nonce)
        cipher = Cipher(algorithm, mode=None, backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(data)
        ret['cipheredData'] = ct
        return ret

    def integrity(data, key):
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data)
        return h.finalize()

    def decryptWithRandomKey(data, iv, key):
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        ret = decryptor.update(data) + decryptor.finalize()
        return ret

    def decryptWithDH(data, key, nonce):
        algorithm = algorithms.ChaCha20(key, nonce)
        cipher = Cipher(algorithm, mode=None, backend=default_backend())
        decryptor = cipher.decryptor()
        ret = decryptor.update(data)
        return ret

    def encryptWithCertServerSide(data, cert):
        pass

    def handShake(self):
        sharedPrime=self.getSharedPrime()
        print(sharedPrime)
        sharedBase = randint(0, 100)
        print(sharedBase)
        secret = randint(0, 100)
        print(secret)
        value = (sharedPrime**secret)%sharedPrime
        print(value)
        CCcert = x5092json.load_certificate(CC.signature)
        x5092json.parse(CCcert)
        f = open("/etc/ssl/certs/Security_Communication_Root_CA.pem")
        cert = x5092json.load_certificate(f)
        x5092json.parse(cert)
        print(cert)
        j= {'UserID': Main.idUtilizador, 'sessionToken':Main.sessionToken, 'sharedPrime':sharedPrime,'sharedBase':sharedBase, 'value': value, 'CCcert':CCcert, 'cert':cert}
        print(j)
        headers = {'content-type':'application/json'}
        r = requests.post("http://192.168.1.70:8080/handShake",data=json.dumps(j),headers=headers)
        print(r.text)

    def getSharedPrime(self):
        lines = open('primes-to-1000k.txt').read().splitlines()
        myline =random.choice(lines)
        print(">>"+myline)
        return int(myline)


class Login(Frame):
    e=None
    f=None
    e1=None
    f1=None
    nomeOutput=None
    nomeOutput1=None
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Login", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        self.controller = controller
        #create account
        labelframe = LabelFrame(self,text="Creat Account")
        labelframe.pack()
        a = Label(labelframe ,text="username").grid(row=0,column = 0)
        b = Label(labelframe ,text="password").grid(row=1,column=0)
        Login.e = Entry(labelframe)
        Login.e.grid(row=0,column=1)
        Login.f = Entry(labelframe,show="*")
        Login.f.grid(row=1,column=1)

        pinText = Label(labelframe, text="PIN").grid(row=2,column=0)
        pinInput = Entry(labelframe,show="*")
        pinInput.grid(row=2,column=1)
        bcc =  Button(labelframe, text="C", command=lambda: self.getId(pinInput.get())).grid(row=2,column=3)


        Login.nomeOutput = Label(labelframe, text="", font=LARGE_FONT)
        Login.nomeOutput.grid(row=3,column=0)

        Button(labelframe, text="Create account", command=self.newUser).grid(row=4,column=0)

        labelframe1 = LabelFrame(self,text="Login")
        labelframe1.pack()
        a1 = Label(labelframe1 ,text="username").grid(row=1,column = 0)
        b1 = Label(labelframe1 ,text="password").grid(row=2,column=0)
        Login.e1 = Entry(labelframe1)
        Login.e1.grid(row=1,column=1)
        Login.f1 = Entry(labelframe1,show="*")
        Login.f1.grid(row=2,column=1)

        pinText1 = Label(labelframe1, text="PIN").grid(row=3,column=0)
        pinInput1 = Entry(labelframe1,show="*")
        pinInput1.grid(row=3,column=1)
        bcc1 =  Button(labelframe1, text="C", command=lambda: self.getId1(pinInput1.get())).grid(row=3,column=3)


        Login.nomeOutput1 = Label(labelframe1, text="", font=LARGE_FONT)
        Login.nomeOutput1.grid(row=4,column=0)

        Button(labelframe1, text="LOGIN", command=self.login).grid(row=5,column=0)

    def newUser(self):
        name = Login.e.get()
        pw=Login.f.get()
        #pwhash = crypt(pw)
        j = {"UserID" : name, "password" : pw}
        headers = {'content-type':'application/json'}
        r = requests.post("http://192.168.1.70:8080/createAccount",data=json.dumps(j),headers=headers)
        print(r.text)
        data = json.loads(r.text)
        if data.get('error'):
            messagebox.showerror("Error",data['description'])


    def login(self):
        name=Login.e1.get()
        pw=Login.f1.get()
        j = {"UserID" : name, "password" : pw}
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

    def getId(self,pin):
        print(pin)
        cc=CC(pin)
        nome = cc.citizen()
        Login.nomeOutput.config(text=nome)
    def getId1(self,pin):
        print(pin)
        cc=CC(pin)
        nome = cc.citizen()
        Login.nomeOutput1.config(text=nome)

class List(Frame):
    auctionID=None
    timeStamp=None
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        label = Label(self, text="List Current Auctions ", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = Button(self, text="List", command=self.listar)
        button.pack(pady=10,padx=10)

        menubar = Menu(self)
        menubar.add_command(label="List Current auctions", command=lambda: controller.show_frame(List))
        menubar.add_command(label="Create auction", command=lambda: controller.show_frame(NewAuction))
        menubar.add_command(label="My auctions", command=lambda: controller.show_frame(MyAuctions))
        menubar.add_command(label="Bid history", command=lambda: controller.show_frame(BidHistory))
        menubar.add_command(label="Logout", command=self.logout)
        controller.config(menu=menubar)

        self.controller = controller


    def logout(self):
        Main.expiration= None;
        Main.idUtilizador = None;
        Main.sessionToken = None;
        print("sair")
        self.controller.show_frame(Login)

    def listar(self):
        with urllib.request.urlopen("http://192.168.1.70:8080/listAllPublicAuctions") as url:
           data = json.loads(url.read().decode())
           print(data)

        for objeto in data:    
            labelframe = LabelFrame(self)
            labelframe.pack(fill="both", expand="yes")
            auctionid = Label(labelframe, text=objeto['AuctionID']).grid(row=0, column=1)
            desc = Label(labelframe, text=objeto['description']).grid(row=0, column=2)
            currentPrice = Label(labelframe, text=objeto['currentPrice']).grid(row=0, column=3)
            endTime = Label(labelframe, text=objeto['endTime']).grid(row=0, column=4)
            AuctionID = objeto['AuctionID']
            b=Button(labelframe, text="Bid", command=lambda: self.goBid(AuctionID)).grid(row=0, column=5)




    def goBid(self, AuctionID):
        List.auctionID = AuctionID
        print(List.auctionID)
        self.controller.show_frame(Bid)

class NewAuction(Frame):

    hidden = True
    hidden1 = True
    startText = None
    startInput = None
    exposedCheck = None
    englishCheck = None
    blindCheck = None
    nbidInput = None
    nbidersInput = None
    tres = None
    seis = None
    doze = None
    vquatro = None
    descInput = None
    imageInput = None
    var1 = None
    var2 = None
    var3 = None
    nomeOutput=None
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Create Auction", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        self.var1=IntVar()
        self.var2=IntVar()
        self.var3=IntVar()

        labelframe = LabelFrame(self)
        labelframe.pack(fill="both", expand="yes")

        self.englishCheck = Checkbutton(labelframe, text="English Auction", variable=self.var1, command=self.toggle_entry).grid(row=0, column=0)

        self.startText = Label(labelframe, text="Starting point")
        self.startText.grid(row=0,column=4)
        self.startInput = Entry(labelframe)
        self.startInput.grid(row=0,column=5)
        self.toggle_entry()

        self.blindCheck = Checkbutton(labelframe, text="Blind Auction", variable=self.var2).grid(row=1,column=0)
        self.exposedCheck = Checkbutton(labelframe, text="Exposed identity", variable=self.var3).grid(row=2,column=0)


        nbidText = Label(labelframe, text="Maximum number of bids").grid(row=3,column=0)
        self.nbidInput = Entry(labelframe)
        self.nbidInput.grid(row=3,column=1)

        nbidersText = Label(labelframe, text="Maximum number of biders").grid(row=4,column=0)
        self.nbidersInput = Entry(labelframe)
        self.nbidersInput.grid(row=4,column=1)

        self.tres=IntVar()
        self.seis=IntVar()
        self.doze=IntVar()
        self.vquatro=IntVar()

        timeText = Label(labelframe, text="Duration").grid(row=5,column=0)
        tresCheck = Checkbutton(labelframe, text="3 hours", variable=self.tres).grid(row=5,column=1)
        seisCheck = Checkbutton(labelframe, text="6 hours", variable=self.seis).grid(row=5,column=2)
        dozeCheck = Checkbutton(labelframe, text="12 hours", variable=self.doze).grid(row=5,column=3)
        vquatroCheck = Checkbutton(labelframe, text="24 hours", variable=self.vquatro).grid(row=5,column=4)

        descText = Label(labelframe, text="Auction description").grid(row=6,column=0)
        self.descInput = Entry(labelframe)
        self.descInput.grid(row=6,column=1)

        imageText = Label(labelframe, text="Image url").grid(row=7,column=0)
        self.imageInput = Entry(labelframe)
        self.imageInput.grid(row=7,column=1)

        pinText = Label(labelframe, text="PIN").grid(row=8,column=0)
        self.pinInput = Entry(labelframe,show="*")
        self.pinInput.grid(row=8,column=1)
        self.pinoutput = Label(labelframe, text="").grid(row=8,column=2)
        bcc =  Button(labelframe, text="C", command=self.getId).grid(row=8,column=3)


        self.nomeOutput = Label(labelframe, text="", font=LARGE_FONT)
        self.nomeOutput.grid(row=9,column=0)



        Button(labelframe, text="Create", command=self.create).grid(row=10,column=4)



    def create(self):
        #print(Main.idUtilizador)
        #print(Main.sessionToken)
        deltatime=None
        counter = 0
        horas = [self.tres, self.seis, self.doze, self.vquatro]
        for hora in horas:
            if hora.get() == 1:
                counter+=1
                if counter > 1:
                    messagebox.showerror("Error","You just can chose one Duration")
                    break
                else:
                    if self.tres.get() == 1 & counter == 1:
                        deltatime = 3
                    if self.seis.get() == 1 & counter == 1:
                        deltatime = 6
                    if self.doze.get() == 1 & counter == 1:
                        deltatime = 12
                    if self.vquatro.get() == 1 & counter == 1:
                        deltatime = 24

        if self.var2.get() == 1 and self.var1.get() == 1:
            messagebox.showerror("Error","You can only choose one type")

        blindAuction=0
        englishAuction=0
        if self.var2.get() == 1:
            blindAuction=1
        else:
            blindAuction=0

        if self.var1.get() == 1:
            englishAuction=1
        else:
            englishAuction=0

        if counter == 1:
            j= {'UserID': Main.idUtilizador, 'sessionToken': Main.sessionToken ,'auction': {'deltaTime': deltatime , 'exposedIdentities': self.var3.get(), 'image':self.imageInput.get(), 'description': self.descInput.get(), 'startingPrice': self.startInput.get(), 'englishAuction':englishAuction,'blindAuction':blindAuction,'maximumNumberBids': self.nbidInput.get(), 'maximumNumberBidders':self.nbidersInput.get()}}
            print(j)
            headers = {'content-type':'application/json'}

            r = requests.post("http://192.168.1.70:8080/createAuction",data=json.dumps(j),headers=headers)
            print(r.text)

    def getId(self):
        print(self.pinInput)
        cc=CC(self.pinInput.get())
        nome = cc.citizen()
        self.nomeOutput.config(text=nome)

    def toggle_entry(self):

        if NewAuction.hidden:
            self.startText.grid_remove()
            self.startInput.grid_remove()
        else:
            self.startText.grid()
            self.startInput.grid()
        NewAuction.hidden = not NewAuction.hidden

class MyAuctions(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="My Auctions", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = Button(self, text="List", command=self.lista)
        button.pack(pady=10,padx=10)

    def lista(self):
        #s= Security()
        #s.handShake()
        j= {'UserID': Main.idUtilizador, 'sessionToken':Main.sessionToken}
        #print(j)
        headers = {'content-type':'application/json'}
        r = requests.post("http://192.168.1.70:8080/listMyAuctions",data=json.dumps(j),headers=headers)
        print(r.text)
        data = json.loads(r.text)

        for objeto in data:
            print(objeto)
            labelframe = LabelFrame(self)
            labelframe.pack(fill="both", expand="yes")
            auctionid = Label(labelframe, text=objeto['AuctionID']).grid(row=0,column=1)
            desc = Label(labelframe, text=objeto['description']).grid(row=0,column=2)
            price = Label(labelframe, text=objeto['currentPrice']).grid(row=0,column=2)

class Auction(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Auction", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        button = Button(self, text="List", command=self.listar)
        button.pack(pady=10,padx=10)

    def listar(self):
        j= {'UserID': Main.idUtilizador, 'sessionToken':str(Main.sessionToken), 'AuctionID': BidHistory.AuctionID}
        headers = {'content-type':'application/json'}
        r = requests.post("http://192.168.1.70:8080/getAuctionInfo",data=json.dumps(j),headers=headers)
        data = json.loads(r.text)
        print(data)
        d  = data['Bids']
        for objeto in d:
            labelframe = LabelFrame(self)
            labelframe.pack(fill="both", expand="yes")
            user = Label(labelframe, text=objeto['UserID']).grid(row=0,column=3)
            myBid = Label(labelframe, text=objeto['value']).grid(row=0,column=4)

class BidHistory(Frame):
    AuctionID=None
    controller = None
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Bid historys", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = Button(self, text="List", command=self.listar)
        button.pack(pady=10,padx=10)

        self.controller = controller

    def listar(self):
        j= {'UserID': Main.idUtilizador, 'sessionToken':Main.sessionToken}
        print(j)
        headers = {'content-type':'application/json'}
        r = requests.post("http://192.168.1.70:8080/listBids",data=json.dumps(j),headers=headers)
        print(r.text)
        data = json.loads(r.text)

        for objeto in data:
            labelframe = LabelFrame(self)
            labelframe.pack(fill="both", expand="yes")
            #image
            auctionId = Label(labelframe, text=objeto['AuctionID']).grid(row=0,column=2)
            desc = Label(labelframe, text=objeto['AuctionDescription']).grid(row=0,column=3)
            myBid = Label(labelframe, text=objeto['value']).grid(row=0,column=4)
            auctionId = objeto['AuctionID']
            print(objeto['ended'])
            if objeto['ended'] == "1":
                b=Button(labelframe, text="Auction", command=lambda: self.goAuction(auctionId)).grid(row=0, column=5)

    def goAuction(self, auctionId):
        BidHistory.AuctionID = auctionId
        self.controller.show_frame(Auction)

    def getActionID():
        return BidHistory.AuctionID

class ClientBid(object):
    #index = None
    #timestamp = None
    #nonce = None
    #previousHash = None
    #hash = None

    def __init__(self, index, previousHash, nonce = 0):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.nonce = nonce
        self.previousHash = previousHash
        self.hash = self.hashFunction()


    def hashFunction(self):
        sha = hashlib.sha256()
        sha.update(str(self.index).encode('utf-8') + str(self.timestamp).encode('utf-8') + str(self.nonce).encode('utf-8') + str(self.previousHash).encode('utf-8'))
        return sha.hexdigest()

    def mine(self, difficulty):
        print("Mining block " + str(self.index))
        zeros = ['0'] * difficulty
        while list(self.hash)[:difficulty] != zeros:
            #incrementing the nonce value everytime the loop runs.
            self.nonce += 1

            #recalculating the hash value
            self.hash = self.hashFunction()
        print('Block mined: ' + self.hash)

class Bid(Frame):
    bidInput=None
    pinInput=None
    nomeOutput=None


    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Bid", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        #print(List.AuctionID)
        labelframe = LabelFrame(self)
        labelframe.pack(fill="both", expand="yes")

        bidText = Label(labelframe, text="Bid").grid(row=0,column=0)
        self.bidInput = Entry(labelframe)
        self.bidInput.grid(row=0,column=1)

        pinText = Label(labelframe, text="PIN").grid(row=5,column=0)
        self.pinInput = Entry(labelframe,show="*")
        self.pinInput.grid(row=5,column=1)
        bcc =  Button(labelframe, text="C", command=self.getId).grid(row=5,column=3)


        self.nomeOutput = Label(labelframe, text="", font=LARGE_FONT)
        self.nomeOutput.grid(row=6,column=0)

        b = Button(labelframe, text="Create", command=self.create).grid(row=9,column=4)



    def create(self):
        j= {'UserID': Main.idUtilizador, 'sessionToken':Main.sessionToken, 'AuctionID':List.auctionID}
        print(j)
        headers = {'content-type':'application/json'}
        r = requests.post("http://192.168.1.70:8080/getPuzzle",data=json.dumps(j),headers=headers)
        print(r.text)
        data = json.loads(r.text)
        index = data['index']
        previousHash = data['previousHash']
        miningDifficulty = data['miningDifficulty']

        cb = ClientBid(index,previousHash)
        cb.mine(miningDifficulty)
        print(index)
        print(cb.hash)
        print(previousHash)
        j= {'sessionToken': Main.sessionToken ,'AuctionID': List.auctionID,'UserID': Main.idUtilizador,'bid': {'timestamp': cb.timestamp, 'value':self.bidInput.get() , 'nonce': cb.nonce, 'hash': cb.hash, 'miningDifficulty': miningDifficulty, 'BidID':index, 'previousHash':previousHash}}
        print(j)
        headers = {'content-type':'application/json'}
        r = requests.post("http://192.168.1.70:8080/submitBid",data=json.dumps(j),headers=headers)
        print(r.text)
        data= json.loads(r.text)
        if data.get('error'):
            print('ola')
            messagebox.showerror("Error", data['description'])

    def getId(self):
        print(self.pinInput)
        cc=CC(self.pinInput.get())
        nome = cc.citizen()
        self.nomeOutput.config(text=nome)

class CC(object):
    certificate=None
    def __init__(self, pin):
        self.pin = pin

    def citizen(self):
        pkcs11 = PyKCS11.PyKCS11Lib()
        lib_path = "/usr/local/lib/libpteidpkcs11.so"
        pkcs11.load(lib_path)
        slot = pkcs11.getSlotList()[0]
        session = pkcs11.openSession(slot)
        print(self.pin)
        session.login(self.pin)

        toSign = "48656c6c6f20776f726c640d0a"

        privKey = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),(PyKCS11.CKA_LABEL,'CITIZEN AUTHENTICATION KEY')])[0]
        signMechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, None)
        signature = bytes(session.sign(privKey, toSign, signMechanism))
        print("\nsignature: "+ str(signature))

        pubKey = session.findObjects([(CKA_CLASS, CKO_PUBLIC_KEY)])[0]
        #signMechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, None)
        #verify = session.verify(pubKey, toSign, signMechanism)

        all_attr = list(PyKCS11.CKA.keys())
        all_attr = [e for e in all_attr if isinstance(e, int)]
        session = pkcs11.openSession(slot)
        print(len(session.findObjects()))
        attributes=None
        CC.certificate=None
        for obj in session.findObjects():
            attr = session.getAttributeValue(obj, all_attr)
            attr = dict(zip(map(PyKCS11.CKA.get, all_attr), attr))
            print('Label:', attr['CKA_LABEL'])
            if attr['CKA_LABEL'] == "CITIZEN AUTHENTICATION CERTIFICATE":
                attributes = attr
        b = bytes(attributes['CKA_VALUE'])
        CC.certificate = x509.load_der_x509_certificate(b, default_backend())
        print(CC.certificate)
        nome=CC.certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        session.logout()
        session.closeSession()
        return nome


app = Main()
app.mainloop()
