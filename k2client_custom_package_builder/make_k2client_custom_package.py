#!/usr/bin/python

# Sassafras K2Client package grabber/customizer

# Grabs the most recent K2 Client release, and configure it for an organization's deployment
# environment. An optional argument is the path to output the pkg to, or else the current
# working directory will be used.

# plist_opts below should be modified to suit. These correspond to values that would be set in
# KeyAccess.pkg's 'k2clientconfig.plist' file. The k2clientconfig script located in
# Contents/Resources of versions prior to 7.0.10 of the K2 Client installer documents the full
# set of options. The options used here are the equivalent to running k2clientconfig with
# the following options:
# k2ConfigOpts = ['-h', 'org.example.k2client', '-g', 'yes', '-s', '2', '-l', 'yes']

plist_opts = {
    'KSAddress': 'org.example.k2client',    # KeyServer address
    'AddressPromptUser': '0',       # address prompting during installation
    'AddressDisableChange': '1',    # address change allowed during installation
    'AddressDefaultCurrent': '0',   # use default address (if '0', override address with one used here)
    'KASettingsLocked': '1',        # lock the preference pane
}

import os
import subprocess
import sys
import urllib
import plistlib
import shutil
import tempfile
import xml.etree.ElementTree as ET

pkgutil = '/usr/sbin/pkgutil'
tmpDownloadDir = tempfile.mkdtemp()
K2ClientURL = 'http://www.sassafras.com/links/K2Client.pkg'
distPkgDownloadPath = os.path.join(tmpDownloadDir, 'K2Client.pkg')

print 'Downloading K2Client from URL %s' % K2ClientURL
urllib.urlretrieve(K2ClientURL, distPkgDownloadPath)

print "Downloaded flat pkg is at %s." % distPkgDownloadPath
expandedPath = os.path.join(tempfile.mkdtemp(), 'pkg')
print "Expanding to %s..." % expandedPath
exp_retcode = subprocess.call([pkgutil, '--expand', distPkgDownloadPath, expandedPath], shell=False)
if exp_retcode:
    print "There was an error expanding the flat pkg. Check whether the .pkg file is valid."
    sys.exit(1)

clientPkginfo = ET.parse(os.path.join(expandedPath, 'KeyAccess.pkg/PackageInfo'))
k2Version = clientPkginfo.getroot().attrib['version']
print 'Version downloaded is %s' % k2Version

print 'Configuring package with custom options:'
print plist_opts
clientconfigPlistPath = os.path.join(expandedPath, 'KeyAccess.pkg/Scripts/k2clientconfig.plist')
clientconfigPlist = plistlib.readPlist(clientconfigPlistPath)
for (k, v) in plist_opts.items():
    clientconfigPlist[k] = v
plistlib.writePlist(clientconfigPlist, clientconfigPlistPath)

k2VersionedPkg = 'K2Client-%s.pkg' % k2Version

if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
    pkgOutputPath = os.path.join(sys.argv[1], k2VersionedPkg)
else:
    pkgOutputPath = os.path.join(os.getcwd(), k2VersionedPkg)

subprocess.call([pkgutil, '--flatten', expandedPath, pkgOutputPath])

print "Cleaning up temp folders..."
shutil.rmtree(tmpDownloadDir)
shutil.rmtree(expandedPath)
print "Done. Finished package written to %s." % pkgOutputPath
