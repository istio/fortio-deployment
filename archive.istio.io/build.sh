#! /bin/bash
#
# Build the archive site
#
# Assumes you have jekyll bundle installed (one time setup
# https://github.com/istio/istio.github.io#localnative-jekyll-install
#
# And you've setup firebase (npm install -g firebase-tools; firebase login)
# After running this script, push to archive.istio.io with "firebase deploy"
#

# List of name:tagOrBranch
TOBUILD=(
  v0.5:release-0.5
  v0.4:release-0.4
  v0.3:release-0.3
  v0.2:release-0.2
  v0.1:release-0.1
)

# Grab the latest list of releases
wget https://raw.githubusercontent.com/istio/istio.github.io/master/_data/releases.yml

GITDIR=istio.github.io

if [ -d $GITDIR ]; then
  cd $GITDIR
  git fetch
else
  git clone https://github.com/istio/istio.github.io.git
  cd $GITDIR
fi

rm ../public/versions.txt 2> /dev/null
for rel in "${TOBUILD[@]}"
do
  NAME=$(echo $rel | cut -d : -f 1)
  TAG=$(echo $rel | cut -d : -f 2)
  echo "### Building '$NAME' from $TAG"
  git checkout -- .
  git clean -f
  git checkout $TAG
  git pull 2> /dev/null
  echo "baseurl: /$NAME" > config_override.yml
  cp ../releases.yml _data
  bundle install
  bundle exec jekyll build --config _config.yml,config_override.yml
  git checkout -- .
  git clean -f
  rm -rf ../public/$NAME
  mv _site ../public/$NAME
  echo $NAME >> ../public/versions.txt
done
rm ../releases.yml
echo "All done!"
