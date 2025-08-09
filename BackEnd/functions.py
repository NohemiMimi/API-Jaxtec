import BackEnd.GlobalInfo.responseMessages as ResponseMessage
import BackEnd.GlobalInfo.keys as Colabskey
from pymongo import MongoClient
from flask import jsonify, request
from bson import ObjectId
from datetime import datetime, timedelta
import pytz

# Conexión a MongoDB Atlas
if Colabskey.dbconn is None:
    mongoConnect = MongoClient(Colabskey.strConnection)
    Colabskey.dbconn = mongoConnect[Colabskey.strDBConnection]

def verificar_usuario(correo, contraseña):
    try:
        usuarios = Colabskey.dbconn["usuarios"]
        usuario = usuarios.find_one({"correo": correo, "contraseña": contraseña})

        if usuario:
            return {
                "success": True,
                "rol": usuario.get("rol", "usuario")  # Si no tiene rol, pone "usuario" por default
            }
        else:
            return {"success": False}
    except Exception as e:
        print("Error al verificar usuario:", e)
        return {"success": False}

def registrar_usuario(correo, contraseña):
    try:
        usuarios = Colabskey.dbconn["usuarios"]

        if usuarios.find_one({"correo": correo}):
            return {"mensaje": "El usuario ya está registrado"}

        nuevo_usuario = {
            "correo": correo,
            "contraseña": contraseña
        }

        usuarios.insert_one(nuevo_usuario)
        return {"mensaje": "Usuario registrado correctamente"}
    except Exception as e:
        print("Error en DB:", e)
        return {"mensaje": "No se pudo registrar el usuario"}

def guardar_contacto(nombre, telefono, mensaje):
    try:
        contactos = Colabskey.dbconn["contactar"]
        nuevo_contacto = {
            "nombre": nombre,
            "telefono": telefono,
            "mensaje": mensaje
        }
        contactos.insert_one(nuevo_contacto)
        return {"success": True}
    except Exception as e:
        print("Error al guardar contacto:", e)
        return {"success": False}

def actualizar_datos_perfil(data):
    try:
        usuarios = Colabskey.dbconn["usuarios"]
        correo = data.get("correo")
        nombre = data.get("nombre")
        imagen = data.get("imagen")

        if not correo:
            return {"mensaje": "Correo es requerido"}

        usuario = usuarios.find_one({"correo": correo})
        if not usuario:
            return {"mensaje": "Usuario no encontrado"}

        nuevos_datos = {}
        if nombre:
            nuevos_datos["nombre"] = nombre
        if imagen:
            nuevos_datos["imagen"] = imagen

        usuarios.update_one({"correo": correo}, {"$set": nuevos_datos})
        return {"mensaje": "Perfil actualizado correctamente"}

    except Exception as e:
        print("Error en actualizar perfil:", e)
        return {"mensaje": "Error al actualizar perfil"}

def obtener_usuario_por_correo(correo):
    try:
        usuarios = Colabskey.dbconn["usuarios"]
        usuario = usuarios.find_one({"correo": correo})
        if not usuario:
            return {"mensaje": "Usuario no encontrado"}

        return {
            "nombre": usuario.get("nombre", ""),
            "imagen": usuario.get("imagen", "")
        }
    except Exception as e:
        print("Error al obtener usuario:", e)
        return {"mensaje": "Error al obtener datos del usuario"}
    

def guardar_mantenimiento(data):
    try:
        marca = data.get("marca")
        modelo = data.get("modelo")
        placa = data.get("placa")
        anio = data.get("anio")
        fecha = data.get("fecha")  # ISO 8601: "2025-07-25T10:00:00"
        servicios = data.get("servicios", [])

        if not all([marca, modelo, placa, anio, fecha]):
            return {"success": False, "mensaje": "Todos los campos son obligatorios"}

        # Convertir fecha a objeto datetime y asegurar horario local
        fecha_inicio = datetime.fromisoformat(fecha)
        fecha_inicio = fecha_inicio.replace(tzinfo=pytz.timezone("America/Mexico_City"))
        fecha_fin = fecha_inicio + timedelta(hours=2)

        # Validaciones de día y horario
        if fecha_inicio.weekday() >= 6:
            return {"success": False, "mensaje": "Solo se permite agendar de lunes a sábado"}

        hora_inicio = fecha_inicio.hour
        if hora_inicio < 9 or fecha_fin.hour > 20 or (hora_inicio == 19 and fecha_fin.hour > 21):
            return {"success": False, "mensaje": "Solo se permite agendar entre 9:00 y 20:00"}

        mantenimientos = Colabskey.dbconn["mantenimiento"]

        # Buscar traslapes de horario en la misma fecha
        conflictos = mantenimientos.find({
            "fecha": {
                "$lt": fecha_fin.isoformat(),
                "$gte": (fecha_inicio - timedelta(hours=2)).isoformat()
            }
        })

        for c in conflictos:
            inicio_existente = datetime.fromisoformat(c["fecha"])
            fin_existente = inicio_existente + timedelta(hours=2)

            if not (fecha_fin <= inicio_existente or fecha_inicio >= fin_existente):
                return {"success": False, "mensaje": "Ya existe un mantenimiento en ese horario"}

        # Guardar mantenimiento
        nuevo = {
            "marca": marca,
            "modelo": modelo,
            "placa": placa,
            "anio": anio,
            "fecha": fecha_inicio.isoformat(),
            "servicios": servicios
        }

        mantenimientos.insert_one(nuevo)
        return {"success": True}

    except Exception as e:
        print("Error al guardar mantenimiento:", e)
        return {"success": False, "mensaje": "Error en el servidor"}
    
def guardar_servicio_correctivo(data):
    try:
        marca = data.get("marca")
        modelo = data.get("modelo")
        placa = data.get("placa")
        anio = data.get("anio")
        problema = data.get("problema", "")  # este campo puede ir vacío
        puede_moverse = data.get("puede_moverse")
        telefono = data.get("telefono")

        if not all([marca, modelo, placa, anio, puede_moverse, telefono]):
            return {"success": False, "mensaje": "Faltan campos obligatorios"}

        servicio = {
            "marca": marca,
            "modelo": modelo,
            "placa": placa,
            "anio": anio,
            "problema": problema,
            "puede_moverse": puede_moverse,
            "telefono": telefono,
            "fecha_solicitud": datetime.now(pytz.timezone("America/Mexico_City")).isoformat()
        }

        servicios = Colabskey.dbconn["servicio-correctivo"]
        servicios.insert_one(servicio)
        return {"success": True, "mensaje": "Servicio guardado correctamente"}

    except Exception as e:
        print("Error al guardar servicio correctivo:", e)
        return {"success": False, "mensaje": "Error en el servidor"}


def guardar_productos(lista_productos):
    try:
        tienda = Colabskey.dbconn["tienda"]

        for producto in lista_productos:
            tienda.insert_one({
                "nombre": producto.get("nombre", ""),
                "precio": producto.get("precio", 0),
                "imagen": producto.get("imagen", "")
            })

        return {"success": True}
    except Exception as e:
        print("Error al guardar productos:", e)
        return {"success": False}

def obtener_productos_tienda():
    try:
        tienda = Colabskey.dbconn["tienda"]
        productos = tienda.find()

        lista = []
        for prod in productos:
            lista.append({
                "nombre": prod.get("nombre", ""),
                "precio": prod.get("precio", 0),
                "imagen": prod.get("imagen", "")
            })

        return lista
    except Exception as e:
        print("Error al obtener productos:", e)
        return []

def guardar_en_carrito(correo, producto):
    try:
        carrito = Colabskey.dbconn["carrito"]
        carrito.insert_one({
            "correo": correo,
            "producto": producto,
            "fecha_agregado": datetime.now().isoformat()
        })
        return {"success": True}
    except Exception as e:
        print("Error al guardar en carrito:", e)
        return {"success": False}


def obtener_carrito_por_usuario(correo):
    try:
        carrito = Colabskey.dbconn["carrito"]
        productos = carrito.find({"correo": correo})

        lista = []
        for item in productos:
            lista.append(item["producto"])

        return lista
    except Exception as e:
        print("Error al obtener carrito del usuario:", e)
        return []


def eliminar_producto_de_carrito(correo, nombre_producto):
    try:
        carrito = Colabskey.dbconn["carrito"]
        resultado = carrito.delete_one({
            "correo": correo,
            "producto.nombre": nombre_producto
        })

        if resultado.deleted_count == 1:
            return {"success": True}
        else:
            return {"success": False}

    except Exception as e:
        print("Error al eliminar producto del carrito:", e)
        return {"success": False}

def guardar_pago_en_db(correo, productos):
    try:
        pagos = Colabskey.dbconn["pago"]
        pagos.insert_one({
            "correo": correo,
            "productos": productos,
            "fecha": datetime.now().isoformat()
        })
        return {"success": True}
    except Exception as e:
        print("Error al guardar pago:", e)
        return {"success": False}




def guardar_direccion_en_db(correo, direccion):
    try:
        pagos = Colabskey.dbconn["pago"]
        # Insertar la dirección en el documento del usuario o crear documento si no existe
        pagos.update_one(
            {"correo": correo},
            {"$addToSet": {"direcciones": direccion}},
            upsert=True
        )
        return {"success": True}
    except Exception as e:
        print("Error al guardar dirección:", e)
        return {"success": False}


def obtener_direcciones_por_correo(correo):
    try:
        pagos = Colabskey.dbconn["pago"]
        doc = pagos.find_one({"correo": correo}, {"_id": 0, "direcciones": 1})
        if doc and "direcciones" in doc:
            return doc["direcciones"]
        else:
            return []
    except Exception as e:
        print("Error al obtener direcciones:", e)
        return []


def eliminar_direccion_de_db(correo, direccion):
    try:
        pagos = Colabskey.dbconn["pago"]
        resultado = pagos.update_one(
            {"correo": correo},
            {"$pull": {"direcciones": direccion}}
        )
        if resultado.modified_count == 1:
            return {"success": True}
        else:
            return {"success": False}
    except Exception as e:
        print("Error al eliminar dirección:", e)
        return {"success": False}


def guardar_tarjeta_en_db(correo, tarjeta):
    try:
        pagos = Colabskey.dbconn["pago"]
        pagos.update_one(
            {"correo": correo},
            {"$addToSet": {"tarjetas": tarjeta}},
            upsert=True
        )
        return {"success": True}
    except Exception as e:
        print("Error al guardar tarjeta:", e)
        return {"success": False}


def obtener_tarjetas_por_correo(correo):
    try:
        pagos = Colabskey.dbconn["pago"]
        doc = pagos.find_one({"correo": correo}, {"_id": 0, "tarjetas": 1})
        if doc and "tarjetas" in doc:
            return doc["tarjetas"]
        else:
            return []
    except Exception as e:
        print("Error al obtener tarjetas:", e)
        return []


def eliminar_tarjeta_de_db(correo, numero_tarjeta):
    try:
        pagos = Colabskey.dbconn["pago"]
        resultado = pagos.update_one(
            {"correo": correo},
            {"$pull": {"tarjetas": {"numero": numero_tarjeta}}}
        )
        if resultado.modified_count == 1:
            return {"success": True}
        else:
            return {"success": False}
    except Exception as e:
        print("Error al eliminar tarjeta:", e)
        return {"success": False}

def guardar_pago_exitoso(correo, productos, total):
    try:
        pagos = Colabskey.dbconn["pago-exitoso"]

        # Obtener último número de pedido
        ultimo_pedido = pagos.find_one(sort=[("numero", -1)])
        siguiente_numero = 1
        if ultimo_pedido and "numero" in ultimo_pedido:
            siguiente_numero = ultimo_pedido["numero"] + 1

        nombres_productos = [p.get("nombre", "") for p in productos]
        descripcion = ", ".join(nombres_productos)
        
        pago_nuevo = {
            "correo": correo,
            "numero": siguiente_numero,
            "descripcion": descripcion,
            "fecha": datetime.now(pytz.timezone("America/Mexico_City")).strftime("%Y-%m-%d %H:%M:%S"),
            "total": total
        }

        pagos.insert_one(pago_nuevo)
        return {"success": True, "mensaje": "Pago exitoso guardado"}
    except Exception as e:
        print("Error al guardar pago exitoso:", e)
        return {"success": False, "mensaje": "Error en el servidor"}

def obtener_interesados():
    try:
        coleccion = Colabskey.dbconn["contactar"]
        interesados = list(coleccion.find())
        for interesado in interesados:
            interesado["_id"] = str(interesado["_id"])  # Convertir ObjectId a string
        return interesados
    except Exception as e:
        print("Error en obtener_interesados:", e)
        return []

def eliminar_interesado(id):
    try:
        coleccion = Colabskey.dbconn["contactar"]
        resultado = coleccion.delete_one({"_id": ObjectId(id)})
        if resultado.deleted_count == 1:
            return {"mensaje": "Interesado eliminado correctamente"}
        else:
            return {"mensaje": "No se encontró el interesado"}
    except Exception as e:
        print("Error al eliminar interesado:", e)
        return {"mensaje": "Error en la base de datos"}
    
def obtener_servicio_correctivo():
    try:
        coleccion = Colabskey.dbconn["servicio-correctivo"]
        servicios = list(coleccion.find())
        for servicio in servicios:
            servicio["_id"] = str(servicio["_id"])
        return servicios
    except Exception as e:
        print("Error al obtener servicio correctivo:", e)
        return []

def eliminar_servicio_correctivo(id):
    try:
        coleccion = Colabskey.dbconn["servicio-correctivo"]
        resultado = coleccion.delete_one({"_id": ObjectId(id)})
        if resultado.deleted_count == 1:
            return {"mensaje": "Servicio eliminado correctamente"}
        else:
            return {"mensaje": "No se encontró el servicio"}
    except Exception as e:
        print("Error al eliminar servicio correctivo:", e)
        return {"mensaje": "Error en la base de datos"}

def guardar_mantenimiento(data):
    try:
        mantenimiento = Colabskey.dbconn["mantenimiento"]

        cita = {
            "correo": data.get("correo"),
            "marca": data.get("marca"),
            "modelo": data.get("modelo"),
            "placa": data.get("placa"),
            "anio": data.get("anio"),
            "fecha": data.get("fecha"),
            "hora": data.get("hora"),
            "tipos": data.get("tipos", [])
        }

        mantenimiento.insert_one(cita)
        return {"mensaje": "Cita de mantenimiento registrada correctamente"}
    except Exception as e:
        print("Error en DB (mantenimiento):", e)
        return {"mensaje": "No se pudo guardar la cita"}

def eliminar_productos_seleccionados(correo, productos):
    try:
        carrito = Colabskey.dbconn["carrito"]

        for nombre in productos:
            carrito.delete_one({"correo": correo})

        return {"mensaje": "Productos eliminados correctamente"}
    except Exception as e:
        print("Error al eliminar productos del carrito:", e)
        return {"mensaje": "No se pudieron eliminar los productos"}

def obtener_mantenimientos():
    try:
        mantenimiento = Colabskey.dbconn["mantenimiento"]
        datos = list(mantenimiento.find({}, {"_id": 0}))  # Excluye el _id
        return datos
    except Exception as e:
        print("Error en DB (get mantenimientos):", e)
        return []

def eliminar_mantenimiento(correo, placa, fecha, hora):
    try:
        mantenimiento = Colabskey.dbconn["mantenimiento"]

        query = {
            "correo": correo,
            "placa": placa,
            "fecha": fecha,
            "hora": hora
        }

        result = mantenimiento.delete_one(query)

        if result.deleted_count > 0:
            return {"mensaje": "Cita eliminada correctamente"}
        else:
            return {"mensaje": "No se encontró la cita para eliminar"}

    except Exception as e:
        print("Error al eliminar cita de mantenimiento:", e)
        return {"mensaje": "No se pudo eliminar la cita"}


def obtener_pedidos_por_correo(correo):
    try:
        pagos = Colabskey.dbconn["pago-exitoso"]
        datos = list(pagos.find({"correo": correo}, {"_id": 0}))  # Excluye _id
        return datos
    except Exception as e:
        print("Error en DB (pedidos por correo):", e)
        return []



def obtener_mantenimiento_historial_usuario(correo):
    try:
        coleccion = Colabskey.dbconn["mantenimiento"]
        mantenimientos = list(coleccion.find({"correo": correo}))
        for m in mantenimientos:
            m["_id"] = str(m["_id"])  # Convertir ObjectId a string
        return mantenimientos
    except Exception as e:
        print("Error en obtener_mantenimiento_historial_usuario:", e)
        return []

def obtener_notificaciones_compras(correo):
    try:
        pagos = Colabskey.dbconn["pago-exitoso"]
        datos = list(pagos.find({"correo": correo}))

        notificaciones = []
        for pedido in datos:
            notificaciones.append({
                "tipo": "compra",
                "titulo": "¡Compra exitosa!",
                "descripcion": f"Tu compra por ${pedido.get('total', 0)} fue realizada con éxito.",
                "fecha": pedido.get("fecha", "")  # Si tienes un campo de fecha
            })

        return notificaciones

    except Exception as e:
        print("Error en obtener_notificaciones_compras:", e)
        return []

