'''
@author: Daniel Suarez
'''
import os
import glob
import ftplib

try:
    import paramiko
    import scp
except:
    pass

import time

import threading
Thread = threading.Thread

# try:
#     from gevent import sleep
# except:
from time import sleep

from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation

class Remote(Thread):
    """
    Remote is a parent class used to define the behaviour of FTP and SSH class. These clases are
    used to upload or download files remotely.

    Non-standard Python modules used:
        None

    Written by:
        "Miguel Urco":mailto:miguel.urco@jro.igp.gob.pe Jun. 03, 2015
    """

    server = None
    username = None
    password = None
    remotefolder = None

    period = 60
    fileList = []
    bussy = False

    def __init__(self, server, username, password, remotefolder, period=60):

        Thread.__init__(self)

        self.setDaemon(True)

        self.status = 0

        self.__server = server
        self.__username = username
        self.__password = password
        self.__remotefolder = remotefolder

        self.period = period

        self.fileList = []
        self.bussy = False

        self.stopFlag = False

        print("[Remote Server] Opening server: %s" %self.__server)
        if self.open(self.__server, self.__username, self.__password, self.__remotefolder):
            print("[Remote Server] %s server was opened successfully" %self.__server)

        self.close()

        self.mutex = threading.Lock()

    def stop(self):

        self.stopFlag = True
        self.join(10)

    def open(self):
        """
        Connect to server and create a connection class (FTP or SSH) to remote server.
        """
        raise NotImplementedError("Implement this method in child class")

    def close(self):
        """
        Close connection to server
        """
        raise NotImplementedError("Implement this method in child class")

    def mkdir(self, remotefolder):
        """
        Create a folder remotely
        """
        raise NotImplementedError("Implement this method in child class")

    def cd(self, remotefolder):
        """
        Change working directory in remote server
        """
        raise NotImplementedError("Implement this method in child class")

    def download(self, filename, localfolder=None):
        """
        Download a file from server to local host
        """
        raise NotImplementedError("Implement this method in child class")

    def sendFile(self, fullfilename):
        """
        sendFile method is used to upload a local file to the current directory in remote server

        Inputs:
            fullfilename        - full path name of local file to store in remote directory

        Returns:
            0 in error case else 1
        """
        raise NotImplementedError("Implement this method in child class")

    def upload(self, fullfilename, remotefolder=None):
        """
        upload method is used to upload a local file to remote directory. This method changes
        working directory before sending a file.

        Inputs:
            fullfilename        - full path name of local file to store in remote directory

            remotefolder    - remote directory

        Returns:
            0 in error case else 1
        """
        print("[Remote Server] Uploading %s to %s:%s" %(fullfilename, self.server, self.remotefolder))

        if not self.status:
            return 0

        if remotefolder == None:
            remotefolder = self.remotefolder

        if not self.cd(remotefolder):
            return 0

        if not self.sendFile(fullfilename):
            print("[Remote Server] Error uploading file %s" %fullfilename)
            return 0

        print("[Remote Server] upload finished successfully")

        return 1

    def delete(self, filename):
        """
        Remove a file from remote server
        """
        pass

    def updateFileList(self, fileList):
        """
        Remove a file from remote server
        """

        if fileList == self.fileList:
            return 0

        self.mutex.acquire()
        #         init = time.time()
        #         
        #         while(self.bussy):
        #             sleep(0.1)
        #             if time.time() - init > 2*self.period:
        #                 return 0
            
        self.fileList = fileList
        self.mutex.release()
        return 1

    def run(self):

        if not self.status:
            print("Finishing FTP service")
            return

        if not self.cd(self.remotefolder):
            raise ValueError("Could not access to the new remote directory: %s" %self.remotefolder)

        while True:

            for i in range(self.period):
                if self.stopFlag:
                    break
                sleep(1)

            if self.stopFlag:
                break
                
            #   self.bussy = True
            self.mutex.acquire()

            print("[Remote Server] Opening %s" %self.__server)
            if not self.open(self.__server, self.__username, self.__password, self.__remotefolder):
                self.mutex.release()
                continue

            for thisFile in self.fileList:
                self.upload(thisFile, self.remotefolder)

            print("[Remote Server] Closing %s" %self.__server)
            self.close()

            self.mutex.release()
            # self.bussy = False

        print("[Remote Server] Thread stopped successfully")

class FTPClient(Remote):

    __ftpClientObj = None

    def __init__(self, server, username, password, remotefolder, period=60):
        """
        """
        Remote.__init__(self, server, username, password, remotefolder, period)

    def open(self, server, username, password, remotefolder):

        """
        This method is used to set FTP parameters and establish a connection to remote server

        Inputs:
            server    - remote server IP Address

            username    - remote server Username

            password    - remote server password

            remotefolder    - remote server current working directory

        Return:
            Boolean     -     Returns 1 if a connection has been established, 0 otherwise

        Affects:
            self.status        - in case of error or fail connection this parameter is set to 0 else 1

        """

        if server == None:
            raise ValueError("FTP server should be defined")

        if username == None:
            raise ValueError("FTP username should be defined")

        if password == None:
            raise ValueError("FTP password should be defined")

        if remotefolder == None:
            raise ValueError("FTP remote folder should be defined")

        try:
            ftpClientObj = ftplib.FTP(server)
        except ftplib.all_errors as e:
            print("[FTP Server]: FTP server connection fail: %s" %server)
            print("[FTP Server]:", e)
            self.status = 0
            return 0

        try:
            ftpClientObj.login(username, password)
        except ftplib.all_errors:
            print("[FTP Server]: FTP username or password are incorrect")
            self.status = 0
            return 0

        if remotefolder == None:
            remotefolder = ftpClientObj.pwd()
        else:
            try:
                ftpClientObj.cwd(remotefolder)
            except ftplib.all_errors:
                print("[FTP Server]: FTP remote folder is invalid: %s" %remotefolder)
                remotefolder = ftpClientObj.pwd()

        self.server = server
        self.username = username
        self.password = password
        self.remotefolder = remotefolder
        self.__ftpClientObj = ftpClientObj
        self.status = 1

        return 1

    def close(self):
        """
        Close connection to remote server
        """
        if not self.status:
            return 0

        self.__ftpClientObj.close()

    def mkdir(self, remotefolder):
        """
        mkdir is used to make a new directory in remote server

        Input:
            remotefolder    - directory name

        Return:
            0 in error case else 1
        """
        if not self.status:
            return 0

        try:
            self.__ftpClientObj.mkd(dirname)
        except ftplib.all_errors:
            print("[FTP Server]: Error creating remote folder: %s" %remotefolder)
            return 0

        return 1

    def cd(self, remotefolder):
        """
        cd is used to change remote working directory on server

        Input:
            remotefolder    - current working directory

        Affects:
            self.remotefolder

        Return:
            0 in case of error else 1
        """
        if not self.status:
            return 0

        if remotefolder == self.remotefolder:
            return 1

        try:
            self.__ftpClientObj.cwd(remotefolder)
        except ftplib.all_errors:
            print('[FTP Server]: Error changing to %s' %remotefolder)
            print('[FTP Server]: Trying to create remote folder')

            if not self.mkdir(remotefolder):
                print('[FTP Server]: Remote folder could not be created')
                return 0

            try:
                self.__ftpClientObj.cwd(remotefolder)
            except ftplib.all_errors:
                return 0

        self.remotefolder = remotefolder

        return 1

    def sendFile(self, fullfilename):

        if not self.status:
            return 0

        fp = open(fullfilename, 'rb')

        filename = os.path.basename(fullfilename)

        command = "STOR %s" %filename

        try:
            self.__ftpClientObj.storbinary(command, fp)
        except ftplib.all_errors as e:
            print("[FTP Server]:", e)
            return 0

        try:
            self.__ftpClientObj.sendcmd('SITE CHMOD 755 ' + filename)
        except ftplib.all_errors as e:
            print("[FTP Server]:", e)

        fp.close()

        return 1

class SSHClient(Remote):

    __sshClientObj = None
    __scpClientObj = None

    def __init__(self, server, username, password, remotefolder, period=60):
        """
        """
        Remote.__init__(self, server, username, password, remotefolder, period)

    def open(self, server, username, password, remotefolder, port=22):

        """
            This method is used to set SSH parameters and establish a connection to a remote server
            
            Inputs:
                server    - remote server IP Address 
                
                username    - remote server Username 
                
                password    - remote server password
                
                remotefolder    - remote server current working directory
            
            Return: void
            
            Affects: 
                self.status        - in case of error or fail connection this parameter is set to 0 else 1

        """
        import socket

        if server == None:
            raise ValueError("SSH server should be defined")

        if username == None:
            raise ValueError("SSH username should be defined")

        if password == None:
            raise ValueError("SSH password should be defined")

        if remotefolder == None:
            raise ValueError("SSH remote folder should be defined")

        sshClientObj = paramiko.SSHClient()

        sshClientObj.load_system_host_keys()
        sshClientObj.set_missing_host_key_policy(paramiko.WarningPolicy())

        self.status = 0
        try:
            sshClientObj.connect(server, username=username, password=password, port=port)
        except paramiko.AuthenticationException as e:
    #             print "SSH username or password are incorrect: %s"
            print("[SSH Server]:", e)
            return 0
        except SSHException as e:
            print("[SSH Server]:", e)
            return 0
        except socket.error:
            self.status = 0
            print("[SSH Server]:", e)
            return 0

        self.status = 1
        scpClientObj = scp.SCPClient(sshClientObj.get_transport(), socket_timeout=30)

        if remotefolder == None:
            remotefolder = self.pwd()

        self.server = server
        self.username = username
        self.password = password
        self.__sshClientObj = sshClientObj
        self.__scpClientObj = scpClientObj
        self.status = 1

        if not self.cd(remotefolder):
            raise ValueError("[SSH Server]: Could not access to remote folder: %s" %remotefolder)
            return 0

        self.remotefolder = remotefolder

        return 1

    def close(self):
        """
            Close connection to remote server
        """
        if not self.status:
            return 0

        self.__scpClientObj.close()
        self.__sshClientObj.close()

    def __execute(self, command):
        """
            __execute a command on remote server
            
            Input:
                command    - Exmaple 'ls -l'
            
            Return:
                0 in error case else 1
        """
        if not self.status:
            return 0

        stdin, stdout, stderr = self.__sshClientObj.exec_command(command)

        result = stderr.readlines()
        if len(result) > 1:
            return 0

        result = stdout.readlines()
        if len(result) > 1:
            return result[0][:-1]

        return 1

    def mkdir(self, remotefolder):
        """
            mkdir is used to make a new directory in remote server
            
            Input:
                remotefolder    - directory name
            
            Return:
                0 in error case else 1
        """

        command = 'mkdir %s' %remotefolder

        return self.__execute(command)

    def pwd(self):

        command = 'pwd'

        return self.__execute(command)

    def cd(self, remotefolder):
        """
            cd is used to change remote working directory on server
            
            Input:
                remotefolder    - current working directory
                
            Affects:
                self.remotefolder
            
            Return: 
                0 in case of error else 1
        """
        if not self.status:
            return 0

        if remotefolder == self.remotefolder:
            return 1

        chk_command = "cd %s; pwd" %remotefolder
        mkdir_command = "mkdir %s" %remotefolder

        if not self.__execute(chk_command):
            if not self.__execute(mkdir_command):
                self.remotefolder = None
                return 0

        self.remotefolder = remotefolder

        return 1

    def sendFile(self, fullfilename):

        if not self.status:
            return 0

        try:
            self.__scpClientObj.put(fullfilename, remote_path=self.remotefolder)
        except scp.ScpError as e:
            print("[SSH Server]", str(e))
            return 0

        remotefile = os.path.join(self.remotefolder, os.path.split(fullfilename)[-1])
        command = 'chmod 775 %s' %remotefile

        return self.__execute(command)

class SendToServer(ProcessingUnit):

    def __init__(self, **kwargs):

        ProcessingUnit.__init__(self, **kwargs)

        self.isConfig = False
        self.clientObj = None        
    
    def setup(self, server, username, password, remotefolder, localfolder, ext='.png', period=60, protocol='ftp', **kwargs):

        self.clientObj = None
        self.localfolder = localfolder
        self.ext = ext
        self.period = period

        if str.lower(protocol) == 'ftp':
            self.clientObj = FTPClient(server, username, password, remotefolder, period)

        if str.lower(protocol) == 'ssh':
            self.clientObj = SSHClient(server, username, password, remotefolder, period)

        if not self.clientObj:
            raise ValueError("%s has been chosen as remote access protocol but it is not valid" %protocol)

        self.clientObj.start()

    def findFiles(self):

        if not type(self.localfolder) == list:
            folderList = [self.localfolder]
        else:
            folderList = self.localfolder

        #Remove duplicate items
        folderList = list(set(folderList))

        fullfilenameList = []

        for thisFolder in folderList:

            print("[Remote Server]: Searching files on %s" %thisFolder)

            filenameList = glob.glob1(thisFolder, '*%s' %self.ext)

            if len(filenameList) < 1:

                continue

            for thisFile in filenameList:
                fullfilename = os.path.join(thisFolder, thisFile)

                if fullfilename in fullfilenameList:
                    continue

                #Only files modified in the last 30 minutes are considered
                if os.path.getmtime(fullfilename) < time.time() - 30*60:
                    continue

                fullfilenameList.append(fullfilename)

        return fullfilenameList

    def run(self, **kwargs):
        if not self.isConfig:
            self.init = time.time()
            self.setup(**kwargs)
            self.isConfig = True
        
        if not self.clientObj.is_alive():
            print("[Remote Server]: Restarting connection ")
            self.setup(**kwargs)
        
        if time.time() - self.init >= self.period:
            fullfilenameList = self.findFiles()

            if self.clientObj.updateFileList(fullfilenameList):
                print("[Remote Server]: Sending the next files ", str(fullfilenameList))
            self.init = time.time()

    def close(self):
        print("[Remote Server] Stopping thread")
        self.clientObj.stop()


class FTP(object):
    """
    Ftp is a public class used to define custom File Transfer Protocol from "ftplib" python module

    Non-standard Python modules used: None

    Written by "Daniel Suarez":mailto:daniel.suarez@jro.igp.gob.pe  Oct. 26, 2010
    """

    def __init__(self,server = None, username=None, password=None, remotefolder=None):
        """
        This method is used to setting parameters for FTP and establishing connection to remote server

        Inputs:
            server    - remote server IP Address

            username    - remote server Username

            password    - remote server password

            remotefolder    - remote server current working directory

        Return: void

        Affects:
            self.status    - in Error Case or Connection Failed this parameter is set to 1 else 0

            self.folderList    - sub-folder list of remote folder

            self.fileList    - file list of remote folder


        """

        if ((server == None) and (username==None) and (password==None) and (remotefolder==None)):
            server, username, password, remotefolder = self.parmsByDefault()

        self.server = server
        self.username = username
        self.password = password
        self.remotefolder = remotefolder
        self.file = None
        self.ftp = None
        self.status = 0

        try:
            self.ftp = ftplib.FTP(self.server)
            self.ftp.login(self.username,self.password)
            self.ftp.cwd(self.remotefolder)            
            #   print 'Connect to FTP Server: Successfully'
        
        except ftplib.all_errors:
            print('Error FTP Service')
            self.status = 1
            return



        self.dirList = []

        try:
            self.dirList = self.ftp.nlst()

        except ftplib.error_perm as resp:
            if str(resp) == "550 No files found":
                    print("no files in this directory")
                    self.status = 1
                    return

        except ftplib.all_errors:
            print('Error Displaying Dir-Files')
            self.status = 1
            return

        self.fileList = []
        self.folderList = []
        #only for test
        for f in self.dirList:
            name, ext = os.path.splitext(f)
            if ext != '':
                self.fileList.append(f)
    #                print 'filename: %s - size: %d'%(f,self.ftp.size(f))

    def parmsByDefault(self):
        server = 'jro-app.igp.gob.pe'
        username = 'wmaster'
        password = 'mst2010vhf'
        remotefolder = '/home/wmaster/graficos'

        return server, username, password, remotefolder


    def mkd(self,dirname):
        """
        mkd is used to make directory in remote server

        Input:
            dirname    - directory name

        Return:
            1 in error case else 0
        """
        try:
            self.ftp.mkd(dirname)
        except:
            print('Error creating remote folder:%s'%dirname)
            return 1

        return 0


    def delete(self,filename):
        """
        delete is used to delete file in current working directory of remote server

        Input:
            filename    - filename to delete in remote folder

        Return:
            1 in error case else 0
        """

        try:
            self.ftp.delete(filename)
        except:
            print('Error deleting remote file:%s'%filename)
            return 1

        return 0

    def download(self,filename,localfolder):
        """
        download is used to downloading file from remote folder into local folder

        Inputs:
            filename    - filename to donwload

            localfolder    - directory local to store filename

        Returns:
            self.status    - 1 in error case else 0
        """

        self.status = 0


        if not(filename in self.fileList):
            print('filename:%s not exists'%filename)
            self.status = 1
            return self.status

        newfilename = os.path.join(localfolder,filename)

        self.file = open(newfilename, 'wb')

        try:
            print('Download: ' + filename)
            self.ftp.retrbinary('RETR ' + filename, self.__handleDownload)
            print('Download Complete')
        except ftplib.all_errors:
            print('Error Downloading ' + filename)
            self.status = 1
            return self.status

        self.file.close()

        return self.status


    def __handleDownload(self,block):
        """
        __handleDownload is used to handle writing file
        """
        self.file.write(block)


    def upload(self,filename,remotefolder=None):
        """
        upload is used to uploading local file to remote directory

        Inputs:
            filename    - full path name of local file to store in remote directory

            remotefolder    - remote directory

        Returns:
            self.status    - 1 in error case else 0
        """

        if remotefolder == None:
            remotefolder = self.remotefolder

        self.status = 0

        try:
            self.ftp.cwd(remotefolder)

            self.file = open(filename, 'rb')

            (head, tail) = os.path.split(filename)

            command = "STOR " + tail

            print('Uploading: ' + tail)
            self.ftp.storbinary(command, self.file)
            print('Upload Completed')

        except ftplib.all_errors:
            print('Error Uploading ' + tail)
            self.status = 1
            return self.status

        self.file.close()

        #back to initial directory in __init__()
        self.ftp.cwd(self.remotefolder)

        return self.status


    def dir(self,remotefolder):
        """
        dir is used to change working directory of remote server and get folder and file list

        Input:
            remotefolder    - current working directory

        Affects:
            self.fileList    - file list of working directory

        Return:
            infoList    - list with filenames and size of file in bytes

            self.folderList    -    folder list
        """

        self.remotefolder = remotefolder
        print('Change to ' + self.remotefolder)
        try:
            self.ftp.cwd(remotefolder)
        except ftplib.all_errors:
            print('Error Change to ' + self.remotefolder)
            infoList = None
            self.folderList = None
            return infoList,self.folderList

        self.dirList = []

        try:
            self.dirList = self.ftp.nlst()

        except ftplib.error_perm as resp:
            if str(resp) == "550 No files found":
                    print("no files in this directory")
                    infoList = None
                    self.folderList = None
                    return infoList,self.folderList
        except ftplib.all_errors:
            print('Error Displaying Dir-Files')
            infoList = None
            self.folderList = None
            return infoList,self.folderList

        infoList = []
        self.fileList = []
        self.folderList = []
        for f in self.dirList:
            name,ext = os.path.splitext(f)
            if ext != '':
                self.fileList.append(f)
                value = (f,self.ftp.size(f))
                infoList.append(value)

            if ext == '':
                self.folderList.append(f)

        return infoList,self.folderList


    def close(self):
        """
        close is used to close and end FTP connection

        Inputs: None

        Return: void

        """
        self.ftp.close()

class SendByFTP(Operation):

    def __init__(self, **kwargs):
        Operation.__init__(self, **kwargs)
        self.status = 1
        self.counter = 0

    def error_print(self, ValueError):

        print(ValueError, 'Error FTP')
        print("don't worry the program is running...")

    def worker_ftp(self, server, username, password, remotefolder, filenameList):

        self.ftpClientObj = FTP(server, username, password, remotefolder)
        for filename in filenameList:
            self.ftpClientObj.upload(filename)
        self.ftpClientObj.close()

    def ftp_thread(self, server, username, password, remotefolder):
        if not(self.status):
            return

        import multiprocessing

        p = multiprocessing.Process(target=self.worker_ftp, args=(server, username, password, remotefolder, self.filenameList,))
        p.start()

        p.join(3)

        if p.is_alive():
            p.terminate()
            p.join()
            print('killing ftp process...')
            self.status = 0
            return

        self.status = 1
        return

    def filterByExt(self, ext, localfolder):
        fnameList = glob.glob1(localfolder,ext)
        self.filenameList = [os.path.join(localfolder,x) for x in fnameList]

        if len(self.filenameList) == 0:
            self.status = 0

    def run(self, dataOut, ext, localfolder, remotefolder, server, username, password, period=1):

        self.counter += 1
        if self.counter >= period:
            self.filterByExt(ext, localfolder)

            self.ftp_thread(server, username, password, remotefolder)

            self.counter = 0

        self.status = 1