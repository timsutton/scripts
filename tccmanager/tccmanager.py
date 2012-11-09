#!/usr/bin/python
#
# Make arbitrary changes to the TCC sqlite3 database, which stores the
# applications that are allowed to access a user's contacts.
#
# Accepted input is in the form of a plist - see the 'tcc_services.plist' example.
# It will add entries that don't already exist and update existing ones. It does not remove
# entries that are present in the DB but not in the input plist.
#
# Ideally we could pass app bundle names or .app paths directly at the command line so that changes can
# be made more atomically or run as one-off commands in a LaunchAgent script, for example.

import sqlite3
import os
import sys
import plistlib
import optparse

TCC_DIR = os.path.expanduser('~/Library/Application Support/com.apple.TCC')
DBPATH = os.path.join(TCC_DIR, 'TCC.db')

def createDB(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute('''CREATE TABLE admin
                 (key TEXT PRIMARY KEY NOT NULL, value INTEGER NOT NULL)''')
    c.execute("INSERT INTO admin VALUES ('version', 4)")
    c.execute('''CREATE TABLE access
                 (service TEXT NOT NULL,
                    client TEXT NOT NULL,
                    client_type INTEGER NOT NULL,
                    allowed INTEGER NOT NULL,
                    prompt_count INTEGER NOT NULL,
                    CONSTRAINT key PRIMARY KEY (service, client, client_type))''')
    c.execute('''CREATE TABLE access_times
                 (service TEXT NOT NULL,
                    client TEXT NOT NULL,
                    client_type INTEGER NOT NULL,
                    last_used_time INTEGER NOT NULL,
                    CONSTRAINT key PRIMARY KEY (service, client, client_type))''')
    c.execute('''CREATE TABLE access_overrides
                 (service TEXT PRIMARY KEY NOT NULL)''')
    conn.commit()
    conn.close()

def main():
    usage = "usage: %prog --plist db_entries.plist | (--allow | --disallow) app.bundle.id"
    o = optparse.OptionParser(usage=usage)
    o.add_option('-p', '--plist', action="store",
        help='Path to a plist to be synced to the TCC db.')
    o.add_option('-a', '--allow', metavar="bundle-id", action="append",
        help='Name of an application bundle ID to allow access to contacts. \
Can be specified multiple times.')
    o.add_option('-d', '--disallow', metavar="bundle-id", action="append",
        help='Name of an application bundle ID to disallow access to contacts. \
Can be specified multiple times.')
    opts, args = o.parse_args()

    if (opts.plist and opts.allow) or (opts.plist and opts.disallow):
        print "--plist option is mutually exclusive to using --allow or --disallow."
        sys.exit(1)

    db_exists = False
    if not os.path.exists(TCC_DIR):
        os.mkdir(TCC_DIR, int('700', 8))
    else:
        db_exists = True

    conn = sqlite3.connect(DBPATH)
    c = conn.cursor()

    # Setup the database if it doesn't already exist
    if not db_exists:
        createDB(DBPATH)

    if opts.plist:
        try:
            apps = plistlib.readPlist(opts.plist)
        except:
            print "Error reading plist!"
            print sys.exc_info()
            print sys.exit(2)
        
        # add or modify any kTCCServiceAddressBook items we might have defined in the plist
        if 'kTCCServiceAddressBook' in apps.keys():
            for app, attrs in apps['kTCCServiceAddressBook'].items():
                data = ('kTCCServiceAddressBook',
                    app,
                    attrs['client_type'],
                    attrs['allowed'],
                    attrs['prompt_count'])
                c.execute('''INSERT or REPLACE INTO access values
                    (?, ?, ?, ?, ?)''', data)
                conn.commit()

    else:
        if opts.allow:
            for bundle_id in opts.allow:
                c.execute('''INSERT or REPLACE INTO access values
                    ('kTCCServiceAddressBook', ?, 0, 1, 0)''', (bundle_id,))
                conn.commit()

        if opts.disallow:
            for bundle_id in opts.disallow:
                c.execute('''INSERT or REPLACE INTO access values
                    ('kTCCServiceAddressBook', ?, 0, 0, 0)''', (bundle_id,))
                conn.commit()

    conn.close()

if __name__ == '__main__':
    main()
