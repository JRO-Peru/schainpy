"""The admin module contains all administrative classes relating to the schain python api.

The main role of this module is to send some reports. It contains a
notification class and a standard error handing class.

$Id: admin.py 3966 2015-12-01 14:32:29Z miguel.urco $
"""
import os
import sys
import time
import traceback
import smtplib
import ConfigParser
import StringIO
from threading import Thread
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from schainpy.utils import log

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

def alarm(level=1, cycle=2):
    '''
    '''

    def target(sound, level, cycle):
        for __ in range(cycle):
            os.system('paplay {}'.format(sound))
            time.sleep(0.5)
    
    sound = os.path.join(get_path(), 'alarm{}.oga'.format(level))
    
    if os.path.exists(sound):
        t = Thread(target=target, args=(sound, level, cycle))
        t.start()
    else:
        log.warning('Unable to play alarm', 'ADMIN')


class SchainConfigure():
    
    __DEFAULT_ADMINISTRATOR_EMAIL = ""
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
        self.__parser = ConfigParser.ConfigParser()
        
        # read conf file into a StringIO with "[madrigal]\n" section heading prepended
        strConfFile = StringIO.StringIO("[schain]\n" + self.__confFile.read())

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
        
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = "(Python SChain API): " + email_from
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
            print "***** Could not connect to server %s *****" %self.__emailServer
            return 0
            
        # Start the server:
    #         smtp.ehlo()
        if self.__emailPass:
            smtp.login(self.__emailFromAddress, self.__emailPass)
        
        # Send the email
        try:
            smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        except:
            print "***** Could not send the email to %s *****" %msg['To']
            smtp.quit()
            return 0
        
        smtp.quit()
        
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
        
        print "***** Sending alert to %s *****" %self.__emailToAddress
        # set up message
    
        sent=self.sendEmail(email_from=self.__emailFromAddress,
                           email_to=self.__emailToAddress,
                           subject=subject,
                           message=message,
                           subtitle=subtitle, 
                           filename=filename)
        
        if not sent:
            return 0
        
        print "***** Your system administrator has been notified *****"
        
        return 1
        
    def notify(self, email, message, subject = "", subtitle="", filename=""):
        """notify sends an email with the given message and title to email.

        Inputs: email (string), message (string), and subject (string)
        
        Returns: void

        Affects: none

        Exceptions: None.
        """
        
        print "Notifying to %s ..." %email
        
        self.sendEmail(email_from=self.__emailFromAddress,
                       email_to=email,
                       subject=subject,
                       message=message,
                       subtitle=subtitle, 
                       filename=filename)
        
        print "***** Your system administrator has been notified *****"

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

if __name__ == '__main__':
    
    test = SchainNotify()

    test.sendAlert('This is a message from the python module SchainNotify', 'Test from SchainNotify')

    print 'Hopefully message sent - check.'
