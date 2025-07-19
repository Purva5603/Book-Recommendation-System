import json
import pickle

import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import numpy as np

app = Flask(__name__, template_folder='C:/Users/putva/OneDrive/Desktop/Book Recommader/template')

# Set the correct path where your .pkl files are stored
PICKLE_DIR = "C:/Users/putva/OneDrive/Desktop/Book Recommader/template"

# Flask-Login setup
app.secret_key = '012345678910abcd'  # Change this to a random secret key for security
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Load required pickle files
def load_pickle(file_name):
    file_path = os.path.join(PICKLE_DIR, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            return pickle.load(file)
    else:
        print(f"Error: {file_name} not found in {PICKLE_DIR}")
        return None


# Load necessary pickle files
popular_df = load_pickle('popular.pkl')
pt = load_pickle('pt.pkl')
books = load_pickle('books.pkl')
similarity_scores = load_pickle('similarity_scores.pkl')

# Ensure all files are loaded properly
if any(obj is None for obj in [popular_df, pt, books, similarity_scores]):
    print("One or more pickle files are missing or could not be loaded. Please check the file paths.")
    exit()  # Stop execution if any file is missing

# Path to the user data file
USER_DATA_FILE = 'users.json'


# Helper function to load users from the JSON file
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}


# Helper function to save users to the JSON file
def save_users(users_data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users_data, file)


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id


# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    users_data = load_users()
    if user_id in users_data:
        return User(user_id)
    return None


@app.route('/')
@login_required
def index():
    if popular_df is None:
        return "Error: popular.pkl file is missing. Please check the logs."

    # Combine the book data into a list of dictionaries for easy access
    books_data = [
        {
            'name': book,
            'author': author,
            'image': image,
            'votes': votes,
            'rating': rating
        }
        for book, author, image, votes, rating in zip(
            popular_df['Book-Title'],
            popular_df['Book-Author'],
            popular_df['Image-URL-M'],
            popular_df['num_ratings'],
            popular_df['avg_rating']
        )
    ]

    return render_template('index.html', books=books_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users_data = load_users()  # Load existing users from the file
        if username in users_data and bcrypt.checkpw(password.encode('utf-8'), users_data[username].encode('utf-8')):
            user = User(username)
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    users_data = load_users()  # Load users from the JSON file
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the username already exists
        if username in users_data:
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('register'))

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        # Hash the password and save the user
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_data[username] = hashed_pw.decode('utf-8')  # Save the hashed password as a string

        # Save the users data back to the file
        save_users(users_data)

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/recommend')
@login_required
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['POST'])
@login_required
def recommend():
    # Check if required files are loaded
    if pt is None or books is None or similarity_scores is None:
        flash('Error: One or more required files are missing. Please check the logs.', 'danger')
        return redirect(url_for('recommend_ui'))

    # Get user input for book name, strip any extra spaces
    user_input = request.form.get('user_input').strip()

    # Check if the input is empty
    if not user_input:
        flash('Please enter a book name.', 'danger')
        return render_template('recommend.html', data=[])

    # Normalize the book titles to lowercase for case-insensitive matching
    normalized_input = user_input.lower()

    # Check if the input is in the book dataset (case-insensitive)
    matching_books = [book for book in pt.index if normalized_input in book.lower()]

    if not matching_books:
        flash('Book not found. Please enter a valid book title.', 'danger')
        return render_template('recommend.html', data=[], error="Book not found. Please enter a valid book title.")

    # Use the first match found for recommendations (adjust if you want to provide multiple options)
    selected_book = matching_books[0]

    # Find the index of the selected book in the matrix
    index = np.where(pt.index == selected_book)[0][0]

    # Get similar books based on the similarity scores
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

    # Prepare book data to display recommendations
    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        if not temp_df.empty:
            item = [
                temp_df.drop_duplicates('Book-Title')['Book-Title'].values[0],
                temp_df.drop_duplicates('Book-Title')['Book-Author'].values[0],
                temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values[0]
            ]
            data.append(item)

    # If no recommendations are found, show an appropriate message
    if not data:
        flash('No recommendations available for the selected book.', 'warning')
        return render_template('recommend.html', data=[])

    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
