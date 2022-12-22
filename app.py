import psycopg2
from flask import Flask, render_template, request, flash, redirect, url_for, session

app = Flask(__name__)
app.config.update(
    SECRET_KEY='23r9ew0hgj8h5g87h5475g39fef83fh83rhf43feq'
)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        conn = psycopg2.connect(dbname='car_showroom', user='postgres',
                                password='12345', host='localhost', port=5432)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM car LIMIT 14')
                cars = cur.fetchall()
    return render_template('home.html', cars=cars)


@app.route('/registration/', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        if username and password and confirm_password and email and first_name and last_name and phone:
            if password == confirm_password:
                conn = psycopg2.connect(dbname='car_showroom', user='postgres',
                                        password='12345', host='localhost', port=5432)
                with conn:
                    with conn.cursor() as cur:
                        cur.execute('CALL add_client(%s,%s,%s,%s,%s,%s)',
                                    (first_name, last_name, phone, email, username, password))
                return redirect(url_for('login'))
            else:
                flash('Passwords do not match')
        else:
            flash('Fill in all fields, please')
    return render_template('registration.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'user_login' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            password_right = None
            user = None
            conn = psycopg2.connect(dbname='car_showroom', user='postgres',
                                    password='12345', host='localhost', port=5432)
            with conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT (password = crypt(%s, password)) AS password FROM client WHERE username = %s',
                                (password, username))
                    password_right = cur.fetchone()
                    cur.execute('SELECT * FROM client WHERE username = %s', (username,))
                    user = cur.fetchone()
            if password_right is not None:
                if password_right[0]:
                    session['user_login'] = True
                    session['user'] = user
                    return redirect(url_for('home'))
                else:
                    flash('Wrong password')
            else:
                flash('User does not exist')
    return render_template('login.html')


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    session.pop('user_login')
    session.pop('user')
    return redirect(url_for('home'))


@app.route('/employee_login/', methods=['GET', 'POST'])
def employee_login():
    if 'employee_login' in session:
        return redirect(url_for('employee_workspace'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            password_right = None
            employee = None
            conn = psycopg2.connect(dbname='car_showroom', user='postgres',
                                    password='12345', host='localhost', port=5432)
            with conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT (password = crypt(%s, password)) AS password FROM employee WHERE username = %s',
                                (password, username))
                    password_right = cur.fetchone()
                    cur.execute('SELECT * FROM client WHERE username = %s', (username,))
                    employee = cur.fetchone()
            if password_right is not None:
                if password_right[0]:
                    session['employee_login'] = True
                    session['employee'] = employee
                    return redirect(url_for('employee_workspace'))
                else:
                    flash('Wrong password')
            else:
                flash('User does not exist')
        else:
            flash('Fill in all fields, please')
    return render_template('employee_login.html')


@app.route('/employee_workspace/', methods=['GET', 'POST'])
def employee_workspace():
    return render_template('employee_workspace.html')


@app.route('/employee_logout/', methods=['GET', 'POST'])
def employee_logout():
    session.pop('employee_login')
    session.pop('employee')
    return redirect(url_for('employee_login'))


@app.route('/car_page/<int:car_no>/', methods=['GET', 'POST'])
def car_page(car_no):
    if request.method == 'GET':
        conn = psycopg2.connect(dbname='car_showroom', user='postgres',
                                password='12345', host='localhost', port=5432)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM car WHERE car_no = %s',
                            (car_no,))
                car = cur.fetchone()
    return render_template('car_page.html', car=car)


@app.route('/create_request/<int:car_no>/<int:client_no>/', methods=['GET', 'POST'])
def create_request(client_no, car_no):
    req = None
    if 'user_login' in session:
        if request.method == 'GET':
            if session.get('user')[0] == client_no:
                conn = psycopg2.connect(dbname='car_showroom', user='postgres',
                                        password='12345', host='localhost', port=5432)
                with conn:
                    with conn.cursor() as cur:
                        cur.execute('SELECT * FROM request WHERE car_no = %s AND client_no = %s',
                                    (car_no, client_no))
                        req = cur.fetchone()
                        if req is None:
                            cur.execute('CALL create_request(%s, %s)',
                                        (car_no, client_no))
            else:
                redirect(url_for('home'))
    else:
        redirect(url_for('login'))
    return render_template('request_page.html', req=req)


if __name__ == '__main__':
    app.run()
