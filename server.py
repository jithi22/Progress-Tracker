from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from sqlite3 import IntegrityError
import os
from AI.academics.predict import predict_with_model

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'a_default_secret_key')

# Function to create the "users" table if it doesn't exist
def create_users_table():
    conn = sqlite3.connect('access.db')
    cursor = conn.cursor()
    # cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call the function to create the table when the server starts
create_users_table()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']

        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('login'))

@app.route('/get_total_log_hours_per_day', methods=['POST'])
def get_total_log_hours_per_day():
    if 'username' in session:
        username = session['username']
        table_name = 'user_' + ''.join(filter(str.isalnum, username))
        target_date = request.json['date']

        conn = sqlite3.connect('access.db')
        cursor = conn.cursor()

        query = f"""
        SELECT DATE(date) as log_date, SUM(log_hour) as total_hours
        FROM {table_name}
        WHERE DATE(date) = DATE(?)
        GROUP BY DATE(date)
        """

        cursor.execute(query, (target_date,))
        total_hours = cursor.fetchone()

        conn.close()
        # print("total",total_hours)
        if total_hours and len(total_hours) >= 2:
            total_hours_dict = {'log_date': total_hours[0], 'total_hours': total_hours[1]}
        else:
            total_hours_dict = {'log_date': None, 'total_hours': 0}    

        return jsonify(total_hours_dict if total_hours else {'log_date': target_date, 'total_hours': 0})
    else:
        return jsonify({'error': 'User not logged in'}), 401

@app.route('/get_user_data')
def get_user_data():
    # print('session -->',session, session['username'])
    if 'username' in session:
        username = session['username']
        table_name = 'user_' + ''.join(filter(str.isalnum, username))

        conn = sqlite3.connect('access.db')
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        user_data = cursor.fetchall()

        conn.close()  
        return jsonify(user_data)
    else:
        return jsonify({'error': 'User not logged in'}), 401

@app.route('/process_user_data')
def process_user_data():
    tune_response = request.args.get('tune', 'false').lower() == 'true'
   
    if 'username' in session:
        username = session['username']
        table_name = 'user_' + ''.join(filter(str.isalnum, username))

        conn = sqlite3.connect('access.db')
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        user_data = cursor.fetchall()

        # Collect texts to predict
        texts_to_predict = [user[2] for user in user_data]
        # Predict in one go
        predictions = predict_with_model(texts_to_predict, tune=tune_response)

        # Dictionary to hold combined log hours for each unique prediction
        combined_data = {}

        for user, prediction in zip(user_data, predictions):
            log_hours = user[1]
            if prediction in combined_data:
                combined_data[prediction] += log_hours
            else:
                combined_data[prediction] = log_hours

            print(user[2], prediction)
        
        conn.close()  
        return jsonify(combined_data)
    else:
        return jsonify({'error': 'User not logged in'}), 401
    
@app.route('/get_current_user')
def get_current_user():
    username = session.get('username')
    if username:
        return jsonify(username=username)
    else:
        return jsonify(username=''), 404


@app.route('/logout')
def logout():
    # Clear the session to log the user out
    session.clear()

    # Redirect to the login page (or home page)
    return redirect(url_for('home'))

@app.route('/create_account', methods=['POST'])
def create_account():
    try:
        username = request.json['username']
        password = request.json['password']
        # Connect to your SQLite database and insert data
        conn = sqlite3.connect('access.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        re = cursor.fetchall()
        # print(re)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        result = jsonify({"status": "success", "message": "Account created"})
        # print("result is :",result) 
        return result 
    except IntegrityError as e:
        conn.rollback()
        error_message = str(e)
        return jsonify({"status": "error", "message": error_message}), 400
    except Exception as e:
        error_message = str(e)
        return jsonify({"status": "error", "message": error_message}), 500

def create_user_storage(username):
    conn = sqlite3.connect('access.db')
    cursor = conn.cursor()
    
    # Ensure username is safe to prevent SQL Injection
    table_name = 'user_' + ''.join(filter(str.isalnum, username))
    
    sql = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_hour FLOAT NOT NULL ,
            info TEXT,
            date DATE NOT NULL
        )
    '''
    cursor.execute(sql)
    
    conn.commit()
    conn.close()

@app.route('/login_account', methods=['POST'])
def login():
    try:
        username = request.json['username']
        password = request.json['password']
        
        # Here you can add the logic to check if the username and password match in the database
        # For example:
        conn = sqlite3.connect('access.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        # Dummy response for demonstration
        if user:
            session['username'] = user[1]
            # print('usr name--->',username, session['username'], user)
            create_user_storage(username)
            return jsonify({"status": "success", "message": "Login successful"})
        else:
            return jsonify({"status": "error", "message": "Invalid username or password"}), 401

    except Exception as e:
        error_message = str(e)
        return jsonify({"status": "error", "message": error_message}), 500



@app.route('/write_record', methods=['POST'])
def write_to_db():
    data = request.get_json()

    # Extract username and record from the POST data
    table_name = data.get('table')
    record = data.get('record')
    # print(table_name, record)
    if not table_name:
        return jsonify({"status": "error", "message": "No username provided"}), 400

    try:
        conn = sqlite3.connect('access.db')
        cursor = conn.cursor()

        # Assuming record is a dictionary like {'log_hour': 1.5, 'date_time': '2024-03-26 12:30:00'}
        columns = ', '.join(record.keys())
        placeholders = ', '.join(['?'] * len(record))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        cursor.execute(sql, list(record.values()))
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": "Record added successfully"})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500   
       
@app.route('/get_recent_records')
def get_recent_records():
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    username = session['username']
    table_name = 'user_' + ''.join(filter(str.isalnum, username))

    conn = sqlite3.connect('access.db')
    cursor = conn.cursor()

    # Get the last 15 records ordered by ID or date, depending on your table structure
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY date DESC LIMIT 10")
    records = cursor.fetchall()

    conn.close()
    return jsonify(records)

@app.route('/delete_record/<int:log_id>', methods=['DELETE'])
def delete_record(log_id):
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    username = session['username']
    table_name = 'user_' + ''.join(filter(str.isalnum, username))

    conn = sqlite3.connect('access.db')
    cursor = conn.cursor()

    # Delete the specific record by log_id
    cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': 'Record deleted'})

if __name__ == '__main__':
    app.run(debug=True)
