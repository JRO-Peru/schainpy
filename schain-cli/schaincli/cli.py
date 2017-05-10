import click
import schainpy
import subprocess
from multiprocessing import cpu_count
from schaincli import templates
import os, sys

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(schainpy.__version__)
    ctx.exit()


@click.command()
@click.option('--version', '-v', is_flag=True, callback=print_version, help='SChain version', type=str)
@click.option('--xml', '-x', default=None, help='xml file', type=click.Path(exists=True, resolve_path=True))
@click.argument('command', default='run', required=True)
def main(command, version, xml):
    """COMMAND LINE INTERFACE FOR SIGNAL CHAIN - JICAMARCA RADIO OBSERVATORY"""
    if xml is not None:
        subprocess.call(['schain --file=' + xml], shell=True)
    elif command == 'generate':
        generate()
    elif command == 'test':
        test()
    else:
        click.echo('\x1b[0;37;41m[ERROR] - Command is not defined.\x1b[0m')

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
    scriptname = inputs['name'] + ".py"
    script = open(scriptname, 'w')
    try:
        script.write(current)
        click.echo('\x1b[0;37;42m[SUCCESS] Script {file} generated\x1b[0m'.format(file=scriptname))
    except Exception as e:
        click.echo('\x1b[0;37;41m[ERROR] I cannot create the file. Do you have writing permissions?\x1b[0m')


def test():
    print templates.basic.format(name='hola', desc= 'desc', path='path', startDate='0', endDate='0')
    click.echo('testing')
