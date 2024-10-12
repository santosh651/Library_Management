from flask import Flask, render_template, request, redirect, flash, session, url_for, make_response
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'library_management'

mysql = MySQL(app)

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=35)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful! You can now log in.', 'success')
        return redirect('/login')
    return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['username'] = username  # Use username as session key
            flash('Login successful!', 'success')
            return redirect('/')
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect('/login')

    username = session['username']
    
    # GET Request - Display Profile
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT organization_name, email, phone_number, student_id FROM users WHERE username = %s", [username])
        user_profile = cur.fetchone()
        cur.close()

        if user_profile:
            profile_data = {
                'organization_name': user_profile[0] or '',  # If None, show empty
                'email': user_profile[1] or '',
                'phone_number': user_profile[2] or '',
                'student_id': user_profile[3] or ''
            }
            return render_template('profile.html', profile=profile_data)
        else:
            flash('Profile not found.', 'danger')
            return redirect('/dashboard')

    # POST Request - Update Profile
    if request.method == 'POST':
        organization_name = request.form.get('organization_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        student_id = request.form.get('student_id')
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE users 
            SET organization_name = %s, email = %s, phone_number = %s, student_id = %s 
            WHERE username = %s
        """, (organization_name, email, phone_number, student_id, username))
        mysql.connection.commit()
        cur.close()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to the home page after updating

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        flash('You need to log in first.', 'danger')
        return redirect('/login')

# Home Redirect
@app.route('/')
def home():
    return redirect('/dashboard')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
