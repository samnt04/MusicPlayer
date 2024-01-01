# MusicPlayer


The program is a Multi-user command line based music player. Users are recommended music based on their preferred genres and popularity of the song.<br>
Additionally, users can search for songs based on keywords and filter their search by selecting genres. The songs and the user data are stored in a mysql database called music containing two tables users and songs.<br>

## MYSQL tables required

**Users**<br>
| Field       	| Type        	| Null 	| Key 	| Defuault 	| Extra          	|
|-------------	|-------------	|------	|-----	|----------	|----------------	|
| uid         	| int(5)      	| NO   	| PRI 	| NULL     	| auto_increment 	|
| uname       	| varchar(30) 	| NO   	| UNI 	| NULL     	|                	|
| pwd         	| varchar(30) 	| NO   	|     	| NULL     	|                	|
| pref_genres 	| blob        	| YES  	|     	| NULL     	|                	|
| signed_in   	| int(1)      	| YES  	|     	| 0        	|                	|

**Songs**<br>
+-----------+--------------+------+-----+---------+----------------+<br>
| Field     | Type         | Null | Key | Default | Extra          |<br>
+-----------+--------------+------+-----+---------+----------------+<br>
| songid    | int(10)      | NO   | PRI | NULL    | auto\_increment |<br>
| song\_name | varchar(100) | YES  | MUL | NULL    |                |<br>
| genre     | varchar(100) | YES  |     | NULL    |                |<br>
| song      | longblob     | NO   |     | NULL    |                |<br>
| extension | varchar(5)   | NO   |     | NULL    |                |<br>
| views     | int(10)      | YES  |     | 0       |                |<br>
+-----------+--------------+------+-----+---------+----------------+<br>


Both tables run on the MyISAM storage engine. The music player uses the fulltext search to implement keyword search. Full text only works on the MYISAM storage engine in mysql 5.5 <br><br>

The source code is divided into modules to make further development easier and to keep the functions and classes organized.<br>
There are 3 modules and a subfolder in the /modules folder they are<br><br>

+-------------------+---------------------------------------------------------+<br>
| Classes.py				|	Contains classes used by all other modules							|<br>
| DB\_interface.py 	|	Contains functions used to retrieve data from database	|<br>
| Interface.py			|	Contains functions used to get data from the user				|<br>
| /tmp							|	Folder in which mp3 files are stored temporarily				|<br>
+-------------------+---------------------------------------------------------+<br>
<br>
Variuous external modules are used besides the mysql-connector module<br><br>

**pickle 			:** In order to get a binary representation of the list of the genres preferred by the user<br><br>
**prettytable :** To print the songs and their other attributes in a neat tabular form<br><br>
**os 					:** In order to delete all the files in the the /tmp folder<br><br>
**Time 				:** Time module to keep track of time<br><br>
**cursor 			:** Cursor to hide/show the terminal cursor<br><br>
**colorama 		:** In order to print a progress bar indicating the progress of the song. ANSI escape codes are used, colorama is required to use ANSI escape codes in windows systems<br><br>
**mutagen 		:** Mutagen contains the class MP3 which gets information on mp3 files used to get the duration of the song<br><br>
**pygame 			:** Pygame mixer is used to play the music<br><br>
**threading 	:** Threading module is required to run a separate thread waiting for the user to play/pause the song<br><br>
**getch 			:** Used to read a single character from stdin without printing it to the user. Is imported from msvcrt (access to microsoft visual c/c++ runtime library) if the operating system is windows<br><br>

for more info refer to<br>
https://shorturl.at/iEGS8<br>
https://drive.google.com/file/d/1mHB5w00IrYe6rMObH4iJEK7TcHi0hs\_s/view<br>
