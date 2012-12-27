#!/usr/bin/python
#
# icnsToWp - Tim Sutton, December 2012

import os
import sys
import xmlrpclib
import optparse
from subprocess import call
from tempfile import mkdtemp
import shutil
from getpass import getpass

WORDPRESS_URL = 'http://macops.ca/xmlrpc.php'
OPTI_TOOL = '/usr/local/bin/optipng'        # optipng's defaults are good enough, no options
COMPRESS_TOOL = '/usr/local/bin/convert'    # using imagemagick
# imagemagick options.. IM docs are poor, use at your own risk
COMPRESS_ARGS = ['-quality', '95', '-depth', '7', '-dither', 'Riemersma']    
ICONUTIL = '/usr/bin/iconutil'

def upload(path, proxy, user, password):
    with open(path, 'rb') as fd:
        imgdata = fd.read()
        # wp.uploadFile endpoint: blogid, username, password, data struct {name, type, bits, overwrite}
        # from API docs:
        # blogid: Not applicable for WordPress, can be any value and will be ignored.
        results = proxy.wp.uploadFile(1, user, password,
        {'name': os.path.basename(path),
        'type': 'image/%s' % (os.path.splitext(path)[1]),
        'bits': xmlrpclib.Binary(imgdata)})
    return results


def main():
    usage = """%prog [options] /path/to/file.icns
Convert a .icns file to one or more png files, optimize and optionally upload to Wordpress"""
    o = optparse.OptionParser(usage=usage)
    o.add_option('-s', '--size', action='append',
        help="Icon size to use - can be specified multiple \
times, should be multiple of 2.")
    o.add_option('-n', '--name',
        help="Name to prepend to file - defaults to name of input .icns file.")
    o.add_option('-w', '--wordpress-upload', action='store_true',
        help="Upload files to Wordpress. Set WORDPRESS_URL in this script to \
http://my-wordpress-site-root/xmlrpc.php and ensure XMLRPC access is enabled.")
    o.add_option('-o', '--optimize', action='store_true',
        help="Optimize file using tools: %s and %s. Modify OPTI_TOOL and \
COMPRESS_TOOL at top of this script edit paths and options." % (OPTI_TOOL, COMPRESS_TOOL))
    o.add_option('-r', '--include-retina', action='store_true',
        help="Include retina (ie. 'file@2x.png') versions")
    opts, args = o.parse_args()

    if len(args) < 1:
        sys.stderr << "Required argument: one or more .icns files to convert!"
        sys.exit

    if opts.wordpress_upload:
        user = raw_input("Wordpress user: ")
        password = getpass("Wordpress password: ")
        proxy = xmlrpclib.ServerProxy(WORDPRESS_URL)

    versions = ['']
    if opts.include_retina:
        versions.append('@2x')

    for icnsfile in args:
        icons_out = mkdtemp()
        call([ICONUTIL, '-c', 'iconset', icnsfile, '-o', icons_out])
        for size in opts.size:
            for version in versions:
                if opts.name:
                    name = opts.name
                else:
                    name = os.path.splitext(os.path.basename(icnsfile))[0]

                iconpath = os.path.join(icons_out, 'icon_%sx%s%s.png' % (size, size, version))
                renamed_iconpath = os.path.join(os.path.dirname(iconpath), os.path.basename(iconpath).replace('icon', name))
                os.rename(iconpath, renamed_iconpath)
                outfile = os.path.join(os.getcwd(), "%s_%s%s.png" % (name, size, version))
                if opts.optimize:
                    # optimize (optipng is in-place)
                    call([OPTI_TOOL, renamed_iconpath])
                    compress_cmd = [COMPRESS_TOOL] + COMPRESS_ARGS
                    # outfile = os.path.join(os.getcwd(), "%s_%s%s.png" % (name, size, version))
                    compress_cmd += [renamed_iconpath, outfile]
                    # compress
                    call(compress_cmd)
                else:
                    # outfile = 
                    shutil.copyfile(renamed_iconpath, outfile)
                if opts.wordpress_upload:
                    results = upload(outfile, proxy, user, password)
                    print "Upload results:"
                    print results
        # clean up
        shutil.rmtree(icons_out)

if __name__ == '__main__':
    main()
