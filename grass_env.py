import os, sys

envt={"GISBASE":"/usr/lib/grass70/","PATH":"$PATH:$GISBASE/bin:$GISBASE/scripts","LD_LIBRARY_PATH":"$LD_LIBRARY_PATH:$GISBASE/lib","GIS_LOCK":"$$","PYTHONPATH":"$PYTHONPATH:$GISBASE/etc/python","grassdb":"grassdata"}

gisbase=os.environ['GISBASE']= envt['GISBASE']
sys.path.append(os.path.join(os.environ['GISBASE'], "etc", "python"))
gisdb=os.path.join(os.environ['HOME'],envt['grassdb'])
