import click
import schainpy
from schaincli import templates
import os, sys

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(schainpy.__version__)
    ctx.exit()


@click.command()
@click.option('--version', '-v', is_flag=True, callback=print_version, help='SChain version', type=str)
@click.argument('command', default='run', required=True)
def main(command, version):
    """COMMAND LINE INTERFACE FOR SIGNAL CHAIN - JICAMARCA RADIO OBSERVATORY"""
    if command == 'generate':
        generate()
        pass
    elif command == 'run':
        pass
    elif command == 'test':
        test()
        pass
    else:
        click.echo('[ERROR] - Command not defined.')

def generate():
    inputs = {}
    inputs['desc'] = click.prompt('Enter a description', default="A schain project", type=str)
    inputs['name'] = click.prompt('Name of the project', default="project", type=str)
    inputs['path'] = click.prompt('Data path', default=os.getcwd(), type=click.Path(exists=True, resolve_path=True))
    inputs['startDate'] = click.prompt('Start date', default='01/01/1970', type=str)
    inputs['endDate'] = click.prompt('End date', default='31/12/2017', type=str)
    inputs['startHour'] = click.prompt('Start hour', default='00:00:00', type=str)
    inputs['endHour'] = click.prompt('End hour', default='23:59:59', type=str)
    script = open(inputs['name'] + ".py", 'w')
    script.write(templates.basic.format(**inputs))

def test():
    print templates.basic.format(name='hola', desc= 'desc', path='path', startDate='0', endDate='0')
    click.echo('testing')
