"""
The admin module contains all administrative classes relating to the schain python api.

The main role of this module is to send some reports. It contains a
notification class and a standard error handing class.

$Id: admin.py 3966 2015-12-01 14:32:29Z miguel.urco $
"""
import os
import sys
import time
import traceback
import smtplib
if sys.version[0] == '3':
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser
import io
from threading import Thread
from multiprocessing import Process
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

import schainpy
from schainpy.utils import log
from schainpy.model.graphics.jroplot_base import popup

def get_path():
    '''
    Return schainpy path
    '''
    
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
            
        return os.path.dirname(os.path.abspath(root))
    except:
        log.error('I am sorry, but something is wrong... __file__ not found')

class Alarm(Process):
    '''
    modes:
      0 - All
      1 - Send email
      2 - Popup message
      3 - Sound alarm
      4 - Send to alarm system TODO
    '''

    def __init__(self, modes=[], **kwargs):
        Process.__init__(self)
        self.modes = modes
        self.kwargs = kwargs

    @staticmethod
    def play_sound():
        sound = os.path.join(get_path(), 'alarm1.oga')
        if os.path.exists(sound):        
            for __ in range(2):
                os.system('paplay {}'.format(sound))
                time.sleep(0.5)
        else:
            log.warning('Unable to play alarm, sound file not found', 'ADMIN')
    
    @staticmethod
    def send_email(**kwargs):
        notifier = SchainNotify()
        notifier.notify(**kwargs)            

    @staticmethod
    def show_popup(message):
        if isinstance(message, list):
            message = message[-1]
        popup(message)

    @staticmethod
    def send_alarm():
        pass

    @staticmethod
    def get_kwargs(kwargs, keys):
        ret = {}
        for key in keys:
            ret[key] = kwargs[key]
        return ret

    def run(self):
        tasks = {
            1 : self.send_email,
            2 : self.show_popup,
            3 : self.play_sound,
            4 : self.send_alarm,
        }

        tasks_args = {
            1: ['email', 'message', 'subject', 'subtitle', 'filename'],
            2: ['message'],
            3: [],
            4: [],
        }
        procs = []
        for mode in self.modes:
            if 0 in self.modes:
                for x in tasks:
                    t = Thread(target=tasks[x], kwargs=self.get_kwargs(self.kwargs, tasks_args[x]))
                    t.start()
                    procs.append(t)
                break
            else:
                t = Thread(target=tasks[mode], kwargs=self.get_kwargs(self.kwargs, tasks_args[mode]))
                t.start()
                procs.append(t)
        for t in procs:
            t.join()


class SchainConfigure():
    
    __DEFAULT_ADMINISTRATOR_EMAIL = "juan.espinoza@jro.igp.gob.pe"
    __DEFAULT_EMAIL_SERVER = "jro-zimbra.igp.gob.pe"
    __DEFAULT_SENDER_EMAIL = "notifier-schain@jro.igp.gob.pe"
    __DEFAULT_SENDER_PASS = ""
    
    __SCHAIN_ADMINISTRATOR_EMAIL = "CONTACT"
    __SCHAIN_EMAIL_SERVER = "MAILSERVER"
    __SCHAIN_SENDER_EMAIL = "MAILSERVER_ACCOUNT"
    __SCHAIN_SENDER_PASS = "MAILSERVER_PASSWORD"
    
    def __init__(self, initFile = None):
        
        # Set configuration file
        if (initFile == None):
            self.__confFilePath = "/etc/schain.conf"
        else:
            self.__confFilePath = initFile

        # open configuration file
        try:
            self.__confFile = open(self.__confFilePath, "r")
        except IOError:
            # can't read from file - use all hard-coded values
            self.__initFromHardCode()
            return
        
        # create Parser using standard module ConfigParser
        self.__parser = ConfigParser()
        
        # read conf file into a StringIO with "[madrigal]\n" section heading prepended
        strConfFile = io.StringIO("[schain]\n" + self.__confFile.read())

        # parse StringIO configuration file
        self.__parser.readfp(strConfFile)
        
        # read information from configuration file
        self.__readConfFile()

        # close conf file
        self.__confFile.close()
    
    
    def __initFromHardCode(self):
        
        self.__sender_email = self.__DEFAULT_SENDER_EMAIL
        self.__sender_pass = self.__DEFAULT_SENDER_PASS
        self.__admin_email = self.__DEFAULT_ADMINISTRATOR_EMAIL
        self.__email_server = self.__DEFAULT_EMAIL_SERVER
    
    def __readConfFile(self):
        """__readConfFile is a private helper function that reads information from the parsed config file.
        
        Inputs: None
        
        Returns: Void.

        Affects: Initializes class member variables that are found in the config file.

        Exceptions: MadrigalError thrown if any key not found.
        """

        # get the sender email
        try:
            self.__sender_email = self.__parser.get("schain", self.__SCHAIN_SENDER_EMAIL)
        except:
            self.__sender_email = self.__DEFAULT_SENDER_EMAIL
        
        # get the sender password
        try:
            self.__sender_pass = self.__parser.get("schain", self.__SCHAIN_SENDER_PASS)
        except:
            self.__sender_pass = self.__DEFAULT_SENDER_PASS
            
        # get the administrator email
        try:
            self.__admin_email = self.__parser.get("schain", self.__SCHAIN_ADMINISTRATOR_EMAIL)
        except:
            self.__admin_email = self.__DEFAULT_ADMINISTRATOR_EMAIL
            
        # get the server email
        try:
            self.__email_server = self.__parser.get("schain", self.__SCHAIN_EMAIL_SERVER)
        except:
            self.__email_server = self.__DEFAULT_EMAIL_SERVER
    
    def getEmailServer(self):
        
        return self.__email_server
    
    def getSenderEmail(self):
        
        return self.__sender_email
    
    def getSenderPass(self):
        
        return self.__sender_pass
    
    def getAdminEmail(self):
        
        return self.__admin_email
    
class SchainNotify:
    """SchainNotify is an object used to send messages to an administrator about a Schain software.

    This object provides functions needed to send messages to an administrator about a Schain , for now
    only sendAlert, which sends an email to the site administrator found is ADMIN_EMAIL

    Usage example:

        import schainpy.admin
    
        try:
        
            adminObj =  schainpy.admin.SchainNotify()
            adminObj.sendAlert('This is important!', 'Important Message')
            
        except schainpy.admin.SchainError, e:
        
            print e.getExceptionStr()


    Non-standard Python modules used:
    None

    Exceptions thrown: None - Note that SchainNotify tries every trick it knows to avoid
    throwing exceptions, since this is the class that will generally be called when there is a problem.

    Change history:

    Written by "Miguel Urco":mailto:miguel.urco@jro.igp.gob.pe  Dec. 1, 2015
    """

    #constants
    
    def __init__(self):
        """__init__ initializes SchainNotify by getting some basic information from SchainDB and SchainSite.

        Note that SchainNotify tries every trick it knows to avoid throwing exceptions, since
        this is the class that will generally be called when there is a problem.

        Inputs: Existing SchainDB object, by default = None.
        
        Returns: void

        Affects: Initializes self.__binDir.

        Exceptions: None.
        """
    
        # note that the main configuration file is unavailable 
        # the best that can be done is send an email to root using localhost mailserver
        confObj = SchainConfigure()
        
        self.__emailFromAddress = confObj.getSenderEmail()
        self.__emailPass = confObj.getSenderPass()
        self.__emailToAddress = confObj.getAdminEmail()
        self.__emailServer  = confObj.getEmailServer()

    def sendEmail(self, email_from, email_to, subject='Error running ...', message="", subtitle="", filename="", html_format=True):

        if not email_to:
            return 0
        
        if not self.__emailServer:
            return 0
        
        log.success('Sending email to {}...'.format(email_to), 'System')

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = "SChain API (v{}) <{}>".format(schainpy.__version__, email_from)
        msg['Reply-to'] = email_from
        msg['To'] = email_to
        
        # That is what u see if dont have an email reader:
        msg.preamble = 'SChainPy'
        
        if html_format:
            message = "<h1> %s </h1>" %subject + "<h3>" + subtitle.replace("\n", "</h3><h3>\n") + "</h3>" + message.replace("\n", "<br>\n")
            message = "<html>\n" + message + '</html>'
        
            # This is the textual part:
            part = MIMEText(message, "html")
        else:
            message = subject + "\n" + subtitle + "\n" + message
            part = MIMEText(message)
            
        msg.attach(part)
        
        if filename and os.path.isfile(filename):
            # This is the binary part(The Attachment):
            part = MIMEApplication(open(filename,"rb").read())
            part.add_header('Content-Disposition', 
                            'attachment',
                            filename=os.path.basename(filename))
            msg.attach(part)
        
        # Create an instance in SMTP server
        try:
            smtp = smtplib.SMTP(self.__emailServer)
        except:
            log.error('Could not connect to server {}'.format(self.__emailServer), 'System')
            return 0
            
        # Start the server:
    #         smtp.ehlo()
        if self.__emailPass:
            smtp.login(self.__emailFromAddress, self.__emailPass)
        
        # Send the email
        try:            
            smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        except:
            log.error('Could not send the email to {}'.format(msg['To']), 'System')
            smtp.quit()
            return 0
        
        smtp.quit()

        log.success('Email sent ', 'System')
        
        return 1
    
    def sendAlert(self, message, subject = "", subtitle="", filename=""):
        """sendAlert sends an email with the given message and optional title.

        Inputs: message (string), and optional title (string)
        
        Returns: void

        Affects: none

        Exceptions: None.
        """
        
        if not self.__emailToAddress:
            return 0
        
        print("***** Sending alert to %s *****" %self.__emailToAddress)
        # set up message
    
        sent=self.sendEmail(email_from=self.__emailFromAddress,
                           email_to=self.__emailToAddress,
                           subject=subject,
                           message=message,
                           subtitle=subtitle, 
                           filename=filename)
        
        if not sent:
            return 0
        
        return 1
        
    def notify(self, email, message, subject = "", subtitle="", filename=""):
        """notify sends an email with the given message and title to email.

        Inputs: email (string), message (string), and subject (string)
        
        Returns: void

        Affects: none

        Exceptions: None.
        """
        
        if email is None:
            email = self.__emailToAddress
        
        self.sendEmail(
            email_from=self.__emailFromAddress,
            email_to=email,
            subject=subject,
            message=message,
            subtitle=subtitle, 
            filename=filename
            )


class SchainError(Exception):
    """SchainError is an exception class that is thrown for all known errors using Schain Py lib.

    Usage example:

        import sys, traceback
        import schainpy.admin
    
        try:
        
            test = open('ImportantFile.txt', 'r')
            
        except:
        
            raise schainpy.admin.SchainError('ImportantFile.txt not opened!',
                                                traceback.format_exception(sys.exc_info()[0],
                                                                        sys.exc_info()[1],
                                                                        sys.exc_info()[2]))
    """


    def __init__(self, strInterpretation, exceptionList=None):
        """ __init__ gathers the interpretation string along with all information from sys.exc_info().

        Inputs:
                strIntepretation - A string representing the programmer's interpretation of
                why the exception occurred

                exceptionList - a list of strings completely describing the exception.
                Generated by traceback.format_exception(sys.exc_info()[0],
                                                        sys.exc_info()[1],
                                                        sys.exc_info()[2])
        
        Returns: Void.

        Affects: Initializes class member variables _strInterp, _strExcList.

        Exceptions: None.
        """
        
        if not exceptionList:
            exceptionList = traceback.format_exception(sys.exc_info()[0],
                                                        sys.exc_info()[1],
                                                        sys.exc_info()[2])
            
        self._strInterp = strInterpretation
        self._strExcList = exceptionList

        
    def getExceptionStr(self):
        """ getExceptionStr returns a formatted string ready for printing completely describing the exception.

        Inputs: None
        
        Returns: A formatted string ready for printing completely describing the exception.

        Affects: None

        Exceptions: None.
        """
        excStr = ''
        excStr = excStr + self._strInterp + '\n\n'

        if self._strExcList != None:
            for item in self._strExcList:
                excStr = excStr + str(item) + '\n'

        return excStr
    
    def __str__(self):
        
        return(self.getExceptionStr())


    def getExceptionHtml(self):
        """ getExceptionHtml returns an Html formatted string completely describing the exception.

        Inputs: None
        
        Returns: A formatted string ready for printing completely describing the exception.

        Affects: None

        Exceptions: None.
        """
        
        excStr = '<BR>The following Schain Python exception has occurred:\n<BR>'
        excStr = excStr + self._strInterp + '\n<BR>\n'

        if self._strExcList != None:
            for item in self._strExcList:
                excStr = excStr + str(item) + '\n<BR>'

        return excStr

class SchainWarning(Exception):
    pass


if __name__ == '__main__':
    
    test = SchainNotify()

    test.sendAlert('This is a message from the python module SchainNotify', 'Test from SchainNotify')

    print('Hopefully message sent - check.')