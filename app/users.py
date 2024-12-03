from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime

from .models.user import User
from .models.orders import Order
from flask import Blueprint

bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models.orders import Order

@bp.route("/user_home")
def user_home():
    user_id = current_user.id
    page = request.args.get('page', default=1, type=int)
    per_page = 5 

    # Fetch paginated orders
    orders = Order.get_all_orders(user_id, page, per_page)
    total_orders = Order.count_orders(user_id)
    total_pages = (total_orders + per_page - 1) // per_page

    return render_template("user_home.html", orders=orders, page=page, total_pages=total_pages)

@bp.route('/update_balance',  methods=['GET', 'POST'])
def update_balance():
    current_balance = float(User.get_balance(current_user.id))
    
    if request.method == 'POST':
        amt = float(request.form['amount'])
        action = request.form['action'] 
        
        if action == "withdraw":
            if amt <= current_balance:
                amt = amt * -1
            else:
                return render_template('update_balance.html', 
                                       error="Trying to withdraw amount greater than balance.")
            
        User.update_balance(current_user.id, amt)
        return redirect(url_for('users.update_balance'))
  
    return render_template('update_balance.html')

class UpdateForm(FlaskForm):
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    email = StringField('Email')
    address = StringField('Address')
    password = PasswordField('Password')
    password2 = PasswordField(
        'Repeat Password', validators=[EqualTo('password')])
    
    submit = SubmitField('Update')


@bp.route('/update_user_info', methods=['GET', 'POST'])
def update_user_info():
    user = User.get(current_user.id)

    form = UpdateForm()

    if request.method == 'POST' and form.validate_on_submit():
        firstname = form.firstname.data if form.firstname.data else user.firstname
        lastname = form.lastname.data if form.lastname.data else user.lastname
        email = form.email.data if form.email.data else user.email
        address = form.address.data if form.address.data else user.address
        password = form.password.data

        if email != user.email and email is not None and User.email_exists(email):
            flash("This email is already in use. Please choose a different one.")
            return render_template('update_user_info.html', title='Update Info', form=form)
        
        User.update_info(
                uid=current_user.id,
                firstname=firstname,
                lastname=lastname,
                email=email,
                address=address,
                password=password)
        
        flash('User info updated')
        return redirect(url_for('users.user_home'))

    return render_template('update_user_info.html', title='Update Info', form=form)


@bp.route('/user/<int:id>', methods=['GET'])
def user_public_view(id):
    user = User.get(id)
    if not user:
        return "User not found", 404
    return render_template('user_public_view.html', user=user)

@bp.route("/user_purchase_analytics/<int:uid>")
def user_purchase_analytics(uid):
    average = User.average_spent(uid)
    num_orders = Order.count_orders(uid)
    return render_template('user_purchase_analytics.html', uid=uid, average=average, num_orders=num_orders)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))
