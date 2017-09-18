import click
import schainpy
import subprocess
import os
import sys
import glob
save_stdout = sys.stdout
sys.stdout = open('trash', 'w')
from multiprocessing import cpu_count
from schaincli import templates
from schainpy import controller_api
from schainpy.model import Operation, ProcessingUnit
from schainpy.utils import log
from importlib import import_module
from pydoc import locate
from fuzzywuzzy import process
from schainpy.utils import paramsFinder
sys.stdout = save_stdout


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(schainpy.__version__)
    ctx.exit()


cliLogger = log.makelogger('schain cli')
PREFIX = 'experiment'


@click.command()
@click.option('--version', '-v', is_flag=True, callback=print_version, help='SChain version', type=str)
@click.option('--xml', '-x', default=None, help='run an XML file', type=click.Path(exists=True, resolve_path=True))
@click.argument('command', default='run', required=True)
@click.argument('nextcommand', default=None, required=False, type=str)
def main(command, nextcommand, version, xml):
    """COMMAND LINE INTERFACE FOR SIGNAL CHAIN - JICAMARCA RADIO OBSERVATORY \n
        Available commands.\n
        --xml: runs a schain XML generated file\n
        run: runs any python script starting 'experiment_'\n
        generate: generates a template schain script\n
        search: return avilable operations, procs or arguments of the give operation/proc\n"""
    if xml is not None:
        runFromXML(xml)
    elif command == 'generate':
        generate()
    elif command == 'test':
        test()
    elif command == 'run':
        runschain(nextcommand)
    elif command == 'search':
        search(nextcommand)
    else:
        log.error('Command {} is not defined'.format(command))

def check_module(possible, instance):
    def check(x):
        try:
            instancia = locate('schainpy.model.{}'.format(x))
            return isinstance(instancia(), instance)
        except Exception as e:
            return False
    clean = clean_modules(possible)
    return [x for x in clean if check(x)]


def clean_modules(module):
    noEndsUnder = [x for x in module if not x.endswith('__')]
    noStartUnder = [x for x in noEndsUnder if not x.startswith('__')]
    noFullUpper = [x for x in noStartUnder if not x.isupper()]
    return noFullUpper


def search(nextcommand):
    if nextcommand is None:
        log.error('There is no Operation/ProcessingUnit to search')
    elif nextcommand == 'procs':
        procs = paramsFinder.getProcs()
        log.success('Current ProcessingUnits are:\n\033[1m{}\033[0m'.format('\n'.join(procs)))

    elif nextcommand == 'operations':
        operations = paramsFinder.getOperations()
        log.success('Current Operations are:\n\033[1m{}\033[0m'.format('\n'.join(operations)))
    else:
        try:
            args = paramsFinder.getArgs(nextcommand)
            log.warning('Use this feature with caution. It may not return all the allowed arguments')
            if len(args) == 0:
                log.success('{} has no arguments'.format(nextcommand))
            else:
                log.success('Showing arguments of {} are:\n\033[1m{}\033[0m'.format(nextcommand, '\n'.join(args)))
        except Exception as e:
            log.error('Module {} does not exists'.format(nextcommand))
            allModules = paramsFinder.getAll()
            similar = process.extractOne(nextcommand, allModules)[0]
            log.success('Showing {} instead'.format(similar))
            search(similar)


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
    inputs['desc'] = click.prompt('Enter a description', default="A schain project", type=str)
    inputs['name'] = click.prompt('Name of the project', default="project", type=str)
    inputs['path'] = click.prompt('Data path', default=os.getcwd(), type=click.Path(exists=True, resolve_path=True))
    inputs['startDate'] = click.prompt('Start date', default='1970/01/01', type=str)
    inputs['endDate'] = click.prompt('End date', default='2017/12/31', type=str)
    inputs['startHour'] = click.prompt('Start hour', default='00:00:00', type=str)
    inputs['endHour'] = click.prompt('End hour', default='23:59:59', type=str)
    inputs['figpath'] = inputs['path'] + '/figs'
    return inputs


def generate():
    inputs = basicInputs()
    inputs['multiprocess'] = click.confirm('Is this a multiprocess script?')
    if inputs['multiprocess']:
        inputs['nProcess'] = click.prompt('How many process?', default=cpu_count(), type=int)
        current = templates.multiprocess.format(**inputs)
    else:
        current = templates.basic.format(**inputs)
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
    controller = controller_api.ControllerThread()
    if not controller.readXml(filename):
        return

    plotterObj = controller.useExternalPlotter()

    controller.start()
    plotterObj.start()

    cliLogger("Finishing all processes")

    controller.join(5)

    cliLogger("End of script")
    return
