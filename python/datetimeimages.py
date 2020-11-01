import os, time, shutil, sys

os.chdir(sys.argv[1])

for f in os.listdir('.'):
    ftime = time.gmtime(os.path.getmtime(f))
    timeDir = time.strftime("%Y-%B", ftime)

    if not os.path.isdir(timeDir):
      os.mkdir(timeDir)
    dst = "%s%s%s" % (timeDir, os.path.sep, f)
    shutil.move(f, dst);
    print('File %s has been moved to %s' % (f, dst))
