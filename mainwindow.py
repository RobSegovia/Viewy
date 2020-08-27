import tkinter, tkinter.filedialog
import PIL.Image, PIL.ImageTk
import cv2


def load_image():
    global tk_image
    global pil_image
    global image_label

    filename = tkinter.filedialog.askopenfilename(initialdir="/", title="Select an Image")
    # load image into CV2 array
    image = cv2.imread(filename)
    # print("cv2.imread type: {}".format(type(image)))
    # convert to PIL colour order
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # print("cv2.cvtColor type: {}".format(type(image)))
    # convert array to PIL format
    pil_image = PIL.Image.fromarray(image)
    # print("PIL.Image.fromarray type: {}".format(type(image)))
    # convert to tkinter format
    tk_image = PIL.ImageTk.PhotoImage(pil_image)
    # print("PIL.ImageTk.PhotoImage type: {}".format(type(image)))

    refresh_image()

    
def refresh_image():
    # create container for loading image
    image_label = tkinter.Label(image_frame, image=tk_image).grid(row=0, column=0)
    # store a reference to the image so it won't be deleted
    # by the garbage collector
    tk_image.image = tk_image


def resize_image():
    # use earlier pil_image to resize then reconvert and display
    tk_image = pil_image.resize((200, 200), PIL.Image.ANTIALIAS)
    # print(tk_image.size)

    # convert to PhotoImage format again
    tk_image = PIL.ImageTk.PhotoImage(tk_image)

    # TODO try put this code in the refresh function
    
    # destroy the image_label container for the image before refreshing
    image_frame.winfo_children()[0].destroy()
    image_label = tkinter.Label(image_frame, image=tk_image).grid(row=0, column=0)
    tk_image.image = tk_image
    



def open_dir():
    pass

if __name__ == "__main__":

    # initial declarations
    mainWindow = tkinter.Tk()
    mainWindow.title("Viewy")
    mainWindow.geometry("640x480")
    mainWindow.configure(background='black')

    image_frame = tkinter.Frame(mainWindow, background='blue')
    image_frame.pack(fill='both', expand=True)

    menubar = tkinter.Menu(mainWindow)
    menu = tkinter.Menu(menubar, tearoff=0)
    menu.add_command(label="Load Image", command=load_image)
    menu.add_command(label="Resize Image", command=resize_image)
    
    menu.add_separator()

    menu.add_command(label="Exit", command=mainWindow.quit)
    menubar.add_cascade(label="File", menu=menu)
    
    mainWindow.config(menu=menubar)
    # load program window
    mainWindow.mainloop()
