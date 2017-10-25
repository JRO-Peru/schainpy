import schainpy
from schainpy.model import Operation, ProcessingUnit
from pydoc import locate

def clean_modules(module):
    noEndsUnder = [x for x in module if not x.endswith('__')]
    noStartUnder = [x for x in noEndsUnder if not x.startswith('__')]
    noFullUpper = [x for x in noStartUnder if not x.isupper()]
    return noFullUpper

def check_module(possible, instance):
    def check(x):
        try:            
            instancia = locate('schainpy.model.{}'.format(x))
            return isinstance(instancia(), instance)
        except Exception as e:
            return False    
    clean = clean_modules(possible)
    return [x for x in clean if check(x)]


def getProcs():
    module = dir(schainpy.model)
    procs = check_module(module, ProcessingUnit)
    try:
        procs.remove('ProcessingUnit')
    except Exception as e:
        pass
    return procs

def getOperations():
    module = dir(schainpy.model)
    noProcs = [x for x in module if not x.endswith('Proc')]
    operations = check_module(noProcs, Operation)
    try:
        operations.remove('Operation')
    except Exception as e:
        pass
    return operations

def getArgs(op):
    module = locate('schainpy.model.{}'.format(op))
    args = module().getAllowedArgs()
    try:
        args.remove('self')
    except Exception as e:
        pass
    try:
        args.remove('dataOut')
    except Exception as e:
        pass
    return args

def getAll():
    allModules = dir(schainpy.model)
    modules = check_module(allModules, Operation)
    modules.extend(check_module(allModules, ProcessingUnit))
    return modules

def formatArgs(op):
    args = getArgs(op)
    
    argsAsKey = ["\t'{}'".format(x) for x in args]
    argsFormatted = ": 'string',\n".join(argsAsKey)

    print op
    print "parameters = { \n" + argsFormatted + ": 'string',\n }"
    print '\n'
    

if __name__ == "__main__":
    getAll()
    [formatArgs(x) for x in getAll()]

    '''
    parameters = {
        'id': ,
        'wintitle': ,
    }
    '''