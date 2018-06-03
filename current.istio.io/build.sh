#! /bin/bash
#
# Build the istio.io site
#
# Assumes you have Hugo installed, and
# that you've setup firebase (npm install -g firebase-tools; firebase login)
# After running this script, push to istio.io with "firebase deploy"
#

# Branch of istio.github.io that should be used to build istio.io
BRANCH=release-0.8
GITDIR=istio.github.io
export DEPLOY_URL=https://istio.io

# Grab the latest list of releases
wget --no-check-certificate https://raw.githubusercontent.com/istio/istio.github.io/master/data/releases.yml

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
cp ../releases.yml data
make prep_generate
make generate
rm -fr ../public
mv public ..
git checkout -- .
git clean -f
rm ../releases.yml

echo "All done!"
