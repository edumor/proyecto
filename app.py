from flask import Flask, render_template, redirect, url_for, request, flash
import os
import mysql.connector

template_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(template_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Necesario para usar flash

# Configuración de la base de datos
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'registros'
}

# Conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(**db_config)

def repeat_string(s, n):
    return s * n  

@app.route('/')
@app.route('/home')
def home():
    db = get_db_connection()
    cursor = db.cursor()
    # si no existe la tabla usuarios
    cursor.execute("SHOW TABLES LIKE 'usuarios'")
    result = cursor.fetchone()
    if not result:
        cursor.execute('''
            CREATE TABLE usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(30),
                nombre_apellido VARCHAR(150),
                email VARCHAR(100),
                empresa VARCHAR(100),
                cargo VARCHAR(100),
                password VARCHAR(30)
            )
        ''')
    cursor.execute('SELECT * FROM usuarios')
    myresult = cursor.fetchall()
    insertObject = []
    column_names = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(column_names, record)))
    cursor.close()
    db.close()
    
    d = "some value"  # Define la variable d
    
    return render_template('index.html', data=insertObject, repeat_string=repeat_string, d=d)
    
    
@app.route('/user', methods=['POST'])
def addUser():
    username = request.form['user']
    name = request.form['name']
    email = request.form['email']
    empresa = request.form['empresa']
    cargo = request.form['cargo']
    password = request.form['password']
    if username and name and email and password:
        db = get_db_connection()
        cursor = db.cursor()
        sql = "INSERT INTO usuarios (usuario, nombre_apellido, email, empresa, cargo, password) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (username, name, email, empresa, cargo, password)
        cursor.execute(sql, data)
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('home'))
    else:
        flash('Ingrese datos requeridos', 'error')
        return redirect(url_for('home'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db = get_db_connection()
    cursor = db.cursor()
    sql = "DELETE FROM usuarios WHERE id = %s"
    cursor.execute(sql, (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    username = request.form.get('username')
    name = request.form.get('name')
    email = request.form.get('email')
    empresa = request.form.get('empresa')
    cargo = request.form.get('cargo')
    password = request.form.get('password')
    if username and name and password:
        try:
            db = get_db_connection()
            cursor = db.cursor()
            sql = "UPDATE usuarios SET usuario = %s, nombre_apellido = %s, email = %s, empresa = %s, cargo = %s, password = %s WHERE id = %s"
            data = (username, name, email, empresa, cargo, password, id)
            cursor.execute(sql, data)
            db.commit()
            cursor.close()
            db.close()
            flash('Usuario actualizado correctamente', 'success')
        except Exception as e:
            db.rollback()
            flash('Error al actualizar el usuario: {}'.format(e), 'error')
        return redirect(url_for('home'))
    else:
        flash('Ingrese todos los datos requeridos', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)