import tkinter
import tkinter.filedialog
import PIL.Image
import PIL.ImageTk
import cv2


class MainWindow():

    menubar = None
    file_menu = None
    view_menu = None
    image_menu = None
    window_menu = None
    help_menu = None

    image_frame = None
    image_label = None
    cv2_image = None
    pil_image = None
    tk_image = None

    def __init__(self, mainWindow):
        mainWindow.title("Viewy")
        mainWindow.geometry("640x480+2500+100")
        mainWindow.configure(background='black')

        self.menubar = tkinter.Menu(mainWindow)
        self.image_frame = tkinter.Frame(mainWindow, background='blue')
        self.image_frame.pack(fill='both', expand=True)

        self.file_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.view_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.image_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.window_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.help_menu = tkinter.Menu(self.menubar, tearoff=0)

        self.file_menu.add_command(
            label="Load Image(s)", command=self.load_image)
        self.file_menu.add_command(label="Load Directory")
        self.file_menu.add_command(label="New Session")
        self.file_menu.add_command(label="Save Session")
        # disable this option
        self.file_menu.entryconfig("Save Session", state="disabled")
        self.file_menu.add_command(label="Load Session")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=mainWindow.quit)

        self.view_menu.add_command(label="Zoom In")
        self.view_menu.add_command(label="Zoom Out")
        self.view_menu.add_command(label="Reset Zoom")
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Flip Vertical")
        self.view_menu.add_command(label="Flip Horizontal")
        self.view_menu.add_command(label="Rotate Left")
        self.view_menu.add_command(label="Rotate Right")
        self.view_menu.add_command(label="Rotate Amount")

        self.image_menu.add_command(label="Undo")
        self.image_menu.add_command(label="Redo")
        self.image_menu.add_command(label="Skip Image")
        self.image_menu.add_command(label="Go Back")
        self.image_menu.add_command(label="Search Image on Google")
        self.image_menu.add_separator()
        self.image_menu.add_command(
            label="Resize Image", command=self.resize_image)
        self.image_menu.add_command(label="Vignette Border")
        self.image_menu.add_command(label="Brighten")
        self.image_menu.add_command(label="Levels - Darken")
        self.image_menu.add_command(label="Median")
        self.image_menu.add_command(label="Upscale Image")

        self.window_menu.add_command(label="Minimize")
        self.window_menu.add_command(label="Maximize")
        self.window_menu.add_separator()
        self.window_menu.add_command(label="Stretch to Height")
        self.window_menu.add_command(label="Stretch to Width")
        self.window_menu.add_separator()
        self.window_menu.add_command(label="Show Sidebar")
        self.window_menu.add_command(label="Hide Sidebar")

        self.help_menu.add_command(label="Help")
        self.help_menu.add_command(label="About")

        # add menubar labels
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(
            label="View", menu=self.view_menu, state='disabled')
        self.menubar.add_cascade(
            label="Image", menu=self.image_menu, state='disabled')
        self.menubar.add_cascade(
            label="Window", menu=self.window_menu)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        mainWindow.config(menu=self.menubar)

    def load_image(self):
        filename = tkinter.filedialog.askopenfilename(
            initialdir="/", title="Select an Image")
        # load image into CV2 array
        self.cv2_image = cv2.imread(filename)
        # print("cv2.imread type: {}".format(type(image)))
        # convert to PIL colour order
        self.cv2_image = cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2RGB)
        # print("cv2.cvtColor type: {}".format(type(image)))
        # convert array to PIL format
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        # print("PIL.Image.fromarray type: {}".format(type(image)))
        # convert to tkinter format
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        # print("PIL.ImageTk.PhotoImage type: {}".format(type(image)))
        self.refresh_image()

    def refresh_image(self):
        # create container for loading image
        self.image_label = tkinter.Label(
            self.image_frame, image=self.tk_image).grid(row=0, column=0)
        # store a reference to the image so it won't be deleted
        # by the garbage collector
        self.tk_image.image = self.tk_image

    def resize_image(self):
        # use earlier pil_image to resize then reconvert and display
        self.tk_image = self.pil_image.resize((200, 200), PIL.Image.ANTIALIAS)
        # convert to PhotoImage format again
        self.tk_image = PIL.ImageTk.PhotoImage(self.tk_image)
        # destroy the image_label container for the image before refreshing
        [child_frame.destroy()
         for child_frame in self.image_frame.winfo_children()]
        print([child_frame for child_frame in self.image_frame.winfo_children()])
        self.refresh_image()

    def enable_menu(self):
        pass

    # TODO fix this
    def disable_menu(self, menu, index):
        menu.entryconfig(index, state="disabled")

    def open_dir(self):
        pass


if __name__ == "__main__":

    # initial declarations
    mainWindow = tkinter.Tk()

    # create instance of MainWindow class, call it 'app'
    app = MainWindow(mainWindow)

    # load program window
    mainWindow.mainloop()
