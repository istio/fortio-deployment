#! /bin/bash
#
# Build the istio.io site
#
# Assumes you have jekyll bundle installed (one time setup
# https://github.com/istio/istio.github.io#localnative-jekyll-install
#
# And you've setup firebase (npm install -g firebase-tools; firebase login)
# After running this script, push to istio.io with "firebase deploy"
#

# Branch of istio.github.io that should be used to build istio.io
BRANCH=release-0.7
GITDIR=istio.github.io

# Grab the latest list of releases
wget https://raw.githubusercontent.com/istio/istio.github.io/master/_data/releases.yml

if [ -d $GITDIR ]; then
  cd $GITDIR
  git fetch
else
  git clone https://github.com/istio/istio.github.io.git
  cd $GITDIR
fi

echo "### Building '$NAME' from $BRANCH"
git checkout -- .
git clean -f
git checkout $BRANCH
git pull 2> /dev/null
echo "baseurl: " > config_override.yml
cp ../releases.yml _data
bundle install
bundle exec jekyll build --config _config.yml,config_override.yml
git checkout -- .
git clean -f
rm -rf ../public
mv _site ../public
rm ../releases.yml

echo "All done!"
