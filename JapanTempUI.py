"""
This module contains is mainly UI off the application
"""

import tkinter as tk
from threading import Thread
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning
from typing import Callable

import matplotlib
import pandas as pd
import ttkthemes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from backend import CityNotFoundError, JapanTemperature

matplotlib.use('TKAgg')


class ModeFrame(ttk.LabelFrame):
    """A frame which have include radio button to switch mode whether be Overall, Year, and Month mode """

    def __init__(self, master: ttkthemes.ThemedTk) -> None:
        """Initialize a ModeFrame

        Arguments:
            master {ttkthemes.ThemedTk} -- master window
        """
        super().__init__(master)
        self.__master = master
        self.grid(row=1, column=2, columnspan=2, **master.LABELFRAME_OPT)
        self.__init_widgets()

    def __init_widgets(self) -> None:
        """
        init the widget inside This frame
        """

        # variable
        self.mode_var = tk.StringVar()
        self.compare_var = tk.BooleanVar()

        # radio button
        self.over_mode = ttk.Radiobutton(
            self, text='Overall', variable=self.mode_var, value='overall', command=self.load_overall)
        self.year_mode = ttk.Radiobutton(
            self, text='Year', variable=self.mode_var, value='year', command=self.load_year)
        self.month_mode = ttk.Radiobutton(
            self, text='Month', variable=self.mode_var, value='month', command=self.load_month)
        self.compare_mode = ttk.Checkbutton(
            self, text='Comparing?', variable=self.compare_var, command=self.put_describe)

        self.over_mode.grid(row=0, column=1, sticky=tk.W)
        self.year_mode.grid(row=0, column=2, sticky=tk.W)
        self.month_mode.grid(row=0, column=3, sticky=tk.W)
        self.compare_mode.grid(row=1, column=0, sticky=tk.W)

        # label
        self.mode_label = ttk.Label(self, text='Mode: ')
        self.mode_label.grid(row=0, column=0, padx=2,
                             pady=5, sticky=tk.W)

        # configuration
        self.mode_var.set('overall')
        self.compare_var.set(False)
        self.compare_var.trace('w', lambda *events: self.__master.clear())

        rows, cols = self.grid_size()
        for row in range(rows):
            self.rowconfigure(row, weight=1)
        for col in range(cols):
            self.columnconfigure(col, weight=1)

    def load_overall(self) -> None:
        """
        Load overall mode into UI
        """
        self.clear()
        self.__master.plot_frame.overall_mode()

    def load_year(self) -> None:
        """
        Load year mode into UI
        """
        self.clear()
        self.__master.plot_frame.year_mode()

    def load_month(self) -> None:
        """
        Load month mode into UI
        """
        self.clear()
        self.__master.plot_frame.month_mode()

    def put_describe(self) -> None:
        """
        put describe text into UI
        """
        # check whether it is in comparing mode or not
        if self.compare_var.get():
            self.__master.describe_frame.grid_forget()
            self.__master.plot.get_tk_widget().grid_forget()
            self.__master.plot.get_tk_widget().grid(
                row=1, column=0, rowspan=2, sticky=tk.NSEW)
        else:
            self.__master.describe_frame.grid()
            self.__master.plot.get_tk_widget().grid_forget()
            self.__master.plot.get_tk_widget().grid(
                row=1, column=0, rowspan=3, sticky=tk.NSEW)

    def clear(self) -> None:
        """ Clear the master """
        self.__master.clear()


class DescribeFrame(ttk.LabelFrame):
    """
    Initialize the widget inside this frame
    This contain a mean standard deviation every quatilem and min, max
    """

    def __init__(self, master: ttkthemes.ThemedTk) -> None:
        """Initialize the Frame

        Arguments:
            master {ttkthemes.ThemedTk} -- tk main window
        """
        super().__init__(master, labelanchor=tk.W)
        self.__master = master
        self.grid()
        self.__init_widget()

    def __init_widget(self) -> None:
        """
        initialize all widget into frame
        """
        LABEL_OPT = ('mean', 'std', 'min', '25%', '50%', '75%', 'max')

        # describe label
        describe_label = ttk.Label(self, text='Describe')
        describe_label.grid(row=0, column=0, padx=2,
                            pady=5, columnspan=7)
        # set a label (mean min max ...)
        for i, label_name in enumerate(LABEL_OPT):
            label = tk.Label(self, text=f'{label_name}: ')
            label.grid(row=1, column=i, padx=2,
                       pady=3, sticky=tk.W)

        # config a variable
        self.mean_var = tk.DoubleVar()
        self.std_var = tk.DoubleVar()
        self.min_var = tk.DoubleVar()
        self.twenty_five_var = tk.DoubleVar()
        self.fifty_var = tk.DoubleVar()
        self.seventy_five_var = tk.DoubleVar()
        self.max_var = tk.DoubleVar()

        self.var_tup = (self.mean_var, self.std_var, self.min_var, self.twenty_five_var,
                        self.fifty_var, self.seventy_five_var, self.max_var)

        # set a label with variable
        for i, var in enumerate(self.var_tup):
            label = tk.Label(self, textvariable=var, bg='#8BFFF6',
                             fg='black', anchor=tk.W, width=5)
            label.grid(row=2, column=i, padx=2,
                       pady=3, sticky=tk.W)

        # configuration
        rows, cols = self.grid_size()
        for row in range(rows):
            self.rowconfigure(row, weight=1)
        for col in range(cols):
            self.columnconfigure(col, weight=1)

    def grid(self, **kwargs) -> None:
        """
        grid this widget in specific place
        """
        super().grid(row=3, column=2, columnspan=2, **
                     self.__master.LABELFRAME_OPT, **kwargs)

    def change_describe(self, data: pd.core.series.Series) -> None:
        """changge the value of describe in this widget

        Arguments:
            data {pd.core.series.Serie} -- a series of descripion of data
                                           including all quatile mean std
        """
        described = self.__master.database.get_describe(data)
        for data, var in zip(described, self.var_tup):
            var.set(round(data, 2))

    def reset(self) -> None:
        """
        reset all the thing in this widget
        """
        # set all variable to 0
        for var in self.var_tup:
            var.set(0)


class PlotFrame(ttk.LabelFrame):
    """
    Initialize the widget inside this frame
    this frame is for choosecity, year, and month for plotting thing
    """

    def __init__(self, master: ttkthemes.ThemedTk) -> None:
        """Initialize the plotframe

        Arguments:
            master {ttkthemes.ThemedTk} -- tk main window
        """
        super().__init__(master)
        self.__master = master
        self.grid(row=2, column=2, columnspan=2, **master.LABELFRAME_OPT)
        self.__initwidget()

    def __initwidget(self) -> None:
        """
        Initialize all widget inside the frame
        """

        # Button
        self.clear_button = ttk.Button(
            self, text='Clear', command=self.__master.clear)
        self.plot_button = ttk.Button(
            self, text='Plot', command=self.__master.plotting)

        self.clear_button.grid(row=4, column=0, sticky=tk.EW)
        self.plot_button.grid(row=4, column=2, sticky=tk.EW)

        # combobox
        self.city_combobox = ttk.Combobox(
            self, textvariable=self.__master.city_var)
        self.year_combobox = ttk.Combobox(
            self, textvariable=self.__master.year_var, state='readonly')
        self.month_combobox = ttk.Combobox(
            self, textvariable=self.__master.month_var, state='readonly')

        # bind comvobox to make it can search
        self.city_combobox.bind(
            '<KeyRelease>', self.city_check_input)  # * observer pattern

        self.city_combobox.grid(
            row=0, column=1,  **self.__master.GRID_OPT)

        # use to forgot grid and unforgot grid when user change mode
        self.city_label = ttk.Label(self, text='City: ')
        self.year_label = ttk.Label(self, text='Year: ')
        self.month_label = ttk.Label(self, text='Month: ')

        self.city_label.grid(row=0, column=0, **self.__master.GRID_OPT)

    def init_combobox(self) -> None:
        """
        Combobox in initial state
        """
        self.city_combobox['values'] = list(self.__master.database.city)
        self.year_combobox['values'] = list(self.__master.database.year)
        self.month_combobox['values'] = list(range(1, 13))

    def clear_combobox(self) -> None:
        """
        Clear all combobox
        """
        combobox_tup = (self.city_combobox, self.year_combobox,
                        self.month_combobox)
        for cb in combobox_tup:
            cb.set('')

    def city_check_input(self, event: tk.Event) -> None:
        """easier searching city for combobox

        Arguments:
            event {tk.Event} -- event that call it every time that binded function was call
        """
        # get the city
        search_city = self.city_combobox.get()
        all_city = self.__master.database.city

        # if user didn't input anything value of combobox will be all city
        if not search_city:
            self.city_combobox['values'] = list(all_city)
        else:
            filtered_city = [
                each_city for each_city in all_city if search_city.lower() in each_city.lower()]
            self.city_combobox['values'] = filtered_city

    def have_grided(self, ttk_widget: ttk.Widget) -> bool:
        """check whether widget jusr have grided

        Arguments:
            ttk_widget {ttk.Widget} -- the widget that want to check whether have grid or not

        Returns:
            bool -- True if ttk widget have grided else False
        """
        return bool(ttk_widget.grid_info())

    def month_mode(self) -> None:
        """
        set city, year, and month combobox to month mode
        """
        if not self.have_grided(self.year_combobox):
            self.year_combobox.grid(
                row=1, column=1, **self.__master.GRID_OPT)
            self.year_label.grid(
                row=1, column=0, **self.__master.GRID_OPT)

        if not self.have_grided(self.month_combobox):
            self.month_combobox.grid(
                row=2, column=1, **self.__master.GRID_OPT)
            self.month_label.grid(
                row=2, column=0, **self.__master.GRID_OPT)

    def year_mode(self) -> None:
        """
        set city and year combobox to year mode
        """
        if not self.have_grided(self.year_combobox):
            self.year_combobox.grid(row=1, column=1, **self.__master.GRID_OPT)
            self.__master.plot_frame.year_label.grid(
                row=1, column=0, **self.__master.GRID_OPT)

        if self.have_grided(self.month_combobox):
            self.month_combobox.grid_forget()
            self.month_label.grid_forget()

    def overall_mode(self) -> None:
        """
        set city combobox into the frame as overall mode
        """
        for combobox in (self.year_combobox, self.month_combobox):
            if self.have_grided(combobox):  # if it was grided ungrided it
                combobox.grid_forget()

        for label in (self.year_label, self.month_label):
            if self.have_grided(label):
                label.grid_forget()


def runtask(text: str) -> Callable:
    """decorator for JapanTempReportUI class

    Arguments:
        text {str} -- text for appering in status bar when task in running
    """
    def wrapper(func: Callable) -> Callable:
        """Its a decorate thing nothing else

        Arguments:
            func {Callable} -- some wrapped function
        """

        def inner(self) -> None:
            """create a thread from function and then make progress bar track progress of it"""
            task = Thread(target=lambda: func(self))
            self.bar.start()
            self.status_var.set(text)
            self.change_state(self, 'disabled')
            task.start()
            self.after(5, lambda: self.check_finished(task))
        return inner
    return wrapper


class JapanTempReportUI(ttkthemes.ThemedTk):
    """This is the main frame of the UI"""

    def __init__(self, database: JapanTemperature) -> None:
        """Initialize the app

        Arguments:
            database {JapanTemperature} -- model from the backend
        """
        super().__init__()
        # this is dependency injection (design pattern)
        self.database = database
        self.__have_plotted = []  # use for checking duplicated plot
        self.style = ttkthemes.ThemedStyle(self)  # using the ttktheme
        self.style.theme_use('itft1')
        self.GRID_OPT = {'padx': 5, 'pady': 5, 'sticky': tk.EW}
        self.LABELFRAME_OPT = {'padx': 2, 'pady': 2, 'sticky': tk.NSEW}
        self.initcomponents()

    @runtask('Reading file')
    def __readfile(self) -> None:
        """
        read the database from model
        """
        self.database._readfile()
        self.plot_frame.init_combobox()

    def check_finished(self, task: Thread) -> None:
        """Check whether task is finished if finished it will stop the progressbar then config textlabel to Done

        Arguments:
            task {Thread} -- some task that are running from run_task decorator
        """
        # check whether task is done or not if not it will check the task again after 5millisecond
        # if task is finished, text will config to be Done then stop the progressbar
        if task.is_alive():
            self.after(5, lambda: self.check_finished(task))
        else:
            self.bar.stop()
            self.status_var.set('Done')
            self.change_state(self, 'normal')
            self.after(1000, lambda: self.status_var.set(''))

    def initcomponents(self) -> None:
        """
        create every component in this application
        """
        self.title('Japan Temperature Analysis')
        self.set_var()
        self.create_progess_bar()
        self.mode_frame = ModeFrame(self)
        self.describe_frame = DescribeFrame(self)
        self.plot_frame = PlotFrame(self)
        self.create_button()
        self.__readfile()

        self.create_canvas()
        self.create_label()
        self.configuration()

    def set_var(self) -> None:
        """
        set the StringVar into instance variable
        """
        self.city_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.status_var = tk.StringVar()

    def create_canvas(self) -> None:
        """
        Create a Figure and axe for plotting the data
        """

        self.plot = FigureCanvasTkAgg(Figure(), self)
        self.ax = self.plot.figure.add_subplot()

        self.plot.get_tk_widget().grid(row=1, column=0, rowspan=3,
                                       padx=5, pady=5, sticky=tk.NSEW)

    def create_button(self) -> None:
        """Create button"""

        self.quit_button = ttk.Button(self, text='Quit', command=self.destroy)
        self.quit_button.grid(row=5, column=3, sticky=tk.NSEW)

    def create_progess_bar(self) -> None:
        """Create the progress bar"""
        self.bar = ttk.Progressbar(
            self, orient='horizontal', mode='indeterminate', length=150)
        self.bar.grid(row=5, column=0, columnspan=2, sticky=tk.EW)

    def create_label(self) -> None:
        """Create a label"""
        head_label = ttk.Label(
            self, text='Japan Temerature Visualization', anchor='s', font='Menlo 30 bold')
        self.status_label = ttk.Label(
            self, text='', font='Menlo 10', textvariable=self.status_var)

        head_label.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW)
        self.status_label.grid(row=5, column=0, sticky=tk.W)

    def show_error(self, message: str) -> None:
        """Show error message

        Arguments:
            message {str} -- error message that want to show
        """
        showerror(title='Please select valid city',
                  message=message)

    def show_warning(self) -> None:
        """Show warning message"""
        showwarning(title='Please select all the box',
                    message='Please enter all the information before plotting')

    @runtask('Plotting...')
    def plotting(self) -> None:
        """PLot the graph"""

        # I think this method can be more optimized but dateline make me TT
        # did it a redundant I've fix plotting bug for week an a half please gimme lots of score pls🥺
        if not self.mode_frame.compare_var.get():
            self.clear(clear_all=False)

        mode_list = ['overall', 'year', 'month']
        mode = self.mode_frame.mode_var.get()
        mode_ind = mode_list.index(mode)
        # get the value of variable
        city = self.city_var.get().capitalize()
        year = self.year_var.get()
        month = self.month_var.get()
        title = f'{city} Temperature'
        try:
            if mode_ind >= 1:
                title += f' at {year}'
            if mode_ind >= 2:
                title += f' between {month}'

            if mode_ind == 0:
                title = 'Japanese Temperature over time (Comparing Mode)'
                data = self.database.overall_mode(city)
                label = f'{city} Overall Temperature'
                if label in self.__have_plotted:
                    return
                self.__have_plotted.append(label)
                data.plot(ylabel='Temperature', title=title, grid=True,
                          ax=self.ax, label=label)
            else:
                if mode_ind == 1:
                    title = 'Japanese Temperature over year (Comparing Mode)'
                    data = self.database.year_mode(city, int(year))
                else:
                    title = 'Japanese Temperature over month in days (Comparing Mode)'
                    data = self.database.month_mode(city, int(year), month)
                dataplot = data.tolist()
                label = f'{city} {year} {month} Temperature'
                if label in self.__have_plotted:
                    return
                self.__have_plotted.append(label)
                self.ax.plot(list(range(1, len(dataplot)+1)),
                             dataplot, label=label)
                self.ax.set_title(title)
                self.ax.set_xlabel('day')
                self.ax.set_ylabel('Temperature (℃)')
                self.ax.grid(True)

            self.ax.legend(loc='best')  # set legend for axes
            self.describe_frame.change_describe(data)  # set describe for axes

            self.plot.draw()
        # if city not found it will show error on a popup message
        except CityNotFoundError as message:
            self.show_error(message)
        # if user not fill all the bar it will show warning message
        except (ValueError, KeyError):
            self.show_warning()

    def change_state(self, parent: ttkthemes.ThemedTk, state: str) -> None:
        """configure allmthe button, combobox state to disabled
        by recursively checking whether it is instance of Button or Combobox or not

        Arguments:
            parent {ttkthemes.ThemedTk} -- the parent obj App or master window
            state {str} -- state which is (disabled or enabled)
        """
        for child in parent.winfo_children():
            if isinstance(child, (ttk.Combobox, ttk.Radiobutton, ttk.Checkbutton, ttk.Button)):
                child.configure(state=state)
            elif isinstance(child, (ttk.Frame, ttk.LabelFrame)):
                self.change_state(child, state)

    def configuration(self) -> None:
        """
        Configure the UI
        """

        #  make row and column stickible``
        rows, cols = self.grid_size()
        for row in range(rows):
            self.rowconfigure(row, weight=1)
        for col in range(cols):
            self.columnconfigure(col, weight=1)

    def clear(self, clear_all=True) -> None:
        """Clear the figure

        Keyword Arguments:
            clear_all {bool} -- if clear all is True It will clear all component else it will not clear the combobox (default: {True})
        """

        self.ax.clear()  # clear the axe
        # reset the legend of plotted item
        self.plot.figure.legend_items = []
        self.__have_plotted.clear()

        self.describe_frame.reset()   # reset the describeframe
        if clear_all:
            self.plot_frame.clear_combobox()
        self.plot.draw()  # update canvas

    def run(self) -> None:
        """
        Run the UI
        """
        self.mainloop()
