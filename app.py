from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from BackEnd import functions as CallMethod
import BackEnd.GlobalInfo.responseMessages as ResponseMessages


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/login", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def login_usuario():
    try:
        data = request.json
        correo = data.get("correo")
        contraseña = data.get("contraseña")

        if not correo or not contraseña:
            return jsonify({"mensaje": "Correo y contraseña son obligatorios"}), 400

        resultado = CallMethod.verificar_usuario(correo, contraseña)

        if resultado.get("success"):
            return jsonify({
                "mensaje": "Inicio de sesión exitoso",
                "rol": resultado.get("rol", "usuario"),
                "correo": correo
            }), 200
        else:
            return jsonify({"mensaje": "Correo o contraseña incorrectos"}), 401

    except Exception as e:
        print("Error en login:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/registro", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def registrar_usuario():
    try:
        data = request.json
        correo = data.get("correo")
        contraseña = data.get("contrasena")

        if not correo or not contraseña:
            return jsonify({"mensaje": "Correo y contraseña son obligatorios"}), 400

        resultado = CallMethod.registrar_usuario(correo, contraseña)
        return jsonify(resultado), 201
    except Exception as e:
        print("Error en registro:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/contactar", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def contacto():
    try:
        data = request.json
        nombre = data.get("nombre")
        telefono = data.get("telefono")
        mensaje = data.get("mensaje")

        if not nombre or not telefono or not mensaje:
            return jsonify({"mensaje": "Todos los campos son obligatorios"}), 400

        resultado = CallMethod.guardar_contacto(nombre, telefono, mensaje)

        if resultado.get("success"):
            return jsonify({"mensaje": "Información guardada correctamente"}), 201
        else:
            return jsonify({"mensaje": "No se pudo guardar la información"}), 500

    except Exception as e:
        print("Error en contacto:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/actualizar_perfil", methods=["POST"])
@cross_origin()
def actualizar_perfil():
    try:
        data = request.json
        resultado = CallMethod.actualizar_datos_perfil(data)
        return jsonify(resultado)
    except Exception as e:
        print("Error en actualizar perfil:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/usuario", methods=["GET"])
@cross_origin()
def obtener_usuario():
    try:
        correo = request.args.get("correo")
        resultado = CallMethod.obtener_usuario_por_correo(correo)
        return jsonify(resultado)
    except Exception as e:
        print("Error al obtener usuario:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500
    
@app.route("/agendar_mantenimiento", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def agendar_mantenimiento():
    try:
        data = request.json
        resultado = CallMethod.guardar_mantenimiento(data)

        if resultado.get("success"):
            return jsonify({"mensaje": "Mantenimiento agendado exitosamente"}), 201
        else:
            return jsonify({"mensaje": resultado.get("mensaje", "Error al agendar mantenimiento")}), 400

    except Exception as e:
        print("Error en agendar mantenimiento:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/guardar-servicio-correctivo", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def guardar_servicio_correctivo():
    try:
        data = request.json
        resultado = CallMethod.guardar_servicio_correctivo(data)
        return jsonify(resultado)
    except Exception as e:
        print("Error en endpoint servicio-correctivo:", e)
        return jsonify({"success": False, "mensaje": "Error en el servidor"}), 500


@app.route("/agregar_productos", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def agregar_productos():
    try:
        data = request.json
        productos = data.get("productos", [])

        if not productos:
            return jsonify({"mensaje": "No se recibieron productos"}), 400

        resultado = CallMethod.guardar_productos(productos)

        if resultado.get("success"):
            return jsonify({"mensaje": "Productos guardados correctamente"}), 200
        else:
            return jsonify({"mensaje": "Error al guardar productos"}), 500
    except Exception as e:
        print("Error en agregar_productos:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/productos", methods=["GET"])
@cross_origin()
def obtener_productos():
    try:
        resultado = CallMethod.obtener_productos_tienda()
        return jsonify(resultado), 200
    except Exception as e:
        print("Error en obtener productos:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/agregar_carrito", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def agregar_al_carrito():
    try:
        data = request.json
        correo = data.get("correo")
        producto = data.get("producto")

        if not correo or not producto:
            return jsonify({"mensaje": "Correo y producto son obligatorios"}), 400

        resultado = CallMethod.guardar_en_carrito(correo, producto)

        if resultado.get("success"):
            return jsonify({"mensaje": "Producto agregado al carrito"}), 201
        else:
            return jsonify({"mensaje": "No se pudo agregar el producto"}), 500

    except Exception as e:
        print("Error en agregar_carrito:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/carrito", methods=["GET"])
@cross_origin()
def obtener_carrito():
    try:
        correo = request.args.get("correo")
        if not correo:
            return jsonify({"mensaje": "Correo es requerido"}), 400

        resultado = CallMethod.obtener_carrito_por_usuario(correo)
        return jsonify(resultado), 200

    except Exception as e:
        print("Error en obtener_carrito:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/eliminar_carrito", methods=["DELETE"])
@cross_origin()
def eliminar_producto_carrito():
    try:
        data = request.json
        correo = data.get("correo")
        nombre_producto = data.get("nombre")

        if not correo or not nombre_producto:
            return jsonify({"mensaje": "Correo y nombre del producto son obligatorios"}), 400

        resultado = CallMethod.eliminar_producto_de_carrito(correo, nombre_producto)
        if resultado.get("success"):
            return jsonify({"mensaje": "Producto eliminado del carrito"}), 200
        else:
            return jsonify({"mensaje": "No se pudo eliminar"}), 500

    except Exception as e:
        print("Error al eliminar del carrito:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500



@app.route("/guardar_pago", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def guardar_pago():
    try:
        data = request.json
        correo = data.get("correo")
        productos = data.get("productos")

        if not correo or not productos:
            return jsonify({"mensaje": "Correo y productos son requeridos"}), 400

        resultado = CallMethod.guardar_pago_en_db(correo, productos)

        if resultado.get("success"):
            return jsonify({"mensaje": "Pago guardado exitosamente"}), 201
        else:
            return jsonify({"mensaje": "No se pudo guardar el pago"}), 500

    except Exception as e:
        print("Error en guardar_pago:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500


    
@app.route("/guardar_direccion", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def guardar_direccion():
    try:
        data = request.json
        correo = data.get("correo")
        direccion = data.get("direccion")

        if not correo or not direccion:
            return jsonify({"mensaje": "Correo y dirección son obligatorios"}), 400

        resultado = CallMethod.guardar_direccion_en_db(correo, direccion)

        if resultado.get("success"):
            return jsonify({"mensaje": "Dirección guardada correctamente"}), 201
        else:
            return jsonify({"mensaje": "No se pudo guardar la dirección"}), 500
    except Exception as e:
        print("Error en guardar_direccion:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500


@app.route("/direcciones", methods=["GET"])
@cross_origin()
def obtener_direcciones():
    try:
        correo = request.args.get("correo")
        if not correo:
            return jsonify({"mensaje": "Correo es obligatorio"}), 400

        resultado = CallMethod.obtener_direcciones_por_correo(correo)
        return jsonify(resultado), 200
    except Exception as e:
        print("Error en obtener_direcciones:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500


@app.route("/eliminar_direccion", methods=["DELETE"])
@cross_origin()
def eliminar_direccion():
    try:
        data = request.json
        correo = data.get("correo")
        direccion = data.get("direccion")

        if not correo or not direccion:
            return jsonify({"mensaje": "Correo y dirección son obligatorios"}), 400

        resultado = CallMethod.eliminar_direccion_de_db(correo, direccion)

        if resultado.get("success"):
            return jsonify({"mensaje": "Dirección eliminada correctamente"}), 200
        else:
            return jsonify({"mensaje": "No se pudo eliminar la dirección"}), 500
    except Exception as e:
        print("Error en eliminar_direccion:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500


@app.route("/guardar_tarjeta", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def guardar_tarjeta():
    try:
        data = request.json
        correo = data.get("correo")
        tarjeta = data.get("tarjeta")

        if not correo or not tarjeta:
            return jsonify({"mensaje": "Correo y tarjeta son obligatorios"}), 400

        resultado = CallMethod.guardar_tarjeta_en_db(correo, tarjeta)

        if resultado.get("success"):
            return jsonify({"mensaje": "Tarjeta guardada correctamente"}), 201
        else:
            return jsonify({"mensaje": "No se pudo guardar la tarjeta"}), 500
    except Exception as e:
        print("Error en guardar_tarjeta:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500


@app.route("/tarjetas", methods=["GET"])
@cross_origin()
def obtener_tarjetas():
    try:
        correo = request.args.get("correo")
        if not correo:
            return jsonify({"mensaje": "Correo es obligatorio"}), 400

        resultado = CallMethod.obtener_tarjetas_por_correo(correo)
        return jsonify(resultado), 200
    except Exception as e:
        print("Error en obtener_tarjetas:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500


@app.route("/eliminar_tarjeta", methods=["DELETE"])
@cross_origin()
def eliminar_tarjeta():
    try:
        data = request.json
        correo = data.get("correo")
        numero = data.get("numero")  # último número de tarjeta o identificador

        if not correo or not numero:
            return jsonify({"mensaje": "Correo y número de tarjeta son obligatorios"}), 400

        resultado = CallMethod.eliminar_tarjeta_de_db(correo, numero)

        if resultado.get("success"):
            return jsonify({"mensaje": "Tarjeta eliminada correctamente"}), 200
        else:
            return jsonify({"mensaje": "No se pudo eliminar la tarjeta"}), 500
    except Exception as e:
        print("Error en eliminar_tarjeta:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/guardar_pago_exitoso", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def guardar_pago_exitoso_endpoint():
    try:
        data = request.json
        correo = data.get("correo")
        productos = data.get("productos")
        total = data.get("total")

        if not correo or not productos or total is None:
            return jsonify({"mensaje": "Datos incompletos"}), 400

        resultado = CallMethod.guardar_pago_exitoso(correo, productos, total)

        if resultado.get("success"):
            return jsonify({"mensaje": "Pago exitoso guardado"}), 201
        else:
            return jsonify({"mensaje": "Error al guardar pago"}), 500

    except Exception as e:
        print("Error en guardar_pago_exitoso:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500    

@app.route("/interesados", methods=["GET"])
@cross_origin(allow_headers=["Content-Type"])
def obtener_interesados():
    try:
        resultado = CallMethod.obtener_interesados()
        return jsonify(resultado), 200
    except Exception as e:
        print("Error al obtener interesados:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/interesados/<id>", methods=["DELETE"])
@cross_origin(allow_headers=["Content-Type"])
def eliminar_interesado(id):
    try:
        resultado = CallMethod.eliminar_interesado(id)
        return jsonify(resultado), 200
    except Exception as e:
        print("Error al eliminar interesado:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500
    
@app.route("/servicio-correctivo", methods=["GET"])
@cross_origin(allow_headers=["Content-Type"])
def obtener_servicio_correctivo():
    try:
        resultado = CallMethod.obtener_servicio_correctivo()
        return jsonify(resultado), 200
    except Exception as e:
        print("Error al obtener servicios correctivos:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/servicio-correctivo/<id>", methods=["DELETE"])
@cross_origin(allow_headers=["Content-Type"])
def eliminar_servicio_correctivo(id):
    try:
        resultado = CallMethod.eliminar_servicio_correctivo(id)
        return jsonify(resultado), 200
    except Exception as e:
        print("Error al eliminar servicio correctivo:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/mantenimiento", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def guardar_mantenimiento():
    try:
        data = request.json
        resultado = CallMethod.guardar_mantenimiento(data)
        return jsonify(resultado), 201
    except Exception as e:
        print("Error al guardar mantenimiento:", e)
        return jsonify({"mensaje": "Error al guardar mantenimiento"}), 500

@app.route("/eliminar-productos-carrito", methods=["DELETE"])
@cross_origin(allow_headers=["Content-Type"])
def eliminar_productos_carrito():
    try:
        data = request.json
        correo = data.get("correo")
        productos = data.get("productos")  # lista de nombres de productos a eliminar

        if not correo or not productos:
            return jsonify({"mensaje": "Correo y lista de productos son requeridos"}), 400

        resultado = CallMethod.eliminar_productos_seleccionados(correo, productos)
        return jsonify(resultado), 200

    except Exception as e:
        print("Error al eliminar productos del carrito:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

@app.route("/mantenimientos", methods=["GET"])
@cross_origin(allow_headers=["Content-Type"])
def obtener_mantenimientos():
    try:
        resultado = CallMethod.obtener_mantenimientos()
        return jsonify(resultado), 200
    except Exception as e:
        print("Error al obtener mantenimientos:", e)
        return jsonify({"mensaje": "Error al obtener mantenimientos"}), 500

@app.route("/mantenimiento", methods=["DELETE"])
@cross_origin(allow_headers=["Content-Type"])
def eliminar_mantenimiento():
    try:
        data = request.json
        correo = data.get("correo")
        placa = data.get("placa")
        fecha = data.get("fecha")
        hora = data.get("hora")

        if not correo or not placa or not fecha or not hora:
            return jsonify({"mensaje": "Faltan datos para eliminar la cita"}), 400

        resultado = CallMethod.eliminar_mantenimiento(correo, placa, fecha, hora)
        return jsonify(resultado), 200
    except Exception as e:
        print("Error al eliminar mantenimiento:", e)
        return jsonify({"mensaje": "Error al eliminar cita"}), 500

@app.route("/pedidos_usuario", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def obtener_pedidos_usuario():
    try:
        data = request.json
        correo = data.get("correo")

        if not correo:
            return jsonify({"mensaje": "Correo requerido"}), 400

        resultado = CallMethod.obtener_pedidos_por_correo(correo)
        return jsonify(resultado), 200
    except Exception as e:
        print("Error al obtener pedidos del usuario:", e)
        return jsonify({"mensaje": "Error al obtener pedidos"}), 500




@app.route("/notificaciones/compras", methods=["POST"])
@cross_origin(allow_headers=["Content-Type"])
def notificaciones_compras():
    try:
        data = request.json
        correo = data.get("correo")

        if not correo:
            return jsonify({"mensaje": "Correo requerido"}), 400

        resultado = CallMethod.obtener_notificaciones_compras(correo)
        return jsonify({"notificaciones": resultado}), 200

    except Exception as e:
        print("Error al obtener notificaciones de compras:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500





if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
