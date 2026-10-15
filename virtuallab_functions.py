# Se deben codificar las siguientes funciones y replicar la funcionalidad descrita en los comentarios
# Además, para la gestión de usuarios y prácticas de laboratorio se debe hacer uso de archivos de texto no se permite
# el uso de motores de bases de datos

import json
import os
from json import dumps # Convertir diccionario a JSON
from json import loads # Convertir JSON a diccionario

usersFile = "server/users.txt"

def writeUserDataToFile(user_data):
    with open(usersFile, "a") as file:
        file.write(dumps(user_data) + "\n")

# Función para registrar un usuario con nombre name, identificador id, rol role y contraseña password.
# Registra el usuario en el sistema si el id del usuario no existe previamente. Si el usuario se pudo registrar debe retornar "User {name} with role {role} registered" de lo contrario
# debe retornar "User already registered"
def registerUser(name,id,role,password):
    
    try:
        file=open(usersFile, "r")        

    except FileNotFoundError:
        #Archivo no existe
        print("File not found, creating a new one.")
         
                      
    else:
        with file:
            lines=file.readlines()
            for line in lines:
                user=loads(line)
                if user["id"]==id:
                    response="User already registered"
                    print(response)
                    return response

    
    #######################################
    user_data = {
        "name": name,
        "id": id,
        "role": role,
        "password": password
    }

    writeUserDataToFile(user_data)
    response=f"User {name} with role {role} registered"
    print(response)
    return response
            




            

# Función que abre una sesión
# Abre una sesión del usuario 
# lo hace si el id del usuario y la contraseña son correctos
# Si la sesión se pudo abrir debe retornar "Session was succesfully opened" de lo contrario
# debe retornar "error"


def openSession(id, password):
    try:
        file = open(usersFile, "r")
    except FileNotFoundError:
        return "error"
    else:
        with file:
            lines = file.readlines()
            for line in lines:
                user = loads(line)
                if str(user["id"]) == str(id) and user["password"] == password:
                    # No duplicar una sesión que ya está abierta.
                    try:
                        with open("server/sessions.txt", "r") as f_session:
                            session_open = any(
                                loads(session_line)["id"] == str(id)
                                for session_line in f_session if session_line.strip()
                            )
                    except FileNotFoundError:
                        session_open = False

                    if not session_open:
                        with open("server/sessions.txt", "a") as f_session:
                            f_session.write(dumps({"id": str(id)}) + "\n")

                    response = "Session was succesfully opened"
                    print(response)
                    return response

    response = "error"
    print(response)
    return response



# Función que cierra una sesión
# Cierra una sesión del usuario
# Si la sesión se pudo cerrar debe retornar "Session was succesfully closed" de lo contrario
# debe retornar "error"
#def closeSession(id):
    response=f"closeSession called by user {id}"
    print(response)
    return response


# Función que cierra una sesión
# Cierra una sesión del usuario
# Si la sesión se pudo cerrar debe retornar "Session was succesfully closed" de lo contrario
# debe retornar "error"
def closeSession(id):
    try:
        file=open("server/sessions.txt", "r")

    except FileNotFoundError:
        return "error"

    else:
        with file:
            lines=file.readlines()

        for line in lines:
            session=loads(line)
            if session["id"]==str(id):
                lines.remove(line)
                with open("server/sessions.txt", "w") as file:
                    file.writelines(lines)

                response="Session was succesfully closed"
                print(response)
                return response

    response="error"
    print(response)
    return response


# Función para recibir una práctica de laboratorio (archivo zip) de un profesor
# Recibe una práctica de laboratorio si el usuario es un profesor y se encuentra con sesión abierta
# Si se recibe el archivo correctamente se debe retornar  "File was succesfully received" de lo contrario
# debe retornar "error"
# Se proporciona un código de ejemplo pero se deben implementar las validaciones de usuario y de sesión abierta
#def uploadLab(id,file_name,file_data):
    upload_dir = "server/labs"
    os.makedirs(upload_dir, exist_ok=True)

    target_path = os.path.join(upload_dir, file_name)
    with open(target_path, "wb") as f:
            f.write(file_data)
    response=f"uploadLab called by user {id}"    
    return response


# Función para recibir una práctica de laboratorio (archivo zip) de un profesor
# Recibe una práctica de laboratorio si el usuario es un profesor y se encuentra con sesión abierta
# Si se recibe el archivo correctamente se debe retornar  "File was succesfully received" de lo contrario
# debe retornar "error"
# Se proporciona un código de ejemplo pero se deben implementar las validaciones de usuario y de sesión abierta
def uploadLab(id,file_name,file_data):

    try:
        file=open(usersFile, "r")

    except FileNotFoundError:
        return "error"

    else:
        with file:
            lines=file.readlines()
            profesor_encontrado=False

            for line in lines:
                user=loads(line)

                if str(user["id"]) == str(id) and user["role"] == "professor":
                    profesor_encontrado = True
                    break

            if not profesor_encontrado:
                return "error"

    try:
        file=open("server/sessions.txt", "r")

    except FileNotFoundError:
        return "error"

    else:
        with file:
            lines=file.readlines()
            sesion_abierta=False

            for line in lines:
                session=loads(line)

                if str(session["id"]) == str(id):
                    sesion_abierta = True
                    break

            if not sesion_abierta:
                return "error"

    if not file_name.endswith(".zip"):
        return "error"

    upload_dir = "server/labs"
    os.makedirs(upload_dir, exist_ok=True)

    target_path = os.path.join(upload_dir, file_name)

    try:
        with open(target_path, "wb") as f:
            f.write(file_data)

        response="File was succesfully received"
        print(response)
        return response

    except OSError:
        return "error"

# Función para enviar una práctica de laboratorio (archivo zip) a un estudiante
# Envía una práctica de laboratorio si el usuario es un estudiante, se encuentra con sesión abierta
# y la práctica de laboratorio está asignada a él.
# Si el archivo no existe debe retornar "error"
# Se proporciona un código de ejemplo pero se deben implementar las validaciones de usuario, sesión abierta y asignación de la práctica de laboratorio
#def downloadLab(id,file_name):
    response=f"error"        
    upload_dir = "server/labs"
    file_path = os.path.join(upload_dir, file_name)
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            response=f"downloadLab called by user {id}"
            print(response)
            return data
    except FileNotFoundError:
        print(response)
        return response

# Función para enviar una práctica de laboratorio (archivo zip) a un estudiante
# Envía una práctica de laboratorio si el usuario es un estudiante, se encuentra con sesión abierta
# y la práctica de laboratorio está asignada a él.
# Si el archivo no existe debe retornar "error"
# Se proporciona un código de ejemplo pero se deben implementar las validaciones de usuario, sesión abierta y asignación de la práctica de laboratorio
def downloadLab(id,file_name):
    response=f"error"

    try:
        file=open(usersFile, "r")

    except FileNotFoundError:
        return response

    else:
        with file:
            lines=file.readlines()
            estudiante_encontrado=False

            for line in lines:
                user=loads(line)

                if user["id"]==str(id) and user["role"]=="student":
                    estudiante_encontrado=True
                    break

            if not estudiante_encontrado:
                return response

    try:
        file=open("server/sessions.txt", "r")

    except FileNotFoundError:
        return response

    else:
        with file:
            lines=file.readlines()
            sesion_abierta=False

            for line in lines:
                session=loads(line)

                if session["id"]==str(id):
                    sesion_abierta=True
                    break

            if not sesion_abierta:
                return response

    try:
        file=open("server/assignments.txt", "r")

    except FileNotFoundError:
        return response

    else:
        with file:
            lines=file.readlines()
            laboratorio_asignado=False

            for line in lines:
                assignment=loads(line)

                if (assignment["student_id"]==str(id)
                    and assignment["lab_name"]==os.path.splitext(file_name)[0]):
                    laboratorio_asignado=True
                    break

            if not laboratorio_asignado:
                return response

    upload_dir = "server/labs"
    file_path = os.path.join(upload_dir, file_name)

    try:
        with open(file_path, "rb") as f:
            data = f.read()
            print("File was succesfully sent")
            return data

    except FileNotFoundError:
        print(response)
        return response


# Función para listar las prácticas de laboratorio disponibles para un estudiante
# Lista las prácticas de laboratorio disponibles para un estudiante si el usuario es un estudiante y se encuentra con sesión abierta
# Si el usuario no es un estudiante o no tiene sesión abierta debe retornar "error"
def listStudentLabs(id):
    if isinstance(id, list) and len(id) > 0:
        id = id[0]
    # Si id viene como un diccionario (ej. {'id': ['787878']})
    elif isinstance(id, dict) and 'id' in id:
        id = id['id'][0] if isinstance(id['id'], list) else id['id']

    id = str(id).strip()
    try:
        with open(usersFile, "r") as f:
            estudiante_encontrado = any(
                str(loads(line.strip()).get("id")) == str(id) and loads(line.strip()).get("role") == "student"
                for line in f if line.strip()
            )
        if not estudiante_encontrado:
            return "error1.1"
    except FileNotFoundError:
        return "error1.2"

    try:
        with open("server/sessions.txt", "r") as f:
            sesion_abierta = any(
                str(loads(line.strip()).get("id")) == str(id)
                for line in f if line.strip()
            )
        if not sesion_abierta:
            return "error1.3"
    except FileNotFoundError:
        return "error1"

    laboratorios = []
    try:
        with open("server/assignments.txt", "r") as f:
            for line in f:
                if line.strip():
                    assignment = loads(line.strip())
                    if str(assignment.get("student_id")) == str(id):
                        lab = assignment.get("lab_name")
                        if lab and lab not in laboratorios:
                            laboratorios.append(lab)
    except FileNotFoundError:
        return dumps([])

    response = dumps(laboratorios)
    print(response)
    return response

# Función para listar las prácticas de laboratorio cargadas por los profesores
# Lista las prácticas de laboratorio cargadas por los profesores si el usuario es un profesor y se encuentra con sesión abierta
# Si el usuario no es un profesor o no tiene sesión abierta debe retornar "error"   
def listProfessorsLabs(id):
    try:
        with open(usersFile, "r") as f:
            profesor_encontrado = any(
                str(loads(line.strip()).get("id")) == str(id) and loads(line.strip()).get("role") == "professor"
                for line in f if line.strip()
            )
        if not profesor_encontrado:
            return "error2.1"
    except FileNotFoundError:
        return "error2.2"

    try:
        with open("server/sessions.txt", "r") as f:
            sesion_abierta = any(
                str(loads(line.strip()).get("id")) == str(id)
                for line in f if line.strip()
            )
        if not sesion_abierta:
            return "error2.3"
    except FileNotFoundError:
        return "error2"

    upload_dir = "server/labs"
    if not os.path.exists(upload_dir):
        return dumps([])

    laboratorios = [f.replace(".zip", "") for f in os.listdir(upload_dir) if f.endswith(".zip")]
    response = dumps(laboratorios)
    print(response)
    return response


# Función para listar los estudiantes registrados en el sistema
# Lista los estudiantes registrados en el sistema si el usuario es un profesor y se encuentra con sesión abierta
# Si el usuario no es un profesor o no tiene sesión abierta debe retornar "error"
def listStudents(id):
    try:
        with open(usersFile, "r") as f:
            profesor_encontrado = any(
                str(loads(line.strip()).get("id")) == str(id) and loads(line.strip()).get("role") == "professor"
                for line in f if line.strip()
            )
        if not profesor_encontrado:
            return "error3.1"
    except FileNotFoundError:
        return "error3.2"

    try:
        with open("server/sessions.txt", "r") as f:
            sesion_abierta = any(
                str(loads(line.strip()).get("id")) == str(id)
                for line in f if line.strip()
            )
        if not sesion_abierta:
            return "error3.3"
    except FileNotFoundError:
        return "error3"

    estudiantes = []
    try:
        with open(usersFile, "r") as f:
            for line in f:
                if line.strip():
                    user = loads(line.strip())
                    if user.get("role") == "student":
                        estudiantes.append(user.get("id"))
    except FileNotFoundError:
        return dumps([])

    response = dumps(estudiantes)
    print(response)
    return response
# Función para asignar una práctica de laboratorio a un estudiante
# Asigna una práctica de laboratorio a un estudiante si el usuario es un profesor y se encuentra con sesión abierta
# Si el usuario no es un profesor o no tiene sesión abierta o el estudiante no existe o la práctica no existe debe retornar "error"
#def assignLab(id,lab_name,student_id):
    response=f"assignLab called by user {id} to assign lab {lab_name} to student {student_id}"        
    print(response)
    return response
    

# Función para asignar una práctica de laboratorio a un estudiante
# Asigna una práctica de laboratorio a un estudiante si el usuario es un profesor y se encuentra con sesión abierta
# Si el usuario no es un profesor o no tiene sesión abierta o el estudiante no existe o la práctica no existe debe retornar "error"
def assignLab(id,lab_name,student_id):
    try:
        file = open(usersFile, "r")
    except FileNotFoundError:
        return "error"
    else:
        with file:
            lines = file.readlines()
            profesor_encontrado = False
            estudiante_encontrado = False

            for line in lines:
                user = loads(line)

                if user["id"] == str(id) and user["role"] == "professor":
                    profesor_encontrado = True

                if user["id"] == str(student_id) and user["role"] == "student":
                    estudiante_encontrado = True

            if not profesor_encontrado or not estudiante_encontrado:
                return "error"

    try:
        file = open("server/sessions.txt", "r")
    except FileNotFoundError:
        return "error"
    else:
        with file:
            lines = file.readlines()
            sesion_abierta = False

            for line in lines:
                session = loads(line)

                if session["id"] == str(id):
                    sesion_abierta = True
                    break

            if not sesion_abierta:
                return "error"

    upload_dir = "server/labs"
    archivo_lab = os.path.join(upload_dir, lab_name + ".zip")

    if not os.path.isfile(archivo_lab):
        return "error"

    assignment = {
        "professor_id": str(id),
        "lab_name": lab_name,
        "student_id": str(student_id)
    }

    # Una misma práctica solo necesita una asignación por estudiante.
    try:
        with open("server/assignments.txt", "r") as file:
            for line in file:
                if line.strip() and loads(line) == assignment:
                    return "success"
    except FileNotFoundError:
        pass

    try:
        with open("server/assignments.txt", "a") as file:
            file.write(dumps(assignment) + "\n")
    except OSError:
        return "error"

    response = "success"
    print(response)
    return response
   
    

                
                
            
        
    
            
