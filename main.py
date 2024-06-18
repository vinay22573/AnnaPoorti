from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user,logout_user,login_manager,LoginManager, UserMixin
from flask_login import login_required,current_user
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user, login_manager, LoginManager, login_required, current_user
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask import render_template

Base = declarative_base()


#My db connection
local_server=True
app = Flask(__name__)

# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



app.secret_key='sarthak'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost:3306/annapoorti'
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Password = db.Column(db.String(100), nullable=False)
    UserType = db.Column(db.Enum('Individual', 'Organization'), nullable=False)
    def get_id(self):
        return str(self.UserID)

    @property
    def is_authenticated(self):
        return True  # Assuming all users are authenticated

    @property
    def is_active(self):
        return True  # Assuming all users are active

    @property
    def is_anonymous(self):
        return False  # Assuming all users are not anonymous

    # donations = relationship('FoodDonation', backref='user', lazy=True)
    # campaigns = relationship('FundraisingCampaign', backref='user', lazy=True)
    # reported_areas = relationship('ReportedArea', backref='user', lazy=True)
    # donations_made = relationship('FundraisingDonation', backref='user', lazy=True)
    # collaborations = relationship('Collaboration', backref='user', lazy=True)
    # leaderboard = relationship('Leaderboard', backref='user', uselist=False)

class FoodDonation(db.Model):
    __tablename__ = 'foodDonations'

    DonationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    DonationDate = db.Column(db.Date)
    FoodDescription = db.Column(db.String(255))
    Quantity = db.Column(db.Integer)

    user = relationship('User', backref='donations')

class FundraisingCampaign(db.Model):
    __tablename__ = 'fundraisingCampaigns'

    CampaignID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    CampaignName = db.Column(db.String(100))
    Description = db.Column(db.Text)
    TargetAmount = db.Column(db.Numeric(10, 2))
    StartDate = db.Column(db.Date)
    EndDate = db.Column(db.Date)

class ReportedArea(db.Model):
    __tablename__ = 'reportedAreas'

    ReportID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    ReportDate = db.Column(db.Date)
    AreaDescription = db.Column(db.String(255))

class FundraisingDonation(db.Model):
    __tablename__ = 'fundraisingDonations'

    DonationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    CampaignID = db.Column(db.Integer, db.ForeignKey('fundraisingCampaigns.CampaignID'), nullable=False)
    DonationDate = db.Column(db.Date)
    Amount = db.Column(db.Numeric(10, 2))

class Leaderboard(db.Model):
    __tablename__ = 'leaderboard'

    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), primary_key=True)
    TotalDonationAmount = db.Column(db.Numeric(10, 2))
    TotalFoodDonated = db.Column(db.Integer)
    TotalAreasReported = db.Column(db.Integer)

class Collaboration(db.Model):
    __tablename__ = 'collaborations'

    CollaborationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    CollaboratorName = db.Column(db.String(100))
    Description = db.Column(db.Text)

class ContactFormEntry(db.Model):
    __tablename__ = 'contactformentry'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)




@app.route("/home")
def home1():
    return render_template('base.html')


@app.route("/About")
def About():
    return render_template('About.html')

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/home")
def home11():
    return render_template('home.html')



@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('psw')
        user = User.query.filter_by(Email=email).first()
        print(email,password,user)

        if user and user.Password == password:
            login_user(user)
            flash("Login Successful", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password", "danger")

    return render_template('login.html')



@app.route('/add_donation')
@login_required
def index():
    return render_template('food_donations.html')

@app.route('/add_donation', methods=['POST','GET'])
@login_required
def add_donation():
    userID = request.form['userID']
    donationDate = datetime.strptime(request.form['donationDate'], '%Y-%m-%d').date()
    foodDescription = request.form['foodDescription']
    quantity = request.form['quantity']

    new_donation = FoodDonation(UserID=userID, DonationDate=donationDate, FoodDescription=foodDescription, Quantity=quantity)
    db.session.add(new_donation)
    db.session.commit()

    return redirect(url_for('index'))




@app.route('/add_fundraising_donation', methods=['GET', 'POST'])
@login_required
def add_fundraising_donation():
    if request.method == 'POST':
        userID = request.form['userID']
        campaignID = request.form['campaignID']
        donationDate = datetime.strptime(request.form['donationDate'], '%Y-%m-%d').date()
        amount = request.form['amount']

        # Create a new FundraisingDonation object and insert it into the database
        new_donation = FundraisingDonation(UserID=userID, CampaignID=campaignID, DonationDate=donationDate, Amount=amount)
        db.session.add(new_donation)
        db.session.commit()

        return redirect(url_for('success'))  # Redirect to a success page or any other page
    else:
        return render_template('fundraising_donation.html')

@app.route('/success')
def success():
    return 'Donation added successfully!'


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        new_entry = ContactFormEntry(name=name, email=email, message=message)
        db.session.add(new_entry)
        db.session.commit()
        
        flash('Your message has been submitted successfully!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')


# @app.route("/events")
# def events():
#     # campaigns = FundraisingCampaign.query.all()
#     return render_template(redirect)



@app.route("/Events")
def Events():
    campaigns = FundraisingCampaign.query.all()
    return render_template("Events.html", campaigns=campaigns)


@app.route("/reported_areas")
@login_required
def reported_areas():
    reported_areas = ReportedArea.query.all()
    return render_template('reported_areas.html', reported_areas=reported_areas)


@app.route("/add_reported_area", methods=['GET', 'POST'])
@login_required
def add_reported_area():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        report_date = request.form.get('report_date')
        area_description = request.form.get('area_description')
        print(user_id,report_date,area_description)
        # print((UserID=user_id, ReportDate=report_date, AreaDescription=area_description))
        new_reported_area = ReportedArea(UserID=user_id, ReportDate=report_date, AreaDescription=area_description)
        db.session.add(new_reported_area)
        db.session.commit()

        flash("Reported area added successfully", "success")
        return redirect(url_for('reported_areas'))

    return render_template('add_reported_area.html')



@app.route("/join_us")
def join_us():
    # Add logic here if needed
    return render_template("join_us.html")



@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "primary")
    return redirect(url_for('home'))



@app.route("/service")
def service():
    # Add logic here if needed
    return render_template("service.html")

# SMTP MAIL SERVER SETTINGS

# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME=params['gmail-user'],
#     MAIL_PASSWORD=params['gmail-password']
# )
# mail = Mail(app)




# @app.route("/")
# def home():
#     # a=User.query.all()
#     # print(a)
#     # return "<p>This is for testing purposesss</p>"
#     # try:
#     #     User.query.all()
#     #     return 'My db is connected'
#     # except:
#     #     return 'my db is not connected'

#     return render_template('index.html')


# @app.route("/login" ,methods=['POST','GET'])
# def login():
#     if request.method=='POST':
#         email=request.form.get('email')
#         password=request.form.get('psw')
#         print(email,password)
#         user=Credentials.query.filter_by(email=email).first()

#         if user and password == user.password:
#             if password == user.password:
#                 login_user(user)
#                 flash("Login Success","primary")
#                 return redirect(url_for('home'))
#         else:
#             flash("invalid credentials","danger")
#             return render_template('login.html')  
#         #         print('login success')
#         #         login_user(user)
#         #         # return("Login Success","primary")
#         #         return render_template('index.html')
#         # else:
#         #     # flash("invalid credentials","danger")
#         #     return render_template('login.html')    
                





#     return render_template('login.html')
#     return render_template('login.html')

# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("Logged out successfully", "primary")
#     return redirect(url_for('home'))



# @app.route("/test")
# def test():
#     return "<p>This is for testing purposesss</p>"

# @app.route("/home")
# def home1():
#     return redirect(url_for('home'))


# @app.route("/service_success",methods=['GET', 'POST'])
# def service_success():
#     return render_template('service_success.html')

# @app.route("/product")
# def product():
#     product= Product.query.all()
#     print(product)
#     return render_template('product.html', products=product)

# # @app.route("/service",methods=['POST','GET'])
# # def service():
# #     service= Service.query.all()
# #     return render_template('service.html', services=service)



# @app.route('/add_to_service_cart', methods=['POST'])
# @login_required
# def add_to_service_cart():
#     service_id = request.form.get('service_id')
#     service = Service.query.get(service_id)
#     if service:
#         # Check if the service is already in the cart
#         cart_item = ServiceCart.query.filter_by(user_id=current_user.User_id, service_id=service_id).first()
#         if cart_item:
#             # If the service is already in the cart, update its quantity
#             print("Service already in cart")
#             # cart_item.quantity += 1
#         else:
#             # If the service is not in the cart, add it to the cart
#             cart_item = ServiceCart(user_id=current_user.User_id, service_id=service_id)
#             db.session.add(cart_item)

#         db.session.commit()
#         flash('Service added to cart successfully', 'success')
#     return redirect(url_for('service_cart'))

# @app.route('/remove_from_service_cart', methods=['POST'])
# @login_required
# def remove_from_service_cart():
#     service_id = request.form.get('service_id')
#     service = Service.query.get(service_id)
#     if service:
#         # Check if the service is in the cart
#         cart_item = ServiceCart.query.filter_by(user_id=current_user.User_id, service_id=service_id).first()
#         if cart_item:
            
#             db.session.delete(cart_item)
#             db.session.commit()
#             print('Service removed from cart successfully', 'success')
#     return redirect(url_for('service_cart'))

# @app.route('/service_cart', methods=['GET', 'POST'])
# @login_required
# def service_cart():
#     if request.method == 'GET':
#         # Retrieve all cart items for the current user
#         cart_items = ServiceCart.query.filter_by(user_id=current_user.User_id).all()

#         # Fetch service details for each cart item
#         services = {}
#         for cart_item in cart_items:
#             service = Service.query.get(cart_item.service_id)
#             if service:
#                 services[cart_item.service_id] = service

#         # Render template with cart items, service details, and total order value
#         return render_template('service_cart.html', cart_items=cart_items, services=services)

#     elif request.method == 'POST':
#         # Handle form submission (if needed)
#         pass

# @app.route("/service", methods=['GET', 'POST'])
# def service():
#     services = Service.query.all()
#     return render_template('service.html', services=services)

# @app.route('/final_service')
# # @login_required
# def final_service():
#     # Retrieve the cart items from the ServiceCart table for the current user
#     user_id = current_user.User_id  # Assuming you have access to the current user
#     cart_items = ServiceCart.query.filter_by(user_id=user_id).all()

#     # Initialize lists to store ordered services and total price
#     ordered_services = []
#     total_price = 0

#     # Iterate through cart items and retrieve corresponding service details
#     for cart_item in cart_items:
#         service = Service.query.get(cart_item.service_id)
#         if service:
#             ordered_services.append(service)
#             total_price += service.Price

#     # Render the final order page with the order details
#     return render_template('final_service.html', ordered_services=ordered_services, total_price=total_price)




# @app.route('/confirm_service', methods=['POST','GET'])
# def confirm_service():
#     user_id = current_user.User_id
#     # Retrieve the cart items from the ServiceCart table
#     cart_items = ServiceCart.query.all()

#     # Check if there are any cart items
#     if cart_items:
#         try:
#             # Create ServiceOrder entries for each cart item
#             for cart_item in cart_items:
#                 max_order_id = db.session.query(func.max(ServiceOrder.Order_ID)).scalar()

#             # If there are no existing orders, set max_order_id to 1
#                 if max_order_id is None:
#                     max_order_id = 1
#                 else:
#                     # Increment the maximum order ID by 1
#                     max_order_id = int(max_order_id) + 1


#                 service_order = ServiceOrder(
#                     Order_ID=max_order_id,
#                     Service_ID=cart_item.service_id,
#                     Order_Date=date.today(),
#                     Status='Pending',
#                     User_ID=user_id
#                 )
#                 db.session.add(service_order)
            
#             # Commit changes to the database
#             db.session.commit()

#             # Clear the ServiceCart table after confirming the order
#             ServiceCart.query.delete()
#             db.session.commit()

#             print('Service order confirmed successfully', 'success')
#         except Exception as e:
#             print('Error confirming service order. Please try again.', 'danger')
#             db.session.rollback()
#             print(str(e))
#     else:
#         print('No services in the cart to confirm', 'warning')

#     # Redirect to the final order page
#     return redirect(url_for('service_success'))



# @app.route('/previous_services', methods=['GET'])
# @login_required
# def previous_services():
#     # Retrieve all previous orders for the current user
#     previous_orders = ServiceOrder.query.filter_by(User_ID=current_user.User_id).all()

#     # Initialize lists to store ordered services and their corresponding statuses
#     ordered_services = []
#     statuses = []

#     # Iterate through previous orders and retrieve corresponding service details and statuses
#     for order in previous_orders:
#         service = Service.query.get(order.Service_ID)
#         if service:
#             ordered_services.append(service)
#             statuses.append(order.Status)

#     # Combine ordered services and statuses into a list of tuples
#     ordered_services_with_status = zip(ordered_services, statuses)

#     # Render the previous orders page with the ordered services and their statuses
#     return render_template('previous_services.html', ordered_services_with_status=ordered_services_with_status)


# # @app.route('/add_to_service_cart', methods=['POST'])
# # def add_to_service_cart():
# #     if request.method == 'POST':
# #         user_id = request.form.get('user_id')
# #         user_id = current_user.User_id

# #         service_id = request.form.get('service_id')
# #         # Check if the service is already in the cart
# #         existing_item = ServiceCart.query.filter_by(user_id=user_id, service_id=service_id).first()
# #         if existing_item:
# #             flash('Service is already in the cart', 'info')
# #         else:
# #             # Add service to the cart
# #             new_item = ServiceCart(user_id=user_id, service_id=service_id)
# #             db.session.add(new_item)
# #             db.session.commit()
# #             flash('Service added to cart successfully', 'success')
# #     return redirect(url_for('service_cart'))

# # @app.route('/service_cart')
# # def service_cart():
# #     user_id = request.args.get('user_id')
# #     user_id = current_user.User_id

# #     if user_id:
# #         # Retrieve cart items for the user
# #         cart_items = ServiceCart.query.filter_by(user_id=user_id).all()
# #         return render_template('service_cart.html', cart_items=cart_items)
# #     else:
# #         # cart_items = ServiceCart.query.filter_by(user_id=user_id).all()
# #         # return render_template('service_cart.html', cart_items=cart_items)
# #         flash('User ID is required to view the service cart', 'danger')
# #         return redirect(url_for('service_cart'))



# # @app.route('/contact', methods=['POST'])
# # def submit_contact_form():
# #     if request.method == 'POST':
# #         name = request.form['name']
# #         email = request.form['email']
# #         message = request.form['message']
        
# #         # Create a new ContactFormEntry object and add it to the database session
# #         entry = ContactFormEntry(name=name, email=email, message=message)
# #         db.session.add(entry)
# #         db.session.commit()
        
# #         return 'Form submitted successfully!' 

# @app.route('/contact', methods=['POST'])
# def submit_contact_form():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         message = request.form.get('message')
#         print(name,email,message)
        
#         try:
#             # Create a new ContactFormEntry object and add it to the database session
#             entry = ContactFormEntry(name=name, email=email, message=message)
#             db.session.add(entry)
#             db.session.commit()
#             return 'Form submitted successfully!'
#         except Exception as e:
#             # Rollback the transaction in case of any error
#             db.session.rollback()
#             return f'Error occurred: {str(e)}'




# # Route to render the contact form page
# @app.route('/contact', methods=['GET'])
# def contact():
#     return render_template('contact.html')

# # if __name__ == '__main__':
# #     db.create_all()
# #     app.run(debug=True)

# # @app.route('/cart', methods=['POST','GET'])
# # def cart():
# #     if request.method == 'GET':
# #         product_id = request.form.get('product_id')
# #         # Add product to cart
# #         # For example:
# #         # Check if the product is already in the cart
# #         cart_item = Cart.query.filter_by(User_id=current_user.User_id, Product_ID=product_id).first()
# #         if cart_item:
# #             # If the product is already in the cart, update its quantity
# #             cart_item.Quantity += 1
# #         else:
# #             # If the product is not in the cart, add it to the cart
# #             cart_item = Cart(User_id=current_user.User_id, Product_ID=product_id, Quantity=1)
# #             db.session.add(cart_item)
# #         db.session.commit()
# #         return redirect(url_for('product'))


# @app.route('/user')
# @login_required
# def user():
#     # Assuming you have a function to retrieve user details from the database
#     user = User.query.filter_by(User_id=current_user.User_id).first()
#     return render_template('user.html', user=user)


# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     product_id = request.form.get('product_id')
#     product = Product.query.get(product_id)
#     if product:
#         if product.Quantity > 0:
#             # Check if the product is already in the cart
#             cart_item = Cart.query.filter_by(User_id=current_user.User_id, Product_ID=product_id).first()
#             if cart_item:
#                 # If the product is already in the cart, update its quantity
#                 cart_item.Quantity += 1
#             else:
#                 # If the product is not in the cart, add it to the cart
#                 cart_item = Cart(User_id=current_user.User_id, Product_ID=product_id, Quantity=1)
#                 db.session.add(cart_item)
#             # Decrease product quantity by 1
#             product.Quantity -= 1
#             db.session.commit()
#             print('Product added to cart successfully', 'success')
#         else:
#             print('Product out of stock', 'danger')
#     return redirect(url_for('product'))

# @app.route('/remove_from_cart', methods=['POST'])
# @login_required
# def remove_from_cart():
#     product_id = request.form.get('product_id')
#     product = Product.query.get(product_id)
#     if product:
#         # Check if the product is in the cart
#         cart_item = Cart.query.filter_by(User_id=current_user.User_id, Product_ID=product_id).first()
#         if cart_item:
#             # Reduce product quantity in the cart by 1
#             if cart_item.Quantity > 1:
#                 cart_item.Quantity -= 1
#             else:
#                 # If quantity is already 1, delete the cart item
#                 db.session.delete(cart_item)
#             # Increase product quantity by 1
#             product.Quantity += 1
#             db.session.commit()
#             print('Product removed from cart successfully', 'success')
#     return redirect(url_for('cart'))

# @app.route('/remove_from_cart_inProductPage', methods=['POST'])
# @login_required
# def remove_from_cart_inProductPage():
#     product_id = request.form.get('product_id')
#     product = Product.query.get(product_id)
#     if product:
#         # Check if the product is in the cart
#         cart_item = Cart.query.filter_by(User_id=current_user.User_id, Product_ID=product_id).first()
#         if cart_item:
#             # Reduce product quantity in the cart by 1
#             if cart_item.Quantity > 1:
#                 cart_item.Quantity -= 1
#             else:
#                 # If quantity is already 1, delete the cart item
#                 db.session.delete(cart_item)
#             # Increase product quantity by 1
#             product.Quantity += 1
#             db.session.commit()
#             flash('Product removed from cart successfully', 'success')
#     return redirect(url_for('product'))



# @app.route('/cart', methods=['POST','GET'])
# @login_required
# def cart():
#     if request.method == 'POST':
#         product_id = request.form.get('product_id')
#         if product_id:
#             # Add product to cart
#             # For example:
#             # Check if the product is already in the cart
#             cart_item = Cart.query.filter_by(User_id=current_user.User_id, Product_ID=product_id).first()
#             if cart_item:
#                 # If the product is already in the cart, update its quantity
#                 cart_item.Quantity += 1
#             else:
#                 # If the product is not in the cart, add it to the cart
#                 cart_item = Cart(User_id=current_user.User_id, Product_ID=product_id, Quantity=1)
#                 db.session.add(cart_item)
#             db.session.commit()
#             print('Product added to cart successfully', 'success')
#             return redirect(url_for('product'))
#         else:
#             print('Invalid product ID', 'danger')
#             return redirect(url_for('product'))  # Redirect to the product page or any appropriate page
#     elif request.method == 'GET':
#         # Handle GET request if needed
#         cart_items = Cart.query.filter_by(User_id=current_user.User_id).all()
    
#         # List to store cart items and their corresponding product details
#         items_with_details = []
    
#         # Loop through each cart item and retrieve product details
#         for cart_item in cart_items:
#             product = Product.query.get(cart_item.Product_ID)
#             print(cart_item.Quantity)
#             a=cart_item.Quantity
#             if product:
#                 items_with_details.append({'product': product, 'quantity': a})
    
#         return render_template('cart.html', cart_items=items_with_details)





# @app.route('/final_order', methods=['GET', 'POST'])
# @login_required  # Requires the user to be logged in
# def final_order():
#     # Retrieve all cart items for the current user
#     cart_items = Cart.query.filter_by(User_id=current_user.User_id).all()
    
#     # Fetch product details for each cart item
#     products = {}
#     for cart_item in cart_items:
#         product = Product.query.get(cart_item.Product_ID)
#         if product:
#             products[cart_item.Product_ID] = product
    
#     # Calculate total order value
#     total_price = sum(products[cart_item.Product_ID].Price * cart_item.Quantity for cart_item in cart_items)
    
#     # Render template with cart items, product details, and total order value
#     return render_template('final_order.html', cart_items=cart_items, products=products, total_price=total_price)


# @app.route('/confirm_order', methods=['GET', 'POST'])
# @login_required
# def confirm_order():
#     # Retrieving all cart items for the current user
#     cart_items = Cart.query.filter_by(User_id=current_user.User_id).all()
#     # abc=ProductOrder.queryfilter_by(max()).all()

    
#     if request.method == 'POST':
#         # Creating ProductOrder instances for each cart item
#         for cart_item in cart_items:
#             max_order_id = db.session.query(func.max(ProductOrder.Order_ID)).scalar()
#             max_order_id=int(max_order_id)+1

#             product_order = ProductOrder(
#                 Order_ID= max_order_id,
#                 Status='Pending',
#                 Quantity=cart_item.Quantity,
#                 Order_Date=date.today(),
#                 User_ID=current_user.User_id,
#                 product_id=cart_item.Product_ID
#             )
#             db.session.add(product_order)
#             db.session.delete(cart_item)  # Remove the cart item after creating the order
        
#         db.session.commit()
#         print('Order placed successfully', 'success')
#         return redirect(url_for('view_order'))  # Redirect to a view orders page after placing the order
    
#     # Fetching product details for each cart item
#     products = {}
#     for cart_item in cart_items:
#         product = Product.query.get(cart_item.Product_ID)
#         if product:
#             products[cart_item.Product_ID] = product
    
#     # Calculating total order value
#     total_price = sum(products[cart_item.Product_ID].Price * cart_item.Quantity for cart_item in cart_items)
    
#     # Rendering the confirm order page
#     return render_template('confirm_order.html', cart_items=cart_items, products=products, total_price=total_price)


# # def confirm_order():
# #     # Retrieve all cart items for the current user
# #     cart_items = Cart.query.filter_by(User_id=current_user.User_id).all()
    
# #     # Fetch product details for each cart item
# #     products = {}
# #     for cart_item in cart_items:
# #         product = Product.query.get(cart_item.Product_ID)
# #         if product:
# #             products[cart_item.Product_ID] = product
    
# #     # Calculate total order value
# #     total_price = sum(products[cart_item.Product_ID].Price * cart_item.Quantity for cart_item in cart_items)
    
# #     # Render the confirm order page
# #     # return render_template('confirm_order.html', cart_items=cart_items, products=products, total_price=total_price)
# #     return 'Your order placed successfully'


# @app.route("/view_order",methods=['GET', 'POST'])
# @login_required
# def view_order():
#     if request.method=='POST':
#         user_orders = ProductOrder.query.filter_by(User_ID=current_user.User_id).all()
    
#         # Create a list to store order details with product name
#         orders_with_product_name = []
        
#         # Iterate through each order and fetch the associated product details
#         for order in user_orders:
#             product = Product.query.get(order.product_id)
#             if product:
#                 orders_with_product_name.append({
#                     'order': order,
#                     'product_name': product.Name
#                 })
        
#         # Render the template with order details and associated product names
#         message = 'Order placed successfully'  # This message can come from the logic after placing an order
#         print("Here are your previous orders", "success")
#         return render_template('view_order1.html', orders=orders_with_product_name, message=message) 
#     # Retrieve all orders for the current user
#     else:
#         user_orders = ProductOrder.query.filter_by(User_ID=current_user.User_id).all()
        
#         # Create a list to store order details with product name
#         orders_with_product_name = []
        
#         # Iterate through each order and fetch the associated product details
#         for order in user_orders:
#             product = Product.query.get(order.product_id)
#             if product:
#                 orders_with_product_name.append({
#                     'order': order,
#                     'product_name': product.Name
#                 })
        
#         # Render the template with order details and associated product names
#         return render_template('view_order.html', orders=orders_with_product_name)
    


# # @app.route("/admin/inventory")
# # def admin_inventory():
# #     # Fetch products from the Cart
# #     cart_products = Cart.query.all()

# #     # Create a dictionary to store product IDs and their corresponding names
# #     product_names = {}
# #     for cart_item in cart_products:
# #         product = Product.query.get(cart_item.Product_ID)
# #         if product:
# #             product_names[cart_item.Product_ID] = product.Name

# #     # Fetch available products from the Product table
# #     available_products = Product.query.all()

# #     # Calculate product quantities in cart
# #     product_quantities = []
# #     for product in available_products:
# #         total_quantity = 0
# #         for cart_item in cart_products:
# #             if cart_item.Product_ID == product.Product_ID:
# #                 total_quantity += cart_item.Quantity
# #         product_quantities.append(total_quantity)

# #     return render_template("admin_inventory.html", available_products=available_products, cart_products=cart_products, product_names=product_names, product_quantities=product_quantities)
# @app.route("/admin/inventory", methods=['GET', 'POST'])
# def admin_inventory():
#     if request.method == 'POST':
#         # Update product quantities based on admin input
#         available_products = Product.query.all()
#         for product in available_products:
#             new_quantity_str = request.form.get(f'quantity_{product.Product_ID}')
#             if new_quantity_str:
#                 try:
#                     new_quantity = int(new_quantity_str)
#                     if new_quantity >= 0:
#                         # Update the quantity in the database
#                         product.Quantity = new_quantity
#                         db.session.commit()
#                 except ValueError:
#                     # Handle invalid input (non-integer)
#                     pass

#     # Fetch products from the Cart
#     cart_products = Cart.query.all()

#     # Create a dictionary to store product IDs and their corresponding names
#     product_names = {}
#     for cart_item in cart_products:
#         product = Product.query.get(cart_item.Product_ID)
#         if product:
#             product_names[cart_item.Product_ID] = product.Name

#     # Fetch available products from the Product table
#     available_products = Product.query.all()

#     # Calculate product quantities in cart
#     product_quantities = []
#     for product in available_products:
#         total_quantity = 0
#         for cart_item in cart_products:
#             if cart_item.Product_ID == product.Product_ID:
#                 total_quantity += cart_item.Quantity
#         product_quantities.append(total_quantity)

#     return render_template("admin_inventory.html", available_products=available_products, cart_products=cart_products, product_names=product_names, product_quantities=product_quantities)

# @app.route("/product_order_audit")
# def product_order_audit():
#     # Fetch audit trail records for product orders
#     audit_records = ProductOrderAudit.query.all()
#     return render_template("product_order_audit.html", audit_records=audit_records)


app.run(debug=True)



# class User(db.Model):
#     User_id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50), nullable=True, default=None)
#     last_name = db.Column(db.String(50), nullable=True, default=None)
#     dd = db.Column(db.Integer, nullable=True, default=None)
#     mm = db.Column(db.Integer, nullable=True, default=None)
#     yyyy = db.Column(db.Integer, nullable=True, default=None)
#     Email = db.Column(db.String(100), nullable=True, default=None)
#     house_number = db.Column(db.String(45), nullable=True, default=None)
#     street_name = db.Column(db.String(100), nullable=True, default=None)
#     apt_number = db.Column(db.String(100), nullable=True, default=None)
#     city = db.Column(db.String(45), nullable=True, default=None)
#     state = db.Column(db.String(45), nullable=True, default=None)
#     pincode = db.Column(db.Integer, nullable=True, default=None)

#     # def __repr__(self):
#     #     return f"User('{self.User_id}', '{self.first_name}', '{self.last_name}', '{self.Email}')"


# class Credentials(UserMixin,db.Model):
#     User_id = db.Column(db.Integer, db.ForeignKey('user.User_id'), primary_key=True)
#     email = db.Column(db.String(100), nullable=False)
#     password = db.Column(db.String(100))
#     def get_id(self):
#         return str(self.User_id)



# class Pets(db.Model):
#     Pet_ID = db.Column(db.Integer, primary_key=True)
#     Name = db.Column(db.String(45), nullable=True, default=None)
#     Breed = db.Column(db.String(45), nullable=True, default=None)
#     Age = db.Column(db.Integer, nullable=True, default=None)
#     Size = db.Column(db.String(45), nullable=True, default=None)
#     Type = db.Column(db.String(45), nullable=True, default=None)

# class UserPets(db.Model):
#     user_pet_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.User_id'), nullable=False)
#     pet_id = db.Column(db.Integer, db.ForeignKey('pets.Pet_ID'), nullable=False)
#     acquisition_date = db.Column(db.Date)

# class Service(db.Model):
#     Service_ID = db.Column(db.Integer, primary_key=True)
#     Name = db.Column(db.String(45), nullable=True, default=None)
#     Price = db.Column(db.Integer, nullable=True, default=None)
#     Duration = db.Column(db.Integer, nullable=True, default=None)
#     Pet_Type = db.Column(db.String(45), nullable=True, default=None)

# class Employee(db.Model):
#     Employee_ID = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(45), nullable=True, default=None)
#     last_name = db.Column(db.String(45), nullable=True, default=None)
#     dd = db.Column(db.Integer, nullable=True, default=None)
#     mm = db.Column(db.Integer, nullable=True, default=None)
#     yyyy = db.Column(db.Integer, nullable=True, default=None)
#     Email = db.Column(db.String(100), nullable=True, default=None)
#     Experience = db.Column(db.Integer, nullable=True, default=None)
#     Status = db.Column(db.String(45), nullable=True, default=None)
#     Rating = db.Column(db.Integer, nullable=True, default=None)



# class Product(db.Model):
#     Product_ID = db.Column(db.Integer, primary_key=True)
#     Name = db.Column(db.String(50), nullable=True, default=None)
#     Brand = db.Column(db.String(45), nullable=True, default=None)
#     Description = db.Column(db.String(100), nullable=True, default=None)
#     Rating = db.Column(db.Integer, nullable=True, default=None)
#     Product_Type = db.Column(db.String(45), nullable=True, default=None)
#     Pet_Category = db.Column(db.String(45), nullable=True, default=None)
#     Quantity = db.Column(db.Integer, nullable=True, default=None)
#     Price = db.Column(db.Integer, nullable=True, default=None)
#     # orders = relationship("ProductOrder", back_populates="Product")


# class ProductOrder(Base,db.Model):
#     ___tablename___ = 'ProductOrder'
#     ___tablename___ = 'product_order'


#     Order_ID = Column(Integer, primary_key=True)
#     Status = Column(String(45), nullable=True, default='Pending')
#     Quantity = Column(Integer, nullable=False)
#     Order_Date = Column(Date, default=date.today())
#     User_ID = Column(Integer, ForeignKey('user.User_id'), nullable=False)
#     product_id = Column(Integer, ForeignKey('product.Product_ID'), nullable=False)

#     # # Define relationships
#     # user = relationship("User", back_populates="orders")
#     # product = relationship("Product", back_populates="orders")



# class PaymentAndHistory(db.Model):
#     Payment_ID = db.Column(db.Integer, primary_key=True)
#     Amount = db.Column(db.Integer, nullable=True, default=None)
#     Payment_mode = db.Column(db.String(100), nullable=True, default=None)
#     Order_type = db.Column(db.String(100), nullable=True, default=None)
#     Payment_Date = db.Column(db.String(10), nullable=True, default=None)
#     Product_Order_ID = db.Column(db.Integer, db.ForeignKey('ProductOrder.Order_ID'), nullable=False)
#     Service_Order_ID = db.Column(db.Integer, db.ForeignKey('service.Service_ID'), nullable=False)

# class ProductReview(db.Model):
#     review_ID = db.Column(db.Integer, primary_key=True)
#     Product_ID = db.Column(db.Integer, db.ForeignKey('product.Product_ID'), nullable=False)
#     User_id = db.Column(db.Integer, db.ForeignKey('user.User_id'), nullable=False)
#     Rating = db.Column(db.Integer, nullable=True, default=None)
#     Date = db.Column(db.String(10), nullable=True, default=None)
#     Description = db.Column(db.String(100), nullable=True, default=None)

# class EmployeeService(db.Model):
#     employee_service_id = db.Column(db.Integer, primary_key=True)
#     employee_id = db.Column(db.Integer, db.ForeignKey('employee.Employee_ID'), nullable=False)
#     service_id = db.Column(db.Integer, db.ForeignKey('service.Service_ID'), nullable=False)

# class Wallet(db.Model):
#     User_id = db.Column(db.Integer, db.ForeignKey('user.User_id'), primary_key=True)
#     Wallet_id = db.Column(db.Integer)
#     Amount = db.Column(db.Float)

# class Cart(db.Model):
#     User_id = db.Column(db.Integer, db.ForeignKey('user.User_id'), primary_key=True)
#     Product_ID = db.Column(db.Integer, db.ForeignKey('product.Product_ID'), primary_key=True)
#     Quantity = db.Column(db.Integer)

# # class ServiceOrder(db.Model):
# #     Order_ID = db.Column(db.Integer, primary_key=True)
# #     Status = db.Column(db.String(45), nullable=False)
# #     dd = db.Column(db.Integer, nullable=False)
# #     mm = db.Column(db.Integer, nullable=False)
# #     yyyy = db.Column(db.Integer, nullable=False)

# class ServiceOrder(db.Model):
#     ___tablename___ = 'service_order'

#     Order_ID = db.Column(db.Integer, primary_key=True)
#     Service_ID = db.Column(db.String(45), default=None)
#     Order_Date = db.Column(db.Date)
#     Status = db.Column(db.String(45), default='Pending')
    
    
#     User_ID = Column(Integer, ForeignKey('user.User_id'), nullable=False)


# class ProductOrderAudit(db.Model):
#     ___tablename___ = 'product_order_audit'

#     audit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     order_id = db.Column(db.Integer)
#     operation_type = db.Column(db.String(10))
#     operation_timestamp = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
#     user_id = db.Column(db.Integer)
#     details = db.Column(db.Text)


# class ContactFormEntry(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), nullable=False)
#     message = db.Column(db.Text, nullable=False)

# class ServiceCart(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.User_id'), nullable=False)
#     service_id = db.Column(db.Integer, db.ForeignKey('service.Service_ID'), nullable=False)

#     def __repr__(self):
#         return f"<ServiceCart(user_id={self.user_id}, service_id={self.service_id})>"




