#! /usr/bin/env python


import sys
from tkinter import messagebox

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import Okta_support

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    Okta_support.set_Tk_var()
    top = Toplevel1 (root)
    Okta_support.init(root, top)
    root.mainloop()

w = None
def create_Toplevel1(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_Toplevel1(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel (root)
    Okta_support.set_Tk_var()
    top = Toplevel1 (w)
    Okta_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_Toplevel1():
    global w
    w.destroy()
    w = None

class Toplevel1:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'

        top.geometry("457x411+713+231")
        top.minsize(72, 15)
        top.maxsize(3712, 1092)
        top.resizable(1,  1)
        top.title("OKTA for AWS Linked Account")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.menubar = tk.Menu(top,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        top.configure(menu = self.menubar)

        self.Frame1 = tk.Frame(top)
        self.Frame1.place(relx=0.022, rely=0.024, relheight=0.944
                , relwidth=0.947)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(background="#d9d9d9")
        self.Frame1.configure(highlightbackground="#d9d9d9")
        self.Frame1.configure(highlightcolor="black")

        self.Label1 = tk.Label(self.Frame1)
        self.Label1.place(relx=0.0, rely=0.0, height=79, width=432)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(background="Black")
        self.Label1.configure(font="-family {Comic Sans MS} -size 13")
        self.Label1.configure(foreground="White")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text='''Add AWS Linked account to OKTA''')

        self.Label2 = tk.Label(self.Frame1)
        self.Label2.place(relx=0.023, rely=0.284, height=51, width=133)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''Application name*''')

        self.Label3 = tk.Label(self.Frame1)
        self.Label3.place(relx=0.023, rely=0.606, height=32, width=130)
        self.Label3.configure(activebackground="#f9f9f9")
        self.Label3.configure(activeforeground="black")
        self.Label3.configure(background="#d9d9d9")
        self.Label3.configure(foreground="#000000")
        self.Label3.configure(highlightbackground="#d9d9d9")
        self.Label3.configure(highlightcolor="black")
        self.Label3.configure(text='''Account number*''')

        def submit():
            if Okta_support.accountNum.get() != "" and Okta_support.appNameAWS.get() != "" and Okta_support.keyid.get() != "" and Okta_support.secretKey.get() != "" and Okta_support.apiKey.get() != "":
                messagebox.showinfo("Info","Checking Credentials...")
                Okta_support.checkCredentials()
            else:
                messagebox.showerror("Info","You must fill all the required fields")

        self.Button1 = tk.Button(self.Frame1)
        self.Button1.place(relx=0.046, rely=0.902, height=22, width=69)
        self.Button1.configure(activebackground="#ececec")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#d9d9d9")
        self.Button1.configure(command=lambda:submit())
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(relief="raised")
        self.Button1.configure(text='''Submit''')

        self.Label4 = tk.Label(self.Frame1)
        self.Label4.place(relx=0.023, rely=0.227, height=35, width=67)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(activeforeground="black")
        self.Label4.configure(background="#d9d9d9")
        self.Label4.configure(font="-family {Al Bayan} -size 13 -weight bold")
        self.Label4.configure(foreground="#000000")
        self.Label4.configure(highlightbackground="#d9d9d9")
        self.Label4.configure(highlightcolor="black")
        self.Label4.configure(text='''OKTA:''')

        self.Label5 = tk.Label(self.Frame1)
        self.Label5.place(relx=0.044, rely=0.528, height=35, width=45)
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(activeforeground="black")
        self.Label5.configure(background="#d9d9d9")
        self.Label5.configure(font="-family {Al Nile} -size 13 -weight bold")
        self.Label5.configure(foreground="#000000")
        self.Label5.configure(highlightbackground="#d9d9d9")
        self.Label5.configure(highlightcolor="black")
        self.Label5.configure(text='''AWS:''')

        self.Label7 = tk.Label(self.Frame1)
        self.Label7.place(relx=0.039, rely=0.686, height=30, width=103)
        self.Label7.configure(activebackground="#f9f9f9")
        self.Label7.configure(activeforeground="black")
        self.Label7.configure(background="#d9d9d9")
        self.Label7.configure(foreground="#000000")
        self.Label7.configure(highlightbackground="#d9d9d9")
        self.Label7.configure(highlightcolor="black")
        self.Label7.configure(text='''Access key ID*''')

        self.Label8 = tk.Label(self.Frame1)
        self.Label8.place(relx=0.042, rely=0.768, height=24, width=83)
        self.Label8.configure(activebackground="#f9f9f9")
        self.Label8.configure(activeforeground="black")
        self.Label8.configure(background="#d9d9d9")
        self.Label8.configure(foreground="#000000")
        self.Label8.configure(highlightbackground="#d9d9d9")
        self.Label8.configure(highlightcolor="black")
        self.Label8.configure(text='''Secret Key*''')

        self.Label6 = tk.Label(self.Frame1)
        self.Label6.place(relx=0.039, rely=0.389, height=24, width=62)
        self.Label6.configure(activebackground="#f9f9f9")
        self.Label6.configure(activeforeground="black")
        self.Label6.configure(background="#d9d9d9")
        self.Label6.configure(foreground="#000000")
        self.Label6.configure(highlightbackground="#d9d9d9")
        self.Label6.configure(highlightcolor="black")
        self.Label6.configure(text='''API key*''')

        self.Entry5 = tk.Entry(self.Frame1)
        self.Entry5.place(relx=0.416, rely=0.309, height=25, relwidth=0.467)
        self.Entry5.configure(background="white")
        self.Entry5.configure(font="TkFixedFont")
        self.Entry5.configure(foreground="#000000")
        self.Entry5.configure(highlightbackground="#d9d9d9")
        self.Entry5.configure(highlightcolor="black")
        self.Entry5.configure(insertbackground="black")
        self.Entry5.configure(selectbackground="blue")
        self.Entry5.configure(selectforeground="white")
        self.Entry5.configure(textvariable=Okta_support.appNameAWS)       

        self.Entry1 = tk.Entry(self.Frame1)
        self.Entry1.place(relx=0.416, rely=0.387, height=25, relwidth=0.467)
        self.Entry1.configure(background="white")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="blue")
        self.Entry1.configure(selectforeground="white")
        self.Entry1.configure(textvariable=Okta_support.apiKey)

        self.Entry2 = tk.Entry(self.Frame1)
        self.Entry2.place(relx=0.416, rely=0.619, height=25, relwidth=0.467)
        self.Entry2.configure(background="white")
        self.Entry2.configure(font="TkFixedFont")
        self.Entry2.configure(foreground="#000000")
        self.Entry2.configure(highlightbackground="#d9d9d9")
        self.Entry2.configure(highlightcolor="black")
        self.Entry2.configure(insertbackground="black")
        self.Entry2.configure(selectbackground="blue")
        self.Entry2.configure(selectforeground="white")
        self.Entry2.configure(textvariable=Okta_support.accountNum)

        self.Entry3 = tk.Entry(self.Frame1)
        self.Entry3.place(relx=0.416, rely=0.696, height=25, relwidth=0.467)
        self.Entry3.configure(background="white")
        self.Entry3.configure(font="TkFixedFont")
        self.Entry3.configure(foreground="#000000")
        self.Entry3.configure(highlightbackground="#d9d9d9")
        self.Entry3.configure(highlightcolor="black")
        self.Entry3.configure(insertbackground="black")
        self.Entry3.configure(selectbackground="blue")
        self.Entry3.configure(selectforeground="white")
        self.Entry3.configure(textvariable=Okta_support.keyid)

        self.Entry4 = tk.Entry(self.Frame1)
        self.Entry4.place(relx=0.416, rely=0.773, height=25, relwidth=0.467)
        self.Entry4.configure(background="white")
        self.Entry4.configure(font="TkFixedFont")
        self.Entry4.configure(foreground="#000000")
        self.Entry4.configure(highlightbackground="#d9d9d9")
        self.Entry4.configure(highlightcolor="black")
        self.Entry4.configure(insertbackground="black")
        self.Entry4.configure(selectbackground="blue")
        self.Entry4.configure(selectforeground="white")
        self.Entry4.configure(textvariable=Okta_support.secretKey)

if __name__ == '__main__':
    vp_start_gui()

