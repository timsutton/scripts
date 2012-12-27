# icnsToWp

## overview

A very simple utility that takes one or more icns files as input and optimizes, compress and uploads select sizes to a Wordpress instance using its XMLRPC API. This API is enabled by default in Wordpress 3.5. There is no proper error handling in this script. Edit the config options at the top of the script to set options for the Wordpress URL and optimization tools if you plan to use these options.

## example usage

<code>icnsToWp.py --size 128 --wordpress-upload --include-retina \
/Applications/TextEdit.app/Contents/Resources/Edit.icns</code>

For detailed usage and options:

<code>icnsToWp.py -h</code>

## optimizing

For the `--optimize` option, this script was only tested with optimizer tool `optipng` and compress tool `convert` (ImageMagick/GraphicsMagick) in mind, but others should work fine if the compress tool takes the following argument structure:

`tool [options here] infile outfile`

`optipng` and `convert` are installed easily with [Homebrew](http://mxcl.github.com/homebrew).
