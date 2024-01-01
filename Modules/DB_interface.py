import Modules.Classes as Classes
import pickle
import mysql.connector
import os

DB_CONN_CONFIG = {"host": "localhost", "user": "root",
                  "passwd": "mysql", "database": "music"}
# try catch block in case config settings is incorrect
try:
    connection = mysql.connector.connect(**DB_CONN_CONFIG)
except Classes.MYSQL_SYNTAX_ERROR:
    raise Classes.DB_SETUP_INCORRECT(
        "IMPROPER SETUP : Create database \"music\" or incorrect db configuration check DB_CONN_CONFIG")
connection.autocommit = True  # enabled in order to automatically commit DML commands
db_cursor = connection.cursor()
db_cursor.execute('set global max_allowed_packet=67108864')  # to facilitate large uploads


def close():
    """
    Closing sequence
    close the connection then delete all files int the tmp folder
    """
    connection.close()
    for file_name in os.listdir("Modules\\tmp"):
        os.remove(f"Modules\\tmp\\{file_name}")


def add_user(uname, pwd):
    """
    Function to add user with username uname and password pwd to the database
    Parameters:
        uname: [str] username
        pwd : [str] password
    an error Class.UNAME_TAKEN is thrown if the username is not unique
    """
    try:
        db_cursor.execute("insert into users(uname, pwd) values(%s, %s)", (uname, pwd))
    except Classes.MYSQL_DUPLICATE_ERROR:   # if username is not unique
        raise Classes.UNAME_TAKEN("username taken!!")


def delete_user(uid):
    """
    Function to delete the user
    Parameters: uid [int] user id of the user
    """
    db_cursor.execute(f"delete from users where uid = {uid}")


def extract_uid(uname, pwd):
    """
    Function to extract the user id if username and password are known
    Parameters:
        uname : [str] username of the user
        pwd : [str] password of the user
    An error Classes.ACCESS_DNE error is thrown a corresponding uid is not found
    Output: [int] the user id of the user
    """
    # get users uid given uname and pwd
    db_cursor.execute("select uid from users where uname = %s and pwd = %s", (uname, pwd))
    uid = db_cursor.fetchone()
    print(uid)
    if uid is None:
        # if user not registered error is raised
        raise Classes.ACCESS_DENIED("Access Denied")
    return int(uid[0])  # turns tuple to int


def signed_in(uid):
    """
    Function to check if the user with the user id is signed in
    Parameters: uid [int] the user id of the user
    Output: [bool] whether the user is signed in or not
    """
    db_cursor.execute(f"select signed_in from users where uid = {uid}")
    return bool(db_cursor.fetchone()[0])


def sign_in(uname, pwd):
    """
    Function to register that the user has signed in
    Parameters:
        uname : [str] username of the user
        pwd:    [str] password of the user
    Throws Classes.ACCESS_DENIED error if the username/pwd is incorrect
    Output:  [int] returns the user id of the signee
    """
    uid = extract_uid(uname, pwd)
    db_cursor.execute("update users set signed_in = 1 where uid = %s", (uid,))
    return uid


def sign_out(uid):
    """
    Function to sign out the user
    Parameters: uid [int] user id of the user
    """
    db_cursor.execute("update users set signed_in = 0 where uid = %s", (uid,))


def modify_preferences(uid, pref_genres):
    """
    Function to modify the users preferences given list of new preferences and user id
    Parameters:
        uid: [int] the user id of the user
        pref_genres: list[str] list of preferred genres of the user
    """
    if pref_genres is not None:
        db_cursor.execute("update users set pref_genres = %s where uid = %s", (pickle.dumps(pref_genres), uid))


def get_preferences(uid):
    """
    Function to get the preferences of the user
    Parameters: uid : [int] the user id of the user
    Output : list[str] list of preferred genres of the user
    """
    db_cursor.execute(f"select pref_genres from users where uid = {uid}")
    rec = db_cursor.fetchone()[0]
    if rec is None:
        return []
    return pickle.loads(rec)


def add_songs(songs):
    """
    Function to add songs to the database
    Parameters: songs: list[Classes.Song] list of Songs to be added
    """
    for song in songs:
        with open(song.file_name, "rb") as file:
            db_cursor.execute("insert into songs(song_name, genre, song, extension) values(%s, %s, %s, %s)",
                              (song.name, song.genre, file.read(), song.file_name.split(".")[-1]))


def get_song(songid):
    """
    Function to get the song using the songid
    Parameters: songid [int] the songid of the song
    Output: [Song] a Song object of the song is returned
    """
    db_cursor.execute(f"select song_name, song, extension from songs where songid = {songid}")  # get songid
    record = db_cursor.fetchone()
    # file name is <songid>.<extension>
    with open(f"Modules\\tmp\\{songid}.{record[2]}", "wb") as file:
        file.write(record[1])
    # increase views
    db_cursor.execute(f"update songs set views = views + 1 where songid = {songid}")
    return Classes.Song(file_name=file.name, name=record[0])


def get_available_genres():
    """
    Function to get a Classes.Table of the available songs in the descending order
    Output: [Classes.Table] a table with fields Genre and Views
    """
    db_cursor.execute("select genre, sum(views) from songs group by genre order by sum(views) desc")
    recs = db_cursor.fetchall()
    # return a Classes.Table object with fields Genre and Views and titled Available Genres
    return Classes.Table(fields=("Genre", "Views"), records=recs, title="\nAvailable Genres")


def recommend(genres=None, search=None):
    """
    Function to get song recommendations
    Parameters:
        genres: list[str] genres to operate on default is None if None operations take place on all the songs
        search : [str] keywords to search in the genre if the search is left as None (default) keyword search does not
        take place
    
    1. if genres is None and search is None an auto_numbered Classes.Table titled Songs of 
    songs with fields songid(hidden), Title, views with records in arranged in the decreasing order of views is returned
    
    2. if genres is not None and search is None a list of auto_numbered Classes.Tables titled
    genres{index number acc to genres list} of songs with fields songid(hidden), Title, views with records arranged in
    decreasing order of views is returned a list of songs with fields songid(hidden)
    
    3. if genres is None and search is not None a Classes.Table titled search results of songs with fields
    songid(hidden),title, views with records arranged in descending order of similarity with keyword is returned
    empty_msg the msg to be printed if the table is empty is set to sorry no matches

    4. if genres is not None and search is not None a combo of 2 and 3 takes place
    """
    out = []
    if genres is not None and search is not None:
        # does keyword search on each genre in genres
        for i, genre in enumerate(genres):
            db_cursor.execute("select songid, song_name, views from songs where genre = %s and match(song_name) "
                              "against(%s)", (genre, search))
            # songid should not be displayed soo it is hidden
            # title is genre no. + genre
            # if the table is empty "sorry no matches is printed
            out.append(
                Classes.Table(fields=('songid', 'Title', 'Views'), hidden=0, records=db_cursor.fetchall(),
                              title=f"{str(i + 1)}. {genre}", empty_msg="sorry no matches"))
        return out
    elif genres is not None and search is None:
        # lists out songs in each genre in decreasing popularity
        for i, genre in enumerate(genres):
            db_cursor.execute("select songid, song_name, views from songs where genre = %s order by views desc",
                              (genre,))
            # songid should not be displayed soo it is hidden
            recs = db_cursor.fetchall()
            out.append(
                Classes.Table(fields=('songid', 'Title', 'Views'), hidden=0,
                              records=recs, title=f"{str(i + 1)}. {genre}"))
        print(len(out))
        return out
    elif genres is None and search is not None:
        # executes keyword search on all the songs in the table
        db_cursor.execute(
            f"select songid, song_name, views from songs where match(song_name) against('{search}')")
        # songid should not be displayed soo it is hidden
        # if the table is empty "sorry no matches is printed
        return Classes.Table(fields=('songid', 'Title', 'Views'), hidden=0, records=db_cursor.fetchall(),
                             empty_msg="sorry no matches", title="Search results")
    elif genres is None and search is None:
        # gives all the songs in the table in decreasing order of popularity
        db_cursor.execute("select songid, song_name, views from songs order by views desc")
        # songid should not be displayed soo it is hidden
        return Classes.Table(fields=('songid', 'Title', 'Views'), hidden=0, records=db_cursor.fetchall(), title="Songs")
