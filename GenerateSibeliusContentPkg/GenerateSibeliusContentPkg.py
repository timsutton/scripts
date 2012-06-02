#!/usr/bin/python

import os
import subprocess
import sys
import time
import tarfile
import optparse
import tempfile

REVERSE_DOMAIN = 'org.awesome.my'


def generateLuggageMakefile(pkgTitle, pkgVersion, sourcePath, destPath):
    """Generate a Luggage Makefile for the project with a single new
    'pack-sibelius-library' rule"""
    makefilePath = os.path.join(destPath, 'Makefile')
    fb = open(makefilePath, 'w')
    fb.write("""
include /usr/local/share/luggage/luggage.make

TITLE=%s
REVERSE_DOMAIN=%s
PACKAGE_VERSION=%s
PAYLOAD=pack-sibelius-library
SOUNDS_DEST_PATH="${WORK_D}/Library/Application Support/Avid/Sibelius Sounds"

pack-sibelius-library:
	sudo mkdir -p ${SOUNDS_DEST_PATH}
	sudo mv "%s" ${SOUNDS_DEST_PATH}/
	sudo chown -R root:admin ${SOUNDS_DEST_PATH}
	sudo chmod -R 755 ${SOUNDS_DEST_PATH}
""" % (pkgTitle, REVERSE_DOMAIN, pkgVersion, sourcePath))
	fb.close()
	

def getPackageInfo():
    """Prompt the user for the name and version of the new package"""
    pkgTitle = raw_input("Enter a name for this package: ")
    rightNow = time.localtime()
    versionDate = "%s.%02d.%02d" % (rightNow.tm_year, rightNow.tm_mon, rightNow.tm_mday)
    pkgVersion = raw_input("Enter a package version: [%s] " % versionDate)
    if not pkgVersion:
        pkgVersion = versionDate
    return (pkgTitle, pkgVersion)


def mountDMGs(files):
    """Given a list of DMGs, mount them one by one, returning a list of tempfile mountpoints"""
    mountPoints = []
    if options.file:
        for item in options.file:
            if os.path.exists(item):
                tmpMount = tempfile.mkdtemp()
                # Mount
                print "Mounting %s..." % os.path.basename(item)
                retcode = subprocess.call(['hdiutil', 'attach', '-nobrowse', '-mountpoint', tmpMount, item])
                if retcode:
                    print "There was an issue mounting the specified image"
                    sys.exit(1)
                else:
                    print "Mounted at %s." % tmpMount
                    # Check if it's a valid content disc
                    if not os.path.exists(os.path.join(tmpMount, 'InstallerData')):
                        print "Not a valid content disc!"
                        sys.exit(1)
                    else:
                        mountPoints.append(tmpMount)

            else:
                print "ERROR: No file at path %s!" % item
        return mountPoints


def unmountDMGs(mountPoints):
    """Given a list of DMGs, unmount them one by one"""
    for mountPoint in mountPoints:
        print "Unmounting %s..." % mountPoint
        subprocess.call(['hdiutil', 'detach', mountPoint])


#
# MAIN
#

usage = """usage: %prog -f [/path/to/dmg] [-f /path/to/another/dmg...]
       %prog --help for more information."""

p = optparse.OptionParser(usage=usage)
p.add_option('--file', '-f', action="append",
                help='''Path to a content dmg. Can be specified multiple times and they will be
                combined into a single package.''')
p.add_option('--make-pkg', '-p', action="store_true",
                help="""Build a pkg with Luggage instead of the default DMG.""")

if os.geteuid() != 0:
    print "ERROR: This script should be run as root, in order for Luggage to run successfully. Exiting..."
    sys.exit(1)

options, arguments = p.parse_args()

if options.file:
    mountPoints = mountDMGs(options.file)
else:
    print "You need to specify at least one content DMG!"
    sys.exit(1)

if mountPoints == []:
    print "No valid DMGs to mount. Exiting..."
    sys.exit(1)

else:
    # Get package info from user interactively
    (pkgTitle, pkgVersion) = getPackageInfo()
    #(pkgTitle, pkgVersion) = ('SibeliusContentTest', '2012.01.15')

    # Set up build dirs
    # buildDirName = 'build' + '.' + pkgTitle
    buildDirPath = os.path.join(os.getcwd(), "build.%s" % pkgTitle)
    libraryExtractPath = os.path.join(buildDirPath, 'Sibelius 7 Sounds')
    if not os.path.exists(buildDirPath):
        os.mkdir(buildDirPath)
        os.mkdir(libraryExtractPath)

    def unbz2File(path):
        tar = tarfile.open(name=path, mode='r:bz2')
        tar.extractall(path=libraryExtractPath)
        tar.close()
        print "%s done" % os.path.basename(path)

    from multiprocessing import Pool
    pool = Pool()

    archivesToProcess = []
    for mountPoint in mountPoints:
        installerDataPath = os.path.join(mountPoint, 'InstallerData')
        for archive in os.listdir(installerDataPath):
            if archive.endswith('.tbz'):
                archivesToProcess.append(os.path.join(installerDataPath, archive))
                print "Added archive %s" % (os.path.join(installerDataPath, archive))
        #        print "Extracting %s..." % archive
        #        subprocess.call(['tar', '-xjvf', os.path.join(installerDataPath, archive), '-C', libraryExtractPath])
        #        unbz2File(os.path.join(installerDataPath, archive), installerDataPath)

    imap_it = pool.imap(unbz2File, archivesToProcess)

    print "Beginning extraction..."
    for item in imap_it:
        pass

#        print "Extracting %s" % os.path.basename(item)

    unmountDMGs(mountPoints)

    # Make the Luggage Makefile
    generateLuggageMakefile(pkgTitle, pkgVersion, libraryExtractPath, buildDirPath)

    # Set up Luggage run
    luggageCmd = ['make']
    if options.make_pkg:
        luggageTarget = 'pkg'
    else:
        luggageTarget = 'dmg'
    luggageCmd.append(luggageTarget)

    # Do Luggage
    print "Building a %s with Luggage..." % luggageTarget
    subprocess.call(luggageCmd, cwd=buildDirPath)
