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




app.run(debug=True)


