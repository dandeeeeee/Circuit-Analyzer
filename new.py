import tkinter
from tkinter import ttk
import sv_ttk
import sympy as sy
from PIL import Image, ImageTk
import pygame

class Window:
    
    def __init__(self):
        self.root = tkinter.Tk()
        self.sound = Sound()
        
        
        
        self.activeEntry = 0
        
        self.entryFrame = tkinter.Frame(self.root)
        
        self.dxEntry = ttk.Entry(self.entryFrame, state="readonly")
        self.dxEntry.grid(row=0, column=0, padx=5)
        setattr(self.dxEntry, "previousEntry", [])
        self.dxEntry.bind("<Button-1>", lambda event: self.switchEntry(0))
        
        self.dxLabel = ttk.Label(self.entryFrame, text="dx")
        self.dxLabel.grid(row=0, column=1)
        
        self.plusLabel = ttk.Label(self.entryFrame, text="+")
        self.plusLabel.grid(row=0, column=2, padx=5)

        self.dyEntry = ttk.Entry(self.entryFrame, state="readonly")
        self.dyEntry.grid(row=0, column=3, padx=5)
        setattr(self.dyEntry, "previousEntry", [])
        self.dyEntry.bind("<Button-1>", lambda event: self.switchEntry(1))
        
        self.dyLabel = ttk.Label(self.entryFrame, text="dy ")
        self.dyLabel.grid(row=0, column=4)
        
        self.zeroLabel = ttk.Label(self.entryFrame, text="= 0")
        self.zeroLabel.grid(row=0, column=5, padx=5)
        
        
        self.entryFrame.grid(row=0, pady=10)
        
        self.firstPageButtonsList = [
            ["CHECK", "HELP", "?", "BASIC", "TRIG"], #will add functionality
            ["AC", "DEL", "7", "8", "9"], 
            ["(", ")", "4", "5", "6"],
            ["*", "/", "1", "2", "3"],
            ["x", "y", "0", "+", "-"]
        ]
        self.buttonFrame1 = tkinter.Frame(self.root)
        self.createButtons(self.firstPageButtonsList, self.buttonFrame1)
        self.buttonFrame1.grid(row=1)
        
        self.secondPageButtonsList = [
            ["CHECK", "HELP", "?", "BASIC", "TRIG"],
            ["AC", "DEL", "sin", "cos", "tan"],
            ["(", ")", "csc", "sec", "cot"],
            [",", "log", "asin", "acos", "atan"],
            ["x", "y", "acsc", "asec", "acot"],
        ]
        self.buttonFrame2 = tkinter.Frame(self.root)
        self.createButtons(self.secondPageButtonsList, self.buttonFrame2)
        self.buttonFrame2.grid(row=1)
        self.buttonFrame2.grid_forget()
        
        
    
    def createButtons(self, buttons, master):
        for i in range(len(buttons)):  # Row
            for j in range(len(buttons[i])):  # Column
                button_text = buttons[i][j]
                button = ttk.Button(master, text=button_text, width=7, 
                                    command=lambda button_text=button_text: self.updateText(button_text))
                button.grid(row=i, column=j, padx=5, pady=5)
    
    def switchEntry(self, entry): #input will be either 0 or 1, 0 is dx and 1 is dy
        self.getActiveEntry().get()
        self.activeEntry = entry
        
    def getActiveEntry(self):
        if self.activeEntry == 0:
            return self.dxEntry
        elif self.activeEntry == 1:
            return self.dyEntry
    
    def updateText(self, text):
        self.getActiveEntry().config(state="normal")
        if text == "AC":
            
            self.getActiveEntry().delete(0, tkinter.END)
            self.getActiveEntry().previousEntry.clear()
        elif text == "DEL":
            if self.getActiveEntry().previousEntry:
                lastEntry = self.getActiveEntry().previousEntry.pop()
                self.getActiveEntry().delete(len(self.getActiveEntry().get()) - len(lastEntry), tkinter.END)
        elif text == "CHECK": 
            answerWindow = tkinter.Toplevel(self.root)
            answerWindow.title("Answer")
        
            answerWindow.geometry("300x200")
            answerWindow.resizable(False, False)
            
            if self.isValid():
                if self.isExact() and self.isHomo() != None:        
                    answerLabel = ttk.Label(answerWindow, text=f"The Equation is Exact and Homo at {self.isHomo()} degree")
                elif self.isExact():
                    answerLabel = ttk.Label(answerWindow, text=f"The Equation is Exact but not Homogenous")
                elif self.isHomo() != None:
                    answerLabel = ttk.Label(answerWindow, text=f"The Equation is not exact but Homo at {self.isHomo()} degree")
                else:
                    answerLabel = ttk.Label(answerWindow, text=f"The Equation is neither exact nor homo")
            else:
                answerLabel = ttk.Label(answerWindow, text=f"Invalid Format")
            answerLabel.pack()
        elif text == "HELP": # will add later
            self.helpWindow()
            
        elif text == "TRIG":
            self.buttonFrame1.grid_forget()
            self.buttonFrame2.grid(row=1)
        elif text == "BASIC":
            self.buttonFrame2.grid_forget()
            self.buttonFrame1.grid(row=1)
        elif text == "?":
            self.aboutWindow()
        else:
            self.getActiveEntry().insert(tkinter.END, text)
            self.getActiveEntry().previousEntry.append(text)
        self.getActiveEntry().config(state="readonly")  
    
    def helpWindow(self):
        answerWindow = tkinter.Toplevel(self.root)
        answerWindow.title("Help")
        
        answerWindow.geometry("300x300")
        answerWindow.resizable(False, False)
            
        answerLabelText = """This is the help window. What you can see here is format required on inputing
- There should be a '*' between each variable and constant. Same applies to parenthesis.
- For exponent, we use the '**' where the left side was the base and the right side was the exponent
- When using log the format should be log(a, n) where a is the argument and n is the base. To use ln forgo the n and just write log(a) where a is the argument"""
            
        answerLabel = ttk.Label(answerWindow, text=answerLabelText, anchor="w", justify="left")
            
        answerLabel.grid(row=0) 
        answerWindow.after(100, lambda: answerLabel.config(wraplength=answerWindow.winfo_width() - 5))
        
    def aboutWindow(self):
        aboutWindow = tkinter.Toplevel(self.root)
        aboutWindow.title("Group Members")
        aboutWindow.resizable(False, False)
        
        
        
        titleLabel = ttk.Label(aboutWindow, text="THANK YOU FOR WATCHING\nGROUP MEMBERS", foreground="green", font=("Comic Sans MS", 40, "bold"), anchor="center")
        titleLabel.grid(row=0, padx=10, pady=10)
        
        jamesFrame = tkinter.Frame(aboutWindow)
        jamesImage = Image.open("images/james.png")
        jamesImage = jamesImage.resize((int(jamesImage.width * 0.2), int(jamesImage.height * 0.2)))
        jamesImage = ImageTk.PhotoImage(jamesImage)
        jamesImageLabel = ttk.Label(jamesFrame, image=jamesImage)
        jamesImageLabel.grid(row=0, column=0)
        jamesTextLabel = ttk.Label(jamesFrame, text="BELEN, JAMES LAURENCE E.", foreground="red", font=("Comic Sans MS", 30, "bold"))
        jamesTextLabel.grid(row=0, column=1, padx=10)
        jamesFrame.grid(row=1, sticky="w", padx=10)
        jamesImageLabel.image = jamesImage
        
        joshFrame = tkinter.Frame(aboutWindow)
        joshImage = Image.open("images/josh.jpg")
        joshImage = joshImage.resize((int(joshImage.width * 0.15), int(joshImage.height * 0.15)))
        joshImage = ImageTk.PhotoImage(joshImage)
        joshImageLabel = ttk.Label(joshFrame, image=joshImage)
        joshImageLabel.grid(column=0)
        joshTextLabel = ttk.Label(joshFrame, text="CAGARA, JOSH LENDL M.", foreground="blue", font=("Comic Sans MS", 30, "bold"))
        joshTextLabel.grid(row=0, column=1, padx=10)
        joshFrame.grid(row=2, sticky="w", padx=10)
        joshImageLabel.image = joshImage
        
        uriFrame = tkinter.Frame(aboutWindow)
        uriImage = Image.open("images/uri.png")
        uriImage = uriImage.resize((int(uriImage.width * 0.15), int(uriImage.height * 0.15)))
        uriImage = ImageTk.PhotoImage(uriImage)
        uriImageLabel = ttk.Label(uriFrame, image=uriImage)
        uriImageLabel.grid(column=0)
        uriTextLabel = ttk.Label(uriFrame, text="ENRIQUEZ, RYEN URI C.", foreground="yellow", font=("Comic Sans MS", 30, "bold"))
        uriTextLabel.grid(row=0, column=1, padx=10)
        uriFrame.grid(row=3, sticky="w", padx=10)
        uriImageLabel.image = uriImage
        
        self.sound.playSound("mp3/sigmaboy.mp3")
        
        aboutWindow.bind("<Destroy>", self.onDestroy)
        
    def onDestroy(self, event):
         self.sound.stopSound()   
        
    
    def isValid(self):
        equation = str(self.dxEntry.get()) + "+" + str(self.dyEntry.get())
        for i in range(len(equation)):
            if i > 0 and equation[i].isalpha() and equation[i - 1].isalpha():
                return False
        try:
            equation = sy.sympify(equation)
        except sy.SympifyError:
            return False
        
        return True
    
    def isExact(self): #todo: catch errors like when if the entry was empty
        x, y = sy.symbols('x y')
        equationdx = str(self.dxEntry.get())
        equationdx = sy.sympify(equationdx)
        answerdx = sy.diff(equationdx, y)
        answerdx = sy.simplify(answerdx)
        
        equationdy = str(self.dyEntry.get())
        equationdy = sy.sympify(equationdy)
        answerdy = sy.diff(equationdy, x)
        answerdy = sy.simplify(answerdy)
        
        if answerdx == answerdy:
            return True
        else:
            return False
        
        
        
    def isHomo(self):
        try:
            x, y, lmbda = sy.symbols('x y lambda')
            equation = sy.sympify(str(self.dxEntry.get())) + sy.sympify(str(self.dyEntry.get()))
            
            equation = equation.subs({x: lmbda * x, y: lmbda  * y})
            #2*xy*cos(x*y) x*cos(x*y)
            degree = sy.Poly(equation, lmbda).degree()
            
            
            terms = equation.as_ordered_terms()
            
            
            if all(sy.Poly(term, lmbda).degree() == degree for term in terms if term.free_symbols):
                return degree
            elif all(sy.Poly(term, lmbda).degree() == 0 and not term.free_symbols for term in terms):
                return degree
            else:
                return None #bad practice na magkaibang type ng variable ung nirereturn pero it is what it is
        except sy.PolynomialError:
            return None
            
        
    
    def run(self):
        sv_ttk.set_theme("light")
        self.root.resizable(False, False)
        self.root.mainloop()

class Sound:
    def __init__(self):
        pygame.mixer.init()
    def playSound(self, path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(loops=-1)
    def stopSound(self):
        pygame.mixer.music.stop()

window = Window()
window.run()