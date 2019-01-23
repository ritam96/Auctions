from tkinter import *
import urllib.request, json


def create():
    print("create new auction")


def toggle_entry():
    global hidden
    if hidden:
        startText.grid_remove()
        startInput.grid_remove()
    else:
        startText.grid()
        startInput.grid()
    hidden = not hidden

def toggle_entry1():
    global hidden1
    if hidden1:
        exposedCheck.grid_remove()
    else:
        exposedCheck.grid()
    hidden1 = not hidden1

hidden = True
hidden1 = True

window = Tk()
window.title("Create auction")

menubar = Menu(window)
menubar.add_command(label="List Current auctions")
menubar.add_command(label="Create auction")
menubar.add_command(label="My auctions")
menubar.add_command(label="Bid history")
menubar.add_command(label="Logout")
window.config(menu=menubar)

var1=IntVar()
var2=IntVar()
var3=IntVar()


labelframe = LabelFrame(window)
labelframe.pack(fill="both", expand="yes")

englishCheck = Checkbutton(labelframe, text="English Auction", variable=var1, command=toggle_entry).grid(row=0, column=0)

startText = Label(labelframe, text="Starting point")
startText.grid(row=0,column=4)
startInput = Entry(labelframe)
startInput.grid(row=0,column=5)
toggle_entry()

blindCheck = Checkbutton(labelframe, text="Blind Auction", variable=var2, command=toggle_entry1).grid(row=1,column=0)
exposedCheck = Checkbutton(labelframe, text="Exposed identity", variable=var3)
exposedCheck.grid(row=1,column=4)
toggle_entry1()

nbidText = Label(labelframe, text="Maximum number of bids").grid(row=2,column=0)
nbidInput = Entry(labelframe)
nbidInput.grid(row=2,column=1)

descText = Label(labelframe, text="Auction description").grid(row=3,column=0)
descInput = Entry(labelframe)
descInput.grid(row=3,column=1)

imageText = Label(labelframe, text="Image url").grid(row=4,column=0)
imageInput = Entry(labelframe)
imageInput.grid(row=4,column=1)

Button(labelframe, text="Create", command=create).grid(row=5,column=4)


window.mainloop()
