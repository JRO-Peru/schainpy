import click
import subprocess
import os
import sys
import glob
import schainpy
from schainpy.controller import Project
from schainpy.model import Operation, ProcessingUnit
from schainpy.utils import log
from importlib import import_module
from pydoc import locate
from fuzzywuzzy import process
from schainpy.cli import templates
import inspect
try:
    from queue import Queue
except:
    from Queue import Queue


def getProcs():
    modules = dir(schainpy.model)
    procs = check_module(modules, 'processing')    
    try:
        procs.remove('ProcessingUnit')
    except Exception as e:
        pass
    return procs

def getOperations():
    module = dir(schainpy.model)
    noProcs = [x for x in module if not x.endswith('Proc')]
    operations = check_module(noProcs, 'operation')
    try:
        operations.remove('Operation')
        operations.remove('Figure')
        operations.remove('Plot')
    except Exception as e:
        pass
    return operations

def getArgs(op):
    module = locate('schainpy.model.{}'.format(op))
    try:
        obj = module(1, 2, 3, Queue())
    except:
        obj = module()

    if hasattr(obj, '__attrs__'):
        args = obj.__attrs__
    else:
        if hasattr(obj, 'myrun'):
            args = inspect.getfullargspec(obj.myrun).args
        else:
            args = inspect.getfullargspec(obj.run).args
    
    try:
        args.remove('self')
    except Exception as e:
        pass
    try:
        args.remove('dataOut')
    except Exception as e:
        pass
    return args

def getDoc(obj):    
    module = locate('schainpy.model.{}'.format(obj))
    try:
        obj = module(1, 2, 3, Queue())
    except:
        obj = module()
    return obj.__doc__

def getAll():
    modules = getOperations()
    modules.extend(getProcs())    
    return modules


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(schainpy.__version__)
    ctx.exit()


PREFIX = 'experiment'

@click.command()
@click.option('--version', '-v', is_flag=True, callback=print_version, help='SChain version', type=str)
@click.argument('command', default='run', required=True)
@click.argument('nextcommand', default=None, required=False, type=str)
def main(command, nextcommand, version):
    """COMMAND LINE INTERFACE FOR SIGNAL CHAIN - JICAMARCA RADIO OBSERVATORY V3.0\n
        Available commands:\n
        xml: runs a schain XML generated file\n
        run: runs any python script'\n
        generate: generates a template schain script\n
        list: return a list of available procs and operations\n
        search: return avilable operations, procs or arguments of the given
                operation/proc\n"""
    if command == 'xml':
        runFromXML(nextcommand)
    elif command == 'generate':
        generate()
    elif command == 'test':
        test()
    elif command == 'run':
        runschain(nextcommand)
    elif command == 'search':
        search(nextcommand)
    elif command == 'list':
        cmdlist(nextcommand)
    else:
        log.error('Command {} is not defined'.format(command))


def check_module(possible, instance):
    def check(x):
        try:
            instancia = locate('schainpy.model.{}'.format(x))
            ret = instancia.proc_type == instance
            return ret
        except Exception as e:
            return False
    clean = clean_modules(possible)
    return [x for x in clean if check(x)]


def clean_modules(module):
    noEndsUnder = [x for x in module if not x.endswith('__')]
    noStartUnder = [x for x in noEndsUnder if not x.startswith('__')]
    noFullUpper = [x for x in noStartUnder if not x.isupper()]
    return noFullUpper

def cmdlist(nextcommand):
    if nextcommand is None:
        log.error('Missing argument, available arguments: procs, operations', '')
    elif nextcommand == 'procs':
        procs = getProcs()
        log.success(
            'Current ProcessingUnits are:\n  {}'.format('\n  '.join(procs)), '')
    elif nextcommand == 'operations':
        operations = getOperations()
        log.success('Current Operations are:\n  {}'.format(
            '\n  '.join(operations)), '')
    else:
        log.error('Wrong argument', '')

def search(nextcommand):
    if nextcommand is None:
        log.error('There is no Operation/ProcessingUnit to search', '')    
    else:
        try:
            args = getArgs(nextcommand)
            doc = getDoc(nextcommand)
            log.success('{}\n{}\n\nparameters:\n  {}'.format(
                nextcommand, doc, ', '.join(args)), ''
                )
        except Exception as e:
            log.error('Module `{}` does not exists'.format(nextcommand), '')
            allModules = getAll()
            similar = [t[0] for t in process.extract(nextcommand, allModules, limit=12) if t[1]>80]
            log.success('Possible modules are: {}'.format(', '.join(similar)), '')

def runschain(nextcommand):
    if nextcommand is None:
        currentfiles = glob.glob('./{}_*.py'.format(PREFIX))
        numberfiles = len(currentfiles)
        if numberfiles > 1:
            log.error('There is more than one file to run')
        elif numberfiles == 1:
            subprocess.call(['python ' + currentfiles[0]], shell=True)
        else:
            log.error('There is no file to run')
    else:
        try:
            subprocess.call(['python ' + nextcommand], shell=True)
        except Exception as e:
            log.error("I cannot run the file. Does it exists?")


def basicInputs():
    inputs = {}
    inputs['name'] = click.prompt(
        'Name of the project', default="project", type=str)
    inputs['desc'] = click.prompt(
        'Enter a description', default="A schain project", type=str)
    inputs['multiprocess'] = click.prompt(
        '''Select data type: 

    - Voltage (*.r):                [1]
    - Spectra (*.pdata):            [2]
    - Voltage and Spectra (*.r):    [3]
    
    -->''', type=int)
    inputs['path'] = click.prompt('Data path', default=os.getcwd(
    ), type=click.Path(exists=True, resolve_path=True))
    inputs['startDate'] = click.prompt(
        'Start date', default='1970/01/01', type=str)
    inputs['endDate'] = click.prompt(
        'End date', default='2018/12/31', type=str)
    inputs['startHour'] = click.prompt(
        'Start hour', default='00:00:00', type=str)
    inputs['endHour'] = click.prompt('End hour', default='23:59:59', type=str)
    inputs['figpath'] = inputs['path'] + '/figs'
    return inputs


def generate():
    inputs = basicInputs()

    if inputs['multiprocess'] == 1:
        current = templates.voltage.format(**inputs)
    elif inputs['multiprocess'] == 2:
        current = templates.spectra.format(**inputs)
    elif inputs['multiprocess'] == 3:
        current = templates.voltagespectra.format(**inputs)
    scriptname = '{}_{}.py'.format(PREFIX, inputs['name'])
    script = open(scriptname, 'w')
    try:
        script.write(current)
        log.success('Script {} generated'.format(scriptname))
    except Exception as e:
        log.error('I cannot create the file. Do you have writing permissions?')


def test():
    log.warning('testing')


def runFromXML(filename):
    controller = Project()
    if not controller.readXml(filename):
        return
    controller.start()
    return
