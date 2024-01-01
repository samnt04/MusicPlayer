import mysql.connector.errors
import prettytable
import colorama
import pygame
from mutagen.mp3 import MP3
import threading
import os
import time
import cursor
if os.name == "nt":
    from msvcrt import getch
else:
    from getch import getch

colorama.init()
pygame.mixer.init()

# Errors
MYSQL_SYNTAX_ERROR = mysql.connector.errors.ProgrammingError
MYSQL_SYNTAX_ERROR.__doc__ = 'Error thrown in case sql syntax is wrong'

MYSQL_DUPLICATE_ERROR = mysql.connector.errors.IntegrityError
MYSQL_DUPLICATE_ERROR.__doc__ = 'Error thrown when there is a duplicate entry in a unique column'


class DB_SETUP_INCORRECT(Exception):
    """Error thrown if the database is setup incorrectly"""
    pass


class UNAME_TAKEN(Exception):
    """Error thrown when the UNAME is already taken"""
    pass


class USER_PREFERENCE_EMPTY(Exception):
    """Error thrown when the user's preferences is empty"""
    pass


class ACCESS_DENIED(Exception):
    """Error thrown if the user is not allowed to access details"""
    pass


def _delete(tuple_in, index):
    """
    Deletes values in the tuple found in the specified indexes
    _delete((1,2,3), 1) -> (1,3)
    _delete((1, 2, 3), [1,2]) -> (1,)
    _delete((1,2,3), None) -> (1,2,3)
    parameters: tuple [tuple], index int|None|list[int]
    """
    if index is None: index = []
    elif type(index) == int: index = [index]
    l = list(tuple_in)
    for i in index: del l[i]
    return tuple(l)


class Table:
    """
    Class Table to deal with displaying Tables of content and choosing values from a table
    Attributes:
        fields : [tuple] tuple of column names
        records : list[tuple] list of records in each row
        hidden : list[int] the indexes of the columns that aren't suppossed to be printed
        title : [str] title of the table to be printed
        auto_number : [bool] set to True by defualt set to False to disable auto numbering
        emtpy_msg : [str] message to be printed if the table is empty set to empty string by default
        cardinality : [int] number of records in the table
        _table : [prettytable.prettytable.PrettyTable] pretty table object
    Methods:
        __init__(self, fields, records=[], hidden=None, title=None, auto_number=True, empty_msg=""): initiates the
                                                                                                    object
        add(self, rec): adds to rec to Table object by appending to records and updating _table object
        get(self, field_name, record_number): gets the value in the table located in column named field_name and row
                                            number record_number
        draw(self): draws the table using the _table object
        choose_single(self, entity, field_name): asks user to choose row number of entity of their choice and gets the 
                                                value using the users selected row number and field_name passed in this
                                                function
        choose_multiple(self, entity, field_name): similiar to choose_single method but lets user to select multiple in
                                                descending order of preference
    """
    def __init__(self, fields, records=[], hidden=None, title=None, auto_number=True, empty_msg=""):
        """
        Instantiates the Table object
        Parameters:
        ----------
            fields: list[str] the name of the columns in the table
            records: list[str|int] the records in the table default is []
            hidden: int|list[int] index of the columns in the table that shouldn't be printed default is None
            title: [str] title of the table to be printed above the table default is None
            auto_number: [bool] whether the records should be numbered when printing default is True
            empty_msg: [str] message to be printed if the table is empty default is empty string ""
        """
        fields = tuple([field.title() for field in fields]) # for uniformity
        self.title = title; self.fields = fields; self.records = records; self.auto_number = auto_number
        self.hidden = hidden; self.empty_msg = empty_msg
        self.cardinality = len(records)
        self._table = prettytable.PrettyTable() # instantiating prettytable object
        self._table.set_style(prettytable.SINGLE_BORDER) # setting prettytable style
        records = [_delete(record, hidden) for record in records] # hiding all hidden records
        fields = _delete(fields, hidden) # hiding all hidden fields
        # if auto numbering is enabled
        if auto_number:
            fields = ("No.",) + fields
            records = [(i + 1,) + record for i, record in enumerate(records)]
        # adding fields and rows to _table object
        self._table.field_names = fields
        self._table.add_rows(records)
        self._table.align = "l"  # align left

    def add(self, rec):
        """
        Adds record the Table object
        Parameters: rec : [tuple] record to be added
        ----------
        """
        self.records.append(rec)  # rec added to records
        rec = _delete(rec, self.hidden) # hiding columns
        self.cardinality += 1
        if self.auto_number:  # in case the table is numbered
            rec = (self.cardinality,) + rec  # cardinality corr to number on table
        self._table.add_row(rec)  # adding rec to pretty table

    def get(self, field_name, record_number):
        """
        Method to get the value at a specific row and in a specific column
        Parameters:
        ----------
            field_name: [str] name of the column
            record_number: [int] record number of the value
        Output: int|str value in the record_number row of the column field_name
        ------
        """
        if record_number in range(1, self.cardinality + 1):
            return self.records[record_number - 1][self.fields.index(field_name.title())]
        else: return

    def draw(self):
        """
        Draws the table
        Output: returns 0 if the table drawn is empty and 1 if it wasn't
        ------
        """
        print(self.title)
        # if table is empty
        if not self.records:
            print(self.empty_msg)
            return 0  # 0 is returned indicating failure
        else:
            print(self._table)
            return 1  # 1 is returned indicating success

    def choose_single(self, entity, field_name):
        """
        Medthod to to let the user choose row number of entity of their choice and gets the 
        value using the users selected row number and field_name passed in this function
        in a table with fields song_name, artist
        Table.choose_single("song", "artist")
        the user will see the message
        'choose song from table by its number'
        and the user chooses 1
        then the value of artist in row no 1 is returned
        Parameters:
        ----------
            entity: [str] entity the user is asked to select
            field_name: [str] name of the column
        """
        print(f"choose {entity} from table by its number")
        choice = input("choice : ").strip()
        if choice.isnumeric():
            choice = int(choice)
        else: return
        return self.get(field_name, choice)

    def choose_multiple_ordered(self, entity, field_name):
        """
        Medthod to to let the user choose row numbers (in decreasing order of preference) of entity of their choice and
        gets the value using the users selected row numbers and field_name passed in this function
        in a table with fields song_name, artist
        Table.choose_single("song", "artist")
        the user will see the message
        'choose song from table by its number'
        and the user chooses 1,2,3
        then the value of artist in row no 1, row no 2 and row no 3 is returned as a list
        Parameters:
        ----------
            entity: [str] entity the user is asked to select
            field_name: [str] name of the column
        Output:
        ------
            list[int|str]: values selected
        """
        print(f"choose {entity}s from table by their numbers in decreasing order of preference",
              "separated by commas like 1,2,3: ", sep="\n")
        choices = input().strip().replace(" ", "").split(",")
        chosen_values = []
        for choice in choices:
            if choice.isnumeric():
                choice = self.get(field_name, int(choice))
                if choice is not None: chosen_values.append(choice)
        return chosen_values


class Song:
    """
    Class to store Song data
    Attributes:
    ----------
        name: [str] name of the song
        genre: [str] genre of the song
        file_name: [str] file path of the song file
        duration: [float] how long the song is in seconds
    Methods: 
        __init__(self, name=None, genre=None, file_name=None) initiates the function
        play(self): plays the song
    """
    def __init__(self, name=None, genre=None, file_name=None):
        """
        Initiates the song object
        Parameters:
        -----------
            name: [str] name of the song default is None
            genre: [str] genre of the song default is None
            file_name: [str] file path where the song file is stored default is None
        """
        self.file_name = file_name; self.name = name; self.genre = genre
        if self.file_name is not None: self.duration = MP3(self.file_name).info.length

    def play(self):
        """Plays the song"""
        MusicPlayer(self).play()


def formatted_time(sec):
    """
    Formats the time in seconds in the minutes:seconds:milliseconds
    Paramaters: sec [float] time in seconds
    ----------
    Output: [str] formatted time
    ------
    formatted_time(156) -> "02:36:00"
    """
    minutes = int(sec//60)
    sec_tmp = sec % 60; sec = int(sec_tmp)
    ms = round((sec_tmp - sec)*100)
    return '{:02}:{:02}:{:02}'.format(minutes, sec, ms)


class Timer:
    """
    Timer class to keep track of time
    Attributes:
        start_time : [float] time at which the Timer object was created in seconds
        offset : [float] offset from the start_time
        max_time : [float] maximum time allowed in seconds
        min_time : [float] minmum time allowed in seconds
        paused_time: [float] time acc to Timer was paused in seconds if the timer is not currently paused value is None
    Methods:
        __init__(self, max_time, min_time=0): initiate the Timer object
        get_time(self): gets the change in time
        add_offset(self, offset_sec): adds an offset to the time
        pause(self): pauses the timer
        unpause(self): unpauses the timer
    """
    def __init__(self, max_time, min_time=0):
        """
        Instantiates the timer object
        Parameters:
        ----------
            max_time : [float] maximum time allowed
            min_time : [float] minmum time allowed None
            paused_time : [float] time acc to Timer at which timer was paused in seconds
        """
        self.start_time = time.time()
        self.offset = 0 # offset from start time
        self.max_time = max_time; self.min_time = min_time
        self.paused_time = None

    def get_time(self):
        """Get time in Timer"""
        if self.paused_time is not None:
            time_out = self.paused_time - self.start_time + self.offset
        else: 
            time_out = time.time() - self.start_time + self.offset
        if time_out <= self.min_time:
            return self.min_time
        elif time_out >= self.max_time:
            return self.max_time
        else:
            return time_out

    
    def pause(self):
        """Pauses the timer"""
        self.paused_time = time.time()

    def unpause(self):
        """Unpauses the timer"""
        if self.paused_time is not None:
            self.offset -= time.time() - self.paused_time
        self.paused_time = None

    def add_offset(self, offset_sec):
        """Add offset from start in timer"""
        self.offset += offset_sec


class MusicPlayer:
    """
    MusicPlayer used to play the music file
    Attributes:
    ----------
        song: [Song] song object of the song to be played
        event_thread: [Thread Object] thread on which user's events are read and acted on
        width : [int] width of the progress bar
        timer: [Timer object] Timer object used to keep track of time in the song
        duration_formatted : [str] duration of the song in minutes:seconds:milliseconds formatt
        instructions: [str] instructions to the user to be printed
    Methods:
    -------
        play_pause(self): plays or pauses the song
        skip(self, offset): skips or rewinds the song based acc to offset to rewind offset is negative
        event_loop(self): event_loop to listen for user events and act upon them
    """
    def play_pause(self):
        """Method to play/pause the music"""
        if pygame.mixer.music.get_busy():
            self.timer.pause()
            pygame.mixer.music.pause()
        else:
            self.timer.unpause()
            pygame.mixer.music.unpause()

    def skip(self, offset):
        """ Method to skip thru song
            Parameters:
            ----------
                offset: [int] in seconds how many secs to be skipped
            MusicPlayer.skip(1) goes forward by 1 second
            MusicPlayer.skip(-1) rewinds by 1 second
        """
        if not pygame.mixer.music.get_busy():
            self.timer.unpause()
            pygame.mixer.music.unpause() 
        self.timer.add_offset(offset * self.song.duration/self.width)
        if self.timer.get_time() == 0: self.timer = Timer(max_time=self.song.duration)
        pygame.mixer.music.set_pos(self.timer.get_time())

    def event_loop(self):
        """Event loop to listen for user events and act upon them"""
        try:
            while True:
                ch = getch().decode("utf-8")    # gets key entered
                if ch in ('\n', '\r'):
                    pygame.mixer.music.unload()
                    return
                elif ch == 'j': self.skip(-1)
                elif ch == 'k': self.play_pause()
                elif ch == 'l': self.skip(1)
        except pygame.error:
            pygame.mixer.music.unload()
            return

    def play(self):
        """Plays the music"""
        cursor.hide()
        print(f"\n\t{self.song.name.title()}")
        pygame.mixer.music.play()
        self.timer = Timer(max_time=self.song.duration)
        self.event_thread.start()   # starts the event thread
        # as long as the event thread is alive
        while self.event_thread.is_alive():
            time.sleep(0.1)
            curr_time = self.timer.get_time()
            done = round(curr_time*self.width/self.song.duration); left = self.width - done
            progress_bar = f"|{'█'*done + '░'*left}|"
            msg = f"\t{formatted_time(curr_time)}{progress_bar}{self.duration_formatted}\n\n\t{self.instructions}"
            print(msg, end="\033[A\r\033[A")
        print(f"\t{self.duration_formatted}|{'█'*self.width}|{self.duration_formatted}\n\n\t{self.instructions}")
        self.event_thread.join()
        print("\n")
        cursor.show()

    def __init__(self, song, width=50):
        """
        Method to initiate the MusicPlayer object
            Paramaters:
            ----------
                song : [Song] song object to be played
                width : [int] width of the progress bar default is 50
        """
        self.song = song
        pygame.mixer.music.load(song.file_name)
        self.event_thread = threading.Thread(target=self.event_loop)
        self.width = width
        self.timer = None
        self.duration_formatted = formatted_time(self.song.duration)
        self.instructions = "press <j> : back, <k> : play/pause, <l> : forward, <enter> : stop"
        