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
import random
import requests
import webbrowser
import subprocess
import time
import pickle


class MainWindow:

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

        self.menubar = None
        self.file_menu = None
        self.view_menu = None
        self.image_menu = None
        self.window_menu = None
        self.help_menu = None

        self.menubar_sel = None
        self.submenu_sel = None

        self.image_frame = None
        self.image_label = None
        self.cv2_image = None
        self.pil_image = None
        self.tk_image = None

        self.screen_width = 0
        self.screen_height = 0
        self.win_width = 640
        self.win_height = 480
        self.win_x_offset = 3000
        self.win_y_offset = 100
        self.image_width = 0
        self.image_height = 0

        self.SBW = 21  # scrollbar width
        self.image_scrollbar = None

        self.image_index = None
        self.filenames_string = None
        self.filenames_list = []
        self.new_filenames_list = []
        self.temp_new_filenames_list = []
        self.new_folders_list = []
        self.total_images = None
        self.image_exists = False
        self.new_session_image_counter = 0
        self.temp_image_counter = 0
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

        self.new_session_win_exists = False
        self.progress_goal = 0
        self.total_progress = 0
        self.done_loading = False
        self.session_loaded = False
        self.temp_list = []
        self.tabs = 0
        self.time_interval_list = []
        self.temp_time_interval_list = []
        self.orig_interval_list = []
        self.current_interval_index = 0
        self.current_interval = 0
        self.timer_paused = True
        self.timer_activated = False
        self.current_interval_copy = 0
        self.time_start = 0.0
        self.time_diff = 0.0
        self.timer_bar_frame_exists = False
        self.new_session_started = False
        self.timer_bar_hidden = True
        self.first_session_run = False
        self.exited_load_imgdir = False
        self.start_clicked = False
        self.edit_start_button_clicked = False

        self.grid_on = False

        self.session_state_list = []
        self.edit_session_path_list = []
        self.temp_edit_session_path_list = []
        self.temp_edit_path_remove_list = []

        self.edit_session_clicked = False

        self.TIMER_BAR_WIDTH = 250
        self.TIMER_BAR_HEIGHT = 24

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

        self.horz_scrollbar = tkinter.Scrollbar(
            self.image_frame, orient=tkinter.HORIZONTAL)
        self.horz_scrollbar.config(command=self.canvas.xview)

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
                10: None,
                11: "Randomize the order of the images"
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

        self.view_menu.add_command(
            label="Zoom In", command=self.zoom_in, accelerator='Scroll ↑')
        self.view_menu.add_command(
            label="Zoom Out", command=self.zoom_out, accelerator='Scroll ↓')
        self.view_menu.add_checkbutton(
            label="Zoom to Window Width", variable=self.zoom_width_var, command=self.zoom_to_width)
        self.view_menu.add_checkbutton(
            label="Zoom to Window Height", variable=self.zoom_height_var, command=self.zoom_to_height)
        self.view_menu.add_checkbutton(
            label="Auto Zoom to Fit Window", variable=self.zoom_auto_var, command=self.zoom_auto)
        self.view_menu.add_command(
            label="Reset Zoom", command=self.zoom_reset, accelerator='R')
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
            label="Next Image", command=self.next_image_func, accelerator='→')
        self.image_menu.add_command(
            label="Previous Image", command=self.prev_image_func, accelerator='←')
        self.image_menu.add_separator()
        self.image_menu.add_command(
            label="Search Image on Google", command=self.search_google)
        self.image_menu.add_separator()
        self.image_menu.add_command(
            label="Vignette Border", command=self.vignette, accelerator='V')
        self.image_menu.add_command(
            label="Brighten", command=self.brighten, accelerator='B')
        self.image_menu.add_command(
            label="Darken", command=self.darken, accelerator='D')
        self.image_menu.add_command(
            label="Levels - Brighten", command=self.levels_brighten, accelerator='G')
        self.image_menu.add_command(
            label="Levels - Darken", command=self.levels_darken, accelerator='F')
        self.image_menu.add_separator()
        self.image_menu.add_checkbutton(
            label="Random Order of Images", variable=self.random_on, command=self.randomizer)

        self.timed_menu.add_command(
            label="Pause/Continue", command=self.pause, accelerator='Space')
        self.timed_menu.add_command(
            label="Next Timed Interval", command=self.next_interval, accelerator='S')
        self.timed_menu.add_command(
            label="Previous Timed Interval", command=self.prev_interval, accelerator='A')
        self.timed_menu.add_separator()
        self.timed_menu.add_command(
            label="Hide/Show Timer Bar", command=self.hide_show_timer_bar, accelerator='H')

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
        # Using anchor= instead of justify= because justify only works for multiline
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
        """ Update the menubar item attribute for use in status bar function """
        self.menubar_sel = mainWindow.call(event.widget, 'index', 'active')

    def status_update(self, event=None):
        """ Updates the status bar at the bottom left of the window """
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
        """ Gets called from the File menu option Load Image"""
        self.load_image_var.set(1)
        self.load()

    def load_dir(self):
        """ Gets called from the File menu option Load Directory"""
        self.load_dir_var.set(1)
        self.load()

    def load(self, event=None):
        """
        Used every time that an image is going to load on screen.
        It differentiates between the different modes available.
        """
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

                for file_name in os.listdir(self.dir_path):
                    full_path = os.path.join(self.dir_path, file_name)

                    # for every extension type in the reference list
                    for string in self.file_types_list:
                        # if the extension exists in the element
                        if file_name[-4:] in string:
                            # then add it to the list
                            self.new_filenames_list.append(full_path)
                    # NOTE: list comprehension version; for loop is more readable in this case
                    # [self.filenames_list.append(full_path) for string in self.file_types_list if (
                    #     file_name[-4:] in string)]

                self.total_images = len(self.new_filenames_list)
                assert self.total_images >= 1

                # this index is always 0 here, it will get ++ or -- as images are iterated later
                self.image_index = 0

            except FileNotFoundError:
                self.status_text.set(" Action canceled - No directory loaded")
            except IndexError:
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
                print("image index:", self.image_index)

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

                w1 = mainWindow.winfo_width()
                h1 = mainWindow.winfo_height()
                w2 = self.image_width
                h2 = self.image_height

                min_of_window = min(w1, h1)
                max_of_window = max(w1, h1)

                win_ratio = w1 / h1
                image_ratio = w2 / h2

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

                # if win is vertical and image is horizontal
                elif win_ratio <= 1 <= image_ratio:
                    # max of image ==> min of window
                    self.resize_image(min_of_window-10, int(
                        min_of_window / image_ratio)-int(10/image_ratio))
                    print("4-")

                # if win is horizontal and image is verical
                elif win_ratio >= 1 >= image_ratio:
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

    def reset_from_session_mode(self):
        """
        When switching from a session to regular image or directory mode,
        this function resets the necessary attributes and disables session
        menus.
        """
        self.new_session_started = False
        self.exited_load_imgdir = True
        self.timer_paused = True
        if not self.timer_bar_hidden:
            self.timer_bar_hidden = True
            self.timer_bar_frame.pack_forget()

        self.file_menu.entryconfig("Edit Session", state='disabled')
        self.file_menu.entryconfig("Save Session", state='disabled')
        self.menubar.entryconfig("Timed Session", state='disabled')

    def set_path(self):
        """
        Splits the full image path into a parent folder path and
        an image name with extension.
        """
        self.image_path.set(self.filenames_list[self.image_index])
        path = os.path.split(os.path.abspath(
            self.filenames_list[self.image_index]))
        self.image_name.set(path[1])
        self.image_folder.set(path[0])
        self.image_size.set("{} x {} px".format(
            self.image_width, self.image_height))

    def restore_menu_items(self):
        """ Restores menu items, used by load() """
        self.menubar.entryconfig("View", state='normal')
        self.menubar.entryconfig("Image", state='normal')
        self.lock_aspect()
        self.window_menu.entryconfig(8, state='normal')
        self.window_menu.entryconfig(9, state='normal')
        self.window_menu.entryconfig(10, state='normal')
        self.window_menu.entryconfig(12, state='normal')
        self.window_menu.entryconfig(13, state='normal')

    def new_session(self):
        """
        Creates the New Session window which also doubles as an
        Edit Session window by reconfiguring the title and a button
        through edit_session().
        """
        self.new_session_win_exists = True

        if not self.edit_session_clicked:
            self.new_session_info(0, 0)  # exclusive to session window
            self.incl_subdirs_var.set(0)  # exclusive to session window

            self.temp_image_counter = 0  # causes empty image counter
            self.temp_new_filenames_list.clear()  # causes empty dir_box ?
            self.temp_time_interval_list.clear()  # causes empty interval box

        self.new_folders_list.clear()

        self.win_location()
        self.new_session_win = tkinter.Toplevel()
        self.new_session_win.resizable(False, False)
        self.new_session_win.title('Start a New Session')
        self.new_session_win.geometry("{}x{}+{}+{}".format(440, 450,
                                                           self.win_x_offset+80, self.win_y_offset+80))

        self.new_session_win.protocol("WM_DELETE_WINDOW", self.canceled)

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

        self.edit_start_button = tkinter.Button(
            bottom_right_frame,
            text="Edit Start",
            bd=4,
            padx=30,
            pady=20,
            state='normal',
            command=self.edit_start)
        self.edit_start_button.grid(row=1, column=1)
        self.edit_start_button.grid_forget()

        self.new_session_info_msg.set(
            "Folders without images will be filtered out")
        self.bottom_frame = tkinter.Label(
            self.new_session_win, textvariable=self.new_session_info_msg)
        self.bottom_frame.grid(
            row=2, column=0, sticky='we', pady=10, columnspan=2)

        self.start_clicked = False

    def canceled(self):
        """
        Temporary lists are cleared so they won't get added later after
        the New Session or the Edit Session windows are reopened;
        gets activated by clickling the X button on those windows
        """
        # clears the temporary folders that were added
        self.temp_edit_session_path_list.clear()
        # clears temp folders that were removed
        self.temp_edit_path_remove_list.clear()

        self.temp_image_counter = 0
        self.new_session_win.destroy()

    def edit_session(self):
        """
        same as new session with current directories pre-loaded
        makes sure Edit Start version of button appears inside new_session()
        """
        self.edit_session_clicked = True
        self.new_session()

        # hide start button and show edit start button
        self.start_button.grid_forget()
        self.edit_start_button.grid(row=1, column=1)

        self.new_session_win.title('Edit current Session')
        self.remove_dir_button.config(state='normal')
        self.remove_dir_label.config(state='normal')
        self.add_time_button.config(state='normal')
        self.move_interval_up_btn.config(state='normal')
        self.move_interval_down_btn.config(state='normal')
        self.remove_interval_button.config(state='normal')
        self.remove_interval_label.config(state='normal')
        self.start_button.config(state='normal')

        self.populate_dir_box(self.edit_session_path_list)

        for item in self.time_interval_list:
            interval = "  {} mins : {} secs".format(item[0], item[1])
            self.intervals_box.insert('end', interval)

        # update which info message
        self.new_session_info(len(self.new_folders_list),
                              self.new_session_image_counter)

        self.temp_image_counter = self.new_session_image_counter

        self.edit_session_clicked = False
        print()

    def start_session(self):
        """ Only runs when Start button is clicked or a session is loaded """

        self.file_menu.entryconfig("Edit Session", state='normal')
        self.file_menu.entryconfig("Save Session", state='normal')
        self.menubar.entryconfig('Timed Session', state='normal')

        if self.new_session_win_exists:
            self.new_session_win.destroy()

        for item in self.new_folders_list:
            self.scan_images(item)
        self.filenames_list = self.temp_new_filenames_list.copy()
        self.temp_new_filenames_list.clear()

        if not self.session_loaded:
            self.start_clicked = True

            self.image_index = 0

            # EDIT button clicked
            if self.edit_start_button_clicked:

                self.edited_folders()
                self.time_interval_list = self.temp_time_interval_list.copy()

            else:
                self.current_interval_index = 0
                self.time_interval_list = self.temp_time_interval_list.copy()

                # copy folders into edit to start the new session
                self.edit_session_path_list = self.temp_edit_session_path_list.copy()

            self.temp_edit_session_path_list.clear()
            self.new_session_image_counter = self.temp_image_counter

        # convert intervals from mins:secs to all secs
        self.interval_in_seconds()

        self.restore_menu_items()
        self.total_images = self.new_session_image_counter
        self.image_exists = True
        self.load()

        # set the first interval
        self.current_interval = self.time_secs_interval_list[self.current_interval_index]
        self.time_diff = 0

        self.timer_activated = True
        self.new_session_started = True
        self.first_session_run = True
        self.timer_bar_hidden = False

        # runs in case the previous mode used was not session mode
        if self.exited_load_imgdir:
            self.exited_load_imgdir = False
            self.timer_bar_hidden = False

        self.status_text.set("Press SPACEBAR to begin/pause timer")

        # create bar if not already created
        if not self.timer_bar_frame_exists:
            self.timer_bar_frame_exists = True

            self.timer_bar_frame = tkinter.Frame(
                self.canvas, height=self.TIMER_BAR_HEIGHT, width=250)
            self.timer_bar_frame.pack(side='bottom')
            self.timer_canvas = tkinter.Canvas(
                self.timer_bar_frame, width=250, height=self.TIMER_BAR_HEIGHT, bg='white')
            self.timer_canvas.pack(fill='both')
            self.timer_bar = self.timer_canvas.create_rectangle(
                0, 0, 0, self.TIMER_BAR_HEIGHT, fill='#33ff00', tags='timer_bar')

        self.timer_bar_frame.pack(side='bottom')
        # reset bar progress
        self.timer_canvas.coords('timer_bar', 0, 0, 0, 12)

    def edit_start(self):
        """ Runs when the Start button is clicked in the Edit Session window """
        self.edit_start_button_clicked = True
        self.start_session()

    def edited_folders(self):
        """ Adds or removes folders from their temporary lists """
        # add each new folder from temp list to regular list
        for item in self.temp_edit_session_path_list:
            self.edit_session_path_list.append(item)

        for item in self.temp_edit_path_remove_list:
            self.recurs_removal(self.edit_session_path_list,
                                item)  # str or []

        self.temp_edit_path_remove_list.clear()
        self.edit_start_button_clicked = False

    def hide_show_timer_bar(self):
        """ Timer bar is shown or hidden; the timer still runs in the background """
        if self.timer_bar_hidden:
            self.timer_bar_frame.pack(side='bottom')
            self.timer_bar_hidden = False
        else:
            self.timer_bar_frame.pack_forget()
            self.timer_bar_hidden = True

    def add_dir(self):
        """ Used to add directories in the Session windows """
        if self.incl_subdirs_var.get() == 1:

            try:
                self.new_session_info_msg.set("... LOADING ...")

                path = tkinter.filedialog.askdirectory(
                    title="Select a directory of images to load (Includes Sub-directories)")

                self.done_loading = True

                all_folders_list = [path]
                empty_folder_list = []

                # don't add list items if they're already in the list
                for item in all_folders_list:

                    if item in self.new_folders_list:
                        all_folders_list.remove(item)
                    else:
                        if not self.contains_images(item):
                            empty_folder_list.append(item)

                if all_folders_list:

                    # call RECURSIVE function
                    self.temp_list = self.recurs_folder_scan(all_folders_list)

                    for folder in empty_folder_list:
                        self.temp_list.remove(folder)

                    # Populate self.dir_box with folders
                    self.populate_dir_box(self.temp_list)

                    for item in self.temp_list:
                        self.temp_edit_session_path_list.append(item)

                        # remove folder from temp del list
                        if item in self.temp_edit_path_remove_list:
                            del(self.temp_edit_path_remove_list[self.temp_edit_path_remove_list.index(
                                item)])

            except PermissionError:
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

                    # remove folder from temp del list
                    if path in self.temp_edit_path_remove_list:
                        del(self.temp_edit_path_remove_list[self.temp_edit_path_remove_list.index(
                            path)])

                    # backup copy for EDIT session
                    self.temp_edit_session_path_list.append(path)

                self.temp_image_counter += self.recount_images(path)

            except FileNotFoundError:
                print("- Folder not added")
            else:
                self.remove_dir_button.config(state='normal')
                self.remove_dir_label.config(state='normal')
                self.add_time_button.config(state='normal')

        self.new_session_info(len(self.new_folders_list),
                              self.temp_image_counter)

        if self.temp_time_interval_list:
            self.start_button.config(state='normal')
            self.edit_start_button.config(state='normal')

    def remove_dir(self):
        """ Removes directories from the Session windows"""

        items = self.dir_box.curselection()

        for item in reversed(items):
            self.dir_box.delete(item)
            self.temp_image_counter -= self.recount_images(
                self.new_folders_list[item])

            # del from edit list
            if len(self.temp_edit_session_path_list) > 0:
                print()
                print(self.temp_edit_session_path_list)
                print("Attempt to run recurs del of TEMP edit path list")
                self.recurs_removal(
                    self.temp_edit_session_path_list,
                    self.new_folders_list[item])  # passing actual item, str or []
            else:
                if self.new_folders_list[item] not in self.temp_edit_path_remove_list:
                    self.temp_edit_path_remove_list.append(
                        self.new_folders_list[item])
                print("Remove list appended ", self.temp_edit_path_remove_list)

            del(self.new_folders_list[item])

        self.new_session_info(len(self.new_folders_list),
                              self.temp_image_counter)

        if not self.new_folders_list:
            self.remove_dir_button.config(state='disabled')
            self.remove_dir_label.config(state='disabled')
            self.start_button.config(state='disabled')
            self.edit_start_button.config(state='disabled')

    def recurs_removal(self, list1: list, item: str) -> int:
        """ Recursively removes paths from the temporary list in Session mode """
        for elem in reversed(list1):
            if type(elem) == str:
                if elem == item:
                    del(list1[list1.index(item)])
                    print("Deleted Item !")
            else:
                print("Searching recurs...")
                # recursively search new list
                self.recurs_removal(elem, item)

        return 0

    def recurs_folder_scan(self, pathlist: list) -> list:
        """ Recursive function that returns sub-folder structure in list form """
        recurs_list = []
        for item in range(len(pathlist)):

            recurs_list.append(pathlist[item])

            # add images in folder to counter
            self.temp_image_counter += self.recount_images(
                pathlist[item])

            sub_paths = [folder.path for folder in os.scandir(
                pathlist[item]) if folder.is_dir()]

            if len(sub_paths) > 0:
                recurs_list.append(self.recurs_folder_scan(sub_paths))

        return recurs_list

    def populate_dir_box(self, folderlist: list):
        """ The directories box is populated in the Session window """
        for item in folderlist:
            if type(item) == str:

                if item not in self.new_folders_list:
                    self.new_folders_list.append(item)

                    folder = " " * self.tabs + item
                    self.dir_box.insert(tkinter.END, folder)
            else:
                self.tabs += 4
                self.populate_dir_box(item)
                self.tabs -= 4

    def _print_path_list(self, tlist: list):
        """
        Prints folder structure in tabbed form according to hierarchy.
        Used for debugging.
        """
        for item in tlist:

            if type(item) == str:
                print("\t" * self.tabs, item)
            else:
                self.tabs += 1
                self._print_path_list(item)
                self.tabs -= 1

    def new_session_info(self, folders=0, images=0):
        """ Updates the message at the bottom of the Session window """
        self.new_session_info_msg.set(
            "{} folders and {} images are queued".format(folders, images))

    def contains_images(self, path: str) -> bool:
        """ Returns True or False if images contained in folder"""
        counter = 0
        for file_name in os.listdir(path):
            full_path = os.path.join(path, file_name)
            for string in self.file_types_list:
                if file_name[-4:] in string:
                    counter += 1
        if counter == 0:
            return False
        else:
            return True

    def recount_images(self, path: str) -> int:
        """ Returns a count of the images in the folder """
        counter = 0
        for file_name in os.listdir(path):
            full_path = os.path.join(path, file_name)
            for string in self.file_types_list:
                if file_name[-4:] in string:
                    self.temp_image_counter += 1
                    counter += 1
        return counter

    def scan_images(self, path: str):
        """ Scan images into temporary master list """
        for file_name in os.listdir(path):
            full_path = os.path.join(path, file_name)
            for string in self.file_types_list:
                if file_name[-4:] in string:
                    self.temp_new_filenames_list.append(full_path)

    def add_timed_interval(self):
        """
        Adds an interval from the values in the Spinboxes and
        populates the intervals box.
        """
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
                if (int_minutes > 0 and int_seconds > 0) or \
                        (int_minutes > 0 and int_seconds == 0) or \
                        (int_minutes == 0 and int_seconds > 0):
                    self.temp_time_interval_list.append(
                        (int_minutes, int_seconds))
                    interval = "  {} mins : {} secs".format(
                        int_minutes, int_seconds)
                    self.intervals_box.insert('end', interval)
                    self.move_interval_up_btn.config(state='normal')
                    self.move_interval_down_btn.config(state='normal')
                    self.remove_interval_button.config(state='normal')
                    self.remove_interval_label.config(state='normal')
                    if self.new_folders_list:
                        self.start_button.config(state='normal')
                        self.edit_start_button.config(state='normal')

                self.reset_spinboxes()

    def move_interval_up(self):
        """ Shifts the selected interval(s) up """

        items = self.intervals_box.curselection()

        for item in reversed(items):

            if item == 0:
                continue
            interval = self.intervals_box.get(item)
            # del and insert in listbox
            self.intervals_box.delete(item)
            self.intervals_box.insert(item-1, interval)
            # del and insert in list
            self.temp_time_interval_list.insert(
                item-1, self.time_interval_list[item])
            del(self.temp_time_interval_list[item+1])

            self.intervals_box.activate(item-1)
            self.intervals_box.select_set(item-1)

    def move_interval_down(self):
        """ Shifts the selected interval(s) down """

        items = self.intervals_box.curselection()
        for item in reversed(items):
            if item == self.intervals_box.size()-1:
                continue
            interval = self.intervals_box.get(item)
            # del and insert in listbox
            self.intervals_box.delete(item)
            self.intervals_box.insert(item+1, interval)
            # del and insert in list
            self.temp_time_interval_list.insert(
                item, self.time_interval_list[item+1])
            del(self.temp_time_interval_list[item+2])

            self.intervals_box.activate(item+1)
            self.intervals_box.select_set(item+1)

    def remove_interval(self):
        """ Removes the interval from the intervals box """
        items = self.intervals_box.curselection()

        for item in reversed(items):
            self.intervals_box.delete(item)
            del(self.temp_time_interval_list[item])

        # if not self.time_interval_list:
        if not self.temp_time_interval_list:
            self.move_interval_up_btn.config(state='disabled')
            self.move_interval_down_btn.config(state='disabled')
            self.remove_interval_button.config(state='disabled')
            self.remove_interval_label.config(state='disabled')
            self.start_button.config(state='disabled')

    def reset_spinboxes(self):
        """ Sets the intervals Spinboxes back to 0 """
        self.minutes_box.delete(0, 'end')
        self.minutes_box.insert('end', 0)
        self.seconds_box.delete(0, 'end')
        self.seconds_box.insert('end', 0)

    def interval_in_seconds(self):
        """ Converts the interval tuples from Min Sec to all Secs """
        temp_list = []
        for item in self.time_interval_list:
            total_secs = item[0] * 60 + item[1]
            temp_list.append(total_secs)

        # new list in seconds
        self.time_secs_interval_list = []
        self.time_secs_interval_list = temp_list.copy()

    def interval_in_mins_secs(self):
        """ Converts from all secs to Min : Secs"""

        if self.time_interval_list[self.current_interval_index][0] == 0:
            secs_interval = self.time_interval_list[self.current_interval_index][1]
            self.status_text.set(
                "Current interval:  {} second(s)".format(secs_interval))
        elif self.time_interval_list[self.current_interval_index][1] == 0:
            mins_interval = self.time_interval_list[self.current_interval_index][0]
            self.status_text.set(
                "Current interval:  {} minute(s)".format(mins_interval))
        else:
            mins_interval = self.time_interval_list[self.current_interval_index][0]
            secs_interval = self.time_interval_list[self.current_interval_index][1]
            self.status_text.set("Current interval:  {} : {} mins:secs".format(
                mins_interval, secs_interval))

    def which_key(self, event):
        """ Handles key presses """
        # print("Which key: ", event.keysym)

        if self.image_exists:

            if event.keysym == 'Right':
                self.next_image = 'Right'
                self.load()
                if self.timer_bar_frame_exists:
                    self.reset_timer()
            elif event.keysym == 'Left':
                self.next_image = 'Left'
                self.load()
                if self.timer_bar_frame_exists:
                    self.reset_timer()
            elif event.keysym == 'r':
                self.load()
            elif self.new_session_started:
                if event.keysym == 'a':
                    if self.current_interval_index > 0:
                        self.current_interval_index -= 1

                        self.current_interval = self.time_secs_interval_list[self.current_interval_index]
                        self.interval_in_mins_secs()

                elif event.keysym == 's':
                    if self.current_interval_index < len(self.time_interval_list)-1:
                        self.current_interval_index += 1

                        self.current_interval = self.time_secs_interval_list[self.current_interval_index]
                        self.interval_in_mins_secs()

                elif event.keysym == 'h':
                    self.hide_show_timer_bar()

                # toggle pause/continue state for timer
                elif event.keysym == 'space' and not self.timer_paused:
                    self.timer_paused = True
                    self.status_text.set("Session has been PAUSED")

                elif event.keysym == 'space' and self.timer_paused:
                    self.timer_paused = False  # un-pause timer
                    self.status_text.set("Session is continuing")

                    self.time_start = time.time() - self.time_diff

                    if self.first_session_run:
                        self.reset_timer()
                        self.first_session_run = False
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
            elif event.keysym == 'l':
                self.grid_toggle()

    def run_timer(self):
        """
        Runs a timer, uses .after() to call this function again after a
        certain amount of milliseconds. The ms are dynamically sized to the
        specific interval to ensure a smooth progress bar progression
        without expending excess processing power in case the interval is
        large.
        """
        if not self.timer_paused:

            self.time_diff = time.time() - self.time_start

            percentage_done = self.time_diff / self.current_interval  # percentage

            self.timer_canvas.coords(
                'timer_bar', 0, 0, self.TIMER_BAR_WIDTH * percentage_done, self.TIMER_BAR_HEIGHT)

            if self.time_diff > self.current_interval:

                self.next_image = 'Right'
                self.load()
                self.reset_timer()

            n = self.TIMER_BAR_WIDTH / self.current_interval
            n = 1 / n * 1000

            self.canvas.after(int(n), self.run_timer)

    def reset_timer(self):
        """ Resets the timer after the interval is complete. """
        if self.timer_bar_frame_exists:
            self.time_start = time.time()
            self.time_diff = 0.0
            self.timer_canvas.coords(
                'timer_bar', 0, 0, 0, self.TIMER_BAR_HEIGHT)

            # reset current interval too in case timer had been paused
            self.current_interval = self.time_secs_interval_list[self.current_interval_index]

    def save_session(self):
        """
        Saves the necessary info to load a session at a later time.
        Uses Pickle to store the info into a .viewy file.
        """
        try:
            file = tkinter.filedialog.asksaveasfilename(
                title='Save Viewy session', defaultextension=".viewy", filetypes=[("viewy files", "*.viewy")])
        except:
            print("Save cancelled")
        else:
            # Save state
            self.session_state_list.append(
                self.new_folders_list)  # folders for Edit Session
            self.session_state_list.append(
                self.filenames_list)  # image names for loading
            self.session_state_list.append(self.temp_new_filenames_list)
            self.session_state_list.append(self.total_images)
            self.session_state_list.append(
                self.new_session_image_counter)  # current image position
            self.session_state_list.append(
                self.time_interval_list)  # list of tuples
            self.session_state_list.append(self.current_interval)  # int
            self.session_state_list.append(self.current_interval_index)  # int
            self.session_state_list.append(self.incl_subdirs_var.get())  # int
            # list of folders for Edit Session
            self.session_state_list.append(self.edit_session_path_list)
            self.session_state_list.append(self.image_index)

            for item in self.session_state_list:
                print(type(item))
            try:
                with open(file, 'wb') as pickle_file:
                    pickle.dump(self.session_state_list, pickle_file)
            except FileNotFoundError:
                print("No file to save")

            print("\t>>> Saved session!")

    def load_session(self):
        """
        Loads a saved .viewy file then uses Pickle to extract the necessary
        info to continue a saved session.
        """
        try:
            file = tkinter.filedialog.askopenfilename(
                title='Load Viewy session', defaultextension=".viewy", filetypes=[("viewy files", "*.viewy")])
        except:
            print("Load cancelled")
        else:
            try:
                with open(file, 'rb') as pickle_file:
                    self.session_state_list = pickle.load(pickle_file)

                self.new_folders_list = self.session_state_list[0].copy()
                self.filenames_list = self.session_state_list[1].copy()
                self.temp_new_filenames_list = self.session_state_list[2].copy(
                )
                self.total_images = self.session_state_list[3]
                self.new_session_image_counter = self.session_state_list[4]
                self.time_interval_list = self.session_state_list[5].copy()
                self.current_interval = self.session_state_list[6]
                self.current_interval_index = self.session_state_list[7]
                self.incl_subdirs_var.set(self.session_state_list[8])
                self.edit_session_path_list = self.session_state_list[9].copy()
                self.image_index = self.session_state_list[10]

                self.temp_time_interval_list = self.session_state_list[5].copy(
                )

                self.session_state_list.clear()

                self.session_loaded = True
                self.start_session()
                self.session_loaded = False

            except FileNotFoundError:
                print("File not found")
            else:
                print("\t>>> Load successful !")

    def zoom(self, event):
        """
        Reads the mouse scroll-wheel direction and directs to the program
        to flow to the proper function.
        """
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self):
        """ Directs a resizing of the image to simulate a zooming-in. """
        if self.image_exists:
            if self.zoom_index < 7:
                self.zoom_index += 1
                factor = self.zoom_factor[self.zoom_index]
                self.resize_image(int(self.original_image_width * factor),
                                  int(self.original_image_height * factor))
                self.zoom_value += 25
                self.zoom_text.set("Zoom: {:.0f}%".format(self.zoom_value))

    def zoom_out(self):
        """ Directs a resizing of the image to simulate a zooming-out. """
        if self.zoom_index > 0:
            self.zoom_index -= 1
            factor = self.zoom_factor[self.zoom_index]
            self.resize_image(int(self.original_image_width * factor),
                              int(self.original_image_height * factor))
            self.zoom_value -= 25
            self.zoom_text.set("Zoom: {:.0f}%".format(self.zoom_value))

    def zoom_to_width(self):
        """
        Directs load() to zoom the image to match the width of the window.
        """
        self.zoom_height_var.set(0)
        self.zoom_auto_var.set(0)
        self.load()

    def zoom_to_height(self):
        """
        Directs load() to zoom the image to the match the height of the window.
        """
        self.zoom_width_var.set(0)
        self.zoom_auto_var.set(0)
        self.load()

    def zoom_auto(self):
        """
        Directs load() to automatically zoom each image taking into account the window
        and image height and width.
        """
        self.zoom_width_var.set(0)
        self.zoom_height_var.set(0)
        self.load()

    def zoom_reset(self):
        """ Resets the image to original size. """
        self.resize_image(self.original_image_width,
                          self.original_image_height)

    def flip_vert(self):
        """ Flips the image vertically. """
        self.cv2_image = cv2.flip(self.cv2_image, 0)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def flip_horz(self):
        """ Flips the image horizontally. """
        self.cv2_image = cv2.flip(self.cv2_image, 1)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def rotate_left(self):
        """ Rotates the image 90 degrees counterclockwise. """
        self.cv2_image = cv2.rotate(
            self.cv2_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def rotate_right(self):
        """ Rotates the image 90 degrees clockwise. """
        self.cv2_image = cv2.rotate(
            self.cv2_image, cv2.ROTATE_90_CLOCKWISE)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def rotate_amount(self):
        """ Work in progress. Rotates image by custom degrees. """
        # TODO it rotates but corners are cut off
        # image_center = tuple(numpy.array(self.cv2_image.shape[1::-1]) / 2)
        # rotate_matrix = cv2.getRotationMatrix2D(image_center, -90, 1.0)
        # self.cv2_image = cv2.warpAffine(self.cv2_image, rotate_matrix,
        #                                 self.cv2_image.shape[1::-1], flags=cv2.INTER_LINEAR)
        pass

    def image_info(self):
        """
        Creates a window which shows info about the image.
        It shows the image name with extension, the image folder path,
        and the image size. The Open Folder button opens the Windows Explorer
        and selects the current image file.
        """
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
        popup.grid_columnconfigure(0, weight=100)
        popup.grid_columnconfigure(1, weight=10)
        popup.grid_columnconfigure(2, weight=1)
        popup.grid_columnconfigure(3, weight=10)
        popup.grid_columnconfigure(4, weight=50)
        popup.grid_columnconfigure(5, weight=50)
        popup.grid_columnconfigure(6, weight=120)

        name = tkinter.Label(popup, text="Name:", anchor=tkinter.E)
        name.grid(row=1, column=1, sticky='e')
        name_box = tkinter.Label(
            popup, textvariable=self.image_name, bg='white', padx=5, width=45, wraplength=320, anchor='w')
        name_box.grid(row=1, column=3, sticky='w')

        path = tkinter.Label(popup, text="Path:", anchor=tkinter.E)
        path.grid(row=3, column=1, sticky='e')
        path_box = tkinter.Label(
            popup, textvariable=self.image_folder, bg='white', padx=5, width=45, wraplength=320, anchor='w')
        path_box.grid(row=3, column=3, sticky='w')

        b1 = tkinter.Button(popup, text="Open Folder",
                            command=self.open_folder)
        b1.grid(row=3, column=4)

        size = tkinter.Label(popup, text="Size:", anchor=tkinter.E)
        size.grid(row=4, column=1, sticky='e')
        size_box = tkinter.Label(
            popup, textvariable=self.image_size, bg='white', padx=5, width=20)
        size_box.grid(row=4, column=3, sticky='w')

    def open_folder(self):
        """ Opens the current file's folder in Windows Explorer and selects the file. """
        # opens just the folder in Win 10
        # folder_path = os.path.split(os.path.abspath(self.image_path.get()))
        # os.startfile(folder_path[0])

        # alternate way of opening the folder w/o selection
        # webbrowser.open('file:///' + folder_path[0])

        # opens win explorer and selects file, works in Windows 10
        subprocess.Popen(
            'explorer /select,{}'.format(self.image_path.get().replace('/', '\\')))

    def next_image_func(self):
        """
        Generates an event that simulates the Right cursor key being pressed.
        Used for skipping to the next image.
        """
        self.canvas.event_generate('<Key>', keysym='Right', when='tail')

    def prev_image_func(self):
        """
        Generates an event that simulates the Left cursor key being pressed.
        Used for going back to the previous image.
        """
        self.canvas.event_generate('<Key>', keysym='Left', when='tail')

    def search_google(self):
        """
        Opens a browser and performs a Google image search for the
        current image.
        """
        filePath = "{}".format(self.filenames_list[self.image_index])
        print(filePath)
        searchUrl = 'http://www.google.com/searchbyimage/upload'
        multipart = {'encoded_image': (filePath, open(
            filePath, 'rb')), 'image_content': ''}
        response = requests.post(
            searchUrl, files=multipart, allow_redirects=False)
        fetchUrl = response.headers['Location']
        webbrowser.open(fetchUrl)

    def resize_image(self, x=200, y=200):
        """ Resizes the image to the passed parameters. Used in zoom, etc. """
        # use earlier pil_image to resize then reconvert and display
        self.tk_image = self.pil_image.resize((x, y), PIL.Image.ANTIALIAS)
        # convert to PhotoImage format again
        self.tk_image = PIL.ImageTk.PhotoImage(self.tk_image)
        # destroy the image before refreshing
        self.canvas.delete("image")
        self.refresh_image()

    def vignette(self):
        """ Creates a darkened aura in the image to give the center focus. """

        zeros = numpy.copy(self.cv2_image)
        zeros[:, :, :] = 0

        a = cv2.getGaussianKernel(self.image_width, self.image_width/2)
        b = cv2.getGaussianKernel(self.image_height, self.image_height/2)
        c = b * a.T
        d = c / c.max()

        zeros[:, :, 0] = self.cv2_image[:, :, 0] * d
        zeros[:, :, 1] = self.cv2_image[:, :, 1] * d
        zeros[:, :, 2] = self.cv2_image[:, :, 2] * d

        self.cv2_image = zeros

        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def brighten(self, value=10):
        """ Brightens the image overall by a small factor. """
        bright_value = numpy.array([value, value, value], dtype=numpy.float32)
        self.cv2_image = numpy.clip(self.cv2_image + bright_value,
                                    0, 255).astype(numpy.uint8)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def darken(self, value=10):
        """ Darkens the brightness of the image by a small factor. """
        dark_value = numpy.array([value, value, value], dtype=numpy.float32)
        self.cv2_image = numpy.clip(self.cv2_image - dark_value,
                                    0, 255).astype(numpy.uint8)
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.refresh_image()

    def levels_brighten(self, inblack=0, inwhite=229.5, gamma=1.0, outblack=0, outwhite=255):
        """ Brightens the colour levels of the image. """
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
        """ Darkens the colour levels of the image. """
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

    # TODO: check for self.grid_on in refresh func
    # TODO: make a popup window to edit grid size/visibility
    def grid_toggle(self):
        if self.grid_on:
            self.grid_on = False
        self.grid_on = True

        self.grid() # get rid of this once checking inside refresh func

    # TODO: make grid appear on image itself when it refreshes
    def grid(self):
        """ Creates a grid that overlays image. """

        self.win_dimensions()

        grid_div = 10
        grid_width = 2

        divx = self.win_width / grid_div
        divy = self.win_height / grid_div
        for n in range(grid_div):
            self.canvas.create_line(divx * n, 0, divx * n, self.win_height, width=grid_width)
            self.canvas.create_line(0, divy * n, self.win_width, divy * n, width=grid_width)

    def randomizer(self):
        """ Shuffles the order of the images. """
        if self.random_on.get() == 1:
            # if random is ON then make a copy of the original order
            # so that it can be reverted when turned off
            self.filenames_list_backup = self.filenames_list.copy()
            random.shuffle(self.filenames_list)
        else:
            # restore original order
            self.filenames_list = self.filenames_list_backup.copy()

    def pause(self):
        """
        Generates event that simulates pressing the Spacebar
        to pause the timer.
        """
        self.canvas.event_generate('<Key>', keysym='space', when='tail')

    def next_interval(self):
        """
        Generates event to simulate pressing the S key to switch
        to the next time interval.
        """
        self.canvas.event_generate('<Key>', keysym='s', when='tail')

    def prev_interval(self):
        """
        Generates event to simulate pressing the A key to switch
        to the previous time interval.
        """
        self.canvas.event_generate('<Key>', keysym='a', when='tail')

    @ staticmethod
    def min_window():
        """ Minimizes the window. """
        mainWindow.wm_state('icon')

    @ staticmethod
    def restore_window():
        """ Restores the window from minimized or maximized state. """
        mainWindow.wm_state('normal')

    def fit_screen_width(self):
        """ Resize the window to fit the width of the screen. """
        self.win_location()  # poll location coords
        self.win_x_offset = 1922
        # -8 pixels to fit perfectly on screen
        self.win_width = self.screen_width-8
        mainWindow.geometry("{}x{}+{}+{}".format(self.win_width,
                                                 mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))

    def fit_screen_height(self):
        """ Resizes the window to fit the height of the screen."""
        self.win_location()
        self.win_y_offset = 0
        # -51 pixels to fit bottom perfectly on screen
        self.win_height = self.screen_height-51
        print("Win height:", self.win_height)
        print("Screen height:", self.screen_height)
        mainWindow.geometry("{}x{}+{}+{}".format(mainWindow.winfo_width(),
                                                 self.win_height, self.win_x_offset, self.win_y_offset))

    @ staticmethod
    def max_window():
        """ Maximizes the window. """
        mainWindow.wm_state('zoomed')

    def lock_aspect(self):
        """ Prevent the image from being accidentally resized. """
        # if there's no image loaded
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
        """ Resizes the window to the width of the image. """
        self.win_location()
        if self.image_width < self.screen_width:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))
        else:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.screen_width, mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))

    def win_fit_height(self):
        """ Resizes the window to the height of the image. """
        self.win_location()
        if self.image_height < self.screen_height:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(mainWindow.winfo_width(), self.image_height + self.SBW, self.win_x_offset, self.win_y_offset))
        else:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(mainWindow.winfo_width(), self.screen_height, self.win_x_offset, self.win_y_offset))

    def win_fit_size(self):
        """ Resizes the window to fit the width and height of the image. """
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

    def b1_release(self, event):
        """ Used when the left mouse button is released. """
        self.b1_released = True
        self.prev_px = None
        self.prev_py = None

    def drag_image(self, event=None):
        """ Code that handles the movement of the image when click-dragging. """
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
                self.now_px = event.x
                self.now_py = event.y
                self.initial_scroll_posx = False
                self.initial_scroll_posy = False

            # if mouse button was released previously
            if self.b1_released and (self.prev_px == None) and (self.prev_py == None):
                self.prev_px = event.x
                self.prev_py = event.y
                self.b1_released = False

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

                # move right or left and reach limits
                if self.diffx > 0 and self.horz_scrollbar.get()[1] <= 1:
                    self.new_posx = self.new_posx - self.img_pxx_percent
                    # print("Right ->")
                elif self.diffx < 0 <= self.horz_scrollbar.get()[0]:
                    self.new_posx = self.new_posx + self.img_pxx_percent
                    # print("<- Left")

                if self.diffy > 0 and self.vert_scrollbar.get()[1] <= 1:
                    self.new_posy = self.new_posy - self.img_pxy_percent
                elif self.diffy < 0 <= self.vert_scrollbar.get()[0]:
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

    def refresh_image(self, event=None):
        """ Reloads the image. Used by various functions. Centers the image. """
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

    def image_dimensions(self, image, imgtype):
        """ Reads the current image's dimensions. """
        if self.image_exists:
            if imgtype == 'tk_image':
                self.image_width = image.width()
                self.image_height = image.height()
            elif imgtype == 'pil_image':
                self.image_width = image.width
                self.image_height = image.height

    def help(self):
        """ Provides description of features. """
        webbrowser.open("help.html")

    def about(self):
        """ Creates a window with info about the author and program. """
        self.win_location()
        about_window = tkinter.Toplevel()
        about_window.title("About Viewy")
        about_window.resizable(False, False)
        about_window.geometry("{}x{}+{}+{}".format(250, 150,
                                                   self.win_x_offset+80, self.win_y_offset+100))

        about_window.grid_rowconfigure(0, weight=5)
        about_window.grid_rowconfigure(1, weight=1)
        about_window.grid_rowconfigure(2, weight=1)
        about_window.grid_rowconfigure(3, weight=1)
        about_window.grid_rowconfigure(4, weight=4)
        about_window.grid_rowconfigure(5, weight=1)
        about_window.grid_rowconfigure(6, weight=5)
        about_window.grid_columnconfigure(0, weight=1)
        about_window.grid_columnconfigure(1, weight=1)
        about_window.grid_columnconfigure(2, weight=1)

        title = tkinter.Label(
            about_window, text="Viewy 1.0", font=("Verdana", 12, 'bold'))
        title.grid(row=1, column=1)
        copyright_ = tkinter.Label(
            about_window, text="Copyright © 2020")
        copyright_.grid(row=2, column=1)
        author = tkinter.Label(
            about_window, text="Robert L. Segovia", font=('Helvetica', 11))
        author.grid(row=3, column=1, sticky='n')
        close = tkinter.Button(about_window, text="Close",
                               command=about_window.destroy)
        close.grid(row=5, column=1, sticky='s')

    def win_dimensions(self):
        """ Reads the current window dimensions. Used by various functions. """
        self.win_width = mainWindow.winfo_width()
        self.win_height = mainWindow.winfo_height()
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

    def win_location(self):
        """ Reads the current window location. Used by various functions. """
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
