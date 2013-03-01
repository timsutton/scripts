#!/bin/sh

# Packaging script for Adobe Encore CS6 "Functional Content".
#
# Thanks, Adobe, for making three different versions of the "functional content"
# available all in different locations. The ESD download, which is actually in a "standard"
# AAMEE-packageable format, contains only a fraction of the content, and we must resort
# to looking for .zip or .7z archives on forums and blog posts.
#
# Define your own ID_PREFIX, NAME and VERSION. Package identifier will be $ID_PREFIX.$NAME.
#
# Requires fpm:
#
# gem install fpm

NAME=AdobeEncoreCS6_Content
ID_PREFIX=org.great.my
VERSION=6.0.2013.03.01
URL=https://blogs.adobe.com/premiereprotrainingfiles/EncoreContent_en-US.zip
ARK=EncoreContent_en-US.zip
MD5=f42ef6070cd29c8fcb0478fe7c71bf22

# download
if [ ! -e "$ARK" ]; then
    curl -k -L -o "$ARK" "$URL"
fi
VERIFY=$(md5 -q $ARK)
if [ "$VERIFY" != "$MD5" ]; then
    echo "md5 don't match. try wiping it and letting it re-download."
    exit
else
    echo "md5 matches."
fi

fpm --verbose \
-s tar \
-t osxpkg \
--osxpkg-identifier-prefix $ID_PREFIX \
-n $NAME \
-v $VERSION \
-C en-US \
--prefix /Applications/Adobe\ Encore\ CS6 \
"$ARK"
