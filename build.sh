# This script generates the nginx configuration file for use within the Docker image
#
# It SHOULD be run before building the image whose build steps are described in ./Dockerfile
tagName=`git describe --abbrev=0 --tags`

# replace api_version in nginx config with latest git tag
sed  "s/{api_version}/$tagName/" nginx.conf.sample > nginx.conf
