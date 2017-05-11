""".

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
"""

import click


def warning(message):
    click.echo(click.style('[WARNING] - ' + message, fg='yellow'))
    pass


def error(message):
    click.echo(click.style('[ERROR] - ' + message, bg='red', fg='white'))
    pass


def success(message):
    click.echo(click.style('[SUCESS] - ' + message, bg='green', fg='white'))
    pass


def log(message):
    click.echo('[LOG] - ' + message)
    pass


def makelogger(topic, bg='reset', fg='reset'):
    def func(message):
        click.echo(click.style('[{}] - '.format(topic.upper()) + message,
                   bg=bg, fg=fg))
    return func
