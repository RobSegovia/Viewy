import tkinter
import tkinter.filedialog
import PIL.Image
import PIL.ImageTk
import cv2
# TODO move non-interface commands to separate module. ex: resize image, levels, etc


class MainWindow:

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

    screen_width = 0
    screen_height = 0
    win_width = 640
    win_height = 480
    win_x_offset = 2500
    win_y_offset = 100
    image_width = 0
    image_height = 0
    # aspect_locked = False

    SBW = 21  # scrollbar width

    image_scrollbar = None

    def __init__(self, mainWindow):
        self.screen_width = mainWindow.winfo_screenwidth()
        self.screen_height = mainWindow.winfo_screenheight()
        # for lock aspect ratio check button
        self.aspect_locked = tkinter.IntVar()

        mainWindow.title("Viewy")
        mainWindow.geometry("{}x{}+{}+{}".format(self.win_width,
                                                 self.win_height,
                                                 self.win_x_offset,
                                                 self.win_y_offset))
        mainWindow.configure(background='black')

        self.win_location()  # TODO del

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
        self.vert_scrollbar.pack(side=tkinter.RIGHT,
                                 fill='y')

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
        self.file_menu.add_command(
            label="Load Directory", command=self.load_dir)
        self.file_menu.add_command(
            label="New Session", command=self.new_session)
        self.file_menu.add_command(
            label="Save Session", command=self.save_session)
        # disable this option
        self.file_menu.entryconfig("Save Session", state="disabled")
        self.file_menu.add_command(
            label="Load Session", command=self.load_session)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=mainWindow.quit)

        self.view_menu.add_command(label="Zoom In", command=self.zoom_in)
        self.view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        self.view_menu.add_command(
            label="Zoom to Screen Width", command=self.zoom_to_width)
        self.view_menu.add_command(
            label="Zoom to Screen Height", command=self.zoom_to_height)
        self.view_menu.add_command(label="Reset Zoom", command=self.zoom_reset)
        self.view_menu.add_separator()
        self.view_menu.add_command(
            label="Flip Vertical", command=self.flip_vert)
        self.view_menu.add_command(
            label="Flip Horizontal", command=self.flip_horz)
        self.view_menu.add_command(
            label="Rotate Left", command=self.rotate_left)
        self.view_menu.add_command(
            label="Rotate Right", command=self.rotate_right)
        self.view_menu.add_command(
            label="Rotate Amount", command=self.rotate_amount)

        self.image_menu.add_command(label="Undo", command=self.undo)
        self.image_menu.add_command(label="Redo", command=self.redo)
        self.image_menu.add_command(
            label="Skip Image", command=self.skip_image)
        self.image_menu.add_command(label="Go Back", command=self.go_back)
        self.image_menu.add_command(
            label="Search Image on Google", command=self.search_google)
        self.image_menu.add_separator()
        self.image_menu.add_command(
            label="Resize Image", command=self.resize_image)
        self.image_menu.add_command(label="Vignette Border")
        self.image_menu.add_command(label="Brighten", command=self.brighten)
        self.image_menu.add_command(
            label="Levels - Darken", command=self.levels_darken)
        self.image_menu.add_command(label="Median", command=self.median)
        self.image_menu.add_command(
            label="Upscale Image", command=self.upscale)

        self.window_menu.add_command(label="Minimize", command=self.min_window)
        self.window_menu.add_command(
            label="Restore", command=self.restore_window)
        self.window_menu.add_command(label="Maximize", command=self.max_window)
        self.window_menu.add_separator()
        self.window_menu.add_checkbutton(
            label="Lock Aspect Ratio", variable=self.aspect_locked, command=self.lock_aspect)
        self.window_menu.add_separator()
        self.window_menu.add_command(
            label="Fit to Height of Image", command=self.win_fit_height, state='disabled')
        self.window_menu.add_command(
            label="Fit to Width of Image", command=self.win_fit_width, state='disabled')
        self.window_menu.add_command(
            label="Fit to Size of Image", command=self.win_fit_size, state='disabled')
        self.window_menu.add_separator()
        self.window_menu.add_command(
            label="Show Sidebar", state='disabled', command=self.show_sidebar)
        self.window_menu.add_command(
            label="Hide Sidebar", state='disabled', command=self.hide_sidebar)

        self.help_menu.add_command(label="Help", command=self.help)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="About", command=self.about)

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
        print(self.aspect_locked.get())

    def load_image(self):
        self.win_location()
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
            # NOTE: add_separator does not have a state!
            self.file_menu.entryconfig(3, state='normal')
            self.menubar.entryconfig("View", state='normal')
            self.menubar.entryconfig("Image", state='normal')
            self.lock_aspect()
            self.window_menu.entryconfig(10, state='normal')
            self.window_menu.entryconfig(11, state='normal')

            self.win_location()

        except:
            # raise
            print("--> No image loaded")

    def load_dir(self):
        pass

    def new_session(self):
        pass

    def save_session(self):
        pass

    def load_session(self):
        pass

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass

    def zoom_to_width(self):
        pass

    def zoom_to_height(self):
        pass

    def zoom_reset(self):
        pass

    def flip_vert(self):
        pass

    def flip_horz(self):
        pass

    def rotate_left(self):
        pass

    def rotate_right(self):
        pass

    def rotate_amount(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

    def skip_image(self):
        pass

    def go_back(self):
        pass

    def search_google(self):
        pass

    def resize_image(self):
        # use earlier pil_image to resize then reconvert and display
        self.tk_image = self.pil_image.resize((200, 200), PIL.Image.ANTIALIAS)
        # convert to PhotoImage format again
        self.tk_image = PIL.ImageTk.PhotoImage(self.tk_image)
        # destroy the image before refreshing
        self.canvas.delete("image")
        self.refresh_image()

    def brighten(self):
        pass

    def levels_darken(self):
        pass

    def median(self):
        pass

    def upscale(self):
        pass

    @staticmethod
    def min_window():
        mainWindow.wm_state('icon')

    @staticmethod
    def restore_window():
        mainWindow.wm_state('normal')

    @staticmethod
    def max_window():
        mainWindow.wm_state('zoomed')

    def lock_aspect(self):
        if not [item for item in self.canvas.find_all()]:
            # if self.aspect_locked.get() == 1:
            self.window_menu.entryconfig(6, state='disabled')
            self.window_menu.entryconfig(7, state='disabled')
            self.window_menu.entryconfig(8, state='disabled')
        else:
            if self.aspect_locked.get() == 1:
                self.window_menu.entryconfig(1, state='disabled')
                self.window_menu.entryconfig(2, state='disabled')
                self.window_menu.entryconfig(6, state='disabled')
                self.window_menu.entryconfig(7, state='disabled')
                self.window_menu.entryconfig(8, state='disabled')
            else:
                self.window_menu.entryconfig(1, state='normal')
                self.window_menu.entryconfig(2, state='normal')
                self.window_menu.entryconfig(6, state='normal')
                self.window_menu.entryconfig(7, state='normal')
                self.window_menu.entryconfig(8, state='normal')

    def win_fit_width(self):
        if (self.image_width < self.screen_width):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))
        else:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.screen_width, mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))
        print("Fit width End v")

    def win_fit_height(self):
        # self.win_location()
        if self.image_height < self.screen_height:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(mainWindow.winfo_width(), self.image_height + self.SBW, self.win_x_offset, self.win_y_offset))
        else:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(mainWindow.winfo_width(), self.screen_height, self.win_x_offset, self.win_y_offset))

    def win_fit_size(self):
        # self.win_location()

        # restore window before applying changes
        if mainWindow.wm_state() == 'zoomed':
            mainWindow.state('normal')

        if (self.image_width < self.screen_width) and (self.image_height < self.screen_height):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, self.image_height + self.SBW,  self.win_x_offset, self.win_y_offset))
        elif (self.image_width < self.screen_width) and (self.image_height >= self.screen_height):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, self.screen_height,  self.win_x_offset, self.win_y_offset))
        elif (self.image_height < self.screen_height) and (self.image_width >= self.screen_width):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.screen_width, self.image_height + self.SBW,  self.win_x_offset, self.win_y_offset))
        else:
            mainWindow.state('zoomed')  # maximize window

        # self.win_location()

    def show_sidebar(self):
        pass

    def hide_sidebar(self):
        pass

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

    def image_dimensions(self, image):
        self.image_width = image.width()
        self.image_height = image.height()

    def help(self):
        pass

    def about(self):
        pass

    def win_location(self):
        self.screen_width, self.screen_height = mainWindow.winfo_screenwidth(
        ), mainWindow.winfo_screenheight()
        self.win_x_offset, self.win_y_offset = mainWindow.winfo_rootx() - \
            8, mainWindow.winfo_rooty()-51
        # print("Screen w h :", self.screen_width, self.screen_height)
        # print("Window x y offsets: ", self.win_x_offset, self.win_y_offset)


if __name__ == "__main__":
    # initial declarations
    mainWindow = tkinter.Tk()
    # create instance of MainWindow class, call it 'app'
    app = MainWindow(mainWindow)
    # load program window
    mainWindow.mainloop()
