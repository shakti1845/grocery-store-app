#importing all the libreries required 
from flask import Flask, render_template, request, redirect, url_for, flash ,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from werkzeug.utils import secure_filename

import os

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # This creates the directory if it doesn't exist




app = Flask(__name__)
    
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER']= 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)
app.app_context().push()


login_manager = LoginManager(app)
login_manager.login_view = 'login'




# User model creating 
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
   

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes for login, logout, and a protected page 
#all routes for user 
#home
@app.route('/')
def home():
    return render_template('home.html')

#login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            products = Products.query.all()
     
            login_user(user)
            session["user_Name"]=user.username
            session['token_session']=user.id
            flash('Logged in successfully!', 'success')
            return render_template('profile.html',user_Name=session.get("user_Name"),products=products,)
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')
        
#new USER registration

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            
            return redirect(url_for('register'))

        new_user=User(username=username,password=password)
        db.session.add(new_user)
        db.session.commit()
       
       
        return redirect(url_for('login'))

    return render_template('register.html')

#logout_user

@app.route('/logout')
@login_required
def logout():
    session.pop('user_Name', None)
    session.pop('token_session', None)
   
    return redirect(url_for('login'))

#profile of user after login
@app.route('/profile')
def profile():
    token_session=session.get('token_session')
    if token_session!=None:
        products = Products.query.all()
        
        return render_template('profile.html',user_Name=session.get("user_Name"),products=products)
    return redirect('/login')



# Product model
class Products(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    qty = db.Column(db.Integer,nullable =False)
    image_filename = db.Column(db.String)
    # manufacture_date = db.Column(db.Date)
    # expiry_date = db.Column(db.Date)

#class category 

# Update the view_products function
@app.route('/remove_item/<int:product_id>')
def remove_item(product_id):
     
    cart = session.get('cart', [])
    for i in cart:
        if i['id']==product_id:
            if i['quantity']==1:
                cart.remove(i)
                
            else:
                product = Products.query.get(product_id)
                i['quantity']=i['quantity']-1
                i['price']=i['price']-product.price
    product = Products.query.get(product_id)
    if product:
            product.qty=product.qty+1 
            db.session.commit()            
    session['cart'] = cart
    return redirect(url_for('view_cart'))
@app.route('/add_category',methods=['POST'])



@app.route('/products_Category', methods=['GET', 'POST'])
def view_products():
    if request.method == 'POST':
        category = request.form['category']
        products = []

        if category:
            products = Products.query.filter_by(category=category).all()
        else:
            products = Products.query.all()

        return render_template('profile.html', products=products, selected_category=category)

    return render_template('profile.html', products=[], selected_category=None)

#searching products
@app.route('/products/search', methods=['GET', 'POST'])
def search_products():
    if request.method == 'POST':
        search_query = request.form['search_query']

        # Query products from the database that match the search query
        products = Products.query.filter(Products.name.ilike('%' + search_query + '%')).all()

        return render_template('profile.html', products=products)

    return redirect(url_for('view_cart'))


#adding product into cart
# 
#  

@app.route('/products/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
  
    # Retrieve the product from the database on the basis of product_id
    product = Products.query.get(product_id)
    if product:
            product.qty=product.qty-1 
            db.session.commit()
    # Create a dictionary with the relevant attributes of the product
    product_dict = {
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'description': product.description,
        'category': product.category,
        'quantity':1
    }
    # Add the product dictionary to the user's cart
    cart = session.get('cart', [])
    check=0
    
    for i in cart:
        if i["id"]==product.id:
            i["quantity"]=i["quantity"]+1
            i["price"]=i["price"]+product.price
            
             
            check=1
    if check==0:
        cart.append(product_dict)
    session['cart'] = cart
    
    
        

    
    return redirect(url_for('view_cart'))



#route to cart 
 
@app.route('/cart')
def view_cart():
    
    cart = session.get('cart', [])
    total_price=0
    for i in cart:
        total_price=total_price+i['price']
    return render_template('view_cart.html', cart=cart,total_price = total_price)

# Process for checkout 
@app.route('/cart/checkout', methods=['POST'])
def checkout():
    # Process for checkout

     
     
    # Update product quantities in the database



    # clear the user's cart after the purchase is completed
    session.pop('cart', None)
    
    return redirect(url_for('profile'))



#admin model 


class Admins(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ADMIN_USERNAME = db.Column(db.String(50), unique=True, nullable=False)
    ADMIN_PASSWORD = db.Column(db.String(100), nullable=False)

    # Set admin credentials
admin = Admins(ADMIN_USERNAME='shakti', ADMIN_PASSWORD='shakti123')



@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    error = "Invalid username or password"  # Initialize error variable outside of POST block

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == admin.ADMIN_USERNAME and password == admin.ADMIN_PASSWORD:
            # Set session variable to indicate admin is logged in
            # You can use Flask session here to handle authentication
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid credentials. Please try again."

    return render_template('adminlogin.html', error=error)

#admin dashboard 

@app.route('/admin_dashboard',methods =['GET','POST'])
def admin_dashboard():
    # Check if admin is logged in
    products =Products.query.all()
    if session.get('admin_logged_in'):
        return render_template('admin_dashboard.html',products =products)
    else:
        return redirect(url_for('adminlogin'))


#product model




#add product 
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        # Handle form submission for adding products
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        category = request.form['category']
        qty = int(request.form['qty'])
        image_file = request.files['image']
        #manufacture_date = request.files['maufacture_date']
        #expiry_date = request.files['expiry_date']
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

    

        # Create a new Product object and add it to the database
        new_product = Products(name=name, price=price, description=description, category=category, qty=qty,image_filename = filename )
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))
        

        # Create a new Product object and add it to the database
        
    
    return render_template('add_product.html', product=None)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


#delete product

@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    product = Products.query.get(product_id)
    if request.method == 'POST':
        if product:
            db.session.delete(product)
            db.session.commit()
            
            return redirect(url_for('admin_dashboard'))
        else:

            return redirect(url_for('admin_dashboard'))
    else:
        return render_template('delete_product.html', product=product, product_id=product_id)





  

#edit product by admin 
# Add a new route and view function for editing products
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Products.query.get(product_id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.description = request.form['description']
        product.category = request.form['category'] 
        product.qty = request.form['qty']
        image_file = request.files.get('image')
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            product.image_filename = filename

        db.session.commit()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_product.html', product=product )


@app.route('/admin_logout')
def admin_logout():
    # Clear session and log out admin
    session.clear()
    return redirect(url_for('adminlogin'))


if __name__ == '__main__':
    app.run(debug=True)






