#! /bin/bash
#
# Build the archive site
#
# Assumes you have Jekyll installed.

# List of name:tagOrBranch
TOBUILD=(
  v1.0:release-1.0
  v0.8:release-0.8
)

TOBUILD_JEKYLL=(
  v0.7:release-0.7
  v0.6:release-0.6
  v0.5:release-0.5
  v0.4:release-0.4
  v0.3:release-0.3
  v0.2:release-0.2
  v0.1:release-0.1
)

# Grab the latest list of releases
wget --no-check-certificate https://raw.githubusercontent.com/istio/istio.github.io/master/data/releases.yml

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
  BASEURL=$(echo /$NAME)
  echo "### Building '$NAME' from $TAG for $BASEURL"
  git checkout -- .
  git clean -f
  git checkout $TAG
  git pull 2> /dev/null
  cp ../releases.yml data

  npm install -g html-minifier
  scripts/gen_site.sh $BASEURL

  git checkout -- .
  git clean -f
  rm -rf ../public/$NAME
  mv public ../public/$NAME
  echo $NAME >> ../public/versions.txt
done

for rel in "${TOBUILD_JEKYLL[@]}"
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
