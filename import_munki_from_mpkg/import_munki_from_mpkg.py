#!/usr/bin/python

# Simple importer script for importing Munki's tools into a repo per component.
# Follows the 'easiest approach' suggested at
# http://code.google.com/p/munki/wiki/UpdatingMunkiTools
#
# Tim Sutton, November 2012

import os
import subprocess
import optparse

# Base munkiimport options (customize to your needs)
MUNKIIMPORT_TEMPLATE = ['/usr/local/munki/munkiimport',
                        '--nointeractive',
                        '--catalog', 'testing',
                        '--subdirectory', 'support/munkitools',
                        '--unattended-install']

# Custom pkginfo options per Munki component
PKGS = {'core': {'import_opts': ['--requires', 'munkitools_launchd',
                            '--displayname', 'Managed Software Update core components',]},
        'app': {'import_opts': ['--requires', 'munkitools_core',
                                '--displayname', 'Managed Software Update',]},
        'launchd': {'import_opts': ['--displayname', 'Managed Software Update launchd support files',]},
        'admin': {'import_opts': ['--requires', 'munkitools_core',
                                  '--displayname', 'Managed Software Update admin tools',]}}

def main():
    usage = "%prog [components] /path/to/munkitools.mpkg\n\
Multiple components can be specified, and only those specified will be imported."
    o = optparse.OptionParser(usage=usage)
    for pkgname in PKGS.keys():
        o.add_option('--%s' % pkgname, action='store_true', default=False, help="Import %s." % pkgname)
    opts, args = o.parse_args()

    mpkg_root = args[0]

    to_import = [k for (k, v) in opts.__dict__.items() if v]
    print "Going to import the following Munki components: %s" % ', '.join(to_import)

    for pname in PKGS.keys():
        PKGS[pname]['path'] = [p for p in os.listdir(os.path.join(mpkg_root, 'Contents/Packages')) \
                        if p.startswith('munkitools_' + pname)][0]

    for pkg in to_import:
        cmd = MUNKIIMPORT_TEMPLATE
        cmd = cmd + PKGS[pkg]['import_opts']
        cmd.append(os.path.join(mpkg_root, 'Contents/Packages', PKGS[pkg]['path']))
        subprocess.call(cmd)

if __name__ == '__main__':
    main()
