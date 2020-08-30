import tkinter
import tkinter.filedialog
import PIL.Image
import PIL.ImageTk
import cv2
# TODO move non-interface commands to separate module. ex: resize image, levels, etc


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

    image_width = 0
    image_height = 0

    SBW = 21  # scrollbar width

    image_scrollbar = None

    def __init__(self, mainWindow):
        mainWindow.title("Viewy")
        mainWindow.geometry("640x480+2500+100")
        mainWindow.configure(background='black')

        # Create Menu, Image backing frame, and Canvas
        self.menubar = tkinter.Menu(mainWindow)
        self.image_frame = tkinter.Frame(
            mainWindow, background='blue')
        self.image_frame.pack(fill=tkinter.BOTH, expand=True)
        self.canvas = tkinter.Canvas(
            self.image_frame, bg='red')

        # Create Scrollbars
        self.vert_scrollbar = tkinter.Scrollbar(
            self.image_frame)
        self.vert_scrollbar.config(command=self.canvas.yview)
        self.vert_scrollbar.pack(
            side=tkinter.RIGHT, fill='y')

        self.horz_scrollbar = tkinter.Scrollbar(
            self.image_frame, orient=tkinter.HORIZONTAL)
        self.horz_scrollbar.pack(side=tkinter.BOTTOM, fill='x')
        self.horz_scrollbar.config(command=self.canvas.xview)

        self.canvas.pack(fill=tkinter.BOTH, expand=True)
        self.canvas.config(
            yscrollcommand=self.vert_scrollbar.set,
            xscrollcommand=self.horz_scrollbar.set,
            scrollregion=(0, 0, self.image_width, self.image_height))
        # print(self.canvas.winfo_width(), self.canvas.winfo_height())

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
        self.view_menu.add_command(label="Zoom to Screen Width")
        self.view_menu.add_command(label="Zoom to Screen Height")
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

        self.window_menu.add_command(label="Minimize", command=self.min_window)
        self.window_menu.add_command(
            label="Restore", command=self.restore_window)
        self.window_menu.add_command(label="Maximize", command=self.max_window)
        self.window_menu.add_separator()
        self.window_menu.add_command(
            label="Fit to Height of Image", command=self.fit_height, state='disabled')
        self.window_menu.add_command(
            label="Fit to Width of Image", command=self.fit_width, state='disabled')
        self.window_menu.add_command(
            label="Fit to Size of Image", command=self.fit_size, state='disabled')
        self.window_menu.add_separator()
        self.window_menu.add_command(label="Show Sidebar", state='disabled')
        self.window_menu.add_command(label="Hide Sidebar", state='disabled')

        self.help_menu.add_command(label="Help")
        self.help_menu.add_separator()
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
        # print(mainWindow.wm_state()) # TODO del

    @staticmethod
    def min_window():
        mainWindow.wm_state('icon')

    @staticmethod
    def restore_window():
        mainWindow.wm_state('normal')

    @staticmethod
    def max_window():
        mainWindow.wm_state('zoomed')

    def load_image(self):
        print(mainWindow.geometry())  # TODO del this
        try:
            filename = tkinter.filedialog.askopenfilename(
                initialdir="/", title="Select an Image")
            # load image into CV2 array
            self.cv2_image = cv2.imread(filename)
            # convert to PIL colour order
            self.cv2_image = cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2RGB)
            # convert array to PIL format
            self.pil_image = PIL.Image.fromarray(self.cv2_image)
            # convert to tkinter format
            self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
            self.image_dimensions(self.tk_image)

            self.refresh_image()

            # enable menu items once an image is loaded
            print(self.file_menu.entrycget(3, 'state'))
            self.file_menu.entryconfig(3, state='normal')
            self.menubar.entryconfig("View", state='normal')
            self.menubar.entryconfig("Image", state='normal')
            self.window_menu.entryconfig(4, state=tkinter.NORMAL)
            self.window_menu.entryconfig(5, state='normal')
            self.window_menu.entryconfig(6, state='normal')
            self.window_menu.entryconfig(8, state='normal')
            self.window_menu.entryconfig(9, state='normal')

        except:
            raise
            print("--> No image loaded")

    def refresh_image(self):
        # delete any previous image before refreshing
        self.canvas.delete("image")

        # load image into canvas
        self.canvas.create_image(
            0, 0, anchor=tkinter.NW, image=self.tk_image, tag="image")
        self.image_dimensions(self.tk_image)
        self.canvas.config(
            yscrollcommand=self.vert_scrollbar.set,
            xscrollcommand=self.horz_scrollbar.set,
            scrollregion=(0, 0, self.image_width, self.image_height))

        # store a reference to the image so it won't be deleted
        # by the garbage collector
        self.tk_image.image = self.tk_image
        # print(mainWindow.wm_state()) # TODO del

    def resize_image(self):
        # use earlier pil_image to resize then reconvert and display
        self.tk_image = self.pil_image.resize((200, 200), PIL.Image.ANTIALIAS)
        # convert to PhotoImage format again
        self.tk_image = PIL.ImageTk.PhotoImage(self.tk_image)
        # destroy the image before refreshing
        self.canvas.delete("image")
        self.refresh_image()

    def image_dimensions(self, image):
        self.image_width = image.width()
        self.image_height = image.height()

    def fit_height(self):
        screen_width, screen_height = mainWindow.winfo_screenwidth(
        ), mainWindow.winfo_screenheight()
        if (self.image_height < screen_height):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(mainWindow.winfo_width(), self.image_height + self.SBW, 1921, 0))
        else:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(mainWindow.winfo_width(), screen_height, 1921, 0))

    def fit_width(self):
        screen_width, screen_height = mainWindow.winfo_screenwidth(
        ), mainWindow.winfo_screenheight()
        if (self.image_width < screen_width):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, mainWindow.winfo_height(), 1921, 0))
        else:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(screen_width, mainWindow.winfo_height(), 1921, 0))

    def fit_size(self):
        # restore window before applying changes
        if mainWindow.wm_state() == 'zoomed':
            mainWindow.state('normal')

        screen_width, screen_height = mainWindow.winfo_screenwidth(
        ), mainWindow.winfo_screenheight()
        if (self.image_width < screen_width) and (self.image_height < screen_height):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, self.image_height + self.SBW, 1921, 0))
        elif (self.image_width < screen_width) and (self.image_height >= screen_height):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, screen_height, 1921, 0))
        elif (self.image_height < screen_height) and (self.image_width >= screen_width):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(screen_width, self.image_height + self.SBW, 1921, 0))
        else:
            mainWindow.state('zoomed')  # maximize window
            # mainWindow.geometry(
            #     "{}x{}+{}+{}".format(screen_width, screen_height, 1921, 0))

    def open_dir(self):
        pass


if __name__ == "__main__":

    # initial declarations
    mainWindow = tkinter.Tk()

    # create instance of MainWindow class, call it 'app'
    app = MainWindow(mainWindow)

    # load program window
    mainWindow.mainloop()
