import tkinter
import tkinter.filedialog
import Modules.DB_interface as DB_interface
import Modules.Classes as Classes


def close(uids):
    """
    Closing sequence signs out user and closes
    Parameter: uid [int] user id of the user
    """
    for uid in uids: DB_interface.sign_out(uid)
    DB_interface.close()


def ask_file_paths():
    """
    Function to ask user for select files
    Output: [str] list of file paths
    """
    root = tkinter.Tk()
    root.withdraw()
    file_paths = tkinter.filedialog.askopenfilenames(title="upload files",
                                                     filetypes=[("music file", "*.mp3"), ("music file", "*.wav")])
    if file_paths is None: return []
    return file_paths


def select_genres():
    """
    Function to let the user select from available genres
    Output: List[str] list of genres chosen by the user
    """
    available = DB_interface.get_available_genres()
    available.draw()
    return available.choose_multiple_ordered(entity="genre", field_name="genre")


def sign_in():
    """
    Function to let the user sign in
    Output: uid [int] user id of the user if login successful otherwise None
    """
    print("\nSign In")
    while True:
        uname = input('\nusername: '); pwd = input('password: ')
        try:
            uid = DB_interface.sign_in(uname, pwd)
            print(f"Welcome, {uname}")
            return uid
        except Classes.ACCESS_DENIED: print('Login unsuccessful')
        if input("Return to menu (y/n) : ").strip().lower() == "y": return


def create_account():
    """Function to let the user create and account"""
    print('\nCREATE NEW ACCOUNT')
    while True:
        uname = input('\nusername: '); pwd = input('password: ')
        try:
            DB_interface.add_user(uname, pwd)
            print("Account has been created successfully")
            return
        except Classes.UNAME_TAKEN: print('User name taken')
        if input("Return to menu (y/n) : ").strip().lower() == "y": return


def delete_account():
    """Function to let the user delete the account"""
    print("\nDELETE ACCOUNT\n")
    # forces user to keep trying till uname and uid is correct
    while True:
        try:
            uid = DB_interface.extract_uid(uname=input('\nyour username: '), pwd=input("password : "))
            print("Are you sure u want to delete your account?")
            if input("y/n : ").strip().lower() == "y":
                DB_interface.delete_user(uid)
                print("account has been deleted")
            print("\n")
            return
        except Classes.ACCESS_DENIED: print("incorrect details")
        if input("Return to menu (y/n) : ").strip().lower() == "y": return


def modify_preferences(uid):
    """
    Function to let the user modify preferences
    Parameters: uid [int] user id of the user
    """
    preferences = DB_interface.get_preferences(uid)
    if preferences:
        records = [(genre,) for genre in preferences]
        Classes.Table(title="\nYour preferred genres", fields=("Genre",), records=records, auto_number=False).draw()
    print("\n")
    DB_interface.modify_preferences(uid=uid, pref_genres=select_genres())
    print("your preference has been saved\n")


def add_songs():
    """Function to let ther user add songs"""
    print("\nSONG UPLOAD\n")
    print("Please select the files you wish to upload")
    # List of Classes.Song objects that will be passed into DB_interface.add_songs to be entered into the db
    songs = []
    # opens file select window and gets files selected
    for file_path in ask_file_paths():
        print(f"\nGenre and title of the song stored at {file_path}")
        genre, name = input("genre : "), input("name : ")
        if genre == "" or name == "": return
        # Song object created and added
        songs.append(Classes.Song(genre=genre, name=name, file_name=file_path))
    print(f"{len(songs)} files have been uploaded")
    print("\n")


def play_from_tables(tables):
    """
    Lets the user select a song from a list of Classes.Table returned by DB_interface.recommend
    and plays the song
    Parameters : tables list[Classes.Table] list of Tables refer to DB_interface.recommend
    """
    success = 0
    for table in tables: success += table.draw()
    if success == 0: return
    while True:
        choice = input("enter genre number : ").strip()
        if choice.isnumeric() and int(choice) <= len(tables):
            songid = tables[int(choice) - 1].choose_single(entity="song", field_name="songid")
            if songid is None: return
            Classes.MusicPlayer(DB_interface.get_song(songid)).play()
        else: print("invalid entry")
        if input("Return to menu (y/n) : ").strip().lower() == "y": return


def play_from_table(table):
    """
    Lets the user select and play a song from Classes.Table returned by DB_interface.recommend and plays the song
    Parameters: Classes.Table refer to DB_interface.recommend
    """
    if table.draw() == 0:
        return
    while True:
        songid = table.choose_single(entity="song", field_name="songid")
        if songid is None: print("invalid entry")
        else: Classes.MusicPlayer(DB_interface.get_song(songid)).play()
        if input("Return to menu (y/n) : ").strip() == "y": return
