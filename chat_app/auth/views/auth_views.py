from flask import Blueprint, render_template, request, redirect, url_for, flash , jsonify,current_app
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from chat_app import db, login_manager, mail,bcrypt
from Models.models import User
from flask_jwt_extended  import create_access_token
from chat_app.auth.form import RegistrationForm,LoginForm,RequestResetForm,ResetPasswordForm

auth_views_module = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates')



@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@auth_views_module.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        current_app.logger.info('Attempt to login by user with email: %s', form.email.data)
        usr = User.query.filter_by(email=form.email.data).first()

        if not usr or not bcrypt.check_password_hash(usr.password, form.password.data):
            current_app.logger.warning('Incorrect login attempt for email: %s', form.email.data)
            flash(u"Incorrect Email or Password", "danger")
            return redirect(url_for('auth.login'))

        access_token = create_access_token(identity=usr.id)
        response = jsonify({"message": "Successfully Signed in", "access_token": access_token})
        login_user(usr)
        return response, 200  
    #     return redirect('/')
    return render_template('auth/login.html',title='Register',form=form)

@auth_views_module.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if request.method == 'POST':
        current_app.logger.info('Signup attempt for email: %s', form.email.data)
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        usr = User.query.filter_by(email=form.email.data).first()

        if usr:
            current_app.logger.warning('Signup attempt with existing email: %s', form.email.data)
            flash(u"Email already exists..!", "danger")
            return redirect(url_for('auth.signup'))

        new_usr = User(username=form.name.data, email=form.email.data, password=hashed_pass,status=1)
        db.session.add(new_usr)
        db.session.commit()
        current_app.logger.info('New user registered with email: %s', form.email.data)
        flash(u"Successfully signed up, Sign in to continue", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/sign-up.html',title='Sign In',form=form)



@auth_views_module.route("/logout")
@login_required
def logout():
    logout_user()
    flash(u"Successfully Signed Out", "info")
    return redirect(url_for('auth.login'))




def send_password_reset_email(user):
    token = user.get_password_reset_token()
    msg = Message("Password Reset Request",
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Visit the following link to reset your password:
    {url_for('auth.reset_password', token=token, _external=True)}
    If you did not make this request then simply ignore this email and nothing will be changed.
    '''
    mail.send(msg)


@auth_views_module.route("/forgotpassword", methods=['GET', 'POST'])
def forgot_password():
    form = RequestResetForm()

    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            current_app.logger.warning('Password reset requested for non-existing email: %s', form.email.data)
            flash('Incorrect email!<br>Try again', "danger")
            return redirect(url_for('auth.forgot_password'))
        send_password_reset_email(user)
        current_app.logger.info('Password reset requested for user: %s', form.email.data)
        flash('An email has been sent to this address with instruction to reset your password.', "info")
        return redirect(url_for('auth.login'))
    return render_template('auth/forgotpassword.html',title='Forgot Password', form=form)


@auth_views_module.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_password_reset_token(token)
    if not user:
        current_app.logger.error('Password reset with invalid or expired token')
        flash('Invalid or Expired link!<br>Resubmit email', "danger")
        return redirect(url_for('auth.forgot_password'))
    form = ResetPasswordForm()
    if request.method == 'POST':
        password = request.form['password']
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pass
        db.session.commit()
        current_app.logger.info('Password successfully reset for user: %s', user.email)
        flash('Your password has been updated', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/resetpassword.html', token=token)
