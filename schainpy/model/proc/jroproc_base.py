'''

$Author: murco $
$Id: jroproc_base.py 1 2012-11-12 18:56:07Z murco $
'''

class ProcessingUnit(object):

    """
    Esta es la clase base para el procesamiento de datos.

    Contiene el metodo "call" para llamar operaciones. Las operaciones pueden ser:
        - Metodos internos (callMethod)
        - Objetos del tipo Operation (callObject). Antes de ser llamados, estos objetos
          tienen que ser agreagados con el metodo "add".

    """
    # objeto de datos de entrada (Voltage, Spectra o Correlation)
    dataIn = None
    dataInList = []

    # objeto de datos de entrada (Voltage, Spectra o Correlation)
    dataOut = None

    operations2RunDict = None

    isConfig = False


    def __init__(self, *args, **kwargs):

        self.dataIn = None
        self.dataInList = []

        self.dataOut = None

        self.operations2RunDict = {}

        self.isConfig = False

        self.args = args
        # if (kwargs):
        #     self.kwargs = kwargs
        self.kwargs = kwargs

    def addOperation(self, opObj, objId):

        """
        Agrega un objeto del tipo "Operation" (opObj) a la lista de objetos "self.objectList" y retorna el
        identificador asociado a este objeto.

        Input:

            object    :    objeto de la clase "Operation"

        Return:

            objId    :    identificador del objeto, necesario para ejecutar la operacion
        """

        self.operations2RunDict[objId] = opObj

        return objId

    def getOperationObj(self, objId):

        if objId not in self.operations2RunDict.keys():
            return None

        return self.operations2RunDict[objId]

    def operation(self, **kwargs):

        """
        Operacion directa sobre la data (dataOut.data). Es necesario actualizar los valores de los
        atributos del objeto dataOut

        Input:

            **kwargs    :    Diccionario de argumentos de la funcion a ejecutar
        """

        raise NotImplementedError

    def callMethod(self, name, **kwargs):

        """
        Ejecuta el metodo con el nombre "name" y con argumentos **kwargs de la propia clase.

        Input:
            name        :    nombre del metodo a ejecutar

            **kwargs     :    diccionario con los nombres y valores de la funcion a ejecutar.

        """

        #Checking the inputs
        if name == 'run':

            if not self.checkInputs():
                self.dataOut.flagNoData = True
                return False
        else:
            #Si no es un metodo RUN la entrada es la misma dataOut (interna)
            if self.dataOut.isEmpty():
                return False

        #Getting the pointer to method
        methodToCall = getattr(self, name)

        #Executing the self method

        if hasattr(self, 'mp'):
            if self.mp is False:
                self.mp = True
                self.start()
        else:
            methodToCall(**kwargs)

        if self.dataOut is None:
            return False

        if self.dataOut.isEmpty():
            return False

        return True

    def callObject(self, objId):

        """
        Ejecuta la operacion asociada al identificador del objeto "objId"

        Input:

            objId        :    identificador del objeto a ejecutar

            **kwargs    :    diccionario con los nombres y valores de la funcion a ejecutar.

        Return:

            None
        """

        if self.dataOut is not None and self.dataOut.isEmpty():
            return False

        externalProcObj = self.operations2RunDict[objId]

        if hasattr(externalProcObj, 'mp'):
            if externalProcObj.mp is False:
                externalProcObj.mp = True
                externalProcObj.start()
        else:
            externalProcObj.run(self.dataOut, **externalProcObj.kwargs)

        return True

    def call(self, opType, opName=None, opId=None):

        """
        Return True si ejecuta la operacion interna nombrada "opName" o la operacion externa
        identificada con el id "opId"; con los argumentos "**kwargs".

        False si la operacion no se ha ejecutado.

        Input:

            opType    :    Puede ser "self" o "external"

                Depende del tipo de operacion para llamar a:callMethod or callObject:

                1. If opType = "self": Llama a un metodo propio de esta clase:

                        name_method = getattr(self, name)
                        name_method(**kwargs)


                2. If opType = "other" o"external": Llama al metodo "run()" de una instancia de la
                   clase "Operation" o de un derivado de ella:

                        instanceName = self.operationList[opId]
                        instanceName.run(**kwargs)

            opName    : Si la operacion es interna (opType = 'self'), entonces el "opName" sera
                        usada para llamar a un metodo interno de la clase Processing

            opId    :    Si la operacion es externa (opType = 'other' o 'external), entonces el
                        "opId" sera usada para llamar al metodo "run" de la clase Operation
                        registrada anteriormente con ese Id

        Exception:
               Este objeto de tipo Operation debe de haber sido agregado antes con el metodo:
               "addOperation" e identificado con el valor "opId"  = el id de la operacion.
               De lo contrario retornara un error del tipo ValueError

        """

        if opType == 'self':

            if not opName:
                raise ValueError, "opName parameter should be defined"

            sts = self.callMethod(opName, **self.kwargs)

        elif opType == 'other' or opType == 'external' or opType == 'plotter':

            if not opId:
                raise ValueError, "opId parameter should be defined"

            if opId not in self.operations2RunDict.keys():
                raise ValueError, "Any operation with id=%s has been added" %str(opId)

            sts = self.callObject(opId)

        else:
            raise ValueError, "opType should be 'self', 'external' or 'plotter'; and not '%s'" %opType

        return sts

    def setInput(self, dataIn):

        self.dataIn = dataIn
        self.dataInList.append(dataIn)

    def getOutputObj(self):

        return self.dataOut

    def checkInputs(self):

        for thisDataIn in self.dataInList:

            if thisDataIn.isEmpty():
                return False

        return True

    def setup(self):

        raise NotImplementedError

    def run(self):

        raise NotImplementedError

    def close(self):
        #Close every thread, queue or any other object here is it is neccesary.
        return

class Operation(object):

    """
    Clase base para definir las operaciones adicionales que se pueden agregar a la clase ProcessingUnit
    y necesiten acumular informacion previa de los datos a procesar. De preferencia usar un buffer de
    acumulacion dentro de esta clase

    Ejemplo: Integraciones coherentes, necesita la informacion previa de los n perfiles anteriores (bufffer)

    """

    __buffer = None
    isConfig = False

    def __init__(self, **kwargs):

        self.__buffer = None
        self.isConfig = False
        self.kwargs = kwargs

    def setup(self):

        self.isConfig = True

        raise NotImplementedError

    def run(self, dataIn, **kwargs):

        """
        Realiza las operaciones necesarias sobre la dataIn.data y actualiza los
        atributos del objeto dataIn.

        Input:

            dataIn    :    objeto del tipo JROData

        Return:

            None

        Affected:
            __buffer    :    buffer de recepcion de datos.

        """
        if not self.isConfig:
            self.setup(**kwargs)

        raise NotImplementedError

    def close(self):

        pass
