from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


# Home page route
@app.route('/')
def home():
    return render_template('index.html')


# Products page route
@app.route('/products')
def products():
    return render_template('products.html')


# Contact page route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Capture the form data (name, email, message)
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        print(f"Message from {name} ({email}): {message}")  # For testing, you can print the message here
        return render_template('contact.html', message_sent=True)
    return render_template('contact.html', message_sent=False)


# Login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Capture the form data (username, password)
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "password":  # Simple hardcoded login check
            return redirect(url_for('home'))  # Redirect to home after successful login
        else:
            return render_template('login.html',
                                   error="Invalid username or password")  # Show error message if login fails
    return render_template('login.html')


# Sign-up page route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Capture form data (username, email, password, confirm password)
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match!")

        # You can save user details to the database here
        return redirect(url_for('login'))  # Redirect to login page after successful sign-up

    return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug=True)
