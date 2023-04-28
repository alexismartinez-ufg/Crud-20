#Importar librerias (PUNTO 5)
import mysql.connector
import re
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from typing import Optional


#Modelo de tabla usuarios   
class Usuario(BaseModel):
    IdUsuario: Optional[int]=None
    Nombre: Optional[str]=None 
    Apellido: Optional[str]=None
    Correo: Optional[str]=None
    FechaCreacion: Optional[str]=None
    Telefono: Optional[str]=None

    
# Expresión regular para validar el correo
correo_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

fecha_regex = r'^\d{4}-\d{2}-\d{2}'

#Guardar la conexión a la base de datos en una variable (PUNTO 6)
mySqlConexion = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="crud20%"
)

#Esta es una instancia de FastAPI, es lo que levanta la api en local :D
app = FastAPI()

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return JSONResponse(get_openapi(title="Parcial 20%", version="1.0.0", routes=app.routes))

@app.get("/docs", include_in_schema=False)
async def get_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="documentación")


#Recomiendo siempre dejar un endpoint para la ruta "/" ya que
#En esta ruta se carga siempre nuestra api y si no defines algo 
#Te mostrara un mensaje de error feo y aquí nada más feo que python
@app.get("/", include_in_schema=False)
async def root():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="documentación")

#Endpoint GET todos los usuarios (PUNTO 7)
@app.get("/usuarios")
def get_usuarios():
    
    #Crear un cursor para ejecutar consultas SQL
    cursor = mySqlConexion.cursor()

    #Ejecutar una consulta SQL para seleccionar todos los usuarios
    query = "SELECT * FROM Usuarios"
    cursor.execute(query)

    #Obtener los resultados de la consulta
    resultados = cursor.fetchall()

    #Cerrar el cursor y la conexión a la base de datos
    cursor.close()

    #Convertir los objetos datetime.date en cadenas de texto, esto se hace ya que en caso de
    #no hacer esta conversión obtendremos una excepción fea del siguiente tipo
    #TypeError: Object of type date is not JSON serializable
    usuarios = [
        {
            "IdUsuario": usuario[0],
            "Nombre": usuario[1],
            "Apellido": usuario[2],
            "Correo": usuario[3],
            "FechaCreacion": str(usuario[4]),
            "Telefono": usuario[5]
        }
        for usuario in resultados
    ]

    #Devolver los usuarios como una respuesta JSON
    #return JSONResponse(content=usuarios)
    return JSONResponse(content=usuarios)

#Endpoint GET un usuario por id (PUNTO 10)
@app.get("/usuarios/{id_usuario}")
def get_usuarioById(id_usuario):

    try:
        id_usuario = int(id_usuario)
    except ValueError:
        return JSONResponse(status_code=400, content={"mensaje": "El ID de usuario debe ser un número entero"})

    
    #Crear un cursor para ejecutar consultas SQL
    cursor = mySqlConexion.cursor()

    #Ejecutar una consulta SQL para seleccionar el usuario con el id especificado
    query = "SELECT * FROM Usuarios WHERE IdUsuario = %s"
    cursor.execute(query, (id_usuario,))

    #Obtener el resultado de la consulta
    resultado = cursor.fetchone()

    #Cerrar el cursor y la conexión a la base de datos
    cursor.close()

    if resultado is None:
        #Si no se encontró ningún usuario con el id especificado, devolver un error 404
        return JSONResponse(status_code=404, content={"mensaje": "Usuario no encontrado"})
    else:
        #Si se encontró el usuario, devolver la información como una respuesta JSON
        usuario = {
            "IdUsuario": resultado[0],
            "Nombre": resultado[1],
            "Apellido": resultado[2],
            "Correo": resultado[3],
            "FechaCreacion": str(resultado[4]),
            "Telefono": resultado[5]
        }
        return JSONResponse(content=usuario)
    

# Endpoint para editar un usuario
@app.put("/usuarios/{id_usuario}")
def actualizar_usuario(id_usuario, usuario: Usuario):

    try:
        id_usuario = int(id_usuario)
    except ValueError:
        return JSONResponse(status_code=400, content={"mensaje": "El ID de usuario debe ser un número entero"})

    try:
        # Crear un cursor para ejecutar consultas SQL
        cursor = mySqlConexion.cursor()

        if usuario.Correo is None or usuario.Correo == '':
            return JSONResponse(status_code=400, content={"error": f"El correo es requerido"})
        
        if not re.match(fecha_regex, usuario.FechaCreacion):
            return JSONResponse(status_code=400, content={"error": f"La fecha no es correcta"})

        if re.match(correo_regex, usuario.Correo):
            # Validar que el correo no esté registrado ya en la base de datos
            query = "SELECT Correo FROM Usuarios WHERE Correo = %s and IdUsuario != %s"
            cursor.execute(query, (usuario.Correo, id_usuario,))
            resultado = cursor.fetchone()
        else:
            return JSONResponse(status_code=400, content={"error": f"{usuario.Correo} no es un correo electrónico válido"})

        if resultado:
            # El correo ya está registrado en la base de datos, devolver un error
            return JSONResponse(status_code=400, content={"error": f"El correo {usuario.Correo} ya está registrado"})


        # Extraer los datos del objeto usuario
        id = id_usuario
        nombre = usuario.Nombre
        apellido = usuario.Apellido
        email = usuario.Correo
        FechaCreacion = usuario.FechaCreacion
        telefono = usuario.Telefono

        if nombre == '' or nombre == None or apellido == '' or apellido == None or FechaCreacion == '' or FechaCreacion== None or telefono == '' or telefono == None:
            return JSONResponse(status_code=400, content={"error": f"Faltan datos requeridos"})

        # Ejecutar una consulta SQL para actualizar la información del usuario
        query = "UPDATE Usuarios SET Nombre=%s, Apellido=%s, Correo=%s, FechaCreacion=%s, Telefono=%s WHERE IdUsuario=%s"
        values = (nombre, apellido, email, FechaCreacion, telefono, id)
        cursor.execute(query, values)

        # Guardar los cambios en la base de datos
        mySqlConexion.commit()

        # Cerrar el cursor y la conexión a la base de datos
        cursor.close()

        # Devolver una respuesta JSON indicando que el usuario ha sido actualizado
        return JSONResponse(content={"mensaje": f"El usuario con id {id} ha sido actualizado"})
    except:
        return JSONResponse(status_code=404, content={"error": f"el usuario no pudo ser actualizado"})


@app.post("/usuarios")
def agregar_usuario(usuario: Usuario):

    try:
        # Crear un cursor para ejecutar consultas SQL
        cursor = mySqlConexion.cursor()

        if usuario.Correo is None or usuario.Correo == '':
            return JSONResponse(status_code=400, content={"error": f"El correo es requerido"})
        
        if not re.match(fecha_regex, usuario.FechaCreacion):
            return JSONResponse(status_code=400, content={"error": f"La fecha no es correcta"})

        if re.match(correo_regex, usuario.Correo):
            # Validar que el correo no esté registrado ya en la base de datos
            query = "SELECT Correo FROM Usuarios WHERE Correo = %s"
            cursor.execute(query, (usuario.Correo,))
            resultado = cursor.fetchone()
        else:
            return JSONResponse(status_code=400, content={"error": f"{usuario.Correo} no es un correo electrónico válido"})

        if resultado:
            # El correo ya está registrado en la base de datos, devolver un error
            return JSONResponse(status_code=400, content={"error": f"El correo {usuario.Correo} ya está registrado"})

        # Extraer los datos del objeto usuario
        id = usuario.IdUsuario
        nombre:str = usuario.Nombre
        apellido:str = usuario.Apellido
        email:str = usuario.Correo
        FechaCreacion:str = usuario.FechaCreacion
        telefono:str = usuario.Telefono

        if nombre == '' or nombre == None or apellido == '' or apellido == None or FechaCreacion == '' or FechaCreacion== None or telefono == '' or telefono == None:
            return JSONResponse(status_code=400, content={"error": f"Faltan datos requeridos"})

        # Ejecutar una consulta SQL para insertar el nuevo usuario en la tabla Usuarios
        query = "INSERT INTO Usuarios (Nombre, Apellido, Correo, FechaCreacion, Telefono) VALUES (%s, %s, %s, %s, %s)"
        values = (nombre, apellido, email, FechaCreacion, telefono)
        cursor.execute(query, values)

        # Guardar los cambios en la base de datos
        mySqlConexion.commit()

        # Cerrar el cursor y la conexión a la base de datos
        cursor.close()

        # Devolver una respuesta JSON indicando que el usuario ha sido agregado
        return JSONResponse(content={"mensaje": f"El usuario ha sido agregado"})
    except Exception as e:
        # Manejar la excepción aquí
        return JSONResponse(status_code=500, content={"error": f"No se pudo agregar el usuario, {e}"})



#Endpoint para eliminar usuario
@app.delete("/usuarios/{id_usuario}")
def eliminar_usuario(id_usuario):

    try:
        id_usuario = int(id_usuario)
    except ValueError:
        return JSONResponse(status_code=400, content={"mensaje": "El ID de usuario debe ser un número entero"})

    try:
        # Crear un cursor para ejecutar consultas SQL
        cursor = mySqlConexion.cursor()

        # Ejecutar una consulta SQL para eliminar el usuario con el id especificado
        query = "DELETE FROM Usuarios WHERE IdUsuario = %s"
        cursor.execute(query, (id_usuario,))

        # Guardar los cambios en la base de datos
        mySqlConexion.commit()

        # Cerrar el cursor y la conexión a la base de datos
        cursor.close()

        # Devolver una respuesta JSON indicando que el usuario ha sido eliminado
        return JSONResponse(content={"mensaje": f"El usuario con id {id_usuario} ha sido eliminado"})
    except:
        return JSONResponse(status_code=404, content={"error": f"El usuario con id {id_usuario} no pudo ser eliminado"})
