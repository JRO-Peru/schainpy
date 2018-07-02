'''
SCHAINPY - LOG
    Simple helper for log standarization
    Usage:
        from schainpy.utils import log
        log.error('A kitten died beacuse of you')
        log.warning('You are doing it wrong but what the heck, I'll allow it)
        log.succes('YOU ROCK!')
    To create your own logger inside your class do it like this:
        from schainpy.utils import log
        awesomeLogger = log.makelogger("never gonna", bg="red", fg="white")
        awesomeLogger('give you up')
    which will look like this:
        [NEVER GONNA] - give you up
    with color red as background and white as foreground.
'''

import click


def warning(message, tag='Warning', nl=True):
    if tag:
        click.echo(click.style('[{}] {}'.format(tag, message), fg='yellow'), nl=nl)
    else:
        click.echo(click.style('{}'.format(message), fg='yellow'), nl=nl)
    pass


def error(message, tag='Error', nl=True):
    if tag:
        click.echo(click.style('[{}] {}'.format(tag, message), fg='red'), nl=nl)
    else:
        click.echo(click.style('{}'.format(message), fg='red'), nl=nl)
    pass


def success(message, tag='Success', nl=True):
    if tag:
        click.echo(click.style('[{}] {}'.format(tag, message), fg='green'), nl=nl)
    else:
        click.echo(click.style('{}'.format(message), fg='green'), nl=nl)
    pass


def log(message, tag='Info', nl=True):
    if tag:
        click.echo('[{}] {}'.format(tag, message), nl=nl)
    else:
        click.echo('{}'.format(message), nl=nl)
    pass


def makelogger(tag, bg='reset', fg='reset'):
    def func(message):
        click.echo(click.style('[{}] {}'.format(
            tag.upper(), message), bg=bg, fg=fg))
    return func
