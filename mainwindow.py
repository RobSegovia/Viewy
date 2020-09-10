import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import PIL.Image
import PIL.ImageTk
import numpy
import cv2
import os
import psutil
import random
import requests
import webbrowser
import subprocess
# TODO move non-interface commands to separate module. ex: resize image, levels, etc


class MainWindow:

    menubar = None
    file_menu = None
    view_menu = None
    image_menu = None
    window_menu = None
    help_menu = None

    menubar_sel = None
    submenu_sel = None

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

    SBW = 21  # scrollbar width

    image_scrollbar = None

    def __init__(self, mainWindow):
        self.screen_width = mainWindow.winfo_screenwidth()
        self.screen_height = mainWindow.winfo_screenheight()
        # for lock aspect ratio check button
        self.aspect_locked = tkinter.IntVar()
        self.status_text = tkinter.StringVar()
        self.status_text.set("  Welcome to Viewy!")
        self.info_text = tkinter.StringVar()
        self.zoom_text = tkinter.StringVar()
        self.zoom_value = 100

        self.image_index = None
        self.filenames_string = None
        self.filenames_list = []
        self.new_filenames_list = []
        self.total_images = None
        self.image_exists = False

        self.load_image_var = tkinter.IntVar()
        self.load_dir_var = tkinter.IntVar()
        self.random_on = tkinter.IntVar()
        self.zoom_auto_var = tkinter.IntVar()
        self.zoom_width_var = tkinter.IntVar()
        self.zoom_height_var = tkinter.IntVar()
        self.image_path = tkinter.StringVar()
        self.image_name = tkinter.StringVar()
        self.image_folder = tkinter.StringVar()
        self.image_size = tkinter.StringVar()

        self.prev_x = 0
        self.prev_y = 0

        self.prev_px = None
        self.prev_py = None
        self.new_posx = 0
        self.new_posy = 0
        self.initial_scroll_posx = True
        self.initial_scroll_posy = True
        self.img_pxx_percent = 0
        self.img_pxy_percent = 0
        self.diffx = 0
        self.diffy = 0
        self.b1_released = True

        self.zoom_factor = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
        self.zoom_index = 3

        self.image_flip = None
        self.image_flipped = False

        mainWindow.title("Viewy")
        mainWindow.geometry("{}x{}+{}+{}".format(self.win_width,
                                                 self.win_height,
                                                 self.win_x_offset,
                                                 self.win_y_offset))
        mainWindow.configure()
        mainWindow.bind('<Key>', self.load)
        mainWindow.bind('<MouseWheel>', self.zoom_in)

        self.win_location()  # TODO del ???

        # Create Menu, Image backing frame, and Canvas
        self.menubar = tkinter.Menu(mainWindow)
        self.menubar.bind('<<MenuSelect>>', self.menubar_selected)

        self.image_frame = tkinter.Frame(
            mainWindow)
        self.image_frame.pack(fill=tkinter.BOTH, expand=True)

        self.canvas = tkinter.Canvas(
            self.image_frame, bg='black')
        self.canvas.bind('<Configure>', self.refresh_image)
        self.canvas.bind('<B1-Motion>', self.drag_image)
        self.canvas.bind('<ButtonRelease-1>', self.b1_release)

        # Create Scrollbars
        self.vert_scrollbar = tkinter.Scrollbar(
            self.image_frame)
        self.vert_scrollbar.config(command=self.canvas.yview)
        # self.vert_scrollbar.pack(side=tkinter.RIGHT,
        #                          fill='y')
        # self.vert_scrollbar.pack_forget()

        self.horz_scrollbar = tkinter.Scrollbar(
            self.image_frame, orient=tkinter.HORIZONTAL)
        self.horz_scrollbar.config(command=self.canvas.xview)
        # self.horz_scrollbar.pack(side=tkinter.BOTTOM, fill='x')
        # self.horz_scrollbar.pack_forget()

        self.canvas.pack(fill=tkinter.BOTH, expand=True)
        self.canvas.config(
            yscrollcommand=self.vert_scrollbar.set,
            xscrollcommand=self.horz_scrollbar.set,
            scrollregion=(0, 0, self.image_width, self.image_height))

        self.file_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.file_menu.bind('<<MenuSelect>>', self.status_update)
        self.view_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.view_menu.bind('<<MenuSelect>>', self.status_update)
        self.image_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.image_menu.bind('<<MenuSelect>>', self.status_update)
        self.timed_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.timed_menu.bind('<<MenuSelect>>', self.status_update)
        self.window_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.window_menu.bind('<<MenuSelect>>', self.status_update)
        self.help_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.help_menu.bind('<<MenuSelect>>', self.status_update)

        self.menu_dict = {
            0: {
                0: "Load 1 or more images",
                1: "Load a directory of images",
                2: "Start a new session and customize timing options",
                3: "Edit a current session",
                4: "Save your current session",
                5: "Load a previously saved session",
                6: None,
                7: "Exit the program"
            },
            1: {
                0: "Zoom into the image",
                1: "Zoom out from the image",
                2: "Zoom image to fit the width of the window",
                3: "Zoom image to fit the height of the window",
                4: "Automatically zoom every image to fit the window",
                5: "Reset the image to its original aspect",
                6: None,
                7: "Flip the image vertically",
                8: "Flip the image horizontally",
                9: "Rotate the image counter-clockwise",
                10: "Rotate the image clockwise",
                11: "Rotate the image by a custom amount",
                12: None,
                13: "Show information about the image"
            },
            2: {
                0: "Undo the last action",
                1: "Redo the undone action",
                2: "Go to the next image",
                3: "Go back to the previous image",
                4: "Search this image on Google",
                5: None,
                6: "Resize the image by custom amount",
                7: "Add a vignette border to the image",
                8: "Brighten the image",
                9: "Apply Levels - Darken to the image",
                10: "Apply a Median filter to the image",
                11: "Upscale the image",
                12: None,
                13: "Randomize the order of the images"
            },
            3: {
                0: "Pause or Continue the timer",
                1: "Skip to the next timer interval",
                2: "Go back to the previous timer interval"
            },
            4: {
                0: "Minimize the program window",
                1: "Restore the program window",
                2: "Fit the window to the screen's width",
                3: "Fit the window to the screen's height",
                4: "Maximize the window",
                5: None,
                6: "Lock the current aspect ratio of the window",
                7: None,
                8: "Fit the window to the width of the image",
                9: "Fit the window to the height of the image",
                10: "Fit the window to the size of the image",
                11: None,
                12: "Show the tools sidebar",
                13: "Hide the tools sidebar"
            },
            5: {
                0: "Access help documentation",
                1: None,
                2: "About this program"
            }
        }

        self.file_types = [
            ('Image Files', '*.jpeg;*.jpg;*.jpe;*.jp2;*.jfif;*.png;*.bmp;*.dib;*.webp;*.tiff;*.tif'),
            ('All Files', '*.*')
        ]
        self.file_types_list = self.file_types[0][1].split(';')

        # add menubar labels
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(
            label="View", menu=self.view_menu, state='disabled')
        self.menubar.add_cascade(
            label="Image", menu=self.image_menu, state='disabled')
        self.menubar.add_cascade(
            label="Timed Session", menu=self.timed_menu, state='normal')
        self.menubar.add_cascade(
            label="Window", menu=self.window_menu)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        self.file_menu.add_command(
            label="Load Image(s)", command=self.load_image)
        # self.file_menu.bind("<<MenuSelect>>", self.status_update)
        self.file_menu.add_command(
            label="Load Directory", command=self.load_dir)
        self.file_menu.add_command(
            label="New Session", command=self.new_session)
        self.file_menu.add_command(
            label="Edit Session", command=self.edit_session)
        self.file_menu.entryconfig("Edit Session", state="disabled")
        self.file_menu.add_command(
            label="Save Session", command=self.save_session)
        self.file_menu.entryconfig("Save Session", state="disabled")
        self.file_menu.add_command(
            label="Load Session", command=self.load_session)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=mainWindow.quit)

        self.view_menu.add_command(label="Zoom In", command=self.zoom_in)
        self.view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        self.view_menu.add_checkbutton(
            label="Zoom to Window Width", variable=self.zoom_width_var, command=self.zoom_to_width)
        self.view_menu.add_checkbutton(
            label="Zoom to Window Height", variable=self.zoom_height_var, command=self.zoom_to_height)
        self.view_menu.add_checkbutton(
            label="Auto Zoom to Fit Window", variable=self.zoom_auto_var, command=self.zoom_auto)
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
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Image Info", command=self.image_info)

        self.image_menu.add_command(label="Undo", command=self.undo)
        self.image_menu.add_command(label="Redo", command=self.redo)
        self.image_menu.add_command(
            label="Next Image", command=self.skip_image)
        self.image_menu.add_command(
            label="Previous Image", command=self.prev_image)
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
        self.image_menu.add_separator()
        self.image_menu.add_checkbutton(
            label="Random Order of Images", variable=self.random_on, command=self.randomizer)

        self.timed_menu.add_command(
            label="Pause/Continue", command=self.pause)
        self.timed_menu.add_command(
            label="Next Timed Interval", command=self.next_interval)
        self.timed_menu.add_command(
            label="Previous Timed Interval", command=self.prev_interval)

        self.window_menu.add_command(label="Minimize", command=self.min_window)
        self.window_menu.add_command(
            label="Restore", command=self.restore_window)
        self.window_menu.add_command(
            label="Fit to Screen Width", command=self.fit_screen_width)
        self.window_menu.add_command(
            label="Fit to Screen Height", command=self.fit_screen_height)
        self.window_menu.add_command(label="Maximize", command=self.max_window)
        self.window_menu.add_separator()
        self.window_menu.add_checkbutton(
            label="Lock Aspect Ratio", variable=self.aspect_locked, command=self.lock_aspect)
        self.window_menu.add_separator()
        self.window_menu.add_command(
            label="Fit to Width of Image", command=self.win_fit_width, state='disabled')
        self.window_menu.add_command(
            label="Fit to Height of Image", command=self.win_fit_height, state='disabled')
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

        mainWindow.config(menu=self.menubar)

        # Status bar at bottom of screen
        # Using anchor= instead of justify= because justify on ly works for multiline
        self.status_bar = tkinter.Label(
            relief=tkinter.SUNKEN, anchor='w', textvariable=self.status_text)
        self.status_bar.pack(side='left', fill='x', expand=True)

        self.zoom_bar = tkinter.Label(
            relief='sunken',
            anchor='e',
            textvariable=self.zoom_text,
            width=15)
        self.zoom_bar.pack(side='right', fill='x')

        # Info bar which sits beside status bar
        self.info_bar = tkinter.Label(
            relief='sunken',
            anchor='e',
            textvariable=self.info_text,
            width=20)
        self.info_bar.pack(side='right', fill='x')

    def menubar_selected(self, event=None):
        # update the menubar item attribute for use in status bar function
        self.menubar_sel = mainWindow.call(event.widget, 'index', 'active')

    def status_update(self, event=None):
        self.submenu_sel = mainWindow.call(event.widget, 'index', 'active')
        if isinstance(self.menubar_sel, int) and isinstance(self.submenu_sel, int):

            # TODO may not need this condition anymore ??
            if self.menu_dict[self.menubar_sel-1][self.submenu_sel] is not None:
                # print(self.menu_dict[self.menubar_sel-1][self.submenu_sel])
                self.status_text.set("  {}".format(
                    self.menu_dict[self.menubar_sel-1][self.submenu_sel]))

        else:
            self.status_text.set("")

    def load_image(self):
        self.load_image_var.set(1)
        self.load()

    def load_dir(self):
        self.load_dir_var.set(1)
        self.load()

    # TODO: requires refactoring !!!!!!!
    def load(self, event=None):

        # poll window location before refreshing
        self.win_location()

        # load one or more images
        if event is None and self.load_image_var.get() == 1:

            try:
                # disable randomization at beginning
                self.random_on.set(0)
                self.total_images = 0
                self.filenames_list.clear()
                # returns tuple of image paths
                self.filenames_string = tkinter.filedialog.askopenfilenames(title="Select one or more images",
                                                                            filetypes=self.file_types)
                # populate tuple items into list items
                for item in self.filenames_string:
                    self.filenames_list.append(item)

                # this index is always 0 here, it will get ++ or -- as images are iterated later
                self.image_index = 0

                self.total_images = len(self.filenames_list)
                assert self.total_images >= 1
                self.image_exists = True

            except:
                # raise
                self.status_text.set("  No image loaded")

            else:
                if self.total_images == 1:
                    self.status_text.set("  Image was loaded successfully")
                elif self.total_images > 1:
                    self.info_text.set("{} of {} images  ".format(
                        self.image_index, self.total_images))
                    self.status_text.set("  {} images were queued successfully".format(
                        len(self.filenames_string)))

                self.restore_menu_items()
            # set to 0 so it won't run next time
            # unless it's turned on by accessing its menu option
            self.load_image_var.set(0)

        # load directory
        elif event is None and self.load_dir_var.get() == 1:

            try:
                self.new_filenames_list.clear()
                # disable randomization at beginning
                self.random_on.set(0)
                # returns tuple of image paths
                self.dir_path = tkinter.filedialog.askdirectory(
                    title="Select a directory of images to load")
                # this index is always 0 here, it will get ++ or -- as images are iterated later
                self.image_index = 0

                for file_name in os.listdir(self.dir_path):
                    full_path = os.path.join(self.dir_path, file_name)

                    # for every extension type in the reference list
                    for string in self.file_types_list:
                        # if the extension exists in the element
                        if (file_name[-4:] in string):
                            # then add it to the list
                            self.new_filenames_list.append(full_path)
                    # NOTE: list comprehension version; for loop is more readable in this case
                    # [self.filenames_list.append(full_path) for string in self.file_types_list if (
                    #     file_name[-4:] in string)]

                self.total_images = len(self.new_filenames_list)
                assert self.total_images >= 1

            except FileNotFoundError:
                # raise
                self.status_text.set(" Action canceled - No directory loaded")
            except IndexError:
                # raise
                self.status_text.set(" No files to load")
            except AssertionError:
                self.status_text.set(" No valid files to load")

            else:
                # reset filenames_list
                self.filenames_list.clear()
                self.image_exists = True
                self.filenames_list = self.new_filenames_list.copy()

                if self.total_images == 1:
                    self.status_text.set("  Image was loaded successfully")
                else:
                    self.info_text.set("{} of {} images  ".format(
                        self.image_index, self.total_images))
                    self.status_text.set("  {} images were queued successfully".format(
                        len(self.filenames_list)))
                self.restore_menu_items()

            self.load_dir_var.set(0)

        # if a key has been pressed, cycle to next/prev image
        if event is not None:
            if event.keysym == 'Right' and self.image_index < len(self.filenames_list) - 1:
                self.image_index += 1
            elif event.keysym == 'Left' and self.image_index > 0:
                self.image_index -= 1

        # if AUTO ZOOM is OFF
        if self.image_exists and self.zoom_auto_var.get() == 0:
            try:
                # print("** if zoom is off, finish loading image in load()\n")
                # load the first image into CV2 array
                # print(self.filenames_list[self.image_index])
                self.cv2_image = cv2.imread(
                    self.filenames_list[self.image_index])

                # convert to PIL colour order
                self.cv2_image = cv2.cvtColor(
                    self.cv2_image, cv2.COLOR_BGR2RGB)
                # convert array to PIL format
                self.pil_image = PIL.Image.fromarray(self.cv2_image)
                # convert to tkinter format
                self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
                self.image_dimensions(self.tk_image, 'tk_image')

                # store original dimensions of image
                self.original_image_width, self.original_image_height = self.image_width, self.image_height
                self.refresh_image()
                self.set_path()
            except IndexError:
                print(" No image to load")
            except:
                raise
                print("-> Image could not be loaded")

        # AUTO ZOOM is ON
        if self.zoom_auto_var.get() == 1:
            try:
                # NOTE image needs to load after key event
                # before it can be resized...
                # load the image into CV2 array
                self.cv2_image = cv2.imread(
                    self.filenames_list[self.image_index])

                # convert to PIL colour order
                self.cv2_image = cv2.cvtColor(
                    self.cv2_image, cv2.COLOR_BGR2RGB)
                # convert array to PIL format
                self.pil_image = PIL.Image.fromarray(self.cv2_image)

                self.image_dimensions(self.pil_image, 'pil_image')
                self.set_path()

                # print("Auto zoom is on:", self.zoom_auto_var.get())
                # print("win size:", mainWindow.winfo_width(),
                #       mainWindow.winfo_height())
                # print("image size:", self.image_width, self.image_height)

                w1 = mainWindow.winfo_width()
                h1 = mainWindow.winfo_height()
                w2 = self.image_width
                h2 = self.image_height

                min_of_window = min(w1, h1)
                max_of_window = max(w1, h1)

                win_ratio = w1 / h1
                image_ratio = w2 / h2

                # print("Min Max of window:", min_of_window, max_of_window)
                # print("Win ratio:", win_ratio)
                # print("Image ratio:", image_ratio)

                # if ratios = same, resize both w and h to same size as window w and h
                if win_ratio == 1 and image_ratio == 1:
                    self.resize_image(w1, h1)
                    print("1-")

                # if both are horizontal
                elif win_ratio >= 1 and image_ratio >= 1:
                    # same size
                    if win_ratio == image_ratio:
                        self.resize_image(w1-10, h1-10)
                        print("2--1")
                    # if window ratio is wider than image ratio
                    # then min of win ==> min of image
                    elif win_ratio > image_ratio:
                        self.resize_image(
                            int(min_of_window * image_ratio)-int(21*image_ratio), min_of_window-21)
                        print("2--2")
                    # if window ratio is less wide than image ratio
                    # then max of win ==> max of image
                    else:
                        self.resize_image(
                            max_of_window-10, int(max_of_window / image_ratio)-int(10/image_ratio))
                        print("2--3")

                # if both are vertical
                elif win_ratio <= 1 and image_ratio <= 1:
                    # same size
                    if win_ratio == image_ratio:
                        self.resize_image(w1, h1)
                        print("3--1")
                    # if window ratio is more(shorter) than image ratio
                    # then max of win ==> max of image
                    elif win_ratio > image_ratio:
                        self.resize_image(
                            int(max_of_window * image_ratio)-int(21*image_ratio), max_of_window-21)
                        print("3--2")
                    # if window ratio is less(taller) than image ratio
                    # then min of win ==> min of image
                    else:
                        self.resize_image(
                            min_of_window-10, int(min_of_window / image_ratio)-int(10/image_ratio))
                        print("3--3")

                # TODO fix this case
                # if win is vertical and image is horizontal
                elif win_ratio <= 1 and image_ratio >= 1:
                    # max of image ==> min of window
                    self.resize_image(min_of_window-10, int(
                        min_of_window / image_ratio)-int(10/image_ratio))
                    print("4-")

                # if win is horizontal and image is verical
                elif win_ratio >= 1 and image_ratio <= 1:
                    # min of window ==> max of image
                    self.resize_image(
                        int(min_of_window * image_ratio)-int(21*image_ratio), min_of_window-21)
                    print("5-")

            except:
                print("-> Zoom ON - No image loaded")

        if self.zoom_width_var.get() == 1:
            ratio = self.original_image_width/self.original_image_height
            width = mainWindow.winfo_width()-21
            self.resize_image(width, int(width / ratio))

        elif self.zoom_height_var.get() == 1:
            ratio = self.original_image_width/self.original_image_height
            height = mainWindow.winfo_height()-42
            self.resize_image(int(height * ratio), height)

        # poll window location after window was refreshed
        self.win_location()

        if self.image_exists:
            if self.zoom_auto_var.get() == 0:
                self.zoom_value = 100
                self.zoom_text.set("Zoom: {}%".format(self.zoom_value))
            if self.total_images >= 1:
                self.info_text.set("Image {} of {}  ".format(
                    self.image_index+1, self.total_images))

        # print("image flip:", self.image_flip,
        #       "image flipped:", self.image_flipped)

    def set_path(self):
        # self.image_path.set(self.filenames_list[self.image_index])
        path = os.path.split(os.path.abspath(
            self.filenames_list[self.image_index]))
        self.image_name.set(path[1])
        self.image_folder.set(path[0])
        # self.image_dimensions(self.tk_image, 'tk_image')
        self.image_size.set("{} x {} px".format(
            self.image_width, self.image_height))
        # print("set_path: ", self.image_path.get())

    def restore_menu_items(self):
        # self.file_menu.entryconfig(3, state='normal')
        self.menubar.entryconfig("View", state='normal')
        self.menubar.entryconfig("Image", state='normal')
        self.lock_aspect()
        self.window_menu.entryconfig(8, state='normal')
        self.window_menu.entryconfig(9, state='normal')
        self.window_menu.entryconfig(10, state='normal')
        self.window_menu.entryconfig(12, state='normal')
        self.window_menu.entryconfig(13, state='normal')

    def new_session(self):
        self.win_location()
        self.new_session_win = tkinter.Toplevel()
        self.new_session_win.resizable(False, False)
        self.new_session_win.title('Start a New Session')
        self.new_session_win.geometry("{}x{}+{}+{}".format(450, 450,
                                                           self.win_x_offset+80, self.win_y_offset+80))
        self.new_session_win.attributes('-topmost', 'true')

        self.new_session_win.grid_rowconfigure(0, weight=10)
        self.new_session_win.grid_rowconfigure(1, weight=1)
        self.new_session_win.grid_rowconfigure(2, weight=5)
        self.new_session_win.grid_rowconfigure(3, weight=1)
        self.new_session_win.grid_rowconfigure(4, weight=1)
        self.new_session_win.grid_rowconfigure(5, weight=1)
        self.new_session_win.grid_rowconfigure(6, weight=1)
        self.new_session_win.grid_rowconfigure(7, weight=4)
        self.new_session_win.grid_rowconfigure(8, weight=1)
        self.new_session_win.grid_rowconfigure(9, weight=1)
        self.new_session_win.grid_rowconfigure(10, weight=8)
        self.new_session_win.grid_rowconfigure(11, weight=1)
        self.new_session_win.grid_rowconfigure(12, weight=1)
        self.new_session_win.grid_rowconfigure(13, weight=10)
        self.new_session_win.grid_columnconfigure(0, weight=4)
        self.new_session_win.grid_columnconfigure(1, weight=1)
        self.new_session_win.grid_columnconfigure(2, weight=1)
        self.new_session_win.grid_columnconfigure(3, weight=1)
        self.new_session_win.grid_columnconfigure(4, weight=1)
        self.new_session_win.grid_columnconfigure(5, weight=5)
        self.new_session_win.grid_columnconfigure(6, weight=4)
        self.new_session_win.grid_columnconfigure(7, weight=6)
        self.new_session_win.grid_columnconfigure(8, weight=4)

        dir_label = tkinter.Label(
            self.new_session_win, text="Directories:", anchor='w')
        dir_label.grid(row=1, column=1, sticky='w')
        dir_box = tkinter.Text(self.new_session_win,
                               width=35, height=10)
        dir_box.grid(row=2, column=1, sticky='w', rowspan=5, columnspan=5)

        add_dir_label = tkinter.Label(
            self.new_session_win, text="Add\nDirectories:", anchor='w', justify='left')
        add_dir_label.grid(row=2, column=7, sticky='w')
        browse_button = tkinter.Button(self.new_session_win, text="Browse")
        browse_button.grid(row=3, column=7)
        incl_subdirs = tkinter.Checkbutton(
            self.new_session_win, text="Include\nSubdirectories", justify='left')
        incl_subdirs.grid(row=4, column=7, sticky='w')

        browse_separator = tkinter.ttk.Separator(
            self.new_session_win, orient='horizontal')
        browse_separator.grid(row=5, column=7, sticky='we')

        remove_dir = tkinter.Button(
            self.new_session_win, text="Remove\nDirectory", state='disabled')
        remove_dir.grid(row=6, column=7)

        # mid_separator = tkinter.ttk.Separator(
        #     self.new_session_win, orient='horizontal')
        # mid_separator.grid(row=7, column=2, sticky='we', columnspan=3)

        add_time_label = tkinter.Label(
            self.new_session_win, text="  Add time intervals per image:")
        add_time_label.grid(row=8, column=1, sticky='w', columnspan=5)

        minute_box = tkinter.Text(
            self.new_session_win, width=3, height=1, padx=5)
        minute_box.grid(row=9, column=1, sticky='e')
        minute_label = tkinter.Label(
            self.new_session_win, text="minutes", anchor='w')
        minute_label.grid(row=9, column=2, sticky='w')

        seconds_box = tkinter.Text(
            self.new_session_win, width=3, height=1, padx=5)
        seconds_box.grid(row=9, column=3, sticky='e')
        seconds_label = tkinter.Label(
            self.new_session_win, text="seconds", anchor='w')
        seconds_label.grid(row=9, column=4, sticky='w')

        add_time_button = tkinter.Button(
            self.new_session_win, text="Add Interval")
        add_time_button.grid(row=9, column=5, sticky='e')

        intervals_box = tkinter.Text(self.new_session_win, width=30, height=8)
        intervals_box.grid(row=10, column=1, rowspan=2, columnspan=5)

        start_button = tkinter.Button(
            self.new_session_win, text="Start", bd=4, padx=20, pady=10)
        start_button.grid(row=11, column=7)

        info_bar = tkinter.Label(self.new_session_win,
                                 text="123 folders and 12345 images selected")
        info_bar.grid(row=13, column=2, columnspan=5)

    def edit_session(self):
        # same as new session with current directories pre-loaded
        pass

    def save_session(self):
        # use pickle ??
        pass

    def load_session(self):
        pass

    def zoom_in(self, event=None):
        # print("Find image:", self.canvas.find_withtag('image')[0])
        # try:
        if self.image_exists:
            if (self.zoom_index < 7) and (event.delta > 0):
                self.zoom_index += 1
                # print("Zoom index:", self.zoom_index)
                factor = self.zoom_factor[self.zoom_index]
                # print("Factor:", factor)
                self.resize_image(int(self.original_image_width * factor),
                                  int(self.original_image_height * factor))
                # print("Zoom value:", self.zoom_value)
                self.zoom_value += 25
                # print("Zoom value:", self.zoom_value)
                # print()
                self.zoom_text.set("Zoom: {:.0f}%".format(self.zoom_value))
            elif event.delta < 0:
                self.zoom_out(event)
        # except:
        #     print("-> No image loaded yet to zoom into")

    def zoom_out(self, event=None):
        if self.zoom_index > 0:
            self.zoom_index -= 1
            # print("Zoom index:", self.zoom_index)
            factor = self.zoom_factor[self.zoom_index]
            # print("Factor:", factor)
            self.resize_image(int(self.original_image_width * factor),
                              int(self.original_image_height * factor))
            # print("Zoom value:", self.zoom_value)
            self.zoom_value -= 25
            # print("Zoom value:", self.zoom_value)
            # print()
            self.zoom_text.set("Zoom: {:.0f}%".format(self.zoom_value))

    def zoom_to_width(self):
        self.zoom_height_var.set(0)
        self.zoom_auto_var.set(0)
        self.load()

    def zoom_to_height(self):
        self.zoom_width_var.set(0)
        self.zoom_auto_var.set(0)
        self.load()

    def zoom_auto(self):
        self.zoom_width_var.set(0)
        self.zoom_height_var.set(0)
        self.load()

    def zoom_reset(self):
        self.resize_image(self.original_image_width,
                          self.original_image_height)

    def flip_vert(self):
        # self.image_flip = 0
        # self.load()
        self.cv2_image = cv2.flip(self.cv2_image, 0)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def flip_horz(self):
        # self.image_flip = 1
        # self.load()
        self.cv2_image = cv2.flip(self.cv2_image, 1)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def rotate_left(self):
        self.cv2_image = cv2.rotate(
            self.cv2_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def rotate_right(self):
        self.cv2_image = cv2.rotate(
            self.cv2_image, cv2.ROTATE_90_CLOCKWISE)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def rotate_amount(self):
        # image_center = tuple(numpy.array(self.cv2_image.shape[1::-1]) / 2)
        # rotate_matrix = cv2.getRotationMatrix2D(image_center, -90, 1.0)
        # self.cv2_image = cv2.warpAffine(self.cv2_image, rotate_matrix,
        #                                 self.cv2_image.shape[1::-1], flags=cv2.INTER_LINEAR)
        pass

    def image_info(self):
        # TODO add a popup window with info about image...size, name, etc
        # tkinter.messagebox.showinfo(
        #     "Image Information", "Is this the message?")
        self.win_location()
        popup = tkinter.Toplevel()
        popup.title('Image Info')
        popup.geometry("{}x{}+{}+{}".format(500, 150,
                                            self.win_x_offset+100, self.win_y_offset+160))
        popup.attributes('-topmost', 'true')
        popup.grid_rowconfigure(0, weight=10)
        popup.grid_rowconfigure(1, weight=1)
        popup.grid_rowconfigure(2, weight=1)
        popup.grid_rowconfigure(3, weight=1)
        popup.grid_rowconfigure(4, weight=1)
        popup.grid_rowconfigure(5, weight=10)
        # popup.grid_rowconfigure(1, weight=1)
        popup.grid_columnconfigure(0, weight=100)
        popup.grid_columnconfigure(1, weight=10)
        popup.grid_columnconfigure(2, weight=1)
        popup.grid_columnconfigure(3, weight=10)
        popup.grid_columnconfigure(4, weight=50)
        popup.grid_columnconfigure(5, weight=50)
        popup.grid_columnconfigure(6, weight=120)

        # path_name = os.path.split(os.path.abspath(self.image_path.get()))

        name = tkinter.Label(popup, text="Name:", anchor=tkinter.E)
        name.grid(row=1, column=1, sticky='e')
        # name_box = tkinter.Text(popup, width=45, height=2, padx=5)
        name_box = tkinter.Label(
            popup, textvariable=self.image_name, bg='white', padx=5, width=45, wraplength=320, anchor='w')
        # name_box.insert(tkinter.END, path_name[1])
        # name_box.config(state='disabled')
        name_box.grid(row=1, column=3, sticky='w')

        path = tkinter.Label(popup, text="Path:", anchor=tkinter.E)
        path.grid(row=3, column=1, sticky='e')
        # path_box = tkinter.Text(popup, width=45, height=2, padx=5)
        path_box = tkinter.Label(
            popup, textvariable=self.image_folder, bg='white', padx=5, width=45, wraplength=320, anchor='w')
        # path_box.insert(tkinter.END, path_name[0])
        # path_box.config(state='disabled')
        path_box.grid(row=3, column=3, sticky='w')

        b1 = tkinter.Button(popup, text="Open Folder",
                            command=self.open_folder)
        b1.grid(row=3, column=4)

        size = tkinter.Label(popup, text="Size:", anchor=tkinter.E)
        size.grid(row=4, column=1, sticky='e')
        # size_string = "{} x {} px".format(self.image_width, self.image_height)
        # size_box = tkinter.Text(popup, width=30, height=1, padx=5)
        size_box = tkinter.Label(
            popup, textvariable=self.image_size, bg='white', padx=5, width=20)
        # size_box.insert(tkinter.END, size_string)
        # size_box.config(state='disabled')
        size_box.grid(row=4, column=3, sticky='w')

    def open_folder(self):
        # subprocess.Popen(
        #     r'explorer /select,"{}"'.format(self.image_path.get()), shell=True)
        folder_path = os.path.split(os.path.abspath(self.image_path.get()))
        os.startfile(folder_path[0])
        # print(folder_path[0])

    def undo(self):
        pass

    def redo(self):
        pass

    def skip_image(self):
        pass

    def prev_image(self):
        pass

    def search_google(self):
        filePath = "{}".format(self.filenames_list[self.image_index])
        print(filePath)
        searchUrl = 'http://www.google.com/searchbyimage/upload'
        multipart = {'encoded_image': (filePath, open(
            filePath, 'rb')), 'image_content': ''}
        response = requests.post(
            searchUrl, files=multipart, allow_redirects=False)
        # print("response type:", type(response))
        # print(response.headers)
        fetchUrl = response.headers['Location']
        # print(fetchUrl)
        webbrowser.open(fetchUrl)

    def resize_image(self, x=200, y=200):
        # print("\t--inside resize_image")
        # print("\t--X Y:", x, y, "New Img Ratio:", x/y)
        # use earlier pil_image to resize then reconvert and display
        self.tk_image = self.pil_image.resize((x, y), PIL.Image.ANTIALIAS)
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

    # disable randomizer until image is loaded
    def randomizer(self):
        if self.random_on.get() == 1:
            # if random is ON then make a copy of the original order
            # so that it can be reverted when turned off
            self.filenames_list_backup = self.filenames_list.copy()
            random.shuffle(self.filenames_list)
        else:
            # restore original order
            self.filenames_list = self.filenames_list_backup.copy()

    def pause(self):
        pass

    def next_interval(self):
        pass

    def prev_interval(self):
        pass

    @ staticmethod
    def min_window():
        mainWindow.wm_state('icon')

    @ staticmethod
    def restore_window():
        mainWindow.wm_state('normal')

    def fit_screen_width(self):
        self.win_location()  # poll location coords
        self.win_x_offset = 1922
        # -8 pixels to fit perfectly on screen
        self.win_width = self.screen_width-8
        mainWindow.geometry("{}x{}+{}+{}".format(self.win_width,
                                                 mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))
        # if self.image_exists:
        #     self.refresh_image()

    def fit_screen_height(self):
        self.win_location()
        self.win_y_offset = 0
        # -51 pixels to fit bottom perfectly on screen
        self.win_height = self.screen_height-51
        print("Win height:", self.win_height)
        print("Screen height:", self.screen_height)
        mainWindow.geometry("{}x{}+{}+{}".format(mainWindow.winfo_width(),
                                                 self.win_height, self.win_x_offset, self.win_y_offset))
        # if self.image_exists:
        #     self.refresh_image()

    @ staticmethod
    def max_window():
        mainWindow.wm_state('zoomed')

    def lock_aspect(self):
        # if there's no image loaded
        # if not [item for item in self.canvas.find_all()]:
        if not self.image_exists:
            if self.aspect_locked.get() == 1:
                mainWindow.resizable(False, False)
                self.window_menu.entryconfig(1, state='disabled')
                self.window_menu.entryconfig(2, state='disabled')
                self.window_menu.entryconfig(3, state='disabled')
                self.window_menu.entryconfig(4, state='disabled')
                self.window_menu.entryconfig(8, state='disabled')
                self.window_menu.entryconfig(9, state='disabled')
                self.window_menu.entryconfig(10, state='disabled')
            else:
                mainWindow.resizable(True, True)
                self.window_menu.entryconfig(1, state='normal')
                self.window_menu.entryconfig(2, state='normal')
                self.window_menu.entryconfig(3, state='normal')
                self.window_menu.entryconfig(4, state='normal')
                self.window_menu.entryconfig(8, state='disabled')
                self.window_menu.entryconfig(9, state='disabled')
                self.window_menu.entryconfig(10, state='disabled')
        else:
            if self.aspect_locked.get() == 1:
                mainWindow.resizable(False, False)
                self.window_menu.entryconfig(1, state='disabled')
                self.window_menu.entryconfig(2, state='disabled')
                self.window_menu.entryconfig(3, state='disabled')
                self.window_menu.entryconfig(4, state='disabled')
                self.window_menu.entryconfig(8, state='disabled')
                self.window_menu.entryconfig(9, state='disabled')
                self.window_menu.entryconfig(10, state='disabled')
            else:
                mainWindow.resizable(True, True)
                self.window_menu.entryconfig(1, state='normal')
                self.window_menu.entryconfig(2, state='normal')
                self.window_menu.entryconfig(3, state='normal')
                self.window_menu.entryconfig(4, state='normal')
                self.window_menu.entryconfig(8, state='normal')
                self.window_menu.entryconfig(9, state='normal')
                self.window_menu.entryconfig(10, state='normal')

    def win_fit_width(self):
        self.win_location()
        if (self.image_width < self.screen_width):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))
        else:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.screen_width, mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))

    def win_fit_height(self):
        self.win_location()
        if self.image_height < self.screen_height:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(mainWindow.winfo_width(), self.image_height + self.SBW, self.win_x_offset, self.win_y_offset))
        else:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(mainWindow.winfo_width(), self.screen_height, self.win_x_offset, self.win_y_offset))
        # self.refresh_image()

    # def refresh_geometry(self):
    #     self.win_location()
    #     mainWindow.geometry("{}x{}+{}+{}".format(mainWindow.winfo_width(),
    #                                              mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))

    def win_fit_size(self):
        self.win_location()

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

    def show_sidebar(self):
        pass

    def hide_sidebar(self):
        pass

    def b1_release(self, event):
        self.b1_released = True
        self.prev_px = None
        self.prev_py = None
        # print("\t\t\t\t\t\tB1 released - prev_px =", self.prev_px)

    def drag_image(self, event=None):
        # self.refresh_geometry()

        # TODO: If image is < window size on any side,
        # the position jumps to side/top when starting to drag.
        # When the window is resized even slightly, the image centers itself where it's supposed to be,
        # also the vert scrollbar activates tho it doesn't have to.

        if self.image_exists and not (
            (self.image_width <= self.canvas.winfo_width()
             and self.image_height <= self.canvas.winfo_height())
        ):
            # Canvas's built in way of dragging:
            # self.canvas.scan_dragto(event.x, event.y, gain=1)

            # My way that I designed before realizing there was an easier way:

            # image was just loaded and at initial scroll pos
            if self.initial_scroll_pos:
                # left side of scrollbar
                self.new_posx = self.horz_scrollbar.get()[0]
                self.new_posy = self.vert_scrollbar.get()[0]
                print("Scroll initial pos X:", self.new_posx)
                print("Scroll initial pos Y:", self.new_posy)
                self.now_px = event.x
                self.now_py = event.y
                self.initial_scroll_posx = False
                self.initial_scroll_posy = False

            # if mouse button was released previously
            if self.b1_released and (self.prev_px == None) and (self.prev_py == None):
                self.prev_px = event.x
                self.prev_py = event.y
                self.b1_released = False
                # print("-" * 50, "First time in loop")

            elif self.b1_released == False and (self.prev_px is not None) and (self.prev_py is not None):
                self.now_px = event.x
                self.now_py = event.y
                self.diffx = self.now_px - self.prev_px
                self.diffy = self.now_py - self.prev_py
                # print("prev px:", self.prev_px, "Diff: ", self.diffx)
                self.prev_px = self.now_px
                self.prev_py = self.now_py

                # gives ratio of one pixel of image
                # used to scroll 1:mouse speed
                self.img_pxx_percent = (
                    1 / self.image_width) * abs(self.diffx)
                self.img_pxy_percent = (
                    1 / self.image_height) * abs(self.diffy)
                # print("img px % {:.5f}".format(self.img_pxx_percent))

                # move right or left and reach limits
                if self.diffx > 0 and self.horz_scrollbar.get()[1] <= 1:
                    self.new_posx = self.new_posx - self.img_pxx_percent
                    # print("Right ->")
                elif self.diffx < 0 and self.horz_scrollbar.get()[0] >= 0:
                    self.new_posx = self.new_posx + self.img_pxx_percent
                    # print("<- Left")

                if self.diffy > 0 and self.vert_scrollbar.get()[1] <= 1:
                    self.new_posy = self.new_posy - self.img_pxy_percent
                elif self.diffy < 0 and self.vert_scrollbar.get()[0] >= 0:
                    self.new_posy = self.new_posy + self.img_pxy_percent

                print("new pos X:", self.new_posx)
                print("new pos Y:", self.new_posy)
                print()

                if self.new_posx > 1:
                    self.new_posx = 1
                if self.new_posx < 0:
                    self.new_posx = 0

                if self.new_posy > 1:
                    self.new_posy = 1
                if self.new_posy < 0:
                    self.new_posy = 0

                if self.image_width > self.canvas.winfo_width() and self.image_height > self.canvas.winfo_height():
                    event.widget.xview_moveto(self.new_posx)
                    event.widget.yview_moveto(self.new_posy)
                elif self.image_width > self.canvas.winfo_width() and self.image_height < self.canvas.winfo_height():
                    event.widget.xview_moveto(self.new_posx)
                elif self.image_width < self.canvas.winfo_width() and self.image_height > self.canvas.winfo_height():
                    event.widget.yview_moveto(self.new_posy)
            # self.refresh_image()
            # print("now_pos: {:.5f}".format(self.now_pos))

    def refresh_image(self, event=None):
        self.canvas.pack_forget()

        if self.image_width > self.canvas.winfo_width() and self.image_height > self.canvas.winfo_height():
            self.vert_scrollbar.pack(side='right', fill='y')
            self.horz_scrollbar.pack(side='bottom', fill='x')
        elif self.image_width > self.canvas.winfo_width():
            self.horz_scrollbar.pack(side='bottom', fill='x')
            self.vert_scrollbar.pack_forget()
        elif self.image_height > self.canvas.winfo_height():
            self.vert_scrollbar.pack(side='right', fill='y')
            self.horz_scrollbar.pack_forget()
        else:
            self.vert_scrollbar.pack_forget()
            self.horz_scrollbar.pack_forget()

        self.canvas.pack(fill=tkinter.BOTH, expand=True)

        # delete any previous items on canvas before refreshing
        self.canvas.delete('all')

        # creates a dummy rectangle roughly the same size as the canvas that
        # resets the ANCHOR value for centering the image.
        # Without it the image may not re-center properly when the window is resized
        if event is not None:
            w, h = event.width, event.height
            # offsets - 3 seems to center image on sides
            # 20 is good for medium images, 0 is perfect for small images...
            xy = 3, 0, w, h
            self.dummy_rect = self.canvas.create_rectangle(xy)
            self.canvas.itemconfig(self.dummy_rect, width=0)

        # returns item ID
        image_id = self.canvas.create_image(int(self.canvas.winfo_width()/2), int(
            self.canvas.winfo_height()/2), anchor='center', image=self.tk_image, tag="image")
        self.image_dimensions(self.tk_image, 'tk_image')

        self.canvas.config(
            yscrollcommand=self.vert_scrollbar.set,
            xscrollcommand=self.horz_scrollbar.set,
            scrollregion=self.canvas.bbox('all'))

        # store a reference to the image so it won't be deleted
        # by the garbage collector
        if self.image_exists:
            self.tk_image.image = self.tk_image

        self.initial_scroll_pos = True

        # print("Win width:", mainWindow.winfo_width(),
        #       "Img width:", self.image_width)
        # print("Win height:", mainWindow.winfo_height(),
        #       "Img height:", self.image_height)
        # print("x:", self.x_offset, "y:", self.y_offset)
        # print()

        # Check MEMORY Usage
        # pid = os.getpid()
        # print(pid)
        # ps = psutil.Process(pid)
        # memory_use = ps.memory_info()
        # print(memory_use)
        # print()

    def image_dimensions(self, image, imgtype):
        if self.image_exists:
            if imgtype == 'tk_image':
                self.image_width = image.width()
                self.image_height = image.height()
            elif imgtype == 'pil_image':
                self.image_width = image.width
                self.image_height = image.height

    def help(self):
        pass

    def about(self):
        pass

    def win_location(self):
        self.screen_width, self.screen_height = mainWindow.winfo_screenwidth(
        ), mainWindow.winfo_screenheight()
        self.win_x_offset, self.win_y_offset = mainWindow.winfo_rootx() - \
            8, mainWindow.winfo_rooty()-51


if __name__ == "__main__":
    # initial declarations
    mainWindow = tkinter.Tk()
    # create instance of MainWindow class, call it 'app'
    app = MainWindow(mainWindow)
    # load program window
    mainWindow.mainloop()
