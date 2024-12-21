from flask import Blueprint, render_template, flash, redirect, request, url_for
from .forms import LoginForm, SignUpForm, PasswordChangeForm
from .models import Customer
from .import db
from flask_login import login_user, login_required, logout_user
import random
import smtplib
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


auth = Blueprint('auth', __name__)

# OTP Generation and Sending Email Utility
def send_otp(email, otp):
    try:
        # Replace with your email details
        sender_email = "your_email@gmail.com"
        sender_password = "your_password"
        recipient_email = email
        
        # Create the email content
        subject = "Your OTP for Signup"
        body = f"Your OTP is {otp}. It will expire in 5 minutes."
        
        message = f"Subject: {subject}\n\n{body}"
        
        # Send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message)
            print("OTP sent successfully!")
    except Exception as e:
        print(f"Error sending OTP: {e}")


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    otp = None
    otp_expiry = None
    
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data
        
        if password1 == password2:
            # Check if the email already exists
            existing_customer = Customer.query.filter_by(email=email).first()
            if existing_customer:
                flash('Email already exists!', 'danger')
                return redirect(url_for('auth.sign_up'))
            
            # Generate OTP and expiry time
            otp = random.randint(100000, 999999)
            otp_expiry = datetime.utcnow() + timedelta(minutes=5)  # OTP expires in 5 minutes
            
            # Send OTP to the user's email
            send_otp(email, otp)

            # Store OTP and expiry time in the session (or database for persistence)
            session['otp'] = otp
            session['otp_expiry'] = otp_expiry
            session['email'] = email
            flash('OTP sent to your email. Please verify within 5 minutes.', 'info')
            return redirect(url_for('auth.verify_otp'))
        
        else:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.sign_up'))
    
    return render_template('signup.html', form=form)

# OTP Verification Route
@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'otp' not in session:
        flash('OTP expired or not generated', 'danger')
        return redirect(url_for('auth.sign_up'))
    
    otp = session['otp']
    otp_expiry = session['otp_expiry']
    email = session['email']
    
    if datetime.utcnow() > otp_expiry:
        flash('OTP has expired, please request a new one', 'danger')
        return redirect(url_for('auth.sign_up'))
    
    if request.method == 'POST':
        entered_otp = request.form['otp']
        
        if str(otp) == entered_otp:
            # Proceed with account creation
            new_customer = Customer(email=email, username=request.form['username'], password=request.form['password1'])
            db.session.add(new_customer)
            db.session.commit()
            flash('Account Created Successfully, You can now Login', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP', 'danger')
            return redirect(url_for('auth.verify_otp'))
    
    return render_template('verify_otp.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        customer = Customer.query.filter_by(email=email).first()

        if customer:
            if customer.verify_password(password=password):
                login_user(customer)
                return redirect('/')
            else:
                flash('Incorrect Email or Password')


        else:
            flash('Account does not exist please Sign Up')

    return render_template('login.html', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    return redirect('/')


@auth.route('/profile/<int:customer_id>') #profile
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    print('Customer ID:, customer_id')
    return render_template('profile.html', customer=customer)


@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):
            if new_password == confirm_new_password:
                customer.password = confirm_new_password 
                db.session.commit()
                flash('Password Updated Successfully')
                return redirect(f'/profile/{customer_id}')
            else:
                flash('New Password does not match!!!')
        else:
            flash('Current Password is Incorrect')
    
    return render_template('change_password.html', form=form)
