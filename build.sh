#!/bin/sh
# if [ "$#" -ne 1 ]; then
#   echo "Usage: $0 build_tag" >&2
#   exit 1
# fi

tagName=`git describe --abbrev=0 --tags`

# replace api_version in nginx config with supplied build tag
sed  "s/{api_version}/$tagName/" nginx.conf.sample > nginx.conf

# build docker image with supplied tag
# docker build -t planr-on.azurecr.io/planr-web-service:$tagName .

# remove nginx conf file
# rm -f nginx.conf

echo "Build succesful for docker image of version:$tagName"
