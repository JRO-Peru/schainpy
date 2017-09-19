"""
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
import os
import sys
import click

def warning(message):
    click.echo(click.style('[WARNING] - ' + message, fg='yellow'))


def error(message):
    click.echo(click.style('[ERROR] - ' + message, fg='red', bg='black'))


def success(message):
    click.echo(click.style(message, fg='green'))


def log(message, topic='LOG'):
    click.echo('[{}] - {}'.format(topic, message))

def makelogger(topic, bg='reset', fg='reset'):
    def func(message):
        click.echo(click.style('[{}] - '.format(topic.upper()) + message,
                   bg=bg, fg=fg))
    return func

class LoggerForFile():
    def __init__(self, filename):
        self.old_stdout=sys.stdout
        cwd = os.getcwd()
        self.log_file = open(os.path.join(cwd, filename), 'w+')
    def write(self, text):
        text = text.rstrip()
        if not text: 
            return
        self.log_file.write(text + '\n')
        self.old_stdout.write(text + '\n')
    def flush(self):
        self.old_stdout.flush()

def logToFile(filename='log.log'):
    logger = LoggerForFile(filename)
    sys.stdout = logger

