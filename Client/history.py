from tkinter import *
import urllib.request, json

import datetime

now = datetime.datetime.now()


window = Tk()
window.title("Bid history")

menubar = Menu(window)
menubar.add_command(label="List Current auctions")
menubar.add_command(label="Create auction")
menubar.add_command(label="My auctions")
menubar.add_command(label="Bid history")
menubar.add_command(label="Logout")
window.config(menu=menubar)



#with urllib.request.urlopen("http://192.168.1.70:8080/list") as url:
#    data = json.loads(url.read().decode())
#    print(data)

data = [{"image": "https://cdn-oppa.meumoveldemadeira.com.br/fotos-moveis/c/o/co_pia-de-cadeira_uma_amarela_1.jpg","desc": "Cadeira amarela" ,"myBid":180,"winingBid":200},
        {"image": "http://www.belleclaire.com.br/colecoes/images/produtos/thumb/CAD19189_695cf48bafaa79fd75399478542a0b2e.jpg","desc": "Cadeira normal" ,"myBid":12,"winingBid":200},
        {"image": "https://i2marabraz-a.akamaihd.net/1800x1800/59/00158762341__2_B_ND.jpg","desc": "Cadeira retro" ,"myBid":12,"winingBid":200}]

for objeto in data:
    labelframe = LabelFrame(window)
    labelframe.pack(fill="both", expand="yes")

    #image

    desc = Label(labelframe, text=objeto['desc']).grid(row=0,column=1)
    myBid = Label(labelframe, text=objeto['myBid']).grid(row=0,column=10)
    winingBid = Label(labelframe, text=objeto['winingBid']).grid(row=0,column=20)

window.mainloop()
