#! /bin/bash
#
# Build the master.istio.io site
#
# Assumes you have jekyll bundle installed (one time setup
# https://github.com/istio/istio.github.io#localnative-jekyll-install
#
# And you've setup firebase (npm install -g firebase-tools; firebase login)
# After running this script, push to archive.istio.io with "firebase deploy"
#

GITDIR=istio.github.io

if [ -d $GITDIR ]; then
  cd $GITDIR
  git fetch
else
  git clone https://github.com/istio/istio.github.io.git
  cd $GITDIR
fi

echo "### Building '$NAME' from $TAG"
git checkout -- .
git clean -f
git checkout master
git pull 2> /dev/null
echo "baseurl: " > config_override.yml
bundle install
bundle exec jekyll build --config _config.yml,config_override.yml
git checkout -- .
git clean -f
rm -rf ../public
mv _site ../public

echo "All done!"
