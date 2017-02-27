#!/bin/sh
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 build_tag" >&2
  exit 1
fi

# replace api_version in nginx config with supplied build tag
sed  "s/{api_version}/$1/" nginx.conf.sample > nginx.conf

# build docker image with supplied tag
docker build -t planr-on.azurecr.io/planr-web-service:$1 .

# remove nginx conf file
rm -f nginx.conf

echo "Build succesful for docker image of version:$1"
