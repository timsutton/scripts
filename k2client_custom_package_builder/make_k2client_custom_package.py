#!/usr/bin/python

# Grab the most recent K2 Client release, and configure it for an organization's deployment
# environment.

# k2ConfigOpts should be modified to suit. For a full help on the available options, run
# the k2clientconfig script located in Contents/Resources of the K2 Client installer.

# The sample options here specify the host (and -g yes to overwrite the existing host),
# a silent install, and for the KeyAccess prefpane to be locked for users.

# configure these for your org:
k2ConfigOpts = ['-h', 'org.example.k2server', '-g', 'yes', '-s', '2', '-l', 'yes']

import os, subprocess, sys, urllib, plistlib, shutil

scriptDir = os.path.dirname(sys.argv[0])
distVolume = '/Volumes/K2Client'		# making assumptions about the volume title...
K2ClientURL = 'http://www.sassafras.com/links/K2Client.dmg'	# download URL from Sassafras
distDmgDownloadPath = os.path.join(scriptDir, 'K2Client.dmg')

k2ConfigCmd = 'k2clientconfig'
k2ConfigPath = os.path.join(scriptDir, 'K2Client.mpkg', 'Contents', 'Resources', k2ConfigCmd)
k2ConfigFull = [ k2ConfigPath ] + k2ConfigOpts
k2ConfigDebug = [ k2ConfigPath ] + ['-d']

print 'Downloading K2Client...'
urllib.urlretrieve(K2ClientURL, os.path.join(scriptDir, distDmgDownloadPath))
print 'Mounting dmg...'
subprocess.call(['/usr/bin/hdiutil', 'attach', '-nobrowse', '-quiet', distDmgDownloadPath])
print 'Copying K2Client.mpkg...'
if os.path.exists(distVolume):
	# being lazy and using cp to ensure copying potential resource forks/xattrs
	subprocess.call(['cp', '-R', '/Volumes/K2Client/K2Client.mpkg', scriptDir])
else:
	sys.exit(1)
print 'Unmounting DMG...'
subprocess.call(['/usr/bin/hdiutil', 'detach', distVolume])

k2Info = plistlib.readPlist(os.path.join(scriptDir, 'K2Client.mpkg/Contents/Info.plist'))
k2Version = k2Info['CFBundleVersion']
print 'Version downloaded is %s' % k2Version
print 'Configuring package with custom options...'
subprocess.call(k2ConfigFull)
print 'Displaying k2clientconfig config...'
subprocess.call(k2ConfigDebug)

k2VersionedFolder = 'K2Client-%s' % k2Version
k2VersionedDmg = k2VersionedFolder + '.dmg'
os.mkdir(os.path.join(scriptDir, k2VersionedFolder))

print 'Wrapping package into %s...' % k2VersionedDmg
shutil.move(os.path.join(scriptDir, 'K2Client.mpkg'), os.path.join(scriptDir, k2VersionedFolder))
subprocess.call(['/usr/bin/hdiutil', 'create', os.path.join(scriptDir, k2VersionedDmg), '-srcfolder', os.path.join(scriptDir, k2VersionedFolder)])
print "Cleaning up..."
shutil.rmtree(os.path.join(scriptDir, k2VersionedFolder))
os.remove(os.path.join(scriptDir, 'K2Client.dmg'))
print "Done."
sys.exit(0)