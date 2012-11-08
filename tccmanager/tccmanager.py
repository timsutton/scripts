#!/usr/bin/python

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
    o = optparse.OptionParser()
    o.add_option('-p', '--plist', action="store",
        help='Path to a plist to be synced to the TCC db.')
    # o.add_option('-a', '--allow', metavar="bundle-id",
    #     help='Name of an application bundle ID to allow access to contacts.')
    # o.add_option('-d', '--disallow', metavar="bundle-id",
    #     help='Name of an application bundle ID to disallow access to contacts.')
    opts, args = o.parse_args()


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

    conn.close()

if __name__ == '__main__':
    main()
