from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production!

# Product data
PRODUCTS = {
    'malunggay': {
        'id': 'malunggay',
        'name': 'Malunggay Soap',
        'price': 10.00,
        'image': 'malunggay.jpg',
        'description': 'Nourishing soap made with malunggay leaves, rich in vitamins and minerals. Perfect for healthy, glowing skin.',
        'ingredients': 'Malunggay extract, Coconut oil, Olive oil, Glycerin',
        'benefits': 'Rich in Vitamin C, promotes healthy skin, natural moisturizer'
    },
    'soapy': {
        'id': 'soapy',
        'name': 'Soapy Soap',
        'price': 15.00,
        'image': 'soapy.jpg',
        'description': 'Classic handmade soap with a gentle formula suitable for all skin types.',
        'ingredients': 'Coconut oil, Palm oil, Glycerin, Essential oils',
        'benefits': 'Gentle cleansing, suitable for sensitive skin, moisturizing'
    },
    'lavender': {
        'id': 'lavender',
        'name': 'Lavender Bliss',
        'price': 20.00,
        'image': 'lavander.jpg',
        'description': 'Calming lavender-infused soap that helps relax your mind and soothe your skin.',
        'ingredients': 'Lavender essential oil, Coconut oil, Shea butter, Glycerin',
        'benefits': 'Calming aroma, stress relief, skin soothing properties'
    },
    'honey': {
        'id': 'honey',
        'name': 'Honey Almond',
        'price': 25.00,
        'image': 'honey.jpg',
        'description': 'Luxurious soap with honey and almond extracts for soft, smooth, and radiant skin.',
        'ingredients': 'Honey, Almond oil, Coconut oil, Glycerin, Vitamin E',
        'benefits': 'Deep moisturizing, anti-aging properties, natural glow'
    }
}

# Orders storage file - use absolute path relative to this file
# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, 'orders.json')
# Users storage file - use absolute path relative to this file
USERS_FILE = os.path.join(BASE_DIR, 'users.json')

# Print paths on startup for debugging
print(f"BASE_DIR: {BASE_DIR}")
print(f"ORDERS_FILE: {ORDERS_FILE}")
print(f"ORDERS_FILE exists: {os.path.exists(ORDERS_FILE)}")
print(f"USERS_FILE: {USERS_FILE}")
print(f"USERS_FILE exists: {os.path.exists(USERS_FILE)}")

def load_orders():
    """Load orders from JSON file"""
    try:
        print(f"load_orders() called - ORDERS_FILE path: {ORDERS_FILE}")
        print(f"Absolute path: {os.path.abspath(ORDERS_FILE)}")
        print(f"File exists: {os.path.exists(ORDERS_FILE)}")

        data = []
        primary_path = ORDERS_FILE

        if os.path.exists(primary_path):
            with open(primary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Loaded data type: {type(data)} from {primary_path}")
        else:
            print(f"Orders file not found at {primary_path}")

        # Fallback: check for orders.json in current working directory (legacy behaviour)
        if (not data) and os.getcwd() != BASE_DIR:
            fallback_path = os.path.join(os.getcwd(), 'orders.json')
            if os.path.exists(fallback_path):
                try:
                    with open(fallback_path, 'r', encoding='utf-8') as f:
                        fallback_data = json.load(f)
                        if isinstance(fallback_data, list) and fallback_data:
                            print(f"Using fallback orders.json at {fallback_path} (found {len(fallback_data)} orders)")
                            data = fallback_data
                            # Optional: copy fallback contents into primary file so future reads succeed
                            try:
                                with open(primary_path, 'w', encoding='utf-8') as pf:
                                    json.dump(fallback_data, pf, indent=2, ensure_ascii=False)
                                print("Synced fallback orders into primary orders.json")
                            except Exception as sync_error:
                                print(f"Unable to sync fallback orders to primary file: {sync_error}")
                except Exception as fb_err:
                    print(f"Error reading fallback orders.json: {fb_err}")

        if isinstance(data, list):
            print(f"Returning {len(data)} orders")
            return data
        elif data:
            # Data exists but is not a list – convert if possible
            try:
                converted = list(data)
                print(f"Converted non-list data to list with length {len(converted)}")
                return converted
            except Exception as convert_error:
                print(f"Warning: orders.json data is not iterable (type {type(data)}): {convert_error}")
        else:
            print("No orders data found; returning empty list")

        return []
    except Exception as e:
        print(f"Error loading orders from {ORDERS_FILE}: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_order(order):
    """Save a new order to JSON file"""
    try:
        print(f"Attempting to save order to: {ORDERS_FILE}")
        print(f"File exists before save: {os.path.exists(ORDERS_FILE)}")
        orders = load_orders()
        print(f"Loaded {len(orders)} existing orders")
        if not isinstance(orders, list):
            print(f"Warning: orders is not a list, converting to list. Type: {type(orders)}")
            orders = []
        orders.append(order)
        print(f"Total orders after append: {len(orders)}")
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)
        print(f"Order saved successfully: {order.get('order_id', 'Unknown')} to {ORDERS_FILE}")
        print(f"File exists after save: {os.path.exists(ORDERS_FILE)}")
        # Verify the save worked
        verify_orders = load_orders()
        print(f"Verification: {len(verify_orders)} orders in file after save")
        return True
    except Exception as e:
        print(f"Error saving order: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_users():
    """Load users from JSON file"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading users: {e}")
        return []
    return []

def save_user(user_data):
    """Save a new user to JSON file"""
    try:
        users = load_users()
        # Check if username or email already exists
        for user in users:
            if user['username'] == user_data['username']:
                return False, "Username already exists!"
            if user['email'] == user_data['email']:
                return False, "Email already registered!"
        
        users.append(user_data)
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True, "User registered successfully!"
    except IOError as e:
        print(f"Error saving user: {e}")
        return False, "Error saving user. Please try again."

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_logged_in') and not session.get('admin_logged_in'):
            # Store the intended destination
            session['next_url'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Cart helper functions
def get_cart():
    """Get cart from session"""
    return session.get('cart', {})

def add_to_cart(product_id, quantity=1):
    """Add product to cart"""
    cart = get_cart()
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    session['cart'] = cart

def remove_from_cart(product_id):
    """Remove product from cart"""
    cart = get_cart()
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart

def update_cart_item(product_id, quantity):
    """Update quantity of item in cart"""
    cart = get_cart()
    if product_id in cart:
        if quantity > 0:
            cart[product_id] = quantity
        else:
            del cart[product_id]
        session['cart'] = cart

def clear_cart():
    """Clear entire cart"""
    session['cart'] = {}

def get_cart_total():
    """Calculate total price of cart"""
    cart = get_cart()
    total = 0
    for product_id, quantity in cart.items():
        if product_id in PRODUCTS:
            total += PRODUCTS[product_id]['price'] * quantity
    return total

def get_cart_count():
    """Get total number of items in cart"""
    cart = get_cart()
    return sum(cart.values())

# Context processor to make session and cart available in all templates
@app.context_processor
def inject_session():
    return dict(session=session, cart_count=get_cart_count())

# Home page route
@app.route('/')
def home():
    return render_template('index.html', products=PRODUCTS)


# Products page route
@app.route('/products')
def products():
    return render_template('products.html', products=PRODUCTS)

# Product detail page route
@app.route('/product/<product_id>')
def product_detail(product_id):
    if product_id not in PRODUCTS:
        return redirect(url_for('products'))
    product = PRODUCTS[product_id]
    return render_template('product_detail.html', product=product)


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
        
        # Check for admin login
        if username == "admin" and password == "password":  # Admin login
            session['admin_logged_in'] = True
            session['username'] = 'admin'
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
        
        # Check for regular user login
        users = load_users()
        user_found = False
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['user_logged_in'] = True
                session['username'] = username
                session['user_email'] = user['email']
                user_found = True
                # Redirect to intended page or home
                next_url = session.pop('next_url', None)
                if next_url:
                    return redirect(next_url)
                return redirect(url_for('home'))  # Redirect to home after successful login
        
        if not user_found:
            return render_template('login.html',
                                   error="Invalid username or password")  # Show error message if login fails
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('user_logged_in', None)
    session.pop('username', None)
    session.pop('user_email', None)
    return redirect(url_for('home'))


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
        
        # Check if username is admin (reserved)
        if username.lower() == "admin":
            return render_template('signup.html', error="Username 'admin' is reserved. Please choose another username.")

        # Save user details
        user_data = {
            'username': username,
            'email': email,
            'password': password,  # In production, use password hashing!
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        success, message = save_user(user_data)
        if success:
            return redirect(url_for('login'))  # Redirect to login page after successful sign-up
        else:
            return render_template('signup.html', error=message)

    return render_template('signup.html')

# Cart routes
@app.route('/cart/add/<product_id>', methods=['POST'])
def add_to_cart_route(product_id):
    if product_id not in PRODUCTS:
        return redirect(url_for('products'))
    
    quantity = int(request.form.get('quantity', 1))
    add_to_cart(product_id, quantity)
    return redirect(request.referrer or url_for('products'))

@app.route('/cart')
def view_cart():
    cart = get_cart()
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        if product_id in PRODUCTS:
            product = PRODUCTS[product_id]
            item_total = product['price'] * quantity
            total += item_total
            cart_items.append({
                'product_id': product_id,
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/update/<product_id>', methods=['POST'])
def update_cart_route(product_id):
    quantity = int(request.form.get('quantity', 1))
    update_cart_item(product_id, quantity)
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<product_id>', methods=['POST'])
def remove_from_cart_route(product_id):
    remove_from_cart(product_id)
    return redirect(url_for('view_cart'))

@app.route('/cart/clear', methods=['POST'])
def clear_cart_route():
    clear_cart()
    return redirect(url_for('view_cart'))

# Checkout page route
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = get_cart()
    
    if not cart:
        return redirect(url_for('view_cart'))
    
    if request.method == 'POST':
        # Get cart items
        cart_items = []
        for product_id, quantity in cart.items():
            if product_id in PRODUCTS:
                product = PRODUCTS[product_id]
                cart_items.append({
                    'product_id': product_id,
                    'product_name': product['name'],
                    'quantity': quantity,
                    'unit_price': product['price'],
                    'total_price': product['price'] * quantity
                })
        
        # Create order for each item (or combine into one order)
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_price = get_cart_total()
        
        # Save order with all items
        order_data = {
            'order_id': order_id,
            'items': cart_items,
            'total_price': total_price,
            'customer_name': request.form['customer_name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'shipping_address': request.form['shipping_address'],
            'city': request.form['city'],
            'postal_code': request.form['postal_code'],
            'payment_method': request.form['payment_method'],
            'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'Pending'
        }
        
        # Save order
        print(f"About to save order: {order_data.get('order_id', 'Unknown')}")
        save_result = save_order(order_data)
        print(f"Save result: {save_result}")
        if save_result:
            # Clear cart after successful order
            clear_cart()
            try:
                return render_template('checkout_success.html', order=order_data)
            except Exception as e:
                print(f"Template rendering error: {e}")
                # Fallback: redirect to home with success message
                return redirect(url_for('home'))
        else:
            # Error saving order, reload checkout page with error
            print("ERROR: Failed to save order!")
            cart_items = []
            total = 0
            for product_id, quantity in cart.items():
                if product_id in PRODUCTS:
                    product = PRODUCTS[product_id]
                    item_total = product['price'] * quantity
                    total += item_total
                    cart_items.append({
                        'product_id': product_id,
                        'product': product,
                        'quantity': quantity,
                        'item_total': item_total
                    })
            user_info = {}
            if session.get('user_logged_in'):
                users = load_users()
                for user in users:
                    if user['username'] == session.get('username'):
                        user_info = {
                            'name': user.get('username', ''),
                            'email': user.get('email', '')
                        }
                        break
            return render_template('checkout.html', cart_items=cart_items, total=total, user_info=user_info, error="Error saving order. Please try again.")
    
    # GET request - show checkout form with cart items
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        if product_id in PRODUCTS:
            product = PRODUCTS[product_id]
            item_total = product['price'] * quantity
            total += item_total
            cart_items.append({
                'product_id': product_id,
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
    
    # Pre-fill user info if logged in
    user_info = {}
    if session.get('user_logged_in'):
        users = load_users()
        for user in users:
            if user['username'] == session.get('username'):
                user_info = {
                    'name': user.get('username', ''),
                    'email': user.get('email', '')
                }
                break
    
    return render_template('checkout.html', cart_items=cart_items, total=total, user_info=user_info)

# Admin dashboard route
@app.route('/admin')
@admin_required
def admin_dashboard():
    try:
        print(f"\n=== ADMIN DASHBOARD LOADING ===")
        print(f"ORDERS_FILE path: {ORDERS_FILE}")
        print(f"Absolute path: {os.path.abspath(ORDERS_FILE)}")
        print(f"File exists: {os.path.exists(ORDERS_FILE)}")
        
        orders = load_orders()
        print(f"load_orders() returned: {type(orders)}, length: {len(orders) if isinstance(orders, list) else 'N/A'}")
        
        # Ensure orders is a list - NEVER return None
        if orders is None:
            print("ERROR: load_orders() returned None! Converting to empty list.")
            orders = []
        elif not isinstance(orders, list):
            print(f"Warning: orders is not a list, type: {type(orders)}, converting to list")
            orders = []
        
        print(f"After validation: orders type={type(orders)}, length={len(orders)}")
        
        # Sort orders by date (newest first) - handle missing order_date safely
        try:
            if orders:
                orders.sort(key=lambda x: x.get('order_date', '') if isinstance(x, dict) and 'order_date' in x else '', reverse=True)
                print(f"Sorted {len(orders)} orders")
        except Exception as sort_error:
            print(f"Error sorting orders: {sort_error}")
            import traceback
            traceback.print_exc()
        
        print(f"Returning {len(orders)} orders to template")
        print(f"Orders variable type: {type(orders)}")
        print(f"Orders is list: {isinstance(orders, list)}")
        print(f"=== END ADMIN DASHBOARD LOADING ===\n")
        
        # Double-check: ensure orders is definitely a list
        if not isinstance(orders, list):
            print("FINAL CHECK: orders is not a list! Converting...")
            orders = []
        
        debug_info = {
            'orders_file': ORDERS_FILE,
            'orders_file_exists': os.path.exists(ORDERS_FILE),
            'cwd': os.getcwd(),
            'orders_count': len(orders) if isinstance(orders, list) else 0
        }
        return render_template('admin_dashboard.html', orders=orders or [], debug_info=debug_info)
    except Exception as e:
        print(f"CRITICAL ERROR in admin_dashboard: {e}")
        import traceback
        traceback.print_exc()
        # Always return a list, never None
        return render_template('admin_dashboard.html', orders=[])

# Update order status route
@app.route('/admin/update_order/<order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    try:
        new_status = request.form.get('status')
        orders = load_orders()
        
        for order in orders:
            if order['order_id'] == order_id:
                order['status'] = new_status
                break
        
        with open(ORDERS_FILE, 'w') as f:
            json.dump(orders, f, indent=2)
    except (IOError, KeyError) as e:
        print(f"Error updating order status: {e}")
    
    return redirect(url_for('admin_dashboard'))

# Delete order route
@app.route('/admin/delete_order/<order_id>', methods=['POST'])
@admin_required
def delete_order(order_id):
    try:
        orders = load_orders()
        orders = [order for order in orders if order['order_id'] != order_id]
        
        with open(ORDERS_FILE, 'w') as f:
            json.dump(orders, f, indent=2)
    except (IOError, KeyError) as e:
        print(f"Error deleting order: {e}")
    
    return redirect(url_for('admin_dashboard'))


if __name__ == "__main__":
    app.run(debug=True)
