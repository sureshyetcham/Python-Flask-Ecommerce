from flask import Blueprint, render_template, request,flash,redirect
from .models import Customer
from .import db
from .forms import PasswordChangeForm
from flask_login import login_user,login_required,logout_user


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')
        customer = Customer.query.filter_by(email=email).first()
        if customer:
            if customer.verify_password(password=password):
                login_user(customer)
                flash('Login Successful!')
                return redirect('/')
            else:
                flash('Invalid Password')
        else:
            flash('Email does not exist')

    return render_template('login.html')



@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():

    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if password1 == password2:
            new_customer = Customer()
            new_customer.email = email
            new_customer.username = username
            new_customer.password = password2

            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('Account Created Successfully, You can now Login')
                return redirect('/login')
            except Exception as e:
                print(e)
                flash('Account Not Created!!, Email already exists')

        print("Username:", username)
        print("Email:", email)
        print("Password:", password1)
        print("Confirm Password:", password2)


        # return "Signup Form Submitted"

    return render_template('signup.html')

@auth.route('/logout',methods=['GET', 'POST'])
@login_required
def logout():

    logout_user()
    flash('Logged out successfully!')

    return redirect('/login')


@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    print(customer_id)
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
                return redirect(f'/profile/{customer.id}')
            else:
                flash('New Passwords do not match!!')

        else:
            flash('Current Password is Incorrect')

    return render_template('change_password.html', form=form)


