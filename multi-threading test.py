import tkinter as tk
from tkinter import messagebox

root = tk.Tk()

canvas1 = tk.Canvas(root, width=300, height=300)
canvas1.pack()


def ExitApplication():
    MsgBox = tk.messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application',
                                       icon='warning')
    if MsgBox == 'yes':
        root.destroy()
    else:
        tk.messagebox.showinfo('Return', 'You will now return to the application screen')


button1 = tk.Button(root, text='Exit Application', command=ExitApplication, bg='brown', fg='white')
canvas1.create_window(150, 150, window=button1)

root.mainloop()