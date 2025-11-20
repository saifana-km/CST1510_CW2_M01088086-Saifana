USER_DATA_FILE = "users.txt"
# Importing bcrypt functions to hash plain text password
import bcrypt
import os
import string
import secrets

if not os.path.exists(USER_DATA_FILE):
    open(USER_DATA_FILE, "w").close()

# Function to hash password
def hash_password(plain_text_password):
    # Encoding plain text password to bytes
    password1 = plain_text_password.encode('utf-8')
    # Generating salt
    salt = bcrypt.gensalt(rounds=12)
    # Hashing password using bcrypt.hashpw()
    password2 = bcrypt.hashpw(password1, salt)
    return password2

# Function to verify against hashed password
def verify_password(plain_text_password, hashed_password):
    password1 = plain_text_password.encode('utf-8')
    if bcrypt.checkpw(password1, hashed_password):
        print("SYSTEM MESSAGE: Password is valid.")
        return True
    else:
        print("Error: Password is invalid.")
        return False

# Function to check user database and passwords
def register_user(username, password):
    with open(USER_DATA_FILE, "r") as f:
        lines = f.readlines()
        for line in lines:
            existing_user = line.strip().split(",")
            if username == existing_user[0] :
                print(f"The username '{username}' already exists.")
                return False
        with open(USER_DATA_FILE, "a") as f:
            hashed = hash_password(password)
            f.write(f"{username},{hashed.decode('utf-8')}\n")
        return True

# Function to check if a user exists
def user_exists(username):
    with open(USER_DATA_FILE, "r") as f:
        lines = f.readlines()
        for line in lines:
            existing_user = line.strip().split(",")
            if username == existing_user[0] :
                return True
        return False

# Function for user login, utilising verify_password() function
def login_user(username, password):
    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            existing_user = line.strip().split(",")
            if username == existing_user[0]:
                hashed = existing_user[1].strip().encode('utf-8') 
                return verify_password(password, hashed)
            else:
                print("Error: User does not exist.")
    return False

# Function to validate username
def validate_username(username):
    if user_exists(username):
        return False, f"The username {username} already exists."
    return True, ""

# Function to validate password
def validate_password(password):
    checkup = False
    checklow = False
    checkdig = False
    checkpunc = False
    strength = []
    error = "Error: Invalid password, cannot contain space(s)."  # Error message if x contains a space
    for i in password:
        if i.isupper():
            checkup = True
        if i.islower():
            checklow = True
        if i.isdigit():
            checkdig = True
        if i in string.punctuation:
            checkpunc = True
        if i.isspace() == True:
            return False, error
    strength.extend([checkup, checklow, checkdig, checkpunc])
    check = 0
    # Checks for password strength
    for flag in strength:
        if flag:
            check += 25
    if check <= 25:
        return False, "Password Too Weak."
    elif check <= 50:
        return True, "Moderate Password."
    elif check <= 75:
        return True, "Good Password."
    else:
        return True, "Strong Password."

# Function which displays main menu
def display_menu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

# Function that creates session tokens
def create_session(username):
    token = secrets.token_hex(16)
    # Store token with timestamp
    return token

# Function that calls main menu function, and respectively runs to go through password program
def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")
    choice = 0
    while choice != '3':
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password = input("Enter a password: ").strip() 
            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            # Register the user
            register_user(username, password)

        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            # Attempt login
            if login_user(username, password):
                print("\nYou are now logged in.")
                print(create_session(username))
                # Optional: Ask if they want to logout or exit
                input("\nPress Enter to return to main menu...")

        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break
    
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
