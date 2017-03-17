tagName=`git describe --abbrev=0 --tags`

# replace api_version in nginx config with latest git tag
sed  "s/{api_version}/$tagName/" nginx.conf.sample > nginx.conf
