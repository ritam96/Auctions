from tkinter import *
import requests
from pbkdf2 import crypt
import json

def newUser():
    name = e.get()
    pw=f.get()
    pwhash = crypt(pw)
    j = {"name" : name, "pass" : pwhash}
    headers = {'content-type':'application/json'}
    r = requests.post("http://192.168.1.70:8080/postTest",data=json.dumps(j),headers=headers)
    print(r.text)

def login():
    '''pwhash = ir buscar o que está encriptado na api
    alleged_pw = f1.get()
    if pwhash == crypt(alleged_pw, pwhash):
        print("Password good")
    else:
        print("Invalid password")'''



    print("outra vez")


window = Tk()
window.title("Login")

menubar = Menu(window)
menubar.add_command(label="List Current auctions")
menubar.add_command(label="Create auction")
menubar.add_command(label="My auctions")
menubar.add_command(label="Bid history")
menubar.add_command(label="Logout")
window.config(menu=menubar)


labelframe = LabelFrame(window,text="Creat Account")
labelframe.pack()
a = Label(labelframe ,text="username").grid(row=0,column = 0)
b = Label(labelframe ,text="password").grid(row=1,column=0)
e = Entry(labelframe)
e.grid(row=0,column=1)
f = Entry(labelframe,show="*")
f.grid(row=1,column=1)
Button(labelframe, text="Create account", command=newUser).grid(row=2,column=0)

labelframe1 = LabelFrame(window,text="Login")
labelframe1.pack()
a1 = Label(labelframe1 ,text="username").grid(row=1,column = 0)
b1 = Label(labelframe1 ,text="password").grid(row=2,column=0)
e1 = Entry(labelframe1).grid(row=1,column=1)
f1 = Entry(labelframe1,show="*").grid(row=2,column=1)
Button(labelframe1, text="LOGIN", command=login).grid(row=3,column=0)


window.mainloop()
