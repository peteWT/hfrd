import datetime
import os
import subprocess as sub
import shlex
import platform as pf


babel = 'gpsbabel -t -i m241 -f /dev/tty.HOLUX_M-241-SPPSlave* -o gpx -F'

gpDir = 'DCIM100GOPRO/'
rDir = "{0}Data Collection/{1}/timeandmotion/"
gpTarget = 'gopro/'
x16target = 'accel/'
gps_target = 'gps/'
timestring = '''{0} {1}\n'''

configstring = ''';X16-1D config file
;set sample rate
;available rates 12, 25, 50, 100, 200, 400
samplerate = 100
;record constantly
deadband = 0
deadbandtimeout = 0
;set file size to 60 minutes of data
samplesperfile = 360000
;set status indicator brightness
statusindicators = high
rebootOnDisconnect
;microres
;see X16-1D user manual for other config options'''


def mountpoint(uname='pete'):
    if pf.system() == 'Linux':
        return {'mnt': '/media/{0}/'.format(uname),
                'ddir': '/home/{0}/box.com/'.format(uname),
                'umt': 'umount'}
    elif pf.systerm() == 'Darwin':
        return {'mnt': '/Volumes/',
                'ddir': '/Users/pete/Box Sync/HFRD/',
                'umt': 'diskutil unmount'}

tDirs = mountpoint()

location = raw_input('''
What HFRD location is the data from
('ShaverLake', 'BigBear', or 'SantaRosa')?''')
# Set output location
rootDir = rDir.format(tDirs['ddir'], location)

date_transfered = datetime.datetime.today()
drive_id = raw_input("Whats the name of the accel drive?")
# set source directory
x16Dir = '{0}{1}/GCDC/'.format(tDirs['mnt'], drive_id)

logger_id = raw_input("What is the device id #?")
gopro_or_logger = raw_input("Is this a datalogging kit (dl) or a GoPro (gp)?")
equipment = raw_input("What equipment was this mounted on?")
hfrd_id = raw_input("What is the HFRD unit id number?")

date_start = raw_input("On what date does the data start (YYYY-MM-DD)?")
date_end = raw_input("On what date does the data end (YYYY-MM-DD)?")
time_start = raw_input("What does the data start to \
reflect the subject (military hh:mm)?")
time_stop = raw_input("What time does the data stop \
reflecting the subject (military hh:mm)?")

inp = '''todays date- {0}
loggingstart_date- {8}
loggingend_date- {9}
logger_id- {1}
gopro_or_logger- {2}
eqipment- {3}
hfrd_id- {4}
time_start- {5}
time_stop- {6}
drive_id- {7}'''.format(date_transfered,
                        logger_id,
                        gopro_or_logger,
                        equipment,
                        hfrd_id,
                        time_start,
                        time_stop,
                        logger_id,
                        date_start,
                        date_end)

check = raw_input('Does this look right (y or Control-D)? {0}'.format(inp))
if gopro_or_logger == 'dl':
    accdir = rootDir+x16target
    gpsdir = rootDir+gps_target
    dname = '{0}{1}{2}_{3}'.format(accdir,
                                   date_transfered.month,
                                   date_transfered.day,
                                   equipment.replace(' ', '').lower())
    if os.path.exists(dname):
        os.rmdir(dname)
        os.mkdir(dname)
    else:
        os.mkdir(dname)
    f = open(dname + '/meta.txt', 'w+')
    f.write(inp)
    f.close()

rsnc = shlex.split('''
rsync -av --progress {0} {1}'''.format(
    x16Dir.replace(' ', '\ '),
    dname.replace(' ', '\ ')+'/'))

t = sub.Popen(rsnc)
t.wait()


dPath = "{0}{1}/".format(tDirs['mnt'], drive_id)
print 'rm {0}/*'.format(dPath+'GCDC')

m = sub.Popen('rm {0}/*'.format(dPath+'GCDC'), shell=True)

cfg = open(dPath+'config.txt', 'w+')
cfg.write(configstring)
cfg.close()

f = open(dPath+'time.txt', 'w+')

now = datetime.datetime.now()
f.write(timestring.format(now.date().isoformat(),
                          now.time().isoformat())
        )

f.close()

print '{0} {1}{2}'.format(tDirs['umt'],
                                     tDirs['mnt'],
                                     drive_id)

#unmt = sub.Popen('{0} {1}{2}'.format(tDirs['umt'],
#                                     tDirs['mnt'],
#                                     drive_id), shell=True)
#unmt.wait()
