generateSibeliusContentPkg
==========================

Overview
--------

Sibelius 7 has a lot of content to optionally install. This script's purpose is to automate the process of repacking this content (or a subset thereof) into an OS X installer package using The Luggage. It takes advantage of Python's multiprocessing module to greatly speed up the bzip2 decompression of the audio sample files to stage them for packaging.

Sibelius ships with 3 content discs, but there is also additional content on the main application disc, as well as content update DMGs available for download. These are all valid input to the script, so it's possible to combine them in multiple packages if desired.


Requirements
------------

* The Luggage
* Python 2.6 or greater
* A _lot_ of disk space (100GB or greater for all content discs, due to space required to stage the package, archive, and wrap in a disk image)


Caveats
-------

There's very little error handling. It also assumes the shell the script is run from will be able to run the 'make' command to process Luggage Makefiles.


Usage
-----

1. Create DMGs of the content discs you want to repackage.
2. Run the script using the -f argument to specify each of these DMGs whose content you want to add to the package. You can use the -f argument multiple times to combine multiple packages.
3. The script will ask a couple questions, the package title, version string, etc.
4. For each disk image, the content will be decompressed to a staging area, a Luggage Makefile will be generated and 'make dmg' will be run against it. There is an optional argument '-p' that will just run 'make pkg' instead.
5. Due to the amount of space required to stage, package and compress the data, you may want to manually run a 'make clean' from this script's working folder to clean up the Luggage temporary files.