import tkinter
import tkinter.ttk
import tkinter.font
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
import threading
import time
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
    win_x_offset = 3000
    win_y_offset = 100
    image_width = 0
    image_height = 0

    SBW = 21  # scrollbar width

    image_scrollbar = None

    def __init__(self, mainWindow):
        # self.exit_threads = threading.Event()

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
        self.temp_new_filenames_list = []
        self.new_folders_list = []
        self.total_images = None
        self.image_exists = False
        self.new_session_image_counter = 0
        self.next_image = None

        self.load_image_var = tkinter.IntVar()
        self.load_dir_var = tkinter.IntVar()
        self.random_on = tkinter.IntVar()
        self.zoom_auto_var = tkinter.IntVar()
        self.zoom_width_var = tkinter.IntVar()
        self.zoom_height_var = tkinter.IntVar()
        self.incl_subdirs_var = tkinter.IntVar()
        self.image_path = tkinter.StringVar()
        self.image_name = tkinter.StringVar()
        self.image_folder = tkinter.StringVar()
        self.image_size = tkinter.StringVar()
        self.new_session_info_msg = tkinter.StringVar()
        self.interval_warning_msg = tkinter.StringVar()

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

        self.temp_list = []
        self.tabs = 0
        self.time_interval_list = []
        self.orig_interval_list = []
        self.current_interval_index = 0
        self.current_interval = 0
        self.timer_paused = True
        self.timer_activated = False
        self.current_interval_copy = 0
        self.time_start = 0.0
        self.time_diff = 0.0
        self.timer_window_exists = False
        self.new_session_started = False
        self.timer_bar_hidden = False
        self.first_session_run = False
        self.exited_load_imgdir = False

        self.timer_x0 = 0
        self.timer_x1 = 0
        self.timer_y0 = 0
        self.timer_y1 = 0
        self.rect_x1 = 0
        self.TIMER_BAR_WIDTH = 250
        self.TIMER_WIN_X = 250
        self.TIMER_WIN_Y = 12
        self.progress_value = 0

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
        # mainWindow.bind('<Key>', self.load)
        mainWindow.bind('<Key>', self.which_key)
        mainWindow.bind('<MouseWheel>', self.zoom)

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
                11: None,
                12: "Show information about the image"
            },
            2: {
                0: "Go to the next image",
                1: "Go back to the previous image",
                2: None,
                3: "Search this image on Google",
                4: None,
                5: "Add a vignette border to the image",
                6: "Brighten the image",
                7: "Darken the image",
                8: "Apply Levels - Brighten the image",
                9: "Apply Levels - Darken the image",
                10: "Apply a Median filter to the image",
                11: None,
                12: "Randomize the order of the images"
            },
            3: {
                0: "Pause or Continue the timer",
                1: "Skip to the next timer interval",
                2: "Go back to the previous timer interval",
                3: None,
                4: "Hide or Show the timer progress bar"
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
            label="Timed Session", menu=self.timed_menu, state='disabled')
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
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Image Info", command=self.image_info)

        self.image_menu.add_command(
            label="Next Image", command=self.next_image_func)
        self.image_menu.add_command(
            label="Previous Image", command=self.prev_image_func)
        self.image_menu.add_separator()
        self.image_menu.add_command(
            label="Search Image on Google", command=self.search_google)
        self.image_menu.add_separator()
        # self.image_menu.add_command(
        #     label="Resize Image", command=self.resize_image)
        self.image_menu.add_command(
            label="Vignette Border", command=self.vignette)
        self.image_menu.add_command(label="Brighten", command=self.brighten)
        self.image_menu.add_command(label="Darken", command=self.darken)
        self.image_menu.add_command(
            label="Levels - Brighten", command=self.levels_brighten)
        self.image_menu.add_command(
            label="Levels - Darken", command=self.levels_darken)
        self.image_menu.add_command(label="Median", command=self.median)
        self.image_menu.add_separator()
        self.image_menu.add_checkbutton(
            label="Random Order of Images", variable=self.random_on, command=self.randomizer)

        self.timed_menu.add_command(
            label="Pause/Continue", command=self.pause)
        self.timed_menu.add_command(
            label="Next Timed Interval", command=self.next_interval)
        self.timed_menu.add_command(
            label="Previous Timed Interval", command=self.prev_interval)
        self.timed_menu.add_separator()
        self.timed_menu.add_command(
            label="Hide/Show Timer Bar", command=self.hide_show_timer_bar)

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

        self.help_menu.add_command(label="Help", command=self.help)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="About", command=self.about)

        mainWindow.config(menu=self.menubar)

        # Status bar at bottom of screen
        # Using anchor= instead of justify= because justify on ly works for multiline
        self.status_bar = tkinter.Label(
            relief=tkinter.SUNKEN, anchor='w', textvariable=self.status_text)
        self.status_bar.pack(side='left', fill='x', expand=True)

        # Info bar which sits beside status bar
        self.info_bar = tkinter.Label(
            relief='sunken',
            anchor='e',
            textvariable=self.info_text,
            width=18)
        self.info_bar.pack(side='right', fill='x')

        self.zoom_bar = tkinter.Label(
            relief='sunken',
            anchor='e',
            textvariable=self.zoom_text,
            width=10)
        self.zoom_bar.pack(side='right', fill='x')

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

                self.reset_from_session_mode()

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

            self.reset_from_session_mode()

            self.load_dir_var.set(0)

        # if a key has been pressed, cycle to next/prev image
        # if event is not None:
        #     if event.keysym == 'Right' and self.image_index < len(self.filenames_list) - 1:
        #         self.image_index += 1
        #     elif event.keysym == 'Left' and self.image_index > 0:
        #         self.image_index -= 1
        if self.next_image is not None:
            if self.next_image == 'Right' and self.image_index < len(self.filenames_list) - 1:
                self.image_index += 1
                self.next_image = None
            elif self.next_image == 'Left' and self.image_index > 0:
                self.image_index -= 1
                self.next_image = None

        # if AUTO ZOOM is OFF
        if self.image_exists and self.zoom_auto_var.get() == 0:
            try:
                # print("** if zoom is off, finish loading image in load()\n")
                # load the first image into CV2 array
                # print(self.filenames_list[self.image_index])
                self.cv2_image = cv2.imread(
                    self.filenames_list[self.image_index])

                try:
                    # convert to PIL colour order
                    self.cv2_image = cv2.cvtColor(
                        self.cv2_image, cv2.COLOR_BGR2RGB)
                except:
                    # load error image
                    self.cv2_image = cv2.imread('error_img.jpg')
                    self.cv2_image = cv2.cvtColor(
                        self.cv2_image, cv2.COLOR_BGR2RGB)
                    self.status_text.set("Image could not load")
                else:
                    self.status_text.set("Image loaded successfully")

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

                try:
                    # convert to PIL colour order
                    self.cv2_image = cv2.cvtColor(
                        self.cv2_image, cv2.COLOR_BGR2RGB)
                except:
                    # load error image
                    self.cv2_image = cv2.imread('error_img.png')
                    self.cv2_image = cv2.cvtColor(
                        self.cv2_image, cv2.COLOR_BGR2RGB)
                    self.status_text.set("Image could not load")
                else:
                    self.status_text.set("Image loaded successfully")

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

    def reset_from_session_mode(self):
        self.new_session_started = False
        self.timer_Window_exists = False
        self.exited_load_imgdir = True
        if not self.timer_bar_hidden:
            self.timer_bar_hidden = True
            self.canvas.tag_raise('image', 'all')
        self.file_menu.entryconfig("Edit Session", state='disabled')
        self.file_menu.entryconfig("Save Session", state='disabled')
        self.menubar.entryconfig("Timed Session", state='disabled')

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

        self.new_session_info(0, 0)
        self.new_session_image_counter = 0
        self.new_folders_list.clear()
        self.temp_new_filenames_list.clear()
        self.time_interval_list.clear()
        self.incl_subdirs_var.set(0)

        self.win_location()
        self.new_session_win = tkinter.Toplevel()
        self.new_session_win.resizable(False, False)
        self.new_session_win.title('Start a New Session')
        self.new_session_win.geometry("{}x{}+{}+{}".format(440, 450,
                                                           self.win_x_offset+80, self.win_y_offset+80))
        # self.new_session_win.attributes('-topmost', 'true')
        # removes move/close functionality
        # self.new_session_win.overrideredirect(True)

        self.new_session_win.grid_rowconfigure(0, weight=10)
        self.new_session_win.grid_rowconfigure(1, weight=10)
        self.new_session_win.grid_rowconfigure(2, weight=1)
        self.new_session_win.grid_columnconfigure(0, weight=8)
        self.new_session_win.grid_columnconfigure(1, weight=3)

        top_left_frame = tkinter.Frame(self.new_session_win)
        top_left_frame.grid(row=0, column=0, sticky='nswe')
        top_right_frame = tkinter.Frame(self.new_session_win)
        top_right_frame.grid(row=0, column=1, sticky='nswe')
        bottom_right_frame = tkinter.Frame(self.new_session_win)
        bottom_right_frame.grid(row=1, column=1, sticky='nswe')
        bottom_left_frame = tkinter.Frame(self.new_session_win)
        bottom_left_frame.grid(row=1, column=0, sticky='nswe')

        top_left_frame.grid_rowconfigure(0, weight=1)
        top_left_frame.grid_rowconfigure(1, weight=1)
        top_left_frame.grid_rowconfigure(2, weight=1)
        top_left_frame.grid_rowconfigure(3, weight=1)
        top_left_frame.grid_columnconfigure(0, weight=2)
        top_left_frame.grid_columnconfigure(1, weight=1)
        top_left_frame.grid_columnconfigure(2, weight=1)

        dir_label = tkinter.Label(
            top_left_frame, text="Directories:", anchor='w')
        dir_label.grid(row=1, column=1, sticky='w')
        self.dir_box = tkinter.Listbox(top_left_frame,
                                       width=40, height=10, selectmode='extended')
        self.dir_box.grid(row=2, column=1, sticky='we')
        dir_box_scrolly = tkinter.Scrollbar(
            top_left_frame,
            orient='vertical',
            width=14,
            command=self.dir_box.yview)
        dir_box_scrolly.grid(row=2, column=2, sticky='nsw')
        dir_box_scrollx = tkinter.Scrollbar(
            top_left_frame,
            orient='horizontal',
            width=14,
            command=self.dir_box.xview)
        dir_box_scrollx.grid(row=3, column=1, sticky='nwe')
        self.dir_box.config(
            yscrollcommand=dir_box_scrolly.set,
            xscrollcommand=dir_box_scrollx.set)

        top_right_frame.grid_rowconfigure(0, weight=1)
        top_right_frame.grid_rowconfigure(1, weight=1)
        top_right_frame.grid_rowconfigure(2, weight=1)
        top_right_frame.grid_rowconfigure(3, weight=1)
        top_right_frame.grid_rowconfigure(4, weight=1)
        top_right_frame.grid_rowconfigure(5, weight=1)
        top_right_frame.grid_rowconfigure(6, weight=1)
        top_right_frame.grid_rowconfigure(7, weight=1)
        top_right_frame.grid_rowconfigure(8, weight=1)
        top_right_frame.grid_columnconfigure(0, weight=4)
        top_right_frame.grid_columnconfigure(1, weight=1)
        top_right_frame.grid_columnconfigure(2, weight=1)
        top_right_frame.grid_columnconfigure(3, weight=4)

        plus_font = tkinter.font.Font(family="Verdana", size=14)
        browse_button = tkinter.Button(
            top_right_frame, text="+", font=plus_font, command=self.add_dir)
        browse_button.grid(row=3, column=1)
        # grab focus after closing Browse window
        self.new_session_win.grab_set()
        add_dir_label = tkinter.Label(
            top_right_frame, text="Add\nDirectory", anchor='w', justify='left')
        add_dir_label.grid(row=3, column=2, sticky='w')
        incl_subdirs = tkinter.Checkbutton(
            top_right_frame, text="Include\nSubdirectories", justify='left', variable=self.incl_subdirs_var)
        incl_subdirs.grid(row=4, column=2, sticky='e')

        browse_separator = tkinter.ttk.Separator(
            top_right_frame, orient='horizontal')
        browse_separator.grid(row=6, column=1, sticky='we', columnspan=2)

        minus_font = tkinter.font.Font(family="Verdana", size=16)
        self.remove_dir_button = tkinter.Button(
            top_right_frame, text="–", font=minus_font, state='disabled', command=self.remove_dir)
        self.remove_dir_button.grid(row=7, column=1)
        self.remove_dir_label = tkinter.Label(
            top_right_frame, text="Remove\nDirectory", anchor='w', justify='left', state='disabled')
        self.remove_dir_label.grid(row=7, column=2, sticky='w')

        # mid_separator = tkinter.ttk.Separator(
        #     , orient='horizontal')
        # mid_separator.grid(row=7, column=2, sticky='we', columnspan=3)

        bottom_left_frame.grid_rowconfigure(0, weight=80)
        bottom_left_frame.grid_rowconfigure(1, weight=4)
        bottom_left_frame.grid_rowconfigure(2, weight=4)
        bottom_left_frame.grid_rowconfigure(3, weight=1)
        bottom_left_frame.grid_rowconfigure(4, weight=4)
        bottom_left_frame.grid_rowconfigure(5, weight=1)
        bottom_left_frame.grid_rowconfigure(6, weight=4)
        bottom_left_frame.grid_columnconfigure(0, weight=4)
        bottom_left_frame.grid_columnconfigure(1, weight=1)
        bottom_left_frame.grid_columnconfigure(2, weight=1)
        bottom_left_frame.grid_columnconfigure(3, weight=1)
        bottom_left_frame.grid_columnconfigure(4, weight=1)
        bottom_left_frame.grid_columnconfigure(5, weight=1)
        bottom_left_frame.grid_columnconfigure(6, weight=1)
        bottom_left_frame.grid_columnconfigure(7, weight=4)

        add_time_label = tkinter.Label(
            bottom_left_frame, text="Add time intervals per image:")
        add_time_label.grid(row=1, column=1, sticky='sw', columnspan=5)

        self.minutes_box = tkinter.Spinbox(
            bottom_left_frame, width=2, from_=0, to=59)
        self.minutes_box.grid(row=2, column=1, sticky='e')
        minute_label = tkinter.Label(
            bottom_left_frame, text="minutes", anchor='w')
        minute_label.grid(row=2, column=2, sticky='w')

        self.seconds_box = tkinter.Spinbox(
            bottom_left_frame, width=2, from_=0, to=59)
        self.seconds_box.grid(row=2, column=3, sticky='e')
        seconds_label = tkinter.Label(
            bottom_left_frame, text="seconds", anchor='w')
        seconds_label.grid(row=2, column=4, sticky='w')

        self.add_time_button = tkinter.Button(
            bottom_left_frame, text="Add", command=self.add_timed_interval, state='disabled')
        self.add_time_button.grid(row=2, column=5, sticky='e')

        self.interval_warning = tkinter.Label(
            bottom_left_frame,
            textvariable=self.interval_warning_msg,
            foreground='red')
        self.interval_warning.grid(row=3, column=1, columnspan=5, sticky='we')

        self.move_interval_up_btn = tkinter.Button(
            bottom_left_frame,
            text=" ↑ ",
            command=self.move_interval_up,
            state='disabled')
        self.move_interval_up_btn.grid(row=4, column=1, sticky='e')
        self.move_interval_down_btn = tkinter.Button(
            bottom_left_frame,
            text=" ↓ ",
            command=self.move_interval_down,
            state='disabled')
        self.move_interval_down_btn.grid(row=5, column=1, sticky='e')

        self.intervals_box = tkinter.Listbox(
            bottom_left_frame, width=18, height=6)
        self.intervals_box.grid(row=4, column=2, rowspan=2,
                                columnspan=3, sticky='nse')
        intervals_box_scroll = tkinter.Scrollbar(
            bottom_left_frame, command=self.intervals_box.yview)
        intervals_box_scroll.grid(row=4, column=5, rowspan=2, sticky='nsw')
        self.intervals_box.config(yscrollcommand=intervals_box_scroll.set)

        self.remove_interval_button = tkinter.Button(
            bottom_left_frame, text=" – ", state='disabled', command=self.remove_interval)
        self.remove_interval_button.grid(row=4, column=6, sticky='sw')
        self.remove_interval_label = tkinter.Label(
            bottom_left_frame, text="Remove\nInterval", anchor='w', justify='left', state='disabled')
        self.remove_interval_label.grid(row=5, column=6, sticky='nw')

        bottom_right_frame.grid_rowconfigure(0, weight=3)
        bottom_right_frame.grid_rowconfigure(1, weight=1)
        bottom_right_frame.grid_rowconfigure(2, weight=1)
        bottom_right_frame.grid_columnconfigure(0, weight=1)
        bottom_right_frame.grid_columnconfigure(1, weight=1)
        bottom_right_frame.grid_columnconfigure(2, weight=1)

        self.start_button = tkinter.Button(
            bottom_right_frame,
            text="Start",
            bd=4,
            padx=30,
            pady=20,
            state='disabled',
            command=self.start_session)
        self.start_button.grid(row=1, column=1)

        self.new_session_info_msg.set(
            "Folders without images will be filtered out")
        bottom_frame = tkinter.Label(
            self.new_session_win, textvariable=self.new_session_info_msg)
        bottom_frame.grid(row=2, column=0, sticky='we', pady=10, columnspan=2)

    def start_session(self):
        self.file_menu.entryconfig("Edit Session", state='normal')
        self.file_menu.entryconfig("Save Session", state='normal')
        self.menubar.entryconfig('Timed Session', state='normal')

        self.new_session_win.destroy()
        for item in self.new_folders_list:
            self.scan_images(item)
        self.filenames_list = self.temp_new_filenames_list.copy()
        self.temp_new_filenames_list.clear()

        self.restore_menu_items()
        self.image_exists = True
        self.image_index = 0
        self.total_images = self.new_session_image_counter
        self.load()

        # convert intervals from mins:secs to all secs
        self.interval_in_seconds()
        # set the first interval
        self.current_interval = self.time_interval_list[0]
        self.current_interval_index = 0
        self.time_diff = 0

        self.timer_activated = True
        self.new_session_started = True
        self.first_session_run = True
        self.timer_window_exists = False

        # runs in case the previous mode used was not session mode
        if self.exited_load_imgdir:
            self.exited_load_imgdir = False

            self.draw_timer_window()
            self.timer_window_exists = True
            self.timer_bar_hidden = False
            print(" first timer window created")

        self.status_text.set("Press SPACEBAR to begin/pause timer")

    def hide_show_timer_bar(self):
        if self.timer_bar_hidden:
            self.timer_bar_hidden = False
            self.canvas.tag_raise('timer_window', 'all')
            self.canvas.tag_raise('timer_bar', 'all')
        else:
            self.timer_bar_hidden = True
            self.canvas.tag_raise('image', 'all')

    def add_dir(self):
        # self.new_filenames_list.clear()

        if self.incl_subdirs_var.get() == 1:
            # print("Include subdirectories")
            try:
                path = tkinter.filedialog.askdirectory(
                    title="Select a directory of images to load (Includes Sub-directories)")
                list_subd_paths = [
                    folder.path for folder in os.scandir(path) if folder.is_dir()]

                all_folders_list = []
                all_folders_list.append(path)
                empty_folder_list = []

                # print("all folders:\t", all_folders_list)

                # don't add list items if they're already in the list
                for item in all_folders_list:
                    # print(item)
                    if item in self.new_folders_list:
                        all_folders_list.remove(item)
                    else:
                        if not self.contains_images(item):
                            empty_folder_list.append(item)  #
                            # all_folders_list.remove(item)

                if all_folders_list:
                    # call RECURSIVE function
                    self.temp_list = self.recurs_folder_scan(all_folders_list)

                    for folder in empty_folder_list:  #
                        self.temp_list.remove(folder)    #

                    # Populate self.self.dir_box with folders
                    self.populate_dir_box(self.temp_list)

            except PermissionError:
                raise
                print("- Permission Error")
            except FileNotFoundError:
                print("- File not found")
            else:
                self.remove_dir_button.config(state='normal')
                self.remove_dir_label.config(state='normal')
                self.add_time_button.config(state='normal')

        else:
            try:
                path = tkinter.filedialog.askdirectory(
                    title="Select a directory of images to load")
                if path not in self.new_folders_list and not path == '':
                    self.new_folders_list.append(path)
                    self.dir_box.insert(tkinter.END, path)

                self.new_session_image_counter += self.recount_images(path)

            except FileNotFoundError:
                print("- Folder not added")
            else:
                self.remove_dir_button.config(state='normal')
                self.remove_dir_label.config(state='normal')
                self.add_time_button.config(state='normal')

        self.new_session_info(len(self.new_folders_list),
                              self.new_session_image_counter)

    def remove_dir(self):
        items = self.dir_box.curselection()
        # print(items)
        for item in reversed(items):
            # print(item)

            self.dir_box.delete(item)
            # print()
            # print("before removing", self.new_session_image_counter)
            self.new_session_image_counter = self.new_session_image_counter - \
                self.recount_images(self.new_folders_list[item])
            # print("after removing", self.new_session_image_counter)
            del(self.new_folders_list[item])
            self.new_session_info(len(self.new_folders_list),
                                  self.new_session_image_counter)

        if not self.new_folders_list:
            # print('LOVE :) '*10)
            self.remove_dir_button.config(state='disabled')
            self.remove_dir_label.config(state='disabled')
        # print('removed - ', self.new_filenames_list)

    # recursive function to return sub-folder structure in list form
    def recurs_folder_scan(self, pathlist):
        recurs_list = []
        for item in range(len(pathlist)):

            recurs_list.append(pathlist[item])

            # add images in folder to counter
            self.new_session_image_counter += self.recount_images(
                pathlist[item])

            sub_paths = [folder.path for folder in os.scandir(
                pathlist[item]) if folder.is_dir()]

            if len(sub_paths) > 0:
                recurs_list.append(self.recurs_folder_scan(sub_paths))

        return recurs_list

    def populate_dir_box(self, folderlist):
        for item in folderlist:
            if type(item) == str:
                # print("\t" * self.tabs, item)
                if item not in self.new_folders_list:
                    self.new_folders_list.append(item)

                    folder = " " * self.tabs + item
                    self.dir_box.insert(tkinter.END, folder)
            else:
                self.tabs += 4
                self.populate_dir_box(item)
                self.tabs -= 4

    # prints folder structure in tabbed form according to hierarchy
    def _print_path_list(self, tlist):
        for item in tlist:
            # print(type(item))
            if type(item) == str:
                print("\t" * self.tabs, item)
            else:
                self.tabs += 1
                self._print_path_list(item)
                self.tabs -= 1

    def new_session_info(self, folders=0, images=0):
        self.new_session_info_msg.set(
            "{} folders and {} images are queued".format(folders, images))

    # returns True or False if images contained in folder
    def contains_images(self, path):
        counter = 0
        for file_name in os.listdir(path):
            full_path = os.path.join(path, file_name)
            for string in self.file_types_list:
                if (file_name[-4:] in string):
                    counter += 1
                    # self.new_session_image_counter += 1
        if counter == 0:
            return False
        else:
            return True

    # returns a COUNT of the images in the folder
    def recount_images(self, path):
        counter = 0
        # print("path", path)
        for file_name in os.listdir(path):
            full_path = os.path.join(path, file_name)
            for string in self.file_types_list:
                if (file_name[-4:] in string):
                    self.new_session_image_counter += 1
                    counter += 1

        # print("recount:", counter)
        return counter

    # scan images into temp master list
    def scan_images(self, path):
        for file_name in os.listdir(path):
            full_path = os.path.join(path, file_name)
            for string in self.file_types_list:
                if (file_name[-4:] in string):
                    self.temp_new_filenames_list.append(full_path)

    def add_timed_interval(self):
        # validate entries
        minutes = self.minutes_box.get()
        seconds = self.seconds_box.get()

        try:
            int_minutes = int(minutes)
            int_seconds = int(seconds)
        except ValueError:
            print("Values must be integers")
            self.interval_warning_msg.set("Values must be integers")
            self.reset_spinboxes()
        else:

            try:
                assert 0 < len(minutes) < 3
                assert 0 < len(seconds) < 3

            except:
                print("Values must be between 0 and 59")
                self.interval_warning_msg.set(
                    "Values must be between 0 and 59")
                self.reset_spinboxes()
            else:

                self.interval_warning_msg.set("")
                if (int_minutes > 0 and int_seconds > 0) or (int_minutes > 0 and int_seconds == 0) or (int_minutes == 0 and int_seconds > 0):
                    self.time_interval_list.append((int_minutes, int_seconds))
                    interval = "  {} mins : {} secs".format(
                        int_minutes, int_seconds)
                    self.intervals_box.insert('end', interval)
                    self.move_interval_up_btn.config(state='normal')
                    self.move_interval_down_btn.config(state='normal')
                    self.remove_interval_button.config(state='normal')
                    self.remove_interval_label.config(state='normal')
                    if self.new_folders_list:
                        self.start_button.config(state='normal')

                self.reset_spinboxes()
                # print(self.time_interval_list)

    def move_interval_up(self):
        items = self.intervals_box.curselection()
        # print(items)
        for item in reversed(items):
            # print(item)
            if item == 0:
                continue
            interval = self.intervals_box.get(item)
            # del and insert in listbox
            self.intervals_box.delete(item)
            self.intervals_box.insert(item-1, interval)
            # del and insert in list
            self.time_interval_list.insert(
                item-1, self.time_interval_list[item])
            del(self.time_interval_list[item+1])

            self.intervals_box.activate(item-1)
            self.intervals_box.select_set(item-1)
        # print('move up', self.time_interval_list)

    def move_interval_down(self):
        items = self.intervals_box.curselection()
        # print(items)
        for item in reversed(items):
            # print(item)
            if item == self.intervals_box.size()-1:
                continue
            interval = self.intervals_box.get(item)
            # del and insert in listbox
            self.intervals_box.delete(item)
            self.intervals_box.insert(item+1, interval)
            # del and insert in list
            self.time_interval_list.insert(
                item, self.time_interval_list[item+1])
            del(self.time_interval_list[item+2])

            self.intervals_box.activate(item+1)
            self.intervals_box.select_set(item+1)
        # print('move down', self.time_interval_list)

    def remove_interval(self):
        items = self.intervals_box.curselection()

        for item in reversed(items):
            self.intervals_box.delete(item)
            del(self.time_interval_list[item])

        if not self.time_interval_list:
            self.move_interval_up_btn.config(state='disabled')
            self.move_interval_down_btn.config(state='disabled')
            self.remove_interval_button.config(state='disabled')
            self.remove_interval_label.config(state='disabled')
            self.start_button.config(state='disabled')

    def reset_spinboxes(self):
        self.minutes_box.delete(0, 'end')
        self.minutes_box.insert('end', 0)
        self.seconds_box.delete(0, 'end')
        self.seconds_box.insert('end', 0)

    def interval_in_seconds(self):
        # print(self.time_interval_list)
        self.orig_interval_list = self.time_interval_list.copy()
        temp_list = []
        for item in self.time_interval_list:
            total_secs = item[0] * 60 + item[1]
            temp_list.append(total_secs)

        self.time_interval_list = []
        self.time_interval_list = temp_list.copy()
        # print(self.time_interval_list)

    def interval_in_mins_secs(self):
        # secs_interval = self.orig_interval_list[self.current_interval_index]
        # print(secs_interval)

        if self.orig_interval_list[self.current_interval_index][0] == 0:
            secs_interval = self.orig_interval_list[self.current_interval_index][1]
            self.status_text.set(
                "Current interval:  {} second(s)".format(secs_interval))
        elif self.orig_interval_list[self.current_interval_index][1] == 0:
            mins_interval = self.orig_interval_list[self.current_interval_index][0]
            self.status_text.set(
                "Current interval:  {} minute(s)".format(mins_interval))
        else:
            mins_interval = self.orig_interval_list[self.current_interval_index][0]
            secs_interval = self.orig_interval_list[self.current_interval_index][1]
            self.status_text.set("Current interval:  {} : {} mins:secs".format(
                mins_interval, secs_interval))

    def which_key(self, event):
        # print("Which key: ", event.keysym)

        if self.image_exists:

            if event.keysym == 'Right':
                self.next_image = 'Right'
                self.load()
                if self.timer_window_exists:
                    self.reset_timer()
            elif event.keysym == 'Left':
                self.next_image = 'Left'
                self.load()
                if self.timer_window_exists:
                    self.reset_timer()
            elif event.keysym == 'r':
                self.load()
            elif self.new_session_started:
                if event.keysym == 'a':
                    if self.current_interval_index > 0:
                        self.current_interval_index -= 1
                        self.current_interval = self.time_interval_list[self.current_interval_index]
                        self.interval_in_mins_secs()
                        self.recalc_interval()
                elif event.keysym == 's':
                    if self.current_interval_index < len(self.time_interval_list)-1:
                        # print("len()", len(self.time_interval_list))
                        self.current_interval_index += 1
                        self.current_interval = self.time_interval_list[self.current_interval_index]
                        self.interval_in_mins_secs()
                        self.recalc_interval()
                elif event.keysym == 'h':
                    self.hide_show_timer_bar()

                # toggle pause/continue state for timer
                elif event.keysym == 'space' and not self.timer_paused:
                    self.timer_paused = True
                    self.status_text.set("Session has been PAUSED")
                    # print("Pause timer ||")
                elif event.keysym == 'space' and self.timer_paused:
                    self.timer_paused = False  # un-pause timer
                    self.status_text.set("Session is continuing")

                    self.time_start = time.time() - self.time_diff
                    # self.time_start = time.time() - self.time_start + self.time_diff
                    # backup the current value
                    self.current_interval_copy = self.current_interval
                    # calculate what's left of interval after pausing
                    # if self.time_diff > 0:
                    #     self.current_interval -= self.time_diff

                    if self.first_session_run:
                        self.update_timer_bar()
                        self.reset_timer()
                        self.first_session_run = False
                        # self.timer_bar_hidden = False
                        self.canvas.tag_raise('timer_window', 'all')
                        self.canvas.tag_raise('timer_bar', 'all')
                        print("First session run")
                    self.run_timer()

            elif event.keysym == 'v':
                self.vignette()
            elif event.keysym == 'b':
                self.brighten()
            elif event.keysym == 'd':
                self.darken()
            elif event.keysym == 'g':
                self.levels_brighten()
            elif event.keysym == 'f':
                self.levels_darken()

    def run_timer(self):

        if not self.timer_paused:

            self.time_diff = time.time() - self.time_start
            # print("\ttime diff:", self.time_diff)
            # print("\tSeconds elapsed: {:.3f}".format(self.time_diff))

            percentage_done = self.time_diff / self.current_interval  # percentage
            self.rect_x1 = self.timer_x0 + self.TIMER_BAR_WIDTH * percentage_done

            # NOTE PROGRESS BAR
            # self.progress_value += factor
            self.progress_bar['value'] = percentage_done * 100

            # print("self.rect_x1:", self.rect_x1)
            self.canvas.coords('timer_bar', self.timer_x0,
                               self.timer_y0, self.rect_x1, self.timer_y1)
            if self.time_diff > self.current_interval:
                # reset the interval
                self.current_interval = self.current_interval_copy
                self.next_image = 'Right'
                self.load()
                self.reset_timer()

                self.progress_value = 0

            n = self.TIMER_BAR_WIDTH / self.current_interval
            n = 1 / n * 1000
            # print(n)

            self.canvas.after(int(n), self.run_timer)

    def recalc_interval(self):
        factor = (self.TIMER_BAR_WIDTH + self.TIMER_BAR_WIDTH /
                  self.current_interval) / self.current_interval / 20
        self.rect_x1 = self.timer_x0-10 + self.TIMER_BAR_WIDTH * \
            (self.time_diff / self.current_interval)
        self.canvas.coords('timer_bar', self.timer_x0,
                           self.timer_y0, self.rect_x1, self.timer_y1)

    def reset_timer(self):
        if self.timer_window_exists:
            # have to minus 1 sec to get correct interval
            self.time_start = time.time() - 1
            self.time_diff = 0.0
            # print("in RESET:")
            # print("\t", self.current_interval,
            #       self.current_interval_index, self.time_interval_list)
            # reset current interval too in case timer had been paused
            self.current_interval = self.time_interval_list[self.current_interval_index]

    def next_interval(self):
        mainWindow.event_generate('<Key>', keysym='s', when='tail')
        # print("Next interval →")

    def prev_interval(self):
        mainWindow.event_generate('<Key>', keysym='a', when='tail')
        # print("Previous interval ←")

    def draw_timer_window(self):

        self.win_dimensions()

        # NOTE
        self.progress_bar = tkinter.ttk.Progressbar(
            self.canvas, orient='horizontal', length=250, mode='determinate')
        self.progress_bar.pack(side='bottom')

        x0 = (self.canvas_width / 2) - self.TIMER_WIN_X/2
        x1 = (self.canvas_width / 2) + self.TIMER_WIN_X/2
        y0 = self.win_height - 42 - self.TIMER_WIN_Y
        y1 = self.win_height - 44
        self.rect_x1 = x1
        self.timer_window = self.canvas.create_rectangle(
            x0, y0, x1, y1, fill='#dedede', tags='timer_window')
        self.timer_bar = self.canvas.create_rectangle(
            x0, y0, x0, y1, fill='#33ff00', tags='timer_bar'
        )
        self.canvas.tag_raise('timer_window', 'all')
        self.canvas.tag_raise('timer_bar', 'all')

        print(self.canvas.find_all())
        for item in self.canvas.find_all():
            print(self.canvas.gettags(item))

        # print('rect created')

        # TODO - another option is to try to create a Toplevel window,
        # which stays topmost and has no titlebar; it will become transparent
        # when hovered out, and maybe even allow custom transparency

        # button1 = tkinter.Button(self.canvas, text="Quit", anchor='w')
        # button1.configure(width=10, activebackground="#33B5E5")
        # button1_window = self.canvas.create_window(
        #     10, 10, anchor='nw', window=button1)

    def update_timer_bar(self):
        self.win_dimensions()

        self.timer_x0 = (self.canvas_width / 2) - self.TIMER_WIN_X/2
        self.timer_x1 = (self.canvas_width / 2) + self.TIMER_WIN_X/2
        self.timer_y0 = self.win_height - 42 - self.TIMER_WIN_Y
        self.timer_y1 = self.win_height - 44

        self.canvas.coords('timer_window', self.timer_x0,
                           self.timer_y0, self.timer_x1, self.timer_y1)

        # Added 2px so that the timer bar reaches the end of the timer window
        # before the image changes
        self.rect_x1 = self.timer_x0 + 2

        self.canvas.coords('timer_bar', self.timer_x0,
                           self.timer_y0, self.rect_x1, self.timer_y1)

        if self.timer_bar_hidden:
            self.canvas.tag_raise('image', 'all')
        else:
            # raise the timer window above all items
            # repeat for the timer bar
            self.canvas.tag_raise('timer_window', 'all')
            self.canvas.tag_raise('timer_bar', 'all')
            print("timer bar should be showing normally")

    def edit_session(self):
        # same as new session with current directories pre-loaded
        pass

    def save_session(self):
        # use pickle ??
        pass

    def load_session(self):
        pass

    def zoom(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self, event=None):
        # print("Find image:", self.canvas.find_withtag('image')[0])
        # try:
        # TODO bug when click Zoom In menu
        if self.image_exists:
            if (self.zoom_index < 7):
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
            # elif event.delta < 0:
            #     self.zoom_out(event)
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
        # TODO it rotates but corners are cut off
        # image_center = tuple(numpy.array(self.cv2_image.shape[1::-1]) / 2)
        # rotate_matrix = cv2.getRotationMatrix2D(image_center, -90, 1.0)
        # self.cv2_image = cv2.warpAffine(self.cv2_image, rotate_matrix,
        #                                 self.cv2_image.shape[1::-1], flags=cv2.INTER_LINEAR)
        pass

    def image_info(self):
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

    def next_image_func(self):
        self.canvas.event_generate('<Key>', keysym='Right', when='tail')

    def prev_image_func(self):
        self.canvas.event_generate('<Key>', keysym='Left', when='tail')

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

    def vignette(self):
        print("Vignette")
        zeros = numpy.copy(self.cv2_image)
        zeros[:, :, :] = 0

        a = cv2.getGaussianKernel(self.image_width, self.image_width/2)
        b = cv2.getGaussianKernel(self.image_height, self.image_height/2)
        c = b * a.T
        d = c / c.max()

        zeros[:, :, 0] = self.cv2_image[:, :, 0] * d
        zeros[:, :, 1] = self.cv2_image[:, :, 1] * d
        zeros[:, :, 2] = self.cv2_image[:, :, 2] * d
        # e = self.cv2_image * d

        self.cv2_image = zeros

        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def brighten(self, value=10):
        bright_value = numpy.array([value, value, value], dtype=numpy.float32)
        self.cv2_image = numpy.clip(self.cv2_image + bright_value,
                                    0, 255).astype(numpy.uint8)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def darken(self, value=10):
        dark_value = numpy.array([value, value, value], dtype=numpy.float32)
        self.cv2_image = numpy.clip(self.cv2_image - dark_value,
                                    0, 255).astype(numpy.uint8)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def levels_brighten(self, inblack=0, inwhite=229.5, gamma=1.0, outblack=0, outwhite=255):
        black_input = numpy.array(
            [inblack, inblack, inblack], dtype=numpy.float32)
        white_input = numpy.array(
            [inwhite, inwhite, inwhite], dtype=numpy.float32)
        gamma_input = numpy.array([gamma, gamma, gamma], dtype=numpy.float32)
        black_output = numpy.array(
            [outblack, outblack, outblack], dtype=numpy.float32)
        white_output = numpy.array(
            [outwhite, outwhite, outwhite], dtype=numpy.float32)

        self.cv2_image = numpy.clip(
            (self.cv2_image - black_input) / (white_input - black_input), 0, 255)
        self.cv2_image = (self.cv2_image ** (1/gamma)) * \
            (white_output - black_output) + black_output
        self.cv2_image = numpy.clip(self.cv2_image, 0, 255).astype(numpy.uint8)

        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()
        print("Levels - brighten")

    def levels_darken(self, inblack=25.5, inwhite=255, gamma=1.0, outblack=0, outwhite=255):
        black_input = numpy.array(
            [inblack, inblack, inblack], dtype=numpy.float32)
        white_input = numpy.array(
            [inwhite, inwhite, inwhite], dtype=numpy.float32)
        gamma_input = numpy.array([gamma, gamma, gamma], dtype=numpy.float32)
        black_output = numpy.array(
            [outblack, outblack, outblack], dtype=numpy.float32)
        white_output = numpy.array(
            [outwhite, outwhite, outwhite], dtype=numpy.float32)

        self.cv2_image = numpy.clip(
            (self.cv2_image - black_input) / (white_input - black_input), 0, 255)
        self.cv2_image = (self.cv2_image ** (1/gamma)) * \
            (white_output - black_output) + black_output
        self.cv2_image = numpy.clip(self.cv2_image, 0, 255).astype(numpy.uint8)

        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()
        print("Levels - darken")

    def median(self):
        pass

    # def upscale(self):
    #     pass

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
        self.canvas.event_generate('<Key>', keysym='space', when='tail')

    def next_interval(self):
        self.canvas.event_generate('<Key>', keysym='s', when='tail')

    def prev_interval(self):
        self.canvas.event_generate('<Key>', keysym='a', when='tail')

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

    # def show_sidebar(self):
    #     pass

    # def hide_sidebar(self):
    #     pass

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
                # print("Scroll initial pos X:", self.new_posx)
                # print("Scroll initial pos Y:", self.new_posy)
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

                # print("new pos X:", self.new_posx)
                # print("new pos Y:", self.new_posy)
                # print()

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
        # self.canvas.delete('all')
        self.canvas.delete('image', 'dummy')

        # creates a dummy rectangle roughly the same size as the canvas that
        # resets the ANCHOR value for centering the image.
        # Without it the image may not re-center properly when the window is resized
        if event is not None:
            w, h = event.width, event.height
            # offsets - 3 seems to center image on sides
            # 20 is good for medium images, 0 is perfect for small images...
            xy = 3, 0, w, h
            self.dummy_rect = self.canvas.create_rectangle(xy, tags='dummy')
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

        # runs if first mode upon starting program is session mode
        if not self.timer_window_exists and self.new_session_started and self.image_exists:
            self.draw_timer_window()
            self.timer_window_exists = True
            print(" first timer window created")
        elif self.timer_window_exists and self.image_exists:
            self.update_timer_bar()

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

    def win_dimensions(self):
        self.win_width = mainWindow.winfo_width()
        self.win_height = mainWindow.winfo_height()
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

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
    # app.exit_threads.set()
