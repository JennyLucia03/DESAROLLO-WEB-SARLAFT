from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response, current_app
from flask_mysqldb import MySQL
#from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from more_itertools import divide
from flask_mail import Mail, Message
from fpdf import FPDF 
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import csv
import datetime
import pdfplumber
import io
import os
import PyPDF2 
import fitz
import database as db1
import re
import fitz  # PyMuPDF
import requests
import pandas as pd
from datetime import datetime
import openpyxl
from config import config
# Models:

from models.ModelUser import ModelUser

# Entities:
from models.entities.User import User

app = Flask(__name__)

#activar seguridad
#csrf = CSRFProtect()
#app.secret_key = 'B!1w8NAt1T^%kvhUI*S^'

db = MySQL(app)
login_manager_app = LoginManager(app)

#acceso a login
id_user=0
#Flask-Mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'coopverify@gmail.com'
app.config['MAIL_PASSWORD'] = 'nudfutrxwosdurfb'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app) 

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            user = User(0, request.form['username'], request.form['password'],"",0,0)
            logged_user = ModelUser.login(db, user)
            session['user_id'] = logged_user.empleado_id
            if logged_user != None:
                if logged_user.password:
                    login_user(logged_user)
                    if logged_user.id_rol == 1:
                        return redirect(url_for('administrador')) 
                    else:
                        return redirect(url_for('home'))   
                else:
                    flash("Contraseña erronea")
                    return render_template('auth/login.html')
            else:
                flash("Usuario no existe")
                return render_template('auth/login.html')
        else:
            return render_template('auth/login.html')
    except Exception as e:
        flash("Usuario no existe")
        return render_template('auth/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#termina el logeo

#rutas para inciar los procesos adminsitrativos
@app.route('/inicio')
def iniciar1():
    return render_template('inicio.html')

#Empleado
@app.route('/home')
@login_required
def home():
    id_user = session.get('user_id')
    try: 
        cursor2 = db1.database.cursor()
        cursor2.execute("SELECT empleado_id from empresas WHERE empleado_id = %s", (id_user,))
        myresult2 = cursor2.fetchall()
        #Convertir los datos a diccionario
        insertObject2 = []
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2:
            insertObject2.append(dict(zip(columnNames2, record2)))
        cursor2.close()
        if myresult2== []:
            data3=False
        else:
            data3=True
        
        if data3==True:
            cursor = db1.database.cursor()
            cursor.execute("SELECT empresas.empresa_id, empresas.Razon_empresa, empresas.Numero_Documento, empleados.pri_nom, empleados.seg_nombre, empleados.primer_apellido, empleados.segundo_apellido FROM empresas INNER JOIN empleados on empleados.empleado_id = empresas.empleado_id WHERE empleados.empleado_id = %s;", (id_user,))
            myresult = cursor.fetchall()
            insertObject = []
            columnNames = [column[0] for column in cursor.description]
            for record in myresult:
                insertObject.append(dict(zip(columnNames, record)))
            cursor.close()
        else:
            cursor = db1.database.cursor()
            cursor.execute("SELECT empleados.pri_nom, empleados.primer_apellido, empresas.Razon_empresa,empresas.Numero_Documento, empresas.empresa_id FROM empleadoempresa INNER JOIN empleados ON empleados.empleado_id=empleadoempresa.empleado_id INNER JOIN empresas ON empresas.empresa_id=empleadoempresa.empresa_id WHERE empleados.empleado_id = %s;", (id_user,))
            myresult = cursor.fetchall()
            insertObject = []
            columnNames = [column[0] for column in cursor.description]
            for record in myresult:
                insertObject.append(dict(zip(columnNames, record)))
            cursor.close()

        cursor4 = db1.database.cursor()
        cursor4.execute("SELECT * FROM empleados where empleado_id= %s",(id_user,))
        myresult4 = cursor4.fetchall()
        #Convertir los datos a diccionario
        insertObject4 = []
        columnNames4=[column4[0] for column4 in cursor4.description]
        for record4 in myresult4:
            insertObject4.append(dict(zip(columnNames4, record4)))
        cursor4.close()

        return render_template('home.html', data=insertObject, data2=insertObject2, data3=data3,data4=insertObject4)
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
        return render_template('home.html', data=insertObject, data2=insertObject2, data3=data3,data4=insertObject4)

#Administrador
@app.route('/administrador')
def administrador():
    return render_template('homeA.html')

@app.route('/Empleados')
def Empleados():
    try:
        cursor = db1.database.cursor()
        cursor.execute("SELECT * FROM tiposnacionalidad")
        myresult = cursor.fetchall()
        #Convertir los datos a diccionario
        insertObject = []
        columnNames=[column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()

        cursor2 = db1.database.cursor()
        cursor2.execute("SELECT * FROM tipos_documento WHERE tipo_documento_id <> 6")
        myresult2 = cursor2.fetchall()
        #Convertir los datos a diccionario
        insertObject2 = []
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2:
            insertObject2.append(dict(zip(columnNames2, record2)))
        cursor2.close()

        cursor3 = db1.database.cursor()
        cursor3.execute("SELECT * FROM tiposdireccionesfisicas")
        myresult3 = cursor3.fetchall()
        #Convertir los datos a diccionario
        insertObject3 = []
        columnNames3=[column3[0] for column3 in cursor3.description]
        for record3 in myresult3:
            insertObject3.append(dict(zip(columnNames3, record3)))
        cursor3.close()

        cursor4 = db1.database.cursor()
        cursor4.execute("SELECT * FROM ciudades")
        myresult4 = cursor4.fetchall()
        #Convertir los datos a diccionario
        insertObject4 = []
        columnNames4=[column4[0] for column4 in cursor4.description]
        for record4 in myresult4:
            insertObject4.append(dict(zip(columnNames4, record4)))
        cursor4.close()

        cursor5 = db1.database.cursor()
        cursor5.execute("SELECT * FROM tipos_telefono")
        myresult5 = cursor5.fetchall()
        #Convertir los datos a diccionario
        insertObject5 = []
        columnNames5=[column5[0] for column5 in cursor5.description]
        for record5 in myresult5:
            insertObject5.append(dict(zip(columnNames5, record5)))
        cursor5.close()

        return render_template('empleados.html', data=insertObject, data2=insertObject2, data3=insertObject3,
                            data4=insertObject4,data5=insertObject5)
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
"""
def verificar_cedula(cedula):
    # Realizar la conexión a la base de datos
    cursor = db1.database.cursor()
    # Realizar la consulta a la base de datos
    query = "SELECT COUNT(*) FROM empleados WHERE documento = %s"
    cursor.execute(query, (cedula,))
    result = cursor.fetchone()
    # Cerrar la conexión a la base de datos
    cursor.close()
    # Verificar si la cédula existe
    if result[0] > 0:
        return True
    else:
        return False
"""
@app.route('/empleadosg',methods=['POST'])
def empleadosg():
    #Nombres, nacionalidad y documento
    primerNombre = request.form['primerNombre']
    segunNombre = request.form['segundoNombre']
    tipoDocumento = request.form.get('tipoDocumento')
    documento = request.form['documento']
    # Lógica para verificar si la cédula existe en la base de datos
    #existe_cedula = verificar_cedula(documento)
    #print("Existe cédula? ",existe_cedula)
    primerApellido = request.form['primerApellido']
    segundoApellido = request.form['segundoApellido']
    tipoNacionalidad = request.form.get('tipoNacionalidad')
    pdf = request.files['archivoPDF']
    if segunNombre=='':
        segunNombre='NA'
    if segundoApellido=='':
        segundoApellido='NA'
    print(primerNombre)
    print(segunNombre)
    print(tipoDocumento)
    print(documento)
    print(primerApellido)
    print(segundoApellido)
    print(tipoNacionalidad)
    print(pdf)
    
    try:
        cursor = db1.database.cursor()
        cursor.execute("SELECT empleado_id FROM empleados ORDER BY empleado_id DESC LIMIT 1;")
        myresult = cursor.fetchall()
        cursor.close()
        ultimo_id = myresult[0][0]
        print("El último id es: ",ultimo_id)
        
        #Direcciones físicas
        #Último empleado
        tipoDireccionFisica = request.form.get('tipoDireccionFisica')
        direccionFisica = request.form['direccionFisica']
        ciudad = request.form.get('ciudad')
        print(tipoDireccionFisica)
        print(direccionFisica)
        print(ciudad)
        #Teléfono
        tipoTelefono = request.form.get('tipoTelefono')
        numeroTelefono = request.form['numeroTelefono']
        print("Tipo telefono: ",tipoTelefono)
        print("Numero de telefono: ",numeroTelefono)
        #Último empleado y ciudad
        #------------------------------------------
        #Direcciones Electrónicas
        correoid = 1
        usuarioCorreo = request.form['usuarioCorreo']
        print("Correo id: ",correoid)
        print("Correo: ",usuarioCorreo)
        #Último empleado
        #------------------------------------------
        #Login
        #usuarioCorreo
        password = request.form['usuarioClave']
        hashed_password = generate_password_hash(password)
        fullname = primerNombre+" "+primerApellido
        idrol = 2
        print("Hashed password: ",hashed_password)
        print("Nombre y apellido: ",fullname)
        print("Id rol: ",idrol)
        #Último empleado

        if primerNombre and tipoDocumento and documento and primerApellido and tipoNacionalidad and pdf:
            pdf_data = pdf.read()
            pdf.seek(0)
            
            cursor = db1.database.cursor()
            sql = "INSERT INTO empleados(pri_nom,seg_nombre,tipo_documento_id,documento,primer_apellido,segundo_apellido,tipo_nacionalidad_id,cedulaPDF) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            data = (primerNombre,segunNombre,tipoDocumento,documento,primerApellido,segundoApellido,tipoNacionalidad,pdf_data)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
        
        else:
            return "Faltan datos en el formulario"

        if tipoDireccionFisica and direccionFisica and ciudad:
            
            cursor = db1.database.cursor()
            sql = "INSERT INTO direccionesempleados (empleado_id, tipo_direccion_id, direccion, ciudad_id) " \
            "SELECT empleado_id, %s, %s, %s " \
            "FROM empleados " \
            "ORDER BY empleado_id DESC LIMIT 1"
            data = (tipoDireccionFisica,direccionFisica,ciudad)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
            
        else:
            return "Faltan datos en el formulario"
        
        if tipoTelefono and numeroTelefono and ciudad:
            
            cursor = db1.database.cursor()
            sql = "INSERT INTO telefonos (tipo_id, numero, empleado_id, ciudad_id) " \
            "SELECT %s, %s, empleado_id, %s " \
            "FROM empleados " \
            "ORDER BY empleado_id DESC LIMIT 1"
            data = (tipoTelefono,numeroTelefono,ciudad)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
            
        else:
            return "Faltan datos en el formulario"
        
        if correoid and usuarioCorreo:
            
            cursor = db1.database.cursor()
            sql = "INSERT INTO direcciones_electronicas (tipo_id, direccion, empleado_id) " \
        "SELECT %s, %s, empleado_id " \
        "FROM empleados " \
        "ORDER BY empleado_id DESC LIMIT 1"
            data = (correoid,usuarioCorreo)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
        
        else:
            return "Faltan datos en el formulario"
        
        if usuarioCorreo and password and fullname and idrol:

            cursor = db1.database.cursor()
            sql = "INSERT INTO login (username, password, fullname, empleado_id, id_rol) " \
        "SELECT %s, %s, %s, empleado_id, %s " \
        "FROM empleados " \
        "ORDER BY empleado_id DESC LIMIT 1"
            data = (usuarioCorreo,hashed_password,fullname,idrol)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
            
        else:
            return "Faltan datos en el formulario"
        
        return redirect(url_for('login'))
    
    except Exception as e:
        print("Error al insertar en la base de datos:", str(e)) 

@app.route('/homeEmpresa')
def homeEmpresa():
    try:
        cursor = db1.database.cursor()
        cursor.execute("SELECT * FROM empleados")
        myresult = cursor.fetchall()
        #Convertir los datos a diccionario
        insertObject = []
        columnNames=[column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()

        cursor2 = db1.database.cursor()
        cursor2.execute("SELECT * FROM tipos_documento")
        myresult2 = cursor2.fetchall()
        #Convertir los datos a diccionario
        insertObject2 = []
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2:
            insertObject2.append(dict(zip(columnNames2, record2)))
        cursor2.close()

        cursor3 = db1.database.cursor()
        cursor3.execute("SELECT * FROM tipos_direccion")
        myresult3 = cursor3.fetchall()
        #Convertir los datos a diccionario
        insertObject3 = []
        columnNames3=[column3[0] for column3 in cursor3.description]
        for record3 in myresult3:
            insertObject3.append(dict(zip(columnNames3, record3)))
        cursor3.close()

        cursor4 = db1.database.cursor()
        cursor4.execute("SELECT * FROM tipos_telefono")
        myresult4 = cursor4.fetchall()
        #Convertir los datos a diccionario
        insertObject4 = []
        columnNames4=[column4[0] for column4 in cursor4.description]
        for record4 in myresult4:
            insertObject4.append(dict(zip(columnNames4, record4)))
        cursor4.close()

        cursor5 = db1.database.cursor()
        cursor5.execute("SELECT * FROM tiposdireccionesfisicas")
        myresult5 = cursor5.fetchall()
        #Convertir los datos a diccionario
        insertObject5 = []
        columnNames5=[column5[0] for column5 in cursor5.description]
        for record5 in myresult5:
            insertObject5.append(dict(zip(columnNames5, record5)))
        cursor5.close()

        cursor6 = db1.database.cursor()
        cursor6.execute("SELECT * FROM ciudades")
        myresult6 = cursor6.fetchall()
        #Convertir los datos a diccionario
        insertObject6 = []
        columnNames6=[column6[0] for column6 in cursor6.description]
        for record6 in myresult6:
            insertObject6.append(dict(zip(columnNames6, record6)))
        cursor6.close()

        return render_template('empresas.html', data=insertObject, data2=insertObject2, data3=insertObject3, data4=insertObject4, data5=insertObject5, data6=insertObject6)
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
        return render_template('homeA.html')

@app.route('/empresa',methods=['POST'])
def empresa():
    #Empresa
    razon = request.form['razonEmpresa']
    tipoDocumento = request.form.get('tipoDocumento')
    documento = request.form['documento']
    pdf = request.files['archivoPDF']
    seleccion = request.form['seleccion']
    print(razon)
    print(tipoDocumento)
    print(documento)
    print(pdf)
    print(seleccion)
    #-----------------------------------------------------
    #Direcciones electrónicas empresas
    #tipoDireccionE = request.form.get('tipoDireccionE')
    tipoDireccionE=1
    direccionContacto = request.form['direccionContacto']
    print("Tipo Direccion electronica: ",tipoDireccionE)
    print("Direccion electronica: ",direccionContacto)
    #ID DE LA ÚLTIMA EMPRESA
    #-----------------------------------------------------
    #Teléfonos empresa
    tipoTelefono = request.form.get('tipoTelefono')
    telefono = request.form['telefono']
    print("Tipo de telefono: ",tipoTelefono)
    print("Telefono: ",telefono)
    #ID DE LA ÚLTIMA EMPRESA
    #-----------------------------------------------------
    #Direcciones físicas empresa
    #ID DE LA ÚLTIMA EMPRESA
    tipoDireccionF = request.form.get('tipoDireccionF')
    direccionFisica = request.form['direccionFisica']
    ciudad = request.form.get('ciudad')
    print("Tipo de direccion fisica: ",tipoDireccionF)
    print("Direccion física: ",direccionFisica)
    print("Tipo de ciudad: ",ciudad)

    #--------------------------OBTENER ID EMPLEADO DEL DATALIST-----------------------------------
    # Dividir el nombre completo en palabras individuales
    palabras = seleccion.split()

    # Obtener los componentes del nombre
    primer_nombre = palabras[0]
    segundo_nombre = palabras[1] if len(palabras) > 1 else ""
    primer_apellido = palabras[-2] if len(palabras) > 2 else ""
    segundo_apellido = palabras[-1] if len(palabras) > 3 else ""

    #Buscar el id del nombre
    cursor=db1.database.cursor()
    # Consulta SQL para seleccionar el ID
    consulta = '''
        SELECT empleado_id FROM empleados WHERE
        pri_nom = %s AND
        seg_nombre = %s AND
        primer_apellido = %s AND
        segundo_apellido = %s
    '''
    # Ejecutar la consulta con los valores de las variables
    cursor.execute(consulta, (primer_nombre, segundo_nombre, primer_apellido, segundo_apellido))

    # Obtener el resultado de la consulta
    resultado = cursor.fetchone()

    # Verificar si se encontró un ID
    if resultado:
        id_encontrado = resultado[0]
        print("ID encontrado:", id_encontrado)
    else:
        print("No se encontró un ID para los componentes del nombre proporcionados.")

    # Cerrar el cursor y la conexión
    cursor.close()
    #--------------------------------------------------------------------------------------------
    #GUARDAR LOS DATOS EN LA BASE DE DATOS
    if razon and tipoDocumento and documento and pdf and id_encontrado:
        pdf_data = pdf.read()
        pdf.seek(0)
        try:
            cursor = db1.database.cursor()
            sql = "INSERT INTO empresas (Razon_empresa, Tipo_documento, Numero_documento, soporte_documento, empleado_id ) VALUES (%s, %s, %s, %s, %s)"
            data = (razon, tipoDocumento, documento, pdf_data, id_encontrado)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
        except Exception as e:
            print("Error al insertar en la base de datos:", str(e)) 
    else:
        return "Faltan datos en el formulario"
    
    if tipoDireccionE and direccionContacto:
        
        try:
            cursor = db1.database.cursor()
            sql = "INSERT INTO direcciones_electronicas_emp (tipo_id, direccion, empresa_id) " \
                "SELECT %s, %s, empresa_id " \
                "FROM empresas " \
                "ORDER BY empresa_id DESC LIMIT 1"
            data = (tipoDireccionE, direccionContacto)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
        except Exception as e:
            print("Error al insertar en la base de datos:", str(e)) 
        
    else:
        return "Faltan datos en el formulario"
    
    if tipoTelefono and telefono:
        
        try:
            cursor = db1.database.cursor()
            sql = "INSERT INTO telefonos_empresas (tipo_id, telefono, empresa_id) " \
                "SELECT %s, %s, empresa_id " \
                "FROM empresas " \
                "ORDER BY empresa_id DESC LIMIT 1"
            data = (tipoTelefono, telefono)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
        except Exception as e:
            print("Error al insertar en la base de datos:", str(e)) 
        
    else:
        return "Faltan datos en el formulario"
    
    if tipoDireccionF and direccionFisica and ciudad:
        
        try:
            cursor = db1.database.cursor()
            sql = "INSERT INTO direccionesempresas (empresa_id, tipo_direccion_id, direccion, ciudad_id) " \
                "SELECT empresa_id, %s, %s, %s " \
                "FROM empresas " \
                "ORDER BY empresa_id DESC LIMIT 1"
            data = (tipoDireccionF,direccionFisica,ciudad)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
        except Exception as e:
            print("Error al insertar en la base de datos:", str(e)) 
        
    else:
        return "Faltan datos en el formulario"
    
    return redirect(url_for('homeEmpresa'))
    
@app.route('/homeItem')
def homeItem():
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * FROM items_generales")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()
        return render_template('item.html',data=insertObject)
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
        return render_template('homeA.html')

@app.route('/item',methods=['POST'])
def item():
    nombreItem = request.form['nombreItem']
    descripcionItem = request.form['descripcionItem']
    today = date.today()
    current_date = today.strftime("%Y-%m-%d")
    if nombreItem and descripcionItem and current_date:
        try:
            cursor = db1.database.cursor()
            sql = "INSERT INTO items_generales (items_generales_nom, items_generales_descr, items_generales_fecha) VALUES (%s, %s, %s)"
            data = (nombreItem, descripcionItem, current_date)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
            return redirect(url_for('homeItem')) 
        except Exception as e:
            print("Error al insertar en la base de datos:", str(e))  

@app.route('/borritem/<int:id>')
def borraritem(id):    
    try:
        cursor = db1.database.cursor()
        sql = "DELETE FROM items_generales WHERE items_generales_id = %s"
        cursor.execute(sql, (id,))
        db1.database.commit()
        return redirect(url_for('homeItem'))
    except Exception as e:
        print("Error al borrar en la base de datos:", str(e)) 

@app.route('/editaritem/<int:id>', methods=['POST'])
def editaritem(id):
    nombreItem = request.form['nombreItem']
    descripcionItem = request.form['descripcionItem']
    if nombreItem and descripcionItem:
        try:
            cursor = db1.database.cursor()
            sql = "UPDATE items_generales SET items_generales_nom = %s, items_generales_descr = %s WHERE items_generales_id = %s"
            data = (nombreItem, descripcionItem, id)
            cursor.execute(sql, data)
            db1.database.commit()
            return redirect(url_for('homeItem')) 
        except Exception as e:
            print("Error al editar en la base de datos:", str(e)) 

@app.route('/itemsHome')
def itemsHome():
    try:
        cursor = db1.database.cursor()
        cursor.execute("SELECT * FROM items_generales")
        myresult = cursor.fetchall()
        #Convertir los datos a diccionario
        insertObject = []
        columnNames=[column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()

        cursor2 = db1.database.cursor()
        cursor2.execute("SELECT i.item_id, i.descripcion, ig.items_generales_descr, i.fecha_creada, ig.items_generales_id FROM items as i INNER JOIN items_generales as ig where i.itemgeneral_id = ig.items_generales_id;")
        myresult2 = cursor2.fetchall()
        #Convertir los datos a diccionario
        insertObject2 = []
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2:
            insertObject2.append(dict(zip(columnNames2, record2)))
        cursor2.close()

        return render_template('items.html', data= insertObject , data2=insertObject2)
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
        return render_template('homeA.html')

@app.route('/items', methods=['POST'])
def items():
    descripcionItem = request.form['descripcionItem']
    tipoItem = request.form.get('tipoItem')
    today = date.today()
    current_date = today.strftime("%Y-%m-%d")
    if descripcionItem and tipoItem and current_date:
        try:
            cursor = db1.database.cursor()
            sql = "INSERT INTO items (descripcion, itemgeneral_id, fecha_creada) VALUES (%s, %s, %s)"
            data = (descripcionItem, tipoItem, current_date)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
            return redirect(url_for('itemsHome'))  
        except Exception as e:
            print("Error al insertar en la base de datos:", str(e)) 

@app.route('/borritems/<int:id>')
def borraritems(id): 
    try:   
        cursor = db1.database.cursor()
        sql = "DELETE FROM items WHERE item_id = %s"
        cursor.execute(sql, (id,))
        db1.database.commit()
        return redirect(url_for('itemsHome'))
    except Exception as e:
        print("Error al borrar en la base de datos:", str(e)) 

@app.route('/editaritems/<int:id>', methods=['POST'])
def editaritems(id):
    descripcionItem = request.form['descripcionItem']
    tipoItem = request.form.get('tipoItem')
    if descripcionItem and tipoItem:
        try:
            cursor = db1.database.cursor()
            sql = "UPDATE items SET descripcion = %s, itemgeneral_id = %s WHERE item_id = %s"
            data = (descripcionItem, tipoItem, id)
            cursor.execute(sql, data)
            db1.database.commit()
            return redirect(url_for('itemsHome')) 
        except Exception as e:
            print("Error al editar en la base de datos:", str(e)) 
    
@app.route('/preguntasHome')
def preguntasHome():
    try:
        cursor = db1.database.cursor()
        cursor.execute("SELECT * FROM items")
        myresult = cursor.fetchall()
        #Convertir los datos a diccionario
        insertObject = []
        columnNames=[column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()

        cursor2 = db1.database.cursor()
        cursor2.execute("SELECT pre.pregunta_id,pre.enunciado,pre.fecha_creada, pre.item_id, it.descripcion,it.descripcion FROM preguntas as pre INNER JOIN items as it where pre.item_id=it.item_id;")
        myresult2 = cursor2.fetchall()
        #Convertir los datos a diccionario
        insertObject2 = []
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2:
            insertObject2.append(dict(zip(columnNames2, record2)))
        cursor2.close()

        return render_template('preguntas.html', data= insertObject , data2=insertObject2)
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
        return render_template('homeA.html')

@app.route('/addpregunta', methods=['POST'])
def addpregunta():
    enunciado = request.form['enunciado']
    tipoItem = request.form.get('tipoItem')
    today = date.today()
    current_date = today.strftime("%Y-%m-%d")
    if enunciado and tipoItem and current_date:
        try:
            cursor = db1.database.cursor()
            sql = "INSERT INTO preguntas (enunciado, fecha_creada, item_id) VALUES (%s, %s, %s)"
            data = (enunciado, current_date, tipoItem)
            cursor.execute(sql, data)
            db1.database.commit()
            cursor.close()
            return redirect(url_for('preguntasHome')) 
        except Exception as e:
            print("Error al insertar en la base de datos:", str(e)) 
    else:
        return "Faltan datos en el formulario"
    
@app.route('/borrarPregunta/<int:id>')
def borrarPregunta(id):  
    try:  
        cursor = db1.database.cursor()
        sql = "DELETE FROM preguntas WHERE pregunta_id = %s"
        cursor.execute(sql, (id,))
        db1.database.commit()
        return redirect(url_for('preguntasHome'))
    except Exception as e:
        print("Error al borrar en la base de datos:", str(e)) 

@app.route('/editarPregunta/<int:id>', methods=['POST'])
def editarPregunta(id):
    enunciado = request.form['enunciado']
    tipoItem = request.form.get('tipoItem')
    if enunciado and tipoItem:
        try:
            cursor = db1.database.cursor()
            sql = "UPDATE preguntas SET enunciado = %s, item_id = %s WHERE pregunta_id = %s"
            data = (enunciado, tipoItem, id)
            cursor.execute(sql, data)
            db1.database.commit()
            return redirect(url_for('preguntasHome')) 
        except Exception as e:
            print("Error al editar en la base de datos:", str(e)) 
    
@app.route('/hprocesosauto')
def hprocesosauto():
    id_empresa = request.args.get('id')
    try:
        cursor = db1.database.cursor()
        cursor.execute("SELECT * FROM empleados")
        myresult = cursor.fetchall()
        #Convertir los datos a diccionario
        insertObject = []
        columnNames=[column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

    try:
        cursor2 = db1.database.cursor()
        cursor2.execute("SELECT * FROM empresas")
        myresult2 = cursor2.fetchall()
        #Convertir los datos a diccionario
        insertObject2 = []
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2:
            insertObject2.append(dict(zip(columnNames2, record2)))
        cursor2.close()
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

    today = date.today()
    current_date = today.strftime("%Y-%m-%d")
    session['ha_visitado_pagina_anterior'] = False
    session['ha_visitar_pagina_anterior'] = False

    return render_template('procesoAuto.html', data=insertObject, data2=insertObject2, data3=current_date, id_empresa=id_empresa)

@app.route('/addProcesoauto',methods=['POST'])
def addProcesoauto():
    if request.method == 'POST':
        #seleccion2 = request.form['seleccion2']
        #seleccion = request.form['seleccion']
        idEmpresa = request.form['idEmpresa']
        print("ID empresa:",idEmpresa)
        id_user = session.get('user_id')
        print("ID usuario:",id_user)
        cargoEmpleado = request.form['cargoEmpleado']
        fecha1 = request.form['calendario']
        fecha2 = request.form['calendario2']
        """
        #---------------------------------------------------------
        #Buscar el id de la empresa
        cursor=db1.database.cursor()
        # Consulta SQL para seleccionar el ID
        consulta = '''
            SELECT empresa_id FROM empresas WHERE
            Razon_empresa = %s
        '''
        # Ejecutar la consulta con los valores de las variables
        cursor.execute(consulta, (seleccion2,))

        # Obtener el resultado de la consulta
        resultado = cursor.fetchone()

        # Verificar si se encontró un ID
        if resultado:
            id_encontrado = resultado[0]
            print("ID encontrado de la empresa:", id_encontrado)
        else:
            print("No se encontró un ID para los componentes del nombre proporcionados.")

        # Cerrar el cursor y la conexión
        cursor.close()
        #---------------------------------------------------------------------------------------------
    
        #--------------------------OBTENER ID EMPLEADO DEL DATALIST-----------------------------------
        # Dividir el nombre completo en palabras individuales
        palabras = seleccion.split()

        # Obtener los componentes del nombre
        primer_nombre = palabras[0]
        segundo_nombre = palabras[1] if len(palabras) > 1 else ""
        primer_apellido = palabras[-2] if len(palabras) > 2 else ""
        segundo_apellido = palabras[-1] if len(palabras) > 3 else ""

        #Buscar el id del nombre
        cursor=db1.database.cursor()
        # Consulta SQL para seleccionar el ID
        consulta = '''
            SELECT empleado_id FROM empleados WHERE
            pri_nom = %s AND
            seg_nombre = %s AND
            primer_apellido = %s AND
            segundo_apellido = %s
        '''
        # Ejecutar la consulta con los valores de las variables
        cursor.execute(consulta, (primer_nombre, segundo_nombre, primer_apellido, segundo_apellido))

        # Obtener el resultado de la consulta
        resultado2 = cursor.fetchone()

        # Verificar si se encontró un ID
        if resultado2:
            id_encontrado2 = resultado2[0]
            print("ID encontrado:", id_encontrado2)
        else:
            print("No se encontró un ID para los componentes del nombre proporcionados.")

        # Cerrar el cursor y la conexión
        cursor.close()
        #--------------------------------------------------------------------------------------------
        """
        #GUARDAR LOS DATOS EN LA BASE DE DATOS
        
        if idEmpresa and id_user and cargoEmpleado and fecha1 and fecha2:
            try:
                cursor = db1.database.cursor()
                sql = "INSERT INTO procesos_autoevaluacion (empresa_id, empleado_id, cargo_empleado, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s)"
                data = (idEmpresa,id_user,cargoEmpleado,fecha1,fecha2)
                cursor.execute(sql, data)
                db1.database.commit()
                cursor.close()
                
                session['ha_visitado_pagina_anterior'] = True
                return redirect(url_for('hderechoshumanos'))
            except Exception as e:
                print("Error al insertar en la base de datos:", str(e)) 
        else:
            return "Faltan datos en el formulario"
    return "Faltan datos en el formulario"
    
@app.route('/hderechoshumanos')
def hderechoshumanos(): 
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * from preguntas WHERE item_id=1;")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()   

        cursor3=db1.database.cursor()
        cursor3.execute("SELECT * from preguntas WHERE item_id=2;")
        myresult3= cursor3.fetchall()
        # pasar as diccionario
        insertObject3=[]
        columnNames3=[column3[0] for column3 in cursor3.description]
        for record3 in myresult3: 
            insertObject3.append(dict(zip(columnNames3,record3)))
        cursor3.close()  

        cursor4=db1.database.cursor()
        cursor4.execute("SELECT * from procesos_autoevaluacion order by proceso_id DESC")
        myresult4= cursor4.fetchall()
        # pasar as diccionario
        insertObject4=[]
        columnNames4=[column4[0] for column4 in cursor4.description]
        for record4 in myresult4: 
            insertObject4.append(dict(zip(columnNames4,record4)))
        cursor4.close()  

        cursor2=db1.database.cursor()
        cursor2.execute("SELECT * from items where itemgeneral_id=1;")
        myresult2= cursor2.fetchall()
        # pasar as diccionario
        insertObject2=[]
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2: 
            insertObject2.append(dict(zip(columnNames2,record2)))
        cursor2.close()  
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

    if not session.get('ha_visitado_pagina_anterior'):
        return redirect('/hprocesosauto')

    return render_template('derechosh.html',data=insertObject,data2=insertObject2,data3=insertObject3,data4=insertObject4)

@app.route('/derechoshg', methods=['POST'])
def derechoshg():
    valores = request.form.getlist('valor')
    valorAdicional = request.form['valorAdicional']
    preguntasid = request.form.getlist('idpreguntas[]')
    print(valores)
    print(valorAdicional)
    print(preguntasid)
    try:
        cursor = db1.database.cursor()
        for i in range(len(valores)):
            if valores and valorAdicional and preguntasid:
                sql = "INSERT INTO respuestas_autoevaluacion (proceso_id, pregunta_id, valor) VALUES (%s, %s, %s)"
                data = (valorAdicional, preguntasid[i], valores[i])
                cursor.execute(sql, data)
                db1.database.commit()
        cursor.close()
    except Exception as e:
        print("Error al insertar en la base de datos:", str(e)) 
    return redirect(url_for('hderechoslaborales'))

@app.route('/hderechoslaborales')
def hderechoslaborales(): 
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * from preguntas WHERE item_id=3;")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()   

        cursor3=db1.database.cursor()
        cursor3.execute("SELECT * from preguntas WHERE item_id=4;")
        myresult3= cursor3.fetchall()
        # pasar as diccionario
        insertObject3=[]
        columnNames3=[column3[0] for column3 in cursor3.description]
        for record3 in myresult3: 
            insertObject3.append(dict(zip(columnNames3,record3)))
        cursor3.close()  

        cursor5=db1.database.cursor()
        cursor5.execute("SELECT * from preguntas WHERE item_id=5;")
        myresult5= cursor5.fetchall()
        # pasar as diccionario
        insertObject5=[]
        columnNames5=[column5[0] for column5 in cursor5.description]
        for record5 in myresult5: 
            insertObject5.append(dict(zip(columnNames5,record5)))
        cursor5.close()  

        cursor6=db1.database.cursor()
        cursor6.execute("SELECT * from preguntas WHERE item_id=6;")
        myresult6= cursor6.fetchall()
        # pasar as diccionario
        insertObject6=[]
        columnNames6=[column6[0] for column6 in cursor6.description]
        for record6 in myresult6: 
            insertObject6.append(dict(zip(columnNames6,record6)))
        cursor6.close()  

        cursor4=db1.database.cursor()
        cursor4.execute("SELECT * from procesos_autoevaluacion order by proceso_id DESC")
        myresult4= cursor4.fetchall()
        # pasar as diccionario
        insertObject4=[]
        columnNames4=[column4[0] for column4 in cursor4.description]
        for record4 in myresult4: 
            insertObject4.append(dict(zip(columnNames4,record4)))
        cursor4.close()  

        cursor2=db1.database.cursor()
        cursor2.execute("SELECT * from items where itemgeneral_id=2;")
        myresult2= cursor2.fetchall()
        # pasar as diccionario
        insertObject2=[]
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2: 
            insertObject2.append(dict(zip(columnNames2,record2)))
        cursor2.close() 
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e))  

    if not session.get('ha_visitado_pagina_anterior'):
        return redirect('/hprocesosauto')

    return render_template('derechosl.html',data=insertObject,data2=insertObject2,data3=insertObject3,data4=insertObject4,data5=insertObject5,data6=insertObject6)

@app.route('/derechoslg', methods=['POST'])
def derechoslg():
    valores = request.form.getlist('valor')
    valorAdicional = request.form['valorAdicional']
    preguntasid = request.form.getlist('idpreguntas[]')
    print(valores)
    print(valorAdicional)
    print(preguntasid)
    try:
        cursor = db1.database.cursor()
        for i in range(len(valores)):
            if valores and valorAdicional and preguntasid:
                sql = "INSERT INTO respuestas_autoevaluacion (proceso_id, pregunta_id, valor) VALUES (%s, %s, %s)"
                data = (valorAdicional, preguntasid[i], valores[i])
                cursor.execute(sql, data)
                db1.database.commit()
        cursor.close()
    except Exception as e:
        print("Error al insertar en la base de datos:", str(e)) 
    
    return redirect(url_for('hmedioambiente'))

@app.route('/hmedioambiente')
def hmedioambiente(): 
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * from preguntas WHERE item_id=7;")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()   

        cursor3=db1.database.cursor()
        cursor3.execute("SELECT * from preguntas WHERE item_id=8;")
        myresult3= cursor3.fetchall()
        # pasar as diccionario
        insertObject3=[]
        columnNames3=[column3[0] for column3 in cursor3.description]
        for record3 in myresult3: 
            insertObject3.append(dict(zip(columnNames3,record3)))
        cursor3.close()  

        cursor5=db1.database.cursor()
        cursor5.execute("SELECT * from preguntas WHERE item_id=9;")
        myresult5= cursor5.fetchall()
        # pasar as diccionario
        insertObject5=[]
        columnNames5=[column5[0] for column5 in cursor5.description]
        for record5 in myresult5: 
            insertObject5.append(dict(zip(columnNames5,record5)))
        cursor5.close()  

        cursor4=db1.database.cursor()
        cursor4.execute("SELECT * from procesos_autoevaluacion order by proceso_id DESC")
        myresult4= cursor4.fetchall()
        # pasar as diccionario
        insertObject4=[]
        columnNames4=[column4[0] for column4 in cursor4.description]
        for record4 in myresult4: 
            insertObject4.append(dict(zip(columnNames4,record4)))
        cursor4.close()  

        cursor2=db1.database.cursor()
        cursor2.execute("SELECT * from items where itemgeneral_id=3;")
        myresult2= cursor2.fetchall()
        # pasar as diccionario
        insertObject2=[]
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2: 
            insertObject2.append(dict(zip(columnNames2,record2)))
        cursor2.close()  
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

    if not session.get('ha_visitado_pagina_anterior'):
        return redirect('/hprocesosauto')

    return render_template('medioambiente.html',data=insertObject,data2=insertObject2,data3=insertObject3,data4=insertObject4,data5=insertObject5)

@app.route('/medioambienteg', methods=['POST'])
def medioambienteg():
    valores = request.form.getlist('valor')
    valorAdicional = request.form['valorAdicional']
    preguntasid = request.form.getlist('idpreguntas[]')
    print(valores)
    print(valorAdicional)
    print(preguntasid)
    try:
        cursor = db1.database.cursor()
        for i in range(len(valores)):
            if valores and valorAdicional and preguntasid:
                sql = "INSERT INTO respuestas_autoevaluacion (proceso_id, pregunta_id, valor) VALUES (%s, %s, %s)"
                data = (valorAdicional, preguntasid[i], valores[i])
                cursor.execute(sql, data)
                db1.database.commit()
        cursor.close()
    except Exception as e:
        print("Error al insertar en la base de datos:", str(e)) 
    return redirect(url_for('hanticorrupcion'))

@app.route('/hanticorrupcion')
def hanticorrupcion(): 
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * from preguntas WHERE item_id=10;")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()   

        cursor4=db1.database.cursor()
        cursor4.execute("SELECT * from procesos_autoevaluacion order by proceso_id DESC")
        myresult4= cursor4.fetchall()
        # pasar as diccionario
        insertObject4=[]
        columnNames4=[column4[0] for column4 in cursor4.description]
        for record4 in myresult4: 
            insertObject4.append(dict(zip(columnNames4,record4)))
        cursor4.close()  

        cursor2=db1.database.cursor()
        cursor2.execute("SELECT * from items where itemgeneral_id=4;")
        myresult2= cursor2.fetchall()
        # pasar as diccionario
        insertObject2=[]
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2: 
            insertObject2.append(dict(zip(columnNames2,record2)))
        cursor2.close() 
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e))  

    if not session.get('ha_visitado_pagina_anterior'):
        return redirect('/hprocesosauto')

    return render_template('anticorrupcion.html',data=insertObject,data2=insertObject2,data4=insertObject4)

@app.route('/anticorrupciong', methods=['POST'])
def anticorrupcion():
    valores = request.form.getlist('valor')
    valorAdicional = request.form['valorAdicional']
    preguntasid = request.form.getlist('idpreguntas[]')
    print(valores)
    print(valorAdicional)
    print(preguntasid)
    try:
        cursor = db1.database.cursor()
        for i in range(len(valores)):
            if valores and valorAdicional and preguntasid:
                sql = "INSERT INTO respuestas_autoevaluacion (proceso_id, pregunta_id, valor) VALUES (%s, %s, %s)"
                data = (valorAdicional, preguntasid[i], valores[i])
                cursor.execute(sql, data)
                db1.database.commit()
        cursor.close()
    except Exception as e:
        print("Error al insertar en la base de datos:", str(e)) 
    
    session['ha_visitar_pagina_anterior'] = True
    return redirect(url_for('hconsolidado'))

@app.route('/hconsolidado')
def hconsolidado(): 
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, items.descripcion, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 1 AND items.item_id = 1 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()   

        cursor2=db1.database.cursor()
        cursor2.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, items.descripcion, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 1 AND items.item_id = 2 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult2= cursor2.fetchall()
        # pasar as diccionario
        insertObject2=[]
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2: 
            insertObject2.append(dict(zip(columnNames2,record2)))
        cursor2.close() 

        cursor3=db1.database.cursor()
        cursor3.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, items.descripcion, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 2 AND items.item_id = 3 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult3= cursor3.fetchall()
        # pasar as diccionario
        insertObject3=[]
        columnNames3=[column3[0] for column3 in cursor3.description]
        for record3 in myresult3: 
            insertObject3.append(dict(zip(columnNames3,record3)))
        cursor3.close()  

        cursor5=db1.database.cursor()
        cursor5.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, items.descripcion, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 2 AND items.item_id = 4 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult5= cursor5.fetchall()
        # pasar as diccionario
        insertObject5=[]
        columnNames5=[column5[0] for column5 in cursor5.description]
        for record5 in myresult5: 
            insertObject5.append(dict(zip(columnNames5,record5)))
        cursor5.close()  

        cursor6=db1.database.cursor()
        cursor6.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, items.descripcion, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 2 AND items.item_id = 5 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult6= cursor6.fetchall()
        # pasar as diccionario
        insertObject6=[]
        columnNames6=[column6[0] for column6 in cursor6.description]
        for record6 in myresult6: 
            insertObject6.append(dict(zip(columnNames6,record6)))
        cursor6.close()  

        cursor4=db1.database.cursor()
        cursor4.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, items.descripcion, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 2 AND items.item_id = 6 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult4= cursor4.fetchall()
        # pasar as diccionario
        insertObject4=[]
        columnNames4=[column4[0] for column4 in cursor4.description]
        for record4 in myresult4: 
            insertObject4.append(dict(zip(columnNames4,record4)))
        cursor4.close()  

        cursor7=db1.database.cursor()
        cursor7.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, items.descripcion, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 3 AND items.item_id = 7 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult7= cursor7.fetchall()
        # pasar as diccionario
        insertObject7=[]
        columnNames7=[column7[0] for column7 in cursor7.description]
        for record7 in myresult7: 
            insertObject7.append(dict(zip(columnNames7,record7)))
        cursor7.close() 

        cursor8=db1.database.cursor()
        cursor8.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, items.descripcion, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 3 AND items.item_id = 8 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult8= cursor8.fetchall()
        # pasar as diccionario
        insertObject8=[]
        columnNames8=[column8[0] for column8 in cursor8.description]
        for record8 in myresult8: 
            insertObject8.append(dict(zip(columnNames8,record8)))
        cursor8.close() 

        cursor9=db1.database.cursor()
        cursor9.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, items.descripcion, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 3 AND items.item_id = 9 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult9= cursor9.fetchall()
        # pasar as diccionario
        insertObject9=[]
        columnNames9=[column9[0] for column9 in cursor9.description]
        for record9 in myresult9: 
            insertObject9.append(dict(zip(columnNames9,record9)))
        cursor9.close() 

        cursor10=db1.database.cursor()
        cursor10.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, items.descripcion, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 4 AND items.item_id = 10 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult10= cursor10.fetchall()
        # pasar as diccionario
        insertObject10=[]
        columnNames10=[column10[0] for column10 in cursor10.description]
        for record10 in myresult10: 
            insertObject10.append(dict(zip(columnNames10,record10)))
        cursor10.close() 

        cursor11=db1.database.cursor()
        cursor11.execute("SELECT respuestas_autoevaluacion.proceso_id, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM respuestas_autoevaluacion INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult11= cursor11.fetchall()
        # pasar as diccionario
        insertObject11=[]
        columnNames11=[column11[0] for column11 in cursor11.description]
        for record11 in myresult11: 
            insertObject11.append(dict(zip(columnNames11,record11)))
        cursor11.close() 
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

    if not session.get('ha_visitar_pagina_anterior'):
        return redirect('/hderechoshumanos')

    return render_template('consolidado.html',data=insertObject,data2=insertObject2,data3=insertObject3,data4=insertObject4,
                           data5=insertObject5,data6=insertObject6, data7=insertObject7, data8=insertObject8, data9=insertObject9, 
                           data10=insertObject10, data11=insertObject11)

@app.route('/hresumen')
def hresumen():
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 1 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()

        cursor2=db1.database.cursor()
        cursor2.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 2 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult2= cursor2.fetchall()
        # pasar as diccionario
        insertObject2=[]
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2: 
            insertObject2.append(dict(zip(columnNames2,record2)))
        cursor2.close() 

        cursor3=db1.database.cursor()
        cursor3.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 3 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult3= cursor3.fetchall()
        # pasar as diccionario
        insertObject3=[]
        columnNames3=[column3[0] for column3 in cursor3.description]
        for record3 in myresult3: 
            insertObject3.append(dict(zip(columnNames3,record3)))
        cursor3.close()  

        cursor4=db1.database.cursor()
        cursor4.execute("SELECT respuestas_autoevaluacion.proceso_id, items_generales.items_generales_nom, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM items INNER JOIN items_generales ON items_generales.items_generales_id = items.itemgeneral_id INNER JOIN preguntas ON preguntas.item_id = items.item_id INNER JOIN respuestas_autoevaluacion ON respuestas_autoevaluacion.pregunta_id = preguntas.pregunta_id INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE itemgeneral_id = 4 AND procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult4= cursor4.fetchall()
        # pasar as diccionario
        insertObject4=[]
        columnNames4=[column4[0] for column4 in cursor4.description]
        for record4 in myresult4: 
            insertObject4.append(dict(zip(columnNames4,record4)))
        cursor4.close()  

        cursor5=db1.database.cursor()
        cursor5.execute("SELECT respuestas_autoevaluacion.proceso_id, FORMAT(AVG(respuestas_autoevaluacion.valor), 2) AS promedio, CONCAT(ROUND((FORMAT(AVG(respuestas_autoevaluacion.valor), 2) / 4 * 100), 0)) AS porcentaje FROM respuestas_autoevaluacion INNER JOIN procesos_autoevaluacion ON procesos_autoevaluacion.proceso_id = respuestas_autoevaluacion.proceso_id WHERE procesos_autoevaluacion.proceso_id = ( SELECT MAX(proceso_id) FROM respuestas_autoevaluacion );")
        myresult5= cursor5.fetchall()
        # pasar as diccionario
        insertObject5=[]
        columnNames5=[column5[0] for column5 in cursor5.description]
        for record5 in myresult5: 
            insertObject5.append(dict(zip(columnNames5,record5)))
        cursor5.close() 
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

    if not session.get('ha_visitar_pagina_anterior'):
        return redirect('/hderechoshumanos')

    return render_template('resumenGerencial.html',data=insertObject,data2=insertObject2,data3=insertObject3,data4=insertObject4,data5=insertObject5)

@app.route('/relacionada')
def relacionada():
    id_empresa = request.args.get('id2')
    id_user = session.get('user_id')
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * FROM empresas WHERE empresa_id <> %s",(id_empresa,))
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
    return render_template('relacionada.html',data=insertObject, id_empresa=id_empresa)

@app.route('/relacionadag',methods=['POST'])
def relacionadag():
    #seleccion1 = request.form.get('seleccion1')  
    try:
        idEmpresaE = request.form['idEmpresaE']
        print("ID empresa evaluante: ",idEmpresaE)
        seleccion2 = request.form.get('seleccion2') 
        comentarios = request.form.get('comentarios') 
        today = date.today()
        current_date = today.strftime("%Y-%m-%d")
        #Buscar el id de la empresa
        cursor=db1.database.cursor()
        consulta = '''            
        SELECT empresa_id FROM empresas WHERE
        Razon_empresa = %s
        '''
        cursor.execute(consulta, (seleccion2,))        
        # Obtener el resultado de la consulta
        resultado = cursor.fetchone()
        # Verificar si se encontró un ID
        if resultado:
            id_encontrado = resultado[0]
            print("ID encontrado de la empresa:", id_encontrado)
        else:
            print("No se encontró un ID para los componentes del nombre proporcionados.")
            # Cerrar el cursor y la conexión
        cursor.close()
        #--------------------------OBTENER CORREO DESTINATARIO--------------------------
        cursor=db1.database.cursor()
        cursor.execute("SELECT Razon_empresa FROM empresas WHERE empresa_id= %s ",(idEmpresaE,))
        myresult= cursor.fetchall()
        empresa = myresult[0][0]
        cursor.close()

        cursor=db1.database.cursor()
        cursor.execute("SELECT direccion FROM direcciones_electronicas_emp WHERE empresa_id= %s ",(id_encontrado,))
        myresult= cursor.fetchall()
        destinatario = myresult[0][0]
        cursor.close()

        asunto = 'Solicitud Documentos'
        mensaje = f"""Saludos desde el sistema Coopverify, le informamos que la empresa {empresa} ha solicitado una evaluación de riesgo según la ley xxxxx, debe ingresar al sistema con usuario y contraseña para adjuntar los siguientes documentos.\nNota: se realizará una verificación de riesgo en los siguientes sistemas informáticos www.sarlaft.com"""
        print(mensaje)
        # Crear el mensaje
        msg = Message(asunto, sender='coopverify@gmail.com', recipients=[destinatario])
        msg.body = mensaje


        if idEmpresaE and id_encontrado and current_date and comentarios:
            
            cursor=db1.database.cursor()
            sql="INSERT INTO relacionada (empresa_padre_id, empresa_hija_id, fecha_revison, comentario) VALUES (%s,%s,%s,%s)"
            data=(idEmpresaE,id_encontrado,current_date, comentarios)
            cursor.execute(sql,data)
            db1.database.commit()
            cursor.close()
            
        try:
            # Enviar el correo
            mail.send(msg)
            return redirect(url_for('home')) 
        except Exception as e:
            return 'Error al enviar el correo: ' + str(e)
    except Exception as e:
        print("Error al insertar en la base de datos:", str(e)) 
    return redirect(url_for('home')) 

# Ruta para validar cédula
"""
@app.route('/validar-cedula', methods=['POST'])
def validar_cedula():
    # Obtener el valor de cedula enviado desde el frontend
    cedula = request.json.get('cedula')
    # Realizar la consulta a la base de datos para verificar si el documento existe
    cursor = db1.database.cursor()
    query = "SELECT documento FROM empleados WHERE documento = %s"
    cursor.execute(query, (cedula,))
    resultado = cursor.fetchone()
    existe_documento = resultado is not None
    # Devolver la respuesta al frontend
    return jsonify({"existeDocumento": existe_documento})
"""
@app.route('/informespn')
def informespn():

    id_empresa = request.args.get('id3')
    id_user = session.get('user_id')
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * FROM empleados WHERE empleado_id <> %s",(id_user,))
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

    now = datetime.now()
    formatted_date = now.strftime('%d/%m/%Y')
    formatted_time = now.strftime('%H:%M:%S')

    return render_template('informes.html',data=insertObject,current_date=formatted_date, current_time=formatted_time,id_empresa=id_empresa)

@app.route('/informesg',methods=['POST'])
def informesg():
    now = datetime.now()
    today = date.today()
    current_date = today.strftime("%Y-%m-%d")
    formatted_time = now.strftime('%H:%M:%S')
    idEmpresaE = request.form['idEmpresaE']
    seleccion2 = request.form['seleccion2']
    try:
         #--------------------------OBTENER ID EMPLEADO DEL DATALIST-----------------------------------
        # Dividir el nombre completo en palabras individuales
        palabras = seleccion2.split()

        # Obtener los componentes del nombre
        primer_nombre = palabras[0]
        segundo_nombre = palabras[1] if len(palabras) > 1 else ""
        primer_apellido = palabras[-2] if len(palabras) > 2 else ""
        segundo_apellido = palabras[-1] if len(palabras) > 3 else ""

        #Buscar el id del nombre
        cursor=db1.database.cursor()
        # Consulta SQL para seleccionar el ID
        consulta = '''
            SELECT empleado_id FROM empleados WHERE
            pri_nom = %s AND
            seg_nombre = %s AND
            primer_apellido = %s AND
            segundo_apellido = %s
            '''
        # Ejecutar la consulta con los valores de las variables
        cursor.execute(consulta, (primer_nombre, segundo_nombre, primer_apellido, segundo_apellido))

        # Obtener el resultado de la consulta
        resultado2 = cursor.fetchone()

        # Verificar si se encontró un ID
        if resultado2:
            id_encontrado2 = resultado2[0]
            print("ID encontrado empleado:", id_encontrado2)
        else:
            print("No se encontró un ID para los componentes del nombre proporcionados.")

        # Cerrar el cursor y la conexión
        cursor.close()
    #--------------------------------------------------------------------------------------------
        print("Id empresa: ",idEmpresaE)
        print("id: ",id_encontrado2)
        if current_date and formatted_time and idEmpresaE and id_encontrado2:
            cursor=db1.database.cursor()
            sql="INSERT INTO informes (fecha,hora,empresa_id,empleado_id) VALUES (%s,%s,%s,%s)"
            data=(current_date,formatted_time,idEmpresaE,id_encontrado2)
            cursor.execute(sql,data)
            db1.database.commit()
            cursor.close()
             
        #--------------------------OBTENER CORREO DESTINATARIO--------------------------
        cursor=db1.database.cursor()
        cursor.execute("SELECT Razon_empresa FROM empresas WHERE empresa_id= %s ",(idEmpresaE,))
        myresult= cursor.fetchall()
        empresa = myresult[0][0]
        cursor.close()

        cursor=db1.database.cursor()
        cursor.execute("SELECT direccion FROM direcciones_electronicas WHERE empleado_id= %s ",(id_encontrado2,))
        myresult= cursor.fetchall()
        destinatario = myresult[0][0]
        cursor.close()

        asunto = 'Solicitud Documentos'
        mensaje = f"""Saludos desde el sistema Coopverify, le informamos que la empresa {empresa} ha solicitado una evaluación de riesgo según la ley xxxxx, debe ingresar al sistema con usuario y contraseña para adjuntar los siguientes documentos.\nNota: se realizará una verificación de riesgo en los siguientes sistemas informáticos www.sarlaft.com"""
        print(mensaje)
        # Crear el mensaje
        msg = Message(asunto, sender='coopverify@gmail.com', recipients=[destinatario])
        msg.body = mensaje

        try:
            # Enviar el correo
            mail.send(msg)
            return redirect(url_for('home')) 
        except Exception as e:
            return 'Error al enviar el correo: ' + str(e)
    except Exception as e:
        print("Error al insertar en la base de datos:", str(e)) 
    return redirect(url_for('home')) 

@app.route('/procesos')
def procesos():
    id_user = session.get('user_id')
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT informes.informe_id, informes.fecha, informes.hora, empresas.Razon_empresa FROM informes INNER JOIN empresas ON empresas.empresa_id = informes.empresa_id INNER JOIN empleados ON empleados.empleado_id = informes.empleado_id WHERE informes.empleado_id = %s",(id_user,))
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
    return render_template('procesos.html',data=insertObject)

@app.route('/subirDocumentos')
def subirDocumentos():
    id_informe = request.args.get('id')
    print("ID informe: ",id_informe)
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * FROM tipos_documento_adjunto WHERE tipo_documento_id = 2 || tipo_documento_id = 3;")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

    return render_template('subirDoc.html',data=insertObject,id_informe=id_informe)

@app.route('/subirDocg',methods=['POST'])
def subirDocg():
    data = request.form
    titulo = data['titulo']
    tarjeta_id = int(data['tarjeta_id'])
    #-----------------------------------------
    archivoPDF = request.files['archivoPDF']
    idInforme = request.form['idInforme']
    archivoPDF = request.files['archivoPDF']
    pdf_data = archivoPDF.read()
    archivoPDF.seek(0)
    print("ID informe: ",idInforme)
    print(f"Datos de tarjeta recibidos: Título: {titulo}, ID: {tarjeta_id}, PDF: {archivoPDF}")
    
    if idInforme and pdf_data and tarjeta_id:
        try:
            cursor=db1.database.cursor()
            sql="INSERT INTO documentos_adjuntos (informe_id,tipo_documento_adjunto,archivo_adjunto) VALUES (%s,%s,%s)"
            data=(idInforme,tarjeta_id,pdf_data)
            cursor.execute(sql,data)
            db1.database.commit()
            cursor.close()
        except Exception as e:
            print("Error al insertar en la base de datos:", str(e)) 
    
    return redirect(url_for('subirDocumentos',id=idInforme)) 

@app.route('/comprobarT',methods=['POST'])
def comprobarT():
    idInforme = request.form['idInforme']
    cursor=db1.database.cursor()
    cursor.execute("SELECT COUNT(informe_id) FROM `documentos_adjuntos` WHERE informe_id= %s;",(idInforme,))
    myresult= cursor.fetchall()
    cursor.close()
    if myresult[0][0]<2:
        try:
            cursor = db1.database.cursor()
            sql = "DELETE FROM documentos_adjuntos WHERE informe_id = %s"
            cursor.execute(sql, (idInforme,))
            db1.database.commit()
            cursor.close()
            flash('Error documentos incompletos vuelva a subir los dos documentos')
            return redirect(url_for('subirDocumentos',id=idInforme))
        except Exception as e:
            print("Error al borrar en la base de datos:", str(e)) 
    
    return redirect(url_for('home')) 

def find_and_display_sequence(numbers, target_sequence, following_sequence_length):
    for i in range(len(numbers) - len(target_sequence) - following_sequence_length + 1):
        if numbers[i:i + len(target_sequence)] == target_sequence:
            result_sequence = numbers[i + len(target_sequence):i + len(target_sequence) + following_sequence_length]
            result_sequence = [num for num in result_sequence if num in [0, 1, 2, 5]]
            return result_sequence
    return None

@app.route('/prueba')
def prueba():
    return render_template('prueba.html')

@app.route('/analyze', methods=['POST'])
def analyze_pdf():
    pdf_file = request.files['pdf']
    if pdf_file:
        pdf_data = pdf_file.read()
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()
        if text:
            cleaned_text = re.sub(r'\s+', ' ', text)
            pdf_document.close()
            # Encuentra todos los números en el texto usando expresiones regulares
            numeros_encontrados = re.findall(r'\d+', cleaned_text)
            # Convierte los números de texto a enteros y colócalos en una lista
            numeros_lista = [int(numero) for numero in numeros_encontrados]
            print(numeros_lista)
            secuencia = [3, 1, 0, 2, 1, 2, 3, 8, 8, 2]
            secuencia_encontrada = False
            resultados = []

            for numero in numeros_lista:
                if secuencia_encontrada:
                    resultados.append(numero)
                    if len(resultados) == 4:
                        break
                elif numero == secuencia[0]:
                    secuencia = secuencia[1:]
                    if len(secuencia) == 0:
                        secuencia_encontrada = True

            if secuencia_encontrada:
                print(resultados)

            #Encontrar segundo código
            # Secuencia buscada
            sequence_to_find = resultados

            # Números siguientes que deseas mostrar
            following_sequence_length = 12

            # Encontrar y mostrar la secuencia filtrada
            filtered_sequence = find_and_display_sequence(numeros_lista, sequence_to_find, following_sequence_length)
            if filtered_sequence:
                print("Secuencia encontrada y filtrada")
            else:
                print("Secuencia no encontrada.")
                
            # Elimina las primeras 5 posiciones
            del filtered_sequence[:6]

            print(filtered_sequence)
        else:
            return f'Error archivo no válido debe ser el archivo original'

        
        return render_template('result.html', text=text)
    else:
        return "No se ha seleccionado un archivo PDF."

@app.route('/visualizarExA')
def visualizarExA():
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT informes.informe_id, informes.fecha, informes.hora, empresas.Razon_empresa, empleados.pri_nom, empleados.primer_apellido, empleados.documento FROM informes INNER JOIN empresas ON empresas.empresa_id = informes.empresa_id INNER JOIN empleados ON empleados.empleado_id = informes.empleado_id;")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()

        return render_template('visualizarUsu.html',data=insertObject)
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

def extract_crimes_from_text(text):
    # Definir la expresión regular para buscar cada descripción del delito
    pattern = r"(?:Descripción del Delito\n)((?:[A-Z][A-Z\s]+ \(LEY \d+ DE \d+\)\n?)+)"

    # Buscar todas las coincidencias del patrón en el texto
    matches = re.findall(pattern, text)

    if matches:
        # Obtener todas las descripciones de delitos encontradas y mantener los saltos de línea
        crimes = [match.strip() for match in matches]
        return crimes
    else:
        return []

def extract_text_between_keywords(pdf_path, keyword1, keyword2):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text()

    # Usar expresiones regulares para buscar todas las ocurrencias de las palabras clave con su contexto
    regex = f"(?i)({keyword1})(.*?){keyword2}"
    matches = re.findall(regex, full_text, re.DOTALL)

    return [match[1].strip() for match in matches]

def identificar_texto_entre_frases(texto):
    # Definir el patrón de búsqueda usando expresiones regulares
    patron = r"SIRI Módulo Inhabilidad legal Fecha de inicio Fecha fin(.*?)ADVERTENCIA"

    # Buscar la primera coincidencia en el texto usando el patrón
    match = re.search(patron, texto, re.DOTALL | re.IGNORECASE)

    # Si no se encuentra ninguna coincidencia, retornar None
    if not match:
        return None

    # Obtener el texto encontrado entre las frases
    texto_encontrado = match.group(1).strip()
    return texto_encontrado

def search_text(text, word):
    pattern = rf"\b{re.escape(word)}\b"
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches

def normalize_text(text):
    # Eliminar espacios en blanco al principio y al final del texto
    normalized_text = text.strip()
    # Eliminar espacios en blanco duplicados
    normalized_text = re.sub(r'\s+', ' ', normalized_text)
    return normalized_text

@app.route('/visualizarEvaluacion')
def visualizarEvaluacion():
    id_informe = request.args.get('id')
    print("ID informe: ",id_informe)
    cuantia =[]
    reportado = []
    policia =[]
    cadena_dos = []
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT documentos_adjuntos.documento_id, tipos_documento_adjunto.nom_tipo_doc, tipos_documento_adjunto.tipo_documento_id FROM documentos_adjuntos INNER JOIN tipos_documento_adjunto ON tipos_documento_adjunto.tipo_documento_id = documentos_adjuntos.tipo_documento_adjunto INNER JOIN informes ON informes.informe_id = documentos_adjuntos.informe_id WHERE informes.informe_id = %s;",(id_informe,))
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()

        cursor2=db1.database.cursor()
        cursor2.execute("SELECT * FROM tipos_documento_adjunto")
        myresult2= cursor2.fetchall()
        # pasar as diccionario
        insertObject2=[]
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2: 
            insertObject2.append(dict(zip(columnNames2,record2)))
        cursor2.close() 

        crimes_list=[]

        cursor = db1.database.cursor()
        cursor.execute("SELECT archivo_adjunto FROM documentos_adjuntos WHERE tipo_documento_adjunto=3 AND informe_id=%s",(id_informe,))
        result = cursor.fetchone()
        cursor.close()

        # Verificar si se encontró el registro y extraer el contenido del PDF
        if result:
            pdf_content = result[0]

            # Cargar el contenido del PDF desde un objeto de flujo de bytes (BytesIO)
            with io.BytesIO(pdf_content) as pdf_file:
                # Leer el contenido del PDF utilizando pdfplumber
                with pdfplumber.open(pdf_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text()

                # Extraer los delitos del texto
                crimes_list = extract_crimes_from_text(pdf_text)
                texto_encontrado = identificar_texto_entre_frases(pdf_text)
                if texto_encontrado==None:
                    texto_encontrado = 'NO EXISTE ANOTACIÓN'
                cadena_dos = [f'{texto_encontrado}']
                if crimes_list == []:
                    crimes_list = ['NO EXISTE ANOTACIÓN']
        else:
            print("Registro no encontrado en la base de datos.")

        cursor = db1.database.cursor()
        cursor.execute("SELECT archivo_adjunto FROM documentos_adjuntos WHERE tipo_documento_adjunto=2 AND informe_id=%s",(id_informe,))
        pdf_blob = cursor.fetchone()[0]

        # Ruta temporal para guardar el archivo PDF antes de procesarlo con pdfplumber
        temp_pdf_path = "temp_pdf.pdf"

        # Guardar el contenido del archivo PDF en una ruta temporal
        with open(temp_pdf_path, "wb") as temp_pdf_file:
            temp_pdf_file.write(pdf_blob)

        # Extraer texto entre las palabras clave utilizando la función extract_text_between_keywords
        texts_between_keywords1 = extract_text_between_keywords(temp_pdf_path, "Cuantía", "Entidad")
        texts_between_keywords2 = extract_text_between_keywords(temp_pdf_path, "Reportado por", "Departamento")

        # Cerrar la conexión a la base de datos
        cursor.close()
        # Imprimir resultados
        if texts_between_keywords1:
            for i, text in enumerate(texts_between_keywords1, start=1):
                palabra1 = f"{i}. Cuantía: {text}"
                cuantia.append(palabra1)
        else:
            cuantia = ['NO EXISTE ANOTACIÓN']

        if texts_between_keywords2:
            for i, text in enumerate(texts_between_keywords2, start=1):
                palabra2 = f"{i}. Reportado por: {text}"
                reportado.append(palabra2)
        else:
            reportado = ['NO EXISTE ANOTACIÓN']

        # Eliminar el archivo temporal después de usarlo
        os.remove(temp_pdf_path)

        cursor = db1.database.cursor()
        cursor.execute("SELECT archivo_adjunto FROM documentos_adjuntos WHERE tipo_documento_adjunto=1 AND informe_id=%s",(id_informe,))
        result2 = cursor.fetchone()
        cursor.close()

        # Verificar si se encontró el registro y extraer el contenido del PDF
        if result2:
            pdf_content = result2[0]

            # Cargar el contenido del PDF desde un objeto de flujo de bytes (BytesIO)
            with io.BytesIO(pdf_content) as pdf_file:
                # Leer el contenido del PDF utilizando pdfplumber
                with pdfplumber.open(pdf_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text()

                # Normalizar el texto
                pdf_text = normalize_text(pdf_text)
                # Palabra que se desea buscar
                word_to_search = "TIENE ASUNTOS PENDIENTES CON LAS AUTORIDADES JUDICIALES"
                word= 'EL RESULTADO DE SU CONSULTA NO PUEDE SER GENERADO'
                if pdf_text:
                    # Realizar el análisis
                    found_phrases = search_text(pdf_text, word_to_search)

                    if found_phrases:
                        print("La(s) frase(s) se encontraron en el PDF:")
                        for phrase in found_phrases:
                            palabra = f"NO {phrase}"
                            policia.append(palabra)
                            print(policia)
                    else:
                        print("La frase no se encontró en el PDF.")

                    found_phrases = search_text(pdf_text, word)
                    if found_phrases:
                        print("La(s) frase(s) se encontraron en el PDF:")
                        for phrase in found_phrases:
                            palabra=phrase.upper()
                            policia.append(palabra)
                    else:
                        print("La frase no se encontró en el PDF.")
                else:
                    print("No se encontró el PDF en la base de datos.")
        else:
            print("Registro no encontrado en la base de datos.")
        #Verificación bases de datos 
        #Contadores sancionados
        # URL de la API
        api_url = "https://www.datos.gov.co/resource/fs36-azrv.json"
        # Realiza la solicitud HTTP a la API
        response = requests.get(api_url)
        # Verifica si la solicitud fue exitosa (código de respuesta 200)
        if response.status_code == 200:
            data = response.json()
            
            # Crea un DataFrame a partir de los datos
            df = pd.DataFrame(data)
            
            # Nombre de la columna que deseas buscar y otros nombres de columna a mostrar
            columna_busqueda = "c_dula"
            columna_tipo = "tipo"
            
            # Verifica si la columna de búsqueda existe en el DataFrame
            if columna_busqueda in df.columns:
                # Limpia los valores de la columna de búsqueda quitando las comas y convirtiéndolos a enteros
                df[columna_busqueda] = df[columna_busqueda].str.replace(',', '').astype(int)
                
                # Busca el número en la columna de búsqueda y muestra la fila si se encuentra
                cursor=db1.database.cursor()
                cursor.execute("SELECT empleados.documento FROM informes INNER JOIN empleados ON empleados.empleado_id = informes.empleado_id WHERE informes.informe_id = %s ",(id_informe,))
                myresult= cursor.fetchall()
                numero_buscado = myresult[0][0]
                numero_buscado = int(numero_buscado)
                cursor.close()
                #numero_buscado = 53038673
                fila_encontrada = df.loc[df[columna_busqueda] == numero_buscado]
                
                # Verifica si se encontró la fila
                if not fila_encontrada.empty:
                    # Obtiene los valores de las columnas especificadas para la fila encontrada
                    tipo_valor = fila_encontrada[columna_tipo].values[0]
                else:
                    tipo_valor = 'NO TIENE ANOTACIÓN'
            else:
                print("La columna de búsqueda especificada no existe en el DataFrame.")
        else:
            print("Error al realizar la solicitud HTTP:", response.status_code)
        print('Tipo valor:',tipo_valor)
        #Proveedores ficticios
        # Ruta del archivo PDF
        pdf_path = open('static/archivos/proveedorF.pdf','rb')
        # Número que deseas buscar
        cursor=db1.database.cursor()
        cursor.execute("SELECT empleados.documento FROM informes INNER JOIN empleados ON empleados.empleado_id = informes.empleado_id WHERE informes.informe_id = %s ",(id_informe,))
        myresult= cursor.fetchall()
        numero_buscado1 = myresult[0][0]
        # Función para buscar el número en el contenido del PDF
        def buscar_numero_en_pdf(pdf_path, numero_buscado1):
            texto_encontrado = []
            # Abrir el archivo PDF
            pdf_document = fitz.open(pdf_path)
            # Recorrer cada página del PDF
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text = page.get_text("text")
                # Verificar si el número buscado está en el texto de la página
                if numero_buscado1 in text:
                    texto_encontrado.append(text)
            # Cerrar el archivo PDF
            pdf_document.close()
            return texto_encontrado

        # Buscar el número en el PDF y mostrar el texto encontrado
        texto_encontrado = buscar_numero_en_pdf(pdf_path, numero_buscado1)
        if texto_encontrado:
            proveedorF = 'SE ENCUENTRA EN LA BASE DE DATOS DE PROVEEDORES FICTICIOS'
        else:
            proveedorF = 'NO TIENE ANOTACIÓN'
        #Lista Clinton SDN

        # Ruta del archivo CSV local
        csv_path = open('static/archivos/sdn.csv','rb') # Reemplaza esto con la ruta correcta
        column_names = ["Codigo", "Sujeto", "0", "Pais", "1", "2", "3", "4", "5", "6", "7", "8"]
        df = pd.read_csv(csv_path, names=column_names, header=0)
        # Limpiar los valores en la columna "Sujeto"
        df['Sujeto'] = df['Sujeto'].str.replace('[.,\-\s]', '', regex=True)
        # Convertir el texto en la columna "Sujeto" a mayúsculas
        df['Sujeto'] = df['Sujeto'].str.upper()
        #Consulta base de datos
        cursor=db1.database.cursor()
        cursor.execute("SELECT empleados.pri_nom, empleados.seg_nombre, empleados.primer_apellido, empleados.segundo_apellido FROM informes INNER JOIN empleados ON empleados.empleado_id = informes.empleado_id WHERE informes.informe_id = %s ",(id_informe,))
        myresult = cursor.fetchall()
        cursor.close()
        # Extraer los nombres y apellidos del resultado
        primer_nombre = myresult[0][0]
        segundo_nombre = myresult[0][1]
        primer_apellido = myresult[0][2]
        segundo_apellido = myresult[0][3]

        # Unir los nombres y apellidos en una sola variable
        nombre_completo = f"{primer_nombre} {segundo_nombre} {primer_apellido} {segundo_apellido}"

        # Remover espacios, puntos, comas y guiones
        nombre_completo_sin_caracteres = nombre_completo.replace(' ', '').replace('.', '').replace(',', '').replace('-', '')

        # Filtrar el DataFrame para encontrar filas que contienen "nombre_completo_sin_caracteres" (sin espacios)
        #filtro = df['Sujeto'].str.contains('FADLALLAHSHAYKHMUHAMMADHUSAYN', case=False, na=False)
        #filtro = df['Sujeto'].str.contains('JULIOFABIOURDINOLAGRAJALES', case=False, na=False)
        filtro = df['Sujeto'].str.contains(nombre_completo_sin_caracteres, case=False, na=False)

        # Obtener un nuevo DataFrame con las filas que cumplen el filtro
        df_filtrado = df[filtro]

        # Verificar si se encontraron filas
        if not df_filtrado.empty:
            sdn = 'SE ENCUENTRA EN ESTA LISTA'
        else:
            sdn= 'NO TIENE ANOTACIÓN'
        #Lista clinton sin sdn
        # Ruta del archivo CSV local
        csv_path1 = open('static/archivos/cons_prim.csv','rb') 

        # Nombres de columna personalizados
        column_names1 = ["Codigo", "Sujeto", "0", "Pais", "1", "2", "3", "4", "5", "6", "7", "8"]

        # Leer el CSV desde la ruta local y crear un DataFrame con los nombres de columna personalizados
        df1 = pd.read_csv(csv_path1, names=column_names1, header=0)

        # Limpiar los valores en la columna "Sujeto"
        df1['Sujeto'] = df1['Sujeto'].str.replace('[.,\-\s]', '', regex=True)

        # Convertir el texto en la columna "Sujeto" a mayúsculas
        df1['Sujeto'] = df1['Sujeto'].str.upper()

        filtro1 = df1['Sujeto'].str.contains(nombre_completo_sin_caracteres, case=False, na=False)

        # Obtener un nuevo DataFrame con las filas que cumplen el filtro
        df_filtrado1 = df1[filtro1]

        # Verificar si se encontraron filas
        if not df_filtrado1.empty:
            nosdn='SE ENCUENTRA EN ESTA LISTA'
        else:
            nosdn='NO TIENE ANOTACIÓN'
        #Contratistas sancionados SECOP
        # URL de la API
        api_url = "https://www.datos.gov.co/resource/4n4q-k399.json"

        # Realiza la solicitud HTTP a la API
        response = requests.get(api_url)

        # Verifica si la solicitud fue exitosa (código de respuesta 200)
        if response.status_code == 200:
            data = response.json()

            # Función para limpiar el número de formato
            def limpiar_numero(numero):
                return numero.replace(".", "").replace(" ", "").replace("-", "")
            
            # Número que estás buscando
            #numero_buscado = "9005152801"
            cursor=db1.database.cursor()
            cursor.execute("SELECT empleados.documento FROM informes INNER JOIN empleados ON empleados.empleado_id = informes.empleado_id WHERE informes.informe_id = %s ",(id_informe,))
            myresult= cursor.fetchall()
            numero_buscado2 = myresult[0][0]
            numero_buscado2 = limpiar_numero(numero_buscado2)
            
            encontrado = False

            for fila in data:
                numero_contratista = fila.get("documento_contratista")
                numero_limpiado = limpiar_numero(numero_contratista)
                
                if numero_limpiado == numero_buscado2:
                    fecha_iso = fila.get("fecha_de_publicacion")
                    fecha_normal = datetime.strptime(fecha_iso, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d")
                    contratista = f'{fila.get("numero_de_resolucion")} con fecha de {fecha_normal}'
                    contratista = contratista.upper()
                    encontrado = True
                    break  # Detener el bucle una vez que se encuentra el número
            
            if not encontrado:
                contratista = 'NO TIENE ANOTACIÓN'
            #Lista de sanciones SIC
            # Ruta al archivo PDF
            pdf_path = open('static/archivos/consumidor.pdf','rb') 

            # Función para extraer datos de una tabla en el PDF
            def extract_table_data(pdf_path, page_index=0):
                with pdfplumber.open(pdf_path) as pdf:
                    page = pdf.pages[page_index]
                    table = page.extract_table()
                    return table

            # Función para limpiar texto
            def limpiar_texto(texto):
                return texto.replace(" ", "").replace(".", "").replace(",", "").replace("-", "")

            # Extraer la tabla del PDF
            table_data = extract_table_data(pdf_path)

            # Crear un DataFrame a partir de los datos de la tabla
            df = pd.DataFrame(table_data[1:], columns=table_data[0])

            # Limpiar la columna "Multado"
            df["Multado"] = df["Multado"].apply(limpiar_texto)

            # Buscar la palabra en la columna "Multado"
            #palabra_buscada = "JUANGUILLERMOCAJIAOOTERO"
            
            cursor=db1.database.cursor()
            cursor.execute("SELECT empleados.pri_nom, empleados.seg_nombre, empleados.primer_apellido, empleados.segundo_apellido FROM informes INNER JOIN empleados ON empleados.empleado_id = informes.empleado_id WHERE informes.informe_id = %s ",(id_informe,))
            myresult = cursor.fetchall()
            cursor.close()
            # Extraer los nombres y apellidos del resultado
            primer_nombre = myresult[0][0]
            segundo_nombre = myresult[0][1]
            primer_apellido = myresult[0][2]
            segundo_apellido = myresult[0][3]

            # Unir los nombres y apellidos en una sola variable
            nombre_completo = f"{primer_nombre} {segundo_nombre} {primer_apellido} {segundo_apellido}"
            palabra_buscada = limpiar_texto(nombre_completo)
            
            #palabra_buscada = limpiar_texto(palabra_buscada)
            resultados = df[df["Multado"].str.contains(palabra_buscada, case=False, na=False)]

            # Mostrar los campos de las columnas "Conducta" y "Sector" de los resultados
            if not resultados.empty:
                for index, row in resultados.iterrows():
                    sic = f'{row["Conducta"]} en el sector de {row["Sector"]}'
                    sic = sic.upper()
            else:
                sic = 'NO TIENE ANOTACIÓN'
            #Personas PEP
            # Ruta al archivo Excel (XLSX)
            xlsx_path = open('static/archivos/pep.xlsx','rb') 

            # Abrir el archivo Excel y obtener la segunda hoja
            wb = openpyxl.load_workbook(xlsx_path)
            sheet_name = wb.sheetnames[1]  # El nombre de la segunda hoja
            sheet = wb[sheet_name]

            # Convertir la hoja a un DataFrame de pandas
            data = sheet.values
            columns = next(data)  # La primera fila como encabezados de columna
            df = pd.DataFrame(data, columns=columns)
            # Supongamos que ya tienes tu DataFrame llamado "df"
            #numero_buscado = "79328589"
            cursor=db1.database.cursor()
            cursor.execute("SELECT empleados.documento FROM informes INNER JOIN empleados ON empleados.empleado_id = informes.empleado_id WHERE informes.informe_id = %s ",(id_informe,))
            myresult= cursor.fetchall()
            numero_buscado3 = myresult[0][0]

            # Filtrar el DataFrame para encontrar la coincidencia
            resultado = df[df["NUMERO_DOCUMENTO"] == numero_buscado3]

            # Mostrar los campos correspondientes si hay resultados
            if not resultado.empty:
                for index, row in resultado.iterrows():
                    pep = f'{row["DENOMINACION_CARGO"]} desde {row["FECHA_VINCULACION"]} hasta {row["FECHA_DESVINCULACION"]}'
                    pep = pep.upper()
            else:
                pep = 'NO TIENE ANOTACIÓN'
            # Otra forma de consultar a la lista sdn a través de la cédula
            # Definir la cédula que estás buscando
            # numero_buscado = "29503761"

            # Abrir el archivo CSV
            with open('static/archivos/sdn.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row:
                        cedula_info = row[-1]
                        inicio_cedula = cedula_info.find("Cedula No.")
                        if inicio_cedula != -1:
                            cedula = cedula_info[inicio_cedula + len("Cedula No."):].split()[0]
                            if cedula == str(numero_buscado):
                                sdn = 'SE ENCUENTRA EN ESTA LISTA'
                                break  
        else:
            print("Error al realizar la solicitud HTTP:", response.status_code)
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
        flash('Documentos aún por subir')
    return render_template('visualizar.html',data=insertObject, informe_id=id_informe, data2=insertObject2,
                           crimes=crimes_list,cuantia=cuantia,reportado=reportado,texto=cadena_dos,
                           policia=policia,tipo_valor=tipo_valor,proveedorF=proveedorF,sdn=sdn,nosdn=nosdn,
                           contratista=contratista,sic=sic,pep=pep)

@app.route('/visualizarEDocg',methods=['POST'])
def visualizarEDocg():
    idInforme = request.form['idInforme']
    contenido = request.form.get('contenido', '')
    tipoDoc = request.form.get('tipoItem')
    print("ID informe: ", idInforme)
    print("Contenido: ",contenido)
    print("Tipo documento: ",tipoDoc)
    
    # Crear el archivo PDF usando reportlab
    doc = SimpleDocTemplate("temp_pdf.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    contenido_paragraphs = [Paragraph(contenido, styles['Normal'])]

    doc.build(contenido_paragraphs)

    # Guardar el archivo PDF en la base de datos
    with open("temp_pdf.pdf", "rb") as pdf_file:
        pdf_data = pdf_file.read()
        if idInforme and pdf_data and tipoDoc:
            try:
                cursor = db1.database.cursor()
                sql="INSERT INTO documentos_adjuntos (informe_id,tipo_documento_adjunto,archivo_adjunto) VALUES (%s,%s,%s)"
                data=(idInforme,tipoDoc,pdf_data)
                cursor.execute(sql,data)
                db1.database.commit()
                cursor.close()
            except Exception as e:
                print("Error al insertar en la base de datos:", str(e)) 
    """
    # Guardar el archivo PDF en una carpeta en tu equipo
    ruta_carpeta = "static/archivos"  # Ajusta la ruta a la carpeta deseada
    nombre_archivo = "nombre_archivo.pdf"  # Ajusta el nombre del archivo según tus necesidades

    with open(os.path.join(ruta_carpeta, nombre_archivo), "wb") as f:
        f.write(pdf_data)
    """
    # Eliminar el archivo temporal
    os.remove("temp_pdf.pdf")
    
    return redirect(url_for('visualizarEvaluacion',id=idInforme))  

#Buscar el nombre
def search_word_in_pdf(pdf_file, word):
    reader = PyPDF2.PdfFileReader(pdf_file)
    total_pages = reader.numPages

    for page_number in range(total_pages):
        page = reader.getPage(page_number)
        text = page.extractText()
        if word in text:
            return True  # La palabra se encontró en el PDF
    
    return False  # La palabra no se encontró en el PDF

@app.route('/visualizarEDoc')
def visualizarEDoc():
    id_informe = request.args.get('id')
    print("ID informe: ",id_informe)
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * FROM tipos_documento_adjunto WHERE tipo_documento_id = 1")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

    return render_template('subirDocUsu.html',data=insertObject,id_informe=id_informe)

@app.route('/pdf_blob/<int:id>/<int:id2>/', methods=['GET'])
def get_pdf(id,id2):
    cursor = db1.database.cursor()
    cursor.execute("SELECT archivo_adjunto FROM documentos_adjuntos WHERE tipo_documento_adjunto=%s AND informe_id=%s", (id2,id))
    data = cursor.fetchone()
    cursor.close()

    if data:
        pdf_data = data[0]
        pdf_file = io.BytesIO(pdf_data)
        pdf_file.seek(0)

        #Se llama la función
        file = io.BytesIO(pdf_data)
        file.seek(0)
        word='TIENE'
        found = search_word_in_pdf(file, word)
        if found:
            print("La palabra se encontró en el PDF. "+word)
        else:
            print("La palabra no se encontró en el PDF.")

        return Response(pdf_file, mimetype='application/pdf')
    
    return "Archivo no encontrado"

@app.route('/pdf_blob2/<int:id>/<int:id2>/', methods=['GET'])
def get_pdf2(id,id2):
    cursor = db1.database.cursor()
    cursor.execute("SELECT archivo_adjunto FROM doc_adj_emp WHERE tipo_documento_adjunto=%s AND id_relacion=%s", (id2,id))
    data = cursor.fetchone()
    cursor.close()

    if data:
        pdf_data = data[0]
        pdf_file = io.BytesIO(pdf_data)
        pdf_file.seek(0)

        #Se llama la función
        file = io.BytesIO(pdf_data)
        file.seek(0)

        return Response(pdf_file, mimetype='application/pdf')
    
    return "Archivo no encontrado"

@app.route('/autorizar')
def autorizar():
    id_user = session.get('user_id')
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * FROM empleados WHERE empleado_id <> %s",(id_user,))
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()

        cursor2=db1.database.cursor()
        cursor2.execute("SELECT * FROM empresas")
        myresult2= cursor2.fetchall()
        # pasar as diccionario
        insertObject2=[]
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2: 
            insertObject2.append(dict(zip(columnNames2,record2)))
        cursor2.close()
    except Exception as e:
        flash('Error')
        print("Error al consultar en la base de datos:", str(e))

    return render_template('autorizar.html',data=insertObject,data2=insertObject2)

@app.route('/autorizarg',methods=['POST'])
def autorizarg():
    try:
        seleccion = request.form['seleccion']
        seleccion2 = request.form['seleccion2']
        comentarios = request.form['comentarios']
        today = date.today()
        current_date = today.strftime("%Y-%m-%d")
        if seleccion and seleccion2 and comentarios and current_date:
            #--------------------------OBTENER ID EMPLEADO DEL DATALIST-----------------------------------
            # Dividir el nombre completo en palabras individuales
            palabras = seleccion.split()

            # Obtener los componentes del nombre
            primer_nombre = palabras[0]
            segundo_nombre = palabras[1] if len(palabras) > 1 else ""
            primer_apellido = palabras[-2] if len(palabras) > 2 else ""
            segundo_apellido = palabras[-1] if len(palabras) > 3 else ""

            #Buscar el id del nombre
            cursor=db1.database.cursor()
            # Consulta SQL para seleccionar el ID
            consulta = '''
                SELECT empleado_id FROM empleados WHERE
                pri_nom = %s AND
                seg_nombre = %s AND
                primer_apellido = %s AND
                segundo_apellido = %s
            '''
            # Ejecutar la consulta con los valores de las variables
            cursor.execute(consulta, (primer_nombre, segundo_nombre, primer_apellido, segundo_apellido))

            # Obtener el resultado de la consulta
            resultado = cursor.fetchone()

            # Verificar si se encontró un ID
            if resultado:
                id_encontrado = resultado[0]
                print("ID encontrado:", id_encontrado)
            else:
                print("No se encontró un ID para los componentes del nombre proporcionados.")

            # Cerrar el cursor y la conexión
            cursor.close()
            #-----------------------------------------------------------------------------------#
            #Buscar el id de la empresa
            cursor=db1.database.cursor()
            # Consulta SQL para seleccionar el ID
            consulta = '''
                SELECT empresa_id FROM empresas WHERE
                Razon_empresa = %s
            '''
            # Ejecutar la consulta con los valores de las variables
            cursor.execute(consulta, (seleccion2,))

            # Obtener el resultado de la consulta
            resultado = cursor.fetchone()

            # Verificar si se encontró un ID
            if resultado:
                id_encontrado2 = resultado[0]
                print("ID encontrado de la empresa:", id_encontrado2)
            else:
                print("No se encontró un ID para los componentes del nombre proporcionados.")

            # Cerrar el cursor y la conexión
            cursor.close()
            if id_encontrado and id_encontrado2:
                cursor=db1.database.cursor()
                sql="INSERT INTO empleadoempresa (empleado_id,empresa_id,fecha_veri,comentario) VALUES (%s,%s,%s,%s)"
                data=(id_encontrado,id_encontrado2,current_date,comentarios)
                cursor.execute(sql,data)
                db1.database.commit()
                cursor.close()
                return redirect(url_for('home'))  
        return redirect(url_for('home'))  
    except Exception as e:
        print("Error al insertar en la base de datos:", str(e)) 
        return redirect(url_for('autorizar')) 
    
@app.route('/procesosE')
def procesosE():
    id_empresa = request.args.get('id')
    id_user = session.get('user_id')
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT relacionada.id_relacion, relacionada.fecha_revison, padre.Razon_empresa AS Razon_empresa_padre, hija.Razon_empresa AS Razon_empresa_hija, relacionada.empresa_padre_id FROM relacionada INNER JOIN empresas AS padre ON padre.empresa_id = relacionada.empresa_padre_id INNER JOIN empresas AS hija ON hija.empresa_id = relacionada.empresa_hija_id WHERE relacionada.empresa_hija_id = %s",(id_empresa,))
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
    return render_template('procesosE.html',data=insertObject)
    
@app.route('/subirDocumentosE')
def subirDocumentosE():
    id_informe = request.args.get('id')
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * FROM tipos_documento_adjunto WHERE tipo_documento_id = 2 || tipo_documento_id = 3 || tipo_documento_id = 17;")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

    return render_template('subirDocE.html',data=insertObject,id_informe=id_informe)

@app.route('/subirDocEmg',methods=['POST'])
def subirDocEmg():
    data = request.form
    titulo = data['titulo']
    tarjeta_id = int(data['tarjeta_id'])
    #-----------------------------------------
    archivoPDF = request.files['archivoPDF']
    idInforme = request.form['idInforme']
    archivoPDF = request.files['archivoPDF']
    pdf_data = archivoPDF.read()
    archivoPDF.seek(0)
    print("ID informe: ",idInforme)
    print(f"Datos de tarjeta recibidos: Título: {titulo}, ID: {tarjeta_id}, PDF: {archivoPDF}")
    
    if idInforme and pdf_data and tarjeta_id:
        try:
            
            cursor=db1.database.cursor()
            sql="INSERT INTO doc_adj_emp (id_relacion,tipo_documento_adjunto,archivo_adjunto) VALUES (%s,%s,%s)"
            data=(idInforme,tarjeta_id,pdf_data)
            cursor.execute(sql,data)
            db1.database.commit()
            cursor.close()
            
        except Exception as e:
            print("Error al insertar en la base de datos:", str(e)) 
    
    return redirect(url_for('subirDocumentosE',id=idInforme)) 

@app.route('/comprobarTE',methods=['POST'])
def comprobarTE():
    idInforme = request.form['idInforme']
    cursor=db1.database.cursor()
    cursor.execute("SELECT COUNT(id_relacion) FROM `doc_adj_emp` WHERE id_relacion= %s;",(idInforme,))
    myresult= cursor.fetchall()
    cursor.close()
    if myresult[0][0]<3:
        try:
            cursor = db1.database.cursor()
            sql = "DELETE FROM doc_adj_emp WHERE id_relacion = %s"
            cursor.execute(sql, (idInforme,))
            db1.database.commit()
            cursor.close()
            flash('Error documentos incompletos vuelva a subir los dos documentos')
            return redirect(url_for('subirDocumentos',id=idInforme))
        except Exception as e:
            print("Error al borrar en la base de datos:", str(e)) 
    
    return redirect(url_for('home')) 

@app.route('/visualizarEmxA')
def visualizarEmxA():
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT relacionada.id_relacion, relacionada.fecha_revison, padre.Razon_empresa AS Razon_empresa_padre, hija.Razon_empresa AS Razon_empresa_hija,hija.Numero_Documento AS documento FROM relacionada INNER JOIN empresas AS padre ON padre.empresa_id = relacionada.empresa_padre_id INNER JOIN empresas AS hija ON hija.empresa_id = relacionada.empresa_hija_id;")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()

        return render_template('visualizarEm.html',data=insertObject)
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 

@app.route('/visualizarEvaluacionEm')
def visualizarEvaluacionEm():
    id_informe = request.args.get('id')
    print("ID informe: ",id_informe)
    cuantia =[]
    reportado = []
    policia =[]
    cadena_dos = []
    insertObject=[]
    insertObject2=[]
    proveedorF = '' 
    sdn=''
    nosdn=''
    contratista=''
    sic=''
    try:
        
        cursor=db1.database.cursor()
        cursor.execute("SELECT doc_adj_emp.doc_emp_id, tipos_documento_adjunto.nom_tipo_doc, tipos_documento_adjunto.tipo_documento_id FROM doc_adj_emp INNER JOIN tipos_documento_adjunto ON tipos_documento_adjunto.tipo_documento_id = doc_adj_emp.tipo_documento_adjunto INNER JOIN relacionada ON relacionada.id_relacion = doc_adj_emp.id_relacion WHERE relacionada.id_relacion = %s;",(id_informe,))
        myresult= cursor.fetchall()
        # pasar as diccionario
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
            print('insertObject:',insertObject)
        cursor.close()

        cursor2=db1.database.cursor()
        cursor2.execute("SELECT * FROM tipos_documento_adjunto")
        myresult2= cursor2.fetchall()
        # pasar as diccionario
        columnNames2=[column2[0] for column2 in cursor2.description]
        for record2 in myresult2: 
            insertObject2.append(dict(zip(columnNames2,record2)))
        cursor2.close() 

        crimes_list=[]

        cursor = db1.database.cursor()
        cursor.execute("SELECT archivo_adjunto FROM doc_adj_emp WHERE tipo_documento_adjunto=3 AND id_relacion=%s",(id_informe,))
        result = cursor.fetchone()
        cursor.close()

        # Verificar si se encontró el registro y extraer el contenido del PDF
        if result:
            pdf_content = result[0]

            # Cargar el contenido del PDF desde un objeto de flujo de bytes (BytesIO)
            with io.BytesIO(pdf_content) as pdf_file:
                # Leer el contenido del PDF utilizando pdfplumber
                with pdfplumber.open(pdf_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text()

                # Extraer los delitos del texto
                patron = r'Fin(.*?)Instancia'
                frases_entre_fin_instancia = re.findall(patron, pdf_text, re.DOTALL)
                for i, frase in enumerate(frases_entre_fin_instancia, start=1):
                    frasec = f'{i}. {frase.strip()}'
                    cadena_dos.append(frasec)

                if cadena_dos == []:
                    cadena_dos = ['NO EXISTE ANOTACIÓN']
                if crimes_list == []:
                    crimes_list = ['NO EXISTE ANOTACIÓN']
        else:
            print("Registro no encontrado en la base de datos.")

        cursor = db1.database.cursor()
        cursor.execute("SELECT archivo_adjunto FROM doc_adj_emp WHERE tipo_documento_adjunto=2 AND id_relacion=%s",(id_informe,))
        pdf_blob = cursor.fetchone()[0]

        # Ruta temporal para guardar el archivo PDF antes de procesarlo con pdfplumber
        temp_pdf_path = "temp_pdf.pdf"

        # Guardar el contenido del archivo PDF en una ruta temporal
        with open(temp_pdf_path, "wb") as temp_pdf_file:
            temp_pdf_file.write(pdf_blob)

        # Extraer texto entre las palabras clave utilizando la función extract_text_between_keywords
        texts_between_keywords1 = extract_text_between_keywords(temp_pdf_path, "Cuantía", "Entidad")
        texts_between_keywords2 = extract_text_between_keywords(temp_pdf_path, "Reportado por", "Departamento")

        # Cerrar la conexión a la base de datos
        cursor.close()
        # Imprimir resultados
        if texts_between_keywords1:
            for i, text in enumerate(texts_between_keywords1, start=1):
                palabra1 = f"{i}. Cuantía: {text}"
                cuantia.append(palabra1)
        else:
            cuantia = ['NO EXISTE ANOTACIÓN']

        if texts_between_keywords2:
            for i, text in enumerate(texts_between_keywords2, start=1):
                palabra2 = f"{i}. Reportado por: {text}"
                reportado.append(palabra2)
        else:
            reportado = ['NO EXISTE ANOTACIÓN']

        # Eliminar el archivo temporal después de usarlo
        import os
        os.remove(temp_pdf_path)

        #Proveedores ficticios
        # Ruta del archivo PDF
        pdf_path = os.path.join(app.root_path, 'static', 'archivos', 'proveedorF.pdf')
        try:
            cursor=db1.database.cursor()
            cursor.execute("SELECT empresas.Numero_Documento FROM relacionada INNER JOIN empresas ON empresas.empresa_id = relacionada.empresa_hija_id WHERE relacionada.id_relacion= %s ",(id_informe,))
            myresult= cursor.fetchall()
            numero_buscado = myresult[0][0]
        except Exception as e:
            print("Error en la base de datos: ",e)
        # Número que deseas buscar
        #numero_buscado = "801004345"

        # Función para buscar el número en el contenido del PDF
        def buscar_numero_en_pdf(pdf_path, numero_buscado):
            texto_encontrado = []

            # Abrir el archivo PDF
            pdf_document = fitz.open(pdf_path)

            # Recorrer cada página del PDF
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text = page.get_text("text")

                # Verificar si el número buscado está en el texto de la página
                if numero_buscado in text:
                    texto_encontrado.append(text)

            # Cerrar el archivo PDF
            pdf_document.close()

            return texto_encontrado

        # Buscar el número en el PDF y mostrar el texto encontrado
        texto_encontrado = buscar_numero_en_pdf(pdf_path, numero_buscado)
        if texto_encontrado:
            print("Texto encontrado en el PDF:",numero_buscado)
            proveedorF='SE ENCUENTRA EN LA BASE DE DATOS DE PROVEEDORES FICTICIOS'
        else:
            print("Número no encontrado en el PDF.")
            proveedorF='NO TIENE ANOTACIÓN'

        #Lista Clinton CDN

        # Ruta del archivo CSV local
        csv_path = open('static/archivos/sdn.csv','rb') # Reemplaza esto con la ruta correcta
        # Nombres de columna personalizados
        column_names = ["Codigo", "Sujeto", "0", "Pais", "1", "2", "3", "4", "5", "6", "7", "8"]
        # Leer el CSV desde la ruta local y crear un DataFrame con los nombres de columna personalizados
        df = pd.read_csv(csv_path, names=column_names, header=0)
        # Limpiar los valores en la columna "Sujeto"
        df['Sujeto'] = df['Sujeto'].str.replace('[.,\-\s]', '', regex=True)
        # Convertir el texto en la columna "Sujeto" a mayúsculas
        df['Sujeto'] = df['Sujeto'].str.upper()
        #Consulta base de datos
        cursor=db1.database.cursor()
        cursor.execute("SELECT empresas.Razon_empresa FROM relacionada INNER JOIN empresas ON empresas.empresa_id = relacionada.empresa_hija_id WHERE relacionada.id_relacion=%s ",(id_informe,))
        myresult = cursor.fetchall()
        cursor.close()
        # Extraer los nombres y apellidos del resultado
        empresa_nombre = myresult[0][0]

        # Unir los nombres y apellidos en una sola variable
        nombre_completo = f"{empresa_nombre}"

        # Remover espacios, puntos, comas y guiones
        nombre_completo_sin_caracteres = nombre_completo.replace(' ', '').replace('.', '').replace(',', '').replace('-', '')

        # Filtrar el DataFrame para encontrar filas que contienen "nombre_completo_sin_caracteres" (sin espacios)
        #filtro = df['Sujeto'].str.contains('FADLALLAHSHAYKHMUHAMMADHUSAYN', case=False, na=False)
        filtro = df['Sujeto'].str.contains(nombre_completo_sin_caracteres, case=False, na=False)

        # Obtener un nuevo DataFrame con las filas que cumplen el filtro
        df_filtrado = df[filtro]

        # Verificar si se encontraron filas
        if not df_filtrado.empty:
            sdn = 'SE ENCUENTRA EN ESTA LISTA'
        else:
            sdn= 'NO TIENE ANOTACIÓN'
        #Lista clinton sin sdn
        # Ruta del archivo CSV local
        csv_path1 = open('static/archivos/cons_prim.csv','rb') # Reemplaza esto con la ruta correcta

        # Nombres de columna personalizados
        column_names1 = ["Codigo", "Sujeto", "0", "Pais", "1", "2", "3", "4", "5", "6", "7", "8"]

        # Leer el CSV desde la ruta local y crear un DataFrame con los nombres de columna personalizados
        df1 = pd.read_csv(csv_path1, names=column_names1, header=0)

        # Limpiar los valores en la columna "Sujeto"
        df1['Sujeto'] = df1['Sujeto'].str.replace('[.,\-\s]', '', regex=True)

        # Convertir el texto en la columna "Sujeto" a mayúsculas
        df1['Sujeto'] = df1['Sujeto'].str.upper()

        filtro1 = df1['Sujeto'].str.contains(nombre_completo_sin_caracteres, case=False, na=False)

        # Obtener un nuevo DataFrame con las filas que cumplen el filtro
        df_filtrado1 = df1[filtro1]

        # Verificar si se encontraron filas
        if not df_filtrado1.empty:
            nosdn='SE ENCUENTRA EN ESTA LISTA'
        else:
            nosdn='NO TIENE ANOTACIÓN'
        #Contratistas sancionados SECOP
        # URL de la API
        api_url = "https://www.datos.gov.co/resource/4n4q-k399.json"

        # Realiza la solicitud HTTP a la API
        response = requests.get(api_url)

        # Verifica si la solicitud fue exitosa (código de respuesta 200)
        if response.status_code == 200:
            data = response.json()

            # Función para limpiar el número de formato
            def limpiar_numero(numero):
                return numero.replace(" ", "").replace(".", "").replace(",", "").replace("-", "")
            
            # Número que estás buscando
            #numero_buscado2 = "9005152801"
            cursor=db1.database.cursor()
            cursor.execute("SELECT empresas.Numero_Documento FROM relacionada INNER JOIN empresas ON empresas.empresa_id = relacionada.empresa_hija_id WHERE relacionada.id_relacion= %s ",(id_informe,))
            myresult= cursor.fetchall()
            numero_buscado2 = myresult[0][0]
            numero_buscado2 = limpiar_numero(numero_buscado2)
            encontrado = False

            for fila in data:
                numero_contratista = fila.get("documento_contratista")
                numero_limpiado = limpiar_numero(numero_contratista)
                
                if numero_limpiado == numero_buscado2:
                    fecha_iso = fila.get("fecha_de_publicacion")
                    fecha_normal = datetime.strptime(fecha_iso, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d")
                    contratista = f'{fila.get("numero_de_resolucion")} con fecha de {fecha_normal}'
                    contratista = contratista.upper()
                    encontrado = True
                    break  # Detener el bucle una vez que se encuentra el número
            
            if not encontrado:
                contratista = 'NO TIENE ANOTACIÓN'
            #Lista de sanciones SIC
            # Ruta al archivo PDF
            pdf_path = open('static/archivos/consumidor.pdf','rb') 

            # Función para extraer datos de una tabla en el PDF
            def extract_table_data(pdf_path, page_index=0):
                with pdfplumber.open(pdf_path) as pdf:
                    page = pdf.pages[page_index]
                    table = page.extract_table()
                    return table

            # Función para limpiar texto
            def limpiar_texto(texto):
                return texto.replace(" ", "").replace(".", "").replace(",", "").replace("-", "")

            # Extraer la tabla del PDF
            table_data = extract_table_data(pdf_path)

            # Crear un DataFrame a partir de los datos de la tabla
            df = pd.DataFrame(table_data[1:], columns=table_data[0])

            # Limpiar la columna "Multado"
            df["Multado"] = df["Multado"].apply(limpiar_texto)

            # Buscar la palabra en la columna "Multado"
            #palabra_buscada = "CHALLENGERSAS"
            
            cursor=db1.database.cursor()
            cursor.execute("SELECT empresas.Razon_empresa FROM relacionada INNER JOIN empresas ON empresas.empresa_id = relacionada.empresa_hija_id WHERE relacionada.id_relacion=%s ",(id_informe,))
            myresult = cursor.fetchall()
            cursor.close()
            # Extraer los nombres y apellidos del resultado
            empresa_nombre = myresult[0][0]

            # Unir los nombres y apellidos en una sola variable
            nombre_completo = f"{empresa_nombre}"
            palabra_buscada = limpiar_texto(nombre_completo)
            
            #palabra_buscada = limpiar_texto(palabra_buscada)
            resultados = df[df["Multado"].str.contains(palabra_buscada, case=False, na=False)]

            # Mostrar los campos de las columnas "Conducta" y "Sector" de los resultados
            if not resultados.empty:
                for index, row in resultados.iterrows():
                    sic = f'{row["Conducta"]} en el sector de {row["Sector"]}'
                    sic = sic.upper()
            else:
                sic = 'NO TIENE ANOTACIÓN'
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
        flash('Documentos aún por subir')
    return render_template('visualizarE.html',data=insertObject, informe_id=id_informe, data2=insertObject2,
                           crimes=crimes_list,cuantia=cuantia,reportado=reportado,texto=cadena_dos,policia=policia,
                           proveedor=proveedorF,sdn=sdn,nosdn=nosdn,contratista=contratista,sic=sic)

@app.route('/tipoadj')
def iniciar():
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * FROM tipos_documento_adjunto")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()
        return render_template('tipoadjun.html',data=insertObject)
    except Exception as e:
        print("Error al consultar la base de datos:", str(e)) 
        return render_template('homeA.html')

@app.route('/gtipoadjun',methods=['POST'])
def guardartipoadjun():
    try:
        Nomtipo_documento=[]
        Nomtipo_documento.append(request.form['tipo_documento'])
        #print(Nomtipo_documento)
        if Nomtipo_documento:
            cursor=db1.database.cursor()
            sql="INSERT INTO tipos_documento_adjunto (nom_tipo_doc) VALUES (%s)"
            data=(Nomtipo_documento)
            cursor.execute(sql,data)
            db1.database.commit()
        return redirect(url_for('iniciar'))  
    except Exception as e:
        print("Error al insertar en la base de datos:", str(e)) 

@app.route('/boradjunto/<int:id>')
def borraradjun(id):   
    try: 
        cursor = db1.database.cursor()
        sql = "DELETE FROM tipos_documento_adjunto WHERE tipo_documento_id = %s"
        cursor.execute(sql, (id,))
        db1.database.commit()
        return redirect(url_for('iniciar'))
    except Exception as e:
        print("Error al borrar en la base de datos:", str(e)) 


@app.route('/editadjunto/<int:id>', methods=['POST'])
def editaradjun(id):
    try:
        Editadjunto = request.form['tipo_documento']
        print(Editadjunto, id)
        if Editadjunto:
            cursor = db1.database.cursor()
            sql = "UPDATE tipos_documento_adjunto SET nom_tipo_doc = %s WHERE tipo_documento_id = %s"
            data = (Editadjunto, id)
            cursor.execute(sql, data)
            db1.database.commit()
        return redirect(url_for('iniciar'))
    except Exception as e:
        print("Error al editar en la base de datos:", str(e)) 

#termina los procesos para administrar datos de los documentos adjuntos

#procesos preguntas
#INSERT INTO `preguntas`(`pregunta_id`, `enunciado`, `fecha_creada`) VALUES ('[value-1]','[value-2]','[value-3]')
@app.route('/listpreg')
def iniciarpre():
    try:
        cursor=db1.database.cursor()
        cursor.execute("SELECT * FROM preguntas")
        myresult= cursor.fetchall()
        # pasar as diccionario
        insertObject=[]
        columnNames=[column[0] for column in cursor.description]
        for record in myresult: 
            insertObject.append(dict(zip(columnNames,record)))
        cursor.close()
        return render_template('autopreg.html',data=insertObject)
    except Exception as e:
        print("Error al consultar en la base de datos:", str(e)) 
        return render_template('homeA.html')

@app.route('/guardarpregru',methods=['POST'])
def guardarpreg():
    try:
        NPregunta=[]
        NPregunta.append(request.form['enunciado'])
        today = date.today()
        current_date = today.strftime("%Y-%m-%d")
        NPregunta.append(current_date)
        print(NPregunta)
        #print(Nomtipo_documento)
        if NPregunta:
            cursor=db1.database.cursor()
            sql="INSERT INTO preguntas (enunciado, fecha_creada) VALUES (%s,%s)"
            data=(NPregunta)
            cursor.execute(sql,data)
            db1.database.commit()
        return redirect(url_for('iniciarpre'))  
    except Exception as e:
        print("Error al insertar en la base de datos:", str(e)) 

@app.route('/borrarpreg/<int:id>')
def borrarpreg(id):  
    try:  
        cursor = db1.database.cursor()
        sql = "DELETE FROM preguntas WHERE pregunta_id = %s"
        cursor.execute(sql, (id,))
        db1.database.commit()
        return redirect(url_for('iniciarpre'))
    except Exception as e:
        print("Error al borrar en la base de datos:", str(e)) 

@app.route('/editarpreg/<int:id>', methods=['POST'])
def editarpreg(id):
    try:
        Editadpreg = request.form['PPregunta']
        print(Editadpreg, id)
        if Editadpreg:
            cursor = db1.database.cursor()
            sql = "UPDATE preguntas SET enunciado = %s WHERE pregunta_id = %s"
            data = (Editadpreg, id)
            cursor.execute(sql, data)
            db1.database.commit()
        return redirect(url_for('iniciarpre'))
    except Exception as e:
        print("Error al editar en la base de datos:", str(e)) 

#termina los procesos para administrar datos de los documentos adjuntos


#termina procesos preguntas




#cualqueir pagina que no este en las rutas es direccionada hacia status_401
@app.route('/protected')
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Página no encontrada</h1>", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])
    #csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(port=3000)
 
 #termina bloque de servidor
    
    #https://youtu.be/Zfpbnmdi-pE
    #<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    
    