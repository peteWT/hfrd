import datetime as dt
import subprocess as sub

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

acdr = raw_input("What is the name of the X drive?")

path = "/Volumes/{0}/".format(acdr)
print 'rm {0}/*'.format(path+'GCDC')

m = sub.Popen('rm {0}/*'.format(path+'GCDC'), shell=True)

t = open(path+'config.txt', 'w+')
t.write(configstring)
t.close()


f = open(path+'time.txt', 'w+')

now = dt.datetime.now()
f.write(timestring.format(now.date().isoformat(),
                          now.time().isoformat())
        )

f.close()

foo = sub.Popen('diskutil unmount /Volumes/'+acdr, shell=True)
foo.wait()
