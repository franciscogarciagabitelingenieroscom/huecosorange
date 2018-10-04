# -*- encoding: utf-8 -*-
import unicodecsv as csv

from datetime import datetime
from django.db import models, connections


def strToField(valor, tipoCampo="CharField", convertirUTF8=True):
    if convertirUTF8:
        valor = valor.decode("cp1252").encode("utf-8")

    if tipoCampo == "BooleanField":
        if valor == "" or valor == "0":
            valor = False
        else:
            valor = True

    if valor == "":
        if tipoCampo == "FloatField" or tipoCampo == "IntegerField":
            valor = 0
        elif tipoCampo == "BooleanField":
            valor = False
        elif tipoCampo == "CharField":
            valor = ""
        else:
            valor = None

    elif tipoCampo == "AutoField":
        valor = valor.replace(".", "")
    elif tipoCampo == "FloatField":
        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")
        if valor == "":
            valor = 0
        else:
            valor = float(valor)
    elif tipoCampo == "IntegerField":
        if valor == "":
            valor = 0
        else:
            valor = valor.replace(".", "")
            valor = int(valor)
    elif tipoCampo == "DateField":
        try:
            valor = datetime.strptime(valor, "%d/%m/%Y")
        except:
            try:
                valor = datetime.strptime(valor, "%m/%d/%Y")
            except:
                valor = None
    elif tipoCampo == "DateTimeField":
        valor = valor.replace("-", "/")
        if len(valor) == 10:
            valor += " 00:00:01"
        try:
            valor = datetime.strptime(valor, "%d/%m/%Y %H:%M:%S")
        except:
            valor = ""
    elif tipoCampo == "TimeField":
        try:
            valor = datetime.strptime(valor[11:], "%H:%M:%S")
        except:
            valor = None

    return valor

def leerCSV(fichero, verbose=False, encoding="utf-8"):
    """
    Lee un CSV abierto
    :param fichero Ruta al fichero
    :param verbose Si saca por pantalla la importación
    :param encoding string, códificación
    """
    cabecera = True  # La primera es la cabecera
    camposCabecera = []  # Lista con los nombres de campos del CSV
    registros = []
    i = 0  # Contador de lineas
    for linea in fichero:
        if cabecera:
            # Leemos los campos de la cabecera
            cabecera = False
            for col, valor in enumerate(linea):
                camposCabecera.append(valor)
                lCabecera = linea
        else:
            # Leemos los valores de la línea y los almacenamos
            camposCSV = {"num_linea": i}
            for col, valor in enumerate(linea):
                if encoding != "uft-8":
                    try:
                        valor = valor.encode("utf-8")
                    except AttributeError:
                        pass

                camposCSV[camposCabecera[col]] = valor
            registros.append(camposCSV)
            if verbose:
                print("cargaCSV %s: " % i, camposCSV)
        i += 1

    return registros


def cargarCSV(ficheroCSV, delimitador=";", **kwargs):
    """
    Importa datos de un CSV
    @param ficheroCSV: request (para formularios) o string (para rutas absolutas por línea comandos)
    @param delimitador: tipo de delimitador
    @param kwargs:
        encoding: por defecto utf-8
        verbose: por defecto False
    """
    fichero = []
    encoding = kwargs.get("encoding", "utf-8")
    verbose = kwargs.get("verbose", False)
    excel = kwargs.get("excel", False)

    # Comprobamos si entra en request o como ruta
    try:
        ficheroLeer = open(ficheroCSV, 'rb')
    except:
        ficheroLeer = ficheroCSV


    fichero = csv.reader(
        ficheroLeer,
        delimiter=delimitador,
        quotechar='"',
        encoding=encoding
    )

    datos = leerCSV(fichero, verbose, encoding)

    # Intentamos cerrar el fichero por si es una ruta
    try:
        ficheroLeer.close()
    except:
        pass

    return datos


class Importacion(models.Model):
    modelo = None
    campos = []
    datos = None
    borrarOriginales = False
    modeloRelacion = None
    relaciones = []
    afterSave = []
    beforeSave = []
    funcionTest = []
    convertirISO = False
    bdOrigen = ""
    camposFijos = []
    errores = []
    correctos = 0
    contador = 0
    variablesAuxiliares = {}
    mensajes = {"warning": [], "info": [], "danger": []}
    verbose = False
    conDireccion = False
    conEmail = False
    conTelefono = False
    camposDireccion = False
    conIban = False

    def __init__(self, modelo, fichero='', *args, **kwargs):
        """
        Importa el modelo que le pasemos
        Basta con que las columnas del CSV tengan el nombre del campo que se corresponde
        :param modelo: Clase del modelo que recibirá la importación
        :param args
        :param kwargs:
            direccion: Boolean, si cargamos o no dirección
            telefono o tlfno: Boolean si cargamos o no telefono
            email: Boolean si cargamos emails
            iban: Boolean si cargamos IBAN
            borrar: Boolean si borramos original

        :return:
        """
        super(Importacion, self).__init__(*args)
        self.modelo = modelo
        self.borrarOriginales = kwargs.get("borrar", False)
        self.errores = []
        self.campos = []
        self.datos = None
        self.modeloRelacion = None
        self.relaciones = []
        self.afterSave = []
        self.beforeSave = []
        self.funcionTest = []
        self.bdOrigen = ""
        self.camposFijos = []
        self.correctos = 0
        self.contador = 0
        self.variablesAuxiliares = {}
        self.convertirISO = False
        self.mensajes = {"warning": [], "info": [], "danger": []}
        self.camposDireccion = {
            "direccion": "direccion", "cp": "cp", "localidad": "localidad", "pais": "pais",
            "telefono1": "telefono1", "telefono2": "telefono2", "telefono3": "telefono3",
            "email": "email", "email2": "email2"
        }
        self.conDireccion = kwargs.get("direccion", False)
        self.conEmail = kwargs.get("email", False)
        self.conTelefono = kwargs.get("telefono", False) or kwargs.get("tlfno", False)
        self.conIban = kwargs.get("iban", False)

        if fichero:
            self.cargarCSV(fichero)

    @property
    def cantidadErrores(self):
        return len(self.errores)

    @property
    def cantidadCorrectos(self):
        return len(self.datos) - self.cantidadErrores

    def inicializar(self):
        self.datos = []  # Preparamos los datos
        self.errores = []
        self.correctos = 0
        self.contador = 0

    def addCampo(self, campoModelo, campoCSV):
        """
        Añade una relación de campo modelo a campo CSV
        :param campoModelo: nombre del campo en el modelo
        :param campoCSV: nombre del campo en el csv

        """
        self.campos.append((campoModelo, campoCSV))

    def addCampos(self, diccionarioCampos):
        """
        Añade todos los campos relacionados
        :param diccionarioCampos: diccionario del tipo {"campoModelo": "campoCSV"}
        """

        for k, v in diccionarioCampos.iteritems():
            self.campos.append((k, v))

    def addRelacion(self, modelo, campoModelo, campoInstancia,  campoCSV):
        """
        Establece los parámetros de una relación entre tablas
        :param modelo: Modelo al que apunta el ForeignKey
        :param campoModelo: Campo de búsqueda
        :param campoInstancia: ForeignKey del módelo al que se importa
        :param campoCSV: Título del campoInstancia en el CSV
        Por ejemplo:
        setRelacion(TipoCurso, "codigo", "tipoCurso", "REFTIPO")
        """
        self.relaciones.append(
            {
                "modeloRelacion": modelo,
                "campoRelacionCSV": campoCSV,
                "campoRelacionModelo": campoModelo,
                "campoRelacionInstancia": campoInstancia
            }
        )

    def addVariable(self, variable, valor):
        """
        Añade una variable que se puede utilizar en las funciones test, beforeSave y afterSave
        :param variable: nombre de la variable
        :param valor: valor
        :return:
        """
        self.variablesAuxiliares[variable] = valor

    def cargarFichero(self, fichero, mostrar=False, excel=True):
        """
        Renombrado para no llevar a confusión
        :param fichero: string ruta o request.FILES["fichero"]
        :param mostrar: Boolean mostrar resultado importado
        :param excel: Boolean (True excel o False CSV)
        :return:
        """
        return self.cargarCSV(fichero, mostrar, excel=True)

    def cargarCSV(self, ficheroCSV, mostrar=False, **kwargs):
        """
        Carga las líneas del fichero CSV en el sistema
        :param ficheroCSV: ruta al fichero o request.FILES[fichero] si es un fichero subido
        :param mostrar: Muestra el resultado importado
        :return: el conjunto de datos
        """
        if self.convertirISO:
            encoding = "iso-8859-1"
        else:
            encoding = "utf-8"

        excel = kwargs.get("excel", False)

        if kwargs.get("inicializar", True):
            self.inicializar()

        fichero = cargarCSV(ficheroCSV, encoding=encoding, verbose=self.verbose, excel=excel, formatoFichero="ruta")

        for linea in fichero:
            self.datos.append(linea)

        if mostrar:
            return self.datos

    def cargarBD(self, bdOrigen, **kwargs):
        """
        Establece como origen una BD alternativa (hay que crear el proxy en DATABASE)
        :param bdOrigen: string con el nombre del proxy
        :return:
        """
        filtroOrigen = kwargs.get("filtroOrigen", None)
        inicializar = kwargs.get("inicializar", True)

        if inicializar:
            self.inicializar()

        self.bdOrigen = bdOrigen  # Para indicar al importar que son instancias
        if filtroOrigen:
            self.datos = self.modelo.objects.using(bdOrigen).filter(**filtroOrigen)
        else:
            self.datos = self.modelo.objects.using(bdOrigen).all()

    def cargarQuery(self, bdOrigen, **kwargs):
        """
        Establece como origen una BD alternativa pero de formato libre
        :param bdOrigen: string con el nombre del proxy
        :param kwargs:
            inicializar: si se inicializan los datos
            tabla: string con el nombre de la tabla a importar
            instruccionSQL: si no se especifica se hace un 'select * from tabla'
        :return:
        """
        if kwargs.get("inicializar", True):
            self.inicializar()
        instruccionSQL = kwargs.get("instruccionSQL", None)
        tabla = kwargs.get("tabla", None)

        self.bdOrigen = ""  # Los datos se importarán como si procedieran de un CSV
        # Conectamos a la bd
        cursor = connections[bdOrigen].cursor()
        if instruccionSQL:
            cursor.execute(instruccionSQL)
        elif tabla:
            cursor.execute("select * from %s" % tabla)
        else:
            raise ValueError("Debe especificar una tabla o una instruccionSQL")

        # Cargamos los datos
        desc = cursor.description
        self.datos = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
        cursor.close()

    def addCamposFijos(self, campos):
        """
        Añadimos valores fijos para ciertos campos
        :param campos: diccionario del tipo {"campo": "valor"}
        :return:
        """
        for key, valor in campos.iteritems():
            self.camposFijos.append([key, valor])

    def addTest(self, funcion):
        """
        Añade una función de testeo que se procesa antes de insertar nada
        :param funcion:
        :return:
        """
        self.funcionTest.append(funcion)

    def addAfterSave(self, funcion):
        """
        Añade una función al after save
        :param funcion: Nombre de la función
        Parámentros de la función
         funcion(instancia, linea, variables)
        """
        self.afterSave.append(funcion)

    def addBeforeSave(self, funcion):
        """
        Añade una función al before Save
        :param funcion:
        Parámentros de la función
         funcion(instancia, linea, variables)
        :return:
        """
        self.beforeSave.append(funcion)

    def modificar(self, campoModelo, campoCSV, crearNuevos=True):
        """
        Modifica los datos del modelo original atendiendo a lo que se carga en el CSV
        :param campoModelo: campo del modelo que sirve de id
        :param campoCSV: campo del CSV que sirve de id
        :param crearNuevos: si la instancia no existe la creamos
        :return:
        """

        # Cargar líneas
        for linea in self.datos:
            try:
                filtro = {campoModelo: linea[campoCSV]}
                item = self.modelo.objects.get(**filtro)
            except:
                item = None

            # Si el item existe lo modificamos
            if item:
                self._cargarLinea(item, linea)
            elif crearNuevos:
                item = self.modelo()
                self._cargarLinea(item, linea)

    def comparar(self, campoModelo, campoCSV, verbose=True):
        """
        Compara los datos del modelo original atendiendo a lo que hay en el CSV
        :param campoModelo: campo del modelo que sirve de id
        :param campoCSV: campo del CSV que sirve de id
        :param verbose: Si se muestra o no por pantalla
        :return: array con las líneas
        """
        resultado = []

        # Cargar líneas
        for linea in self.datos:
            try:
                filtro = {campoModelo: linea[campoCSV]}
                item = self.modelo.objects.get(**filtro)
            except:
                item = None

            # Listamos los cambios
            i = 0
            for campos in self.campos:
                i += 1
                if item:
                    valorModelo = str(getattr(item, campos[0])).ljust(40)
                else:
                    valorModelo = "N/A".ljust(40)
                valorLinea = linea[campos[1]]
                l = "%s %s" % (valorModelo, valorLinea)
                resultado.append(l)
                if verbose:
                    print(l)

            if i > 1:
                resultado.append("-".ljust(80, "-"))
                if verbose:
                    print("-".ljust(80, "-"))
            i = 0

        return resultado

    def importar(self):
        """
        Importa los datos
        :return:
        """
        # Tomamos nota de la hora de inicio
        horaInicio = datetime.now()
        cantidadDatos = len(self.datos)

        # Si no hay campos tomamos todos los del modelo
        if not self.campos:
            for campo in self.modelo._meta.get_fields():
                try:
                    self.addCampo(campo.name, campo.name)
                except:
                    pass
        # Comprobamos si hay que borrar los originales
        if self.borrarOriginales:
            self.modelo.objects.all().delete()

        # Realizamos la importación
        if self.bdOrigen:  # Los datos vienen de otra BD
            for item in self.datos:
                instancia = item
                instancia.save()
        else:  # Los datos vienen de un fichero (dividimos en paquetes de 500 para no saturar)
            i = 0
            for linea in self.datos:
                i += 1
                instancia = self.modelo()
                self._cargarLinea(instancia, linea)
                if self.verbose:
                    print ("Cargada instancia %s: %s" % (i, instancia))
                else:
                    print("%s: %s de %s" % (self.modelo.__name__, i, cantidadDatos))

        # Resultados
        horaFin = datetime.now()

        resultados = {
            "Hora inicio": horaInicio.strftime("%H:%M"),
            "Hora fin": horaFin.strftime("%H:%M"),
            "Correctos": self.cantidadCorrectos,
            "Errores": self.cantidadErrores
        }

        return resultados

    def exportar(self, ficheroCSV, registros=None):
        """
        Exporta al CSV
        :return:
        """
        # Inicializamos
        if not registros:
            registros = self.modelo.objects.all()
        linea = []

        # Exportamos
        with open(ficheroCSV, 'wb') as csvfile:
            fichero = csv.writer(csvfile, delimiter=";", quotechar='"')
            # Primera línea: títulos del campo en el CSV
            for campo in self.campos:
                linea.append(campo[1])
            fichero.writerow(linea)

            # Líneas siguientes: registros
            for item in registros:
                linea = []
                for campo in self.campos:
                    dato = getattr(item, campo[0])
                    try:
                        dato = dato.encode("utf-8")
                    except:
                        pass
                    linea.append(dato)
                fichero.writerow(linea)

    def _cargarLinea(self, instancia, linea):
        """
        Importa líneas en las instancias
        Si se ha definido modeloRelacion se encarga de relacionarlas con otros modelos
        :param instancia:
        :param linea:
        :return:
        """
        # Añadimos a la línea el contador de importación
        linea["contadorImportacion"] = self.contador
        self.contador += 1
        # Comprobamos si hay funciones test
        # Las funciones test devuelven True (procesar) o False (no procesar)
        procesar = True
        if self.funcionTest:
            for test in self.funcionTest:
                procesar = test(instancia, linea, self.variablesAuxiliares)

        # Si alguno de los test dio negativo no procesamos
        if not procesar:
            return None

        for campo in self.campos:
            # Inicializamos
            campoInstancia = campo[0]

            # Averiguamos el tipo de campo
            tipoCampo = self.modelo._meta.get_field(campoInstancia).get_internal_type()
            excluidos = ["ForeignKey", "ManyToMayField"]
            cargar = campo[1] in linea and not tipoCampo in excluidos

            # Si se puede cargar lo hacemos
            if cargar:
                try:
                    campoCSV = strToField(linea[campo[1]], tipoCampo, self.convertirISO)
                except:
                    try:
                        campoCSV = strToField(linea[campo[1]], tipoCampo)
                    except:
                        campoCSV = linea[campo[1]]
                setattr(instancia, campoInstancia, campoCSV)

        # Cargamos los campos relacionados
        for relacion in self.relaciones:
            filtro = {relacion["campoRelacionModelo"]: linea[relacion["campoRelacionCSV"]]}
            try:
                instanciaRelacionada = relacion["modeloRelacion"].objects.get(**filtro)
            except:
                instanciaRelacionada = None
            try:
                setattr(instancia, relacion["campoRelacionInstancia"], instanciaRelacionada)
            except:
                self.errores.append(self.contador)
                return False

        # Si hay campos fijos los grabamos
        for campo in self.camposFijos:
            setattr(instancia, campo[0], campo[1])

        # Si tiene funciones beforeSave
        if self.beforeSave:
            for funcion in self.beforeSave:
                funcion(instancia, linea, self.variablesAuxiliares)

        # Grabamos la línea
        grabar = True
        try:
            instancia.save()
        except:
            print("====================================")
            print("Error al cargar la linea: %s\n" % linea)
            print("====================================")
            grabar = False

        # Si hay que pasar la direccion es una persona
        self.cargarDireccion(linea, instancia)

        # Si tiene IBAN es una persona
        if self.conIban:
            iban = linea["iban"].replace("-", "").replace(" ", "")
            instancia.setIBAN(iban)
            instancia.save()

        # Si tiene funciones afterSave
        if self.afterSave and grabar:
            for funcion in self.afterSave:
                funcion(instancia, linea, self.variablesAuxiliares)

    def eliminarRepeticiones(self, campoComprobacion):
        """
        Elimina los items que tengan el campoComprobacion repetido
        :param campoComprobacion: Campo a tener en cuenta
        :return: cantidad de items eliminados
        """
        items = self.modelo.objects.all().order_by(campoComprobacion)
        valorAnterior = ""
        contador = 0
        for item in items:
            valorComprobar = getattr(item, campoComprobacion)
            if valorComprobar == valorAnterior:
                item.delete()
                contador += 1
            else:
                valorAnterior = valorComprobar

        return contador

    def addMensaje(self, tipo, linea):
        """
        Añade un mensaje a uno de los tipos existentes
        :param tipo: 'info', 'alert', 'danger'
        :param linea: texto de la línea a añadir
        :return: None
        """
        self.mensajes[tipo].append(linea)

    def setDireccion(self, **kwargs):
        """
        Establece si se debe cargar teléfonos y/o direcciones
        :param kwargs:
        :return:
        """
        self.conDireccion = kwargs.get("direccion", False)
        self.conTelefono = kwargs.get("telefono", False)
        self.conEmail = kwargs.get("email", False)

        campos = kwargs.get("campos", None)
        if campos:
            self.camposDireccion = campos

    def cargarDireccion(self, linea, instancia):
        """
        Carga la dirección contenida en la línea para las personas
        :param linea:
        :param instancia:
        :return:
        """
        if self.conDireccion:
            try:
                direccion = linea[self.camposDireccion["direccion"]]
            except KeyError:
                direccion = ""
            try:
                cp = linea[self.camposDireccion["cp"]]
            except KeyError:
                cp = ""
            try:
                localidad = linea[self.camposDireccion["localidad"]]
            except KeyError:
                localidad = ""
            try:
                provincia = linea[self.camposDireccion["provincia"]]
            except KeyError:
                provincia = ""
            try:
                pais = linea[self.camposDireccion["pais"]]
            except KeyError:
                pais = ""
            if direccion or cp or localidad or provincia or pais:
                instancia.addDireccion(
                    direccion, cp, localidad, provincia, pais
                )

        if self.conTelefono:
            try:
                t1 = linea[self.camposDireccion["telefono1"]]
            except KeyError:
                t1 = ""
            try:
                t2 = linea[self.camposDireccion["telefono2"]]
            except KeyError:
                t2 = ""
            try:
                t3 = linea[self.camposDireccion["telefono3"]]
            except KeyError:
                t3 = ""
            if t1:
                instancia.addTlfno(t1)
            if t2:
                instancia.addTlfno(t2)
            if t3:
                instancia.addTlfno(t3)

        if self.conEmail:
            try:
                email = linea[self.camposDireccion["email"]]
            except KeyError:
                email = ""
            try:
                email2 = linea[self.camposDireccion["email2"]]
            except KeyError:
                email2 = ""
            if email:
                instancia.addEmail(email)
            if email2:
                instancia.addEmail(email2)
