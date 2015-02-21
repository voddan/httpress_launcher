#!/usr/bin/python
# coding=utf-8
# ssh_connection.py
#
# пароль, если не указан, то используем ssh ключ
#
# a) копируем httpress в /tmp/ на remote hosts с помощью pscp.pssh
# b) запускаем эту программу с помощью psssh
# c) парсим output и суммируем то что нужно суммировать, считаем среднее там где нужно считать среднее.
# d) выводим агрегированный output в stdout - всё


__author__ = 'voddan'
__package__ = None

import paramiko

host = '192.168.0.104'
user = 'voddan'
secret = '04061996'
port = 22


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # ????
client.connect(hostname=host, username=user, password=secret, port=port)
sftp = client.open_sftp()

# print client.exec_command('ls /tmp/')[1].read()
print client.exec_command('ls -l /tmp/httpress_launcher/')[1].read()
print client.exec_command('whoami')[1].read()

# -----------------

remotepath = '/tmp/httpress_launcher/'
remotename = 'httpress_mock_slow_error.py'
localpath = '../bin/' + remotename
comline = '-n 100 -c 10 http://www.mit.edu/'

try:
    sftp.mkdir(remotepath, mode=0777)
except Exception, e:
    print e.message
    pass

sftp.chmod(remotepath, 0777)

sftp.put(localpath, remotepath + remotename)
sftp.chmod(remotepath + remotename, 0700)

print client.exec_command('ls -l ' + remotepath)[1].read()

command = remotepath + remotename + ' ' + comline
# comand = remotepath + remotename + ' ' + comline + ' > ' + remotepath + 'log'
print command
# (inp, out, err) = client.exec_command(command)
# print 'out\n', out.read()
# print 'err\n', err.read()

stdout = client.exec_command(command)[1]

print 'waiting..'
print stdout.read()


print client.exec_command('ls -l ' + remotepath)[1].read()


# ------------
client.close()


# transport = paramiko.Transport((host, port))
# transport.connect(username=user, password=secret)
# sftp = paramiko.SFTPClient.from_transport(transport)
#
# remotepath = '/tmp/httpress_launcher/'
# remotename = 'test1'
# localpath = '../bin/test'
#
# sftp.mkdir(remotepath)
#
# sftp.put(localpath, remotepath + remotename)
#
# sftp.close()
# transport.close()