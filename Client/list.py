import urllib.request, json
from tkinter import *
import io



window = Tk()
window.title("List Current auctions")

def newAuction():
    execfile("newAuction.py")




menubar = Menu(window)
menubar.add_command(label="List Current auctions")
menubar.add_command(label="Create auction", command=newAuction)
menubar.add_command(label="My auctions")
menubar.add_command(label="Bid history")
menubar.add_command(label="Logout")
window.config(menu=menubar)

def callback():
    print("BID")

#with urllib.request.urlopen("http://192.168.1.70:8080/list") as url:
#    data = json.loads(url.read().decode())
#    print(data)

data = [{"image": "https://cdn-oppa.meumoveldemadeira.com.br/fotos-moveis/c/o/co_pia-de-cadeira_uma_amarela_1.jpg","desc": "Cadeira amarela" ,"currentPrice":180},
        {"image": "http://www.belleclaire.com.br/colecoes/images/produtos/thumb/CAD19189_695cf48bafaa79fd75399478542a0b2e.jpg","desc": "Cadeira normal" ,"currentPrice":12},
        {"image": "https://i2marabraz-a.akamaihd.net/1800x1800/59/00158762341__2_B_ND.jpg","desc": "Cadeira retro" ,"currentPrice":12}]

for objeto in data:
    labelframe = LabelFrame(window)
    labelframe.pack(fill="both", expand="yes")


    desc = Label(labelframe, text=objeto['desc']).grid(row=0,column=1)

    currentPrice = Label(labelframe, text=objeto['currentPrice']).grid(row=0,column=10)

    b = Button(labelframe, text="Bid", command=callback).grid(row=0,column=20)



window.mainloop()
