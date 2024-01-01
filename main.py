import Modules.Interface as Interface
import Modules.DB_interface as DB_interface


def main_menu():
    uids = []
    while True:
        print('\n\tChoose 1 to sign in.',
              '\tChoose 2 to create a new account.',
              '\tChoose 3 to delete account',
              '\tChoose 4 to exit.', sep='\n')
        choice = input('choice : ').strip()
        if choice == "1":
            uid = Interface.sign_in()
            if uid is not None:
                uids.append(uid)
                if input("do u wish to edit your preferences? (y/n) : ").strip().lower() == "y":
                    Interface.modify_preferences(uid)
                add_listen_menu(uid)
            continue
        elif choice == "2": Interface.create_account()
        elif choice == "3": Interface.delete_account()
        elif choice == "4":
            print("Exiting the application now...")
            Interface.close(uids)
            return
        else:
            print('Invalid input. Please re-enter your choice.')


def add_listen_menu(uid):
    while True:
        print('\n\tChoose 1 to add songs.',
              '\tChoose 2 to listen to songs.',
              '\tChoose 3 to go back', sep='\n')
        choice = input('choice : ').strip()
        if choice == '1': Interface.add_songs()
        elif choice == '2': listen(uid)
        elif choice == '3':
            print("\n")
            return
        else:
            print('Invalid input. Please re-enter your choice.')


def listen(uid):
    while True:
        print('\n\tChoose 1 to display songs.',
              '\tChoose 2 to display specific genre',
              '\tChoose 3 to search for a song.',
              '\tChoose 4 to go back', sep='\n')
        choice = input('choice : ').strip()
        if choice == '1':
            user_prefs = DB_interface.get_preferences(uid)
            # if user preference is non empty
            if user_prefs:
                Interface.play_from_tables(DB_interface.recommend(genres=user_prefs))
            else:
                print("You can modify your user preferences")
                Interface.play_from_table(DB_interface.recommend())
        elif choice == '2':
            genres = Interface.select_genres()
            if not genres: continue
            Interface.play_from_tables(DB_interface.recommend(genres=genres))
        elif choice == '3':
            search_word = input("enter the name of the song to be searched : ").strip()
            if input("do you wish to search in specific genres? (y/n) : ").strip().lower() == "y":
                genres = Interface.select_genres()
                if not genres: continue
                Interface.play_from_tables(DB_interface.recommend(genres=genres, search=search_word))
            else:
                Interface.play_from_table(DB_interface.recommend(search=search_word))
        elif choice == '4':
            return
        else:
            print('Invalid input. Please re-enter your choice.')

main_menu()