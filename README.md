# MusicPlayer


The program is a Multi-user command line based music player. Users are recommended music based on their preferred genres and popularity of the song.
Additionally, users can search for songs based on keywords and filter their search by selecting genres. The songs and the user data are stored in a mysql database called ╬ô├ç├┐music╬ô├ç├û containing two tables users and songs.

## MYSQL tables required

Users
+-------------+-------------+------+-----+---------+----------------+
| Field       | Type        | Null | Key | Default | Extra          |
+-------------+-------------+------+-----+---------+----------------+
| uid         | int(5)      | NO   | PRI | NULL    | auto\_increment |
| uname       | varchar(30) | NO   | UNI | NULL    |                |
| pwd         | varchar(30) | NO   |     | NULL    |                |
| pref\_genres | blob        | YES  |     | NULL    |                |
| signed\_in   | int(1)      | YES  |     | 0       |                |
+-------------+-------------+------+-----+---------+----------------+

Songs
+-----------+--------------+------+-----+---------+----------------+
| Field     | Type         | Null | Key | Default | Extra          |
+-----------+--------------+------+-----+---------+----------------+
| songid    | int(10)      | NO   | PRI | NULL    | auto\_increment |
| song\_name | varchar(100) | YES  | MUL | NULL    |                |
| genre     | varchar(100) | YES  |     | NULL    |                |
| song      | longblob     | NO   |     | NULL    |                |
| extension | varchar(5)   | NO   |     | NULL    |                |
| views     | int(10)      | YES  |     | 0       |                |
+-----------+--------------+------+-----+---------+----------------+


Both tables run on the MyISAM storage engine. The music player uses the fulltext search to implement keyword search. Full text only works on the MYISAM storage engine in mysql 5.5

The source code is divided into modules to make further development easier and to keep the functions and classes organized.
There are 3 modules and a subfolder in the /modules folder they are

+-----------------+--------------------------------------------------------+
| Classes.py      | Contains classes used by all other modules             |
| DB\_interface.py | Contains functions used to retrieve data from database |
| Interface.py    | Contains functions used to get data from the user      |
| /tmp            | Folder in which mp3 files are stored temporarily       |
+-----------------+--------------------------------------------------------+

Variuous external modules are used besides the mysql-connector module

**pickle : ** In order to get a binary representation of the list of the genres preferred by the user
**prettytable : ** To print the songs and their other attributes in a neat tabular form
**os : ** In order to delete all the files in the the /tmp folder
**Time : ** Time module to keep track of time
**cursor : ** Cursor to hide/show the terminal╬ô├ç├ûs cursor
**colorama : ** In order to print a progress bar indicating the progress of the song. ANSI escape codes are used, colorama is required to use ANSI escape codes in windows systems
**mutagen : ** Mutagen contains the class MP3 which gets information on mp3 files used to get the duration of the song
**pygame : ** Pygame╬ô├ç├ûs mixer is used to play the music
**threading : ** Threading module is required to run a separate thread waiting for the user to play/pause the song
**getch : ** Used to read a single character from stdin without printing it to the user. Is imported from msvcrt (access to microsoft visual c/c++ runtime library) if the operating system is windows

for more info refer to
https://shorturl.at/iEGS8
https://drive.google.com/file/d/1mHB5w00IrYe6rMObH4iJEK7TcHi0hs\_s/view
