#Importar librerias (PUNTO 5)
import mysql.connector
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html


#Modelo de tabla usuarios   
class Usuario(BaseModel):
    IdUsuario: int
    Nombre: str
    Apellido: str
    Correo: str
    FechaCreacion: str
    Telefono: str

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
    return JSONResponse(get_openapi(title="Tu API", version="0.0.1", routes=app.routes))

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
def get_usuarioById(id_usuario: int):
    
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
@app.put("/usuarios")
def actualizar_usuario(usuario: Usuario):

    try:
        # Crear un cursor para ejecutar consultas SQL
        cursor = mySqlConexion.cursor()

        # Extraer los datos del objeto usuario
        id = usuario.IdUsuario
        nombre = usuario.Nombre
        apellido = usuario.Apellido
        email = usuario.Correo
        FechaCreacion = usuario.FechaCreacion
        telefono = usuario.Telefono

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


# Endpoint para agregar un usuario
@app.post("/usuarios")
def agregar_usuario(usuario: Usuario):

    try:
        # Crear un cursor para ejecutar consultas SQL
        cursor = mySqlConexion.cursor()

        # Extraer los datos del objeto usuario
        id = usuario.IdUsuario
        nombre = usuario.Nombre
        apellido = usuario.Apellido
        email = usuario.Correo
        FechaCreacion = usuario.FechaCreacion
        telefono = usuario.Telefono

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
    except:
        return JSONResponse(status_code=404, content={"error": f"el usuario no pudo ser agregado"})
    
    # Endpoint DELETE para eliminar un usuario


#Endpoint para eliminar usuario
@app.delete("/usuarios/{id_usuario}")
def eliminar_usuario(id_usuario: int):
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
