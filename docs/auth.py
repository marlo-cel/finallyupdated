import bcrypt
import os
USER_DATA_FILE= "../DATA/users.txt"

def hash_password(password):
    pass_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pass_bytes, salt)

    return hashed.decode('utf-8')

def verify_password(password, hashed):
    plain_bytes = password.encode('utf-8')
    hash_bytes = hashed.encode('utf-8')

    return bcrypt.checkpw(plain_bytes, hash_bytes)

def register_user(username, password):
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            for line in file:
                stored_username, _ = line.strip().split(',')
                if stored_username == username:
                    print("\nUsername already exists.")
                    return False
    hashed_password = hash_password(password)

    with open(USER_DATA_FILE, 'a') as file:
        file.write(f"{username},{hashed_password}\n")

    return True

def user_exists(username):
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, 'r') as file:
        for line in file:
            stored_username, _ = line.strip().split(',')
            if stored_username == username:
                return True

    return False

def login_user(username, password):
    if not os.path.exists(USER_DATA_FILE):
        print("\nNo users registered yet.")
        return False
    with open(USER_DATA_FILE, 'r') as file:
        for line in file:
            stored_username, stored_hash = line.strip().split(',')

            if stored_username == username:
                if verify_password(password, stored_hash):
                    print("\nLogin successful!")
                    return True
                else:
                    print("\nIncorrect password.")
                    return False
    print("\nUsername not found.")
    return False

def validate_username(username):
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if ',' in username or ' ' in username:
        return False, "Username cannot contain commas or spaces."
    if user_exists(username):
        return False, "Username already exists."
    return True, ""

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def display_menu():
    """Displays the main menu options."""
    print("\n" + "=" * 50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("=" * 50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-" * 50)


def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password = input("Enter a password: ").strip()

            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            register_user(username, password)

        elif choice == '2':
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            if login_user(username, password):
                print("\nYou are now logged in.")
                print("(In a real application, you would now access the dashboard or user area.)")
                input("\nPress Enter to return to main menu...")
            else:
                print("\nError: Invalid username or password.")

        elif choice == '3':
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
