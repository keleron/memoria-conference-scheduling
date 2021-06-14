from tkinter import *
window = Tk()
btn = Button(window, text='OK')
btn.bind('<Button-1>', MyButtonClicked)
