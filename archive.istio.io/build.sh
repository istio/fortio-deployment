#! /bin/bash
# Build the archive sites

set -e

TOBUILD=(v0.1:release-0.1 v0.2:2863aff3e633e6047e9758be5272f894badaa259 v0.3:12577b7bba1de2f7265b0db7041192a7e04c10ce v0.4:4eeb1699fd464522a2b6dfe64e1fd404a2530ce1)

GITDIR=istio.github.io

if [ -d $GITDIR ]; then
  cd $GITDIR
  git fetch
else
  git clone https://github.com/istio/istio.github.io.git
  cd $GITDIR
fi

for rel in "${TOBUILD[@]}"
do
  NAME=$(echo $rel | cut -d : -f 1)
  TAG=$(echo $rel | cut -d : -f 2)
	echo "Building '$NAME' from $TAG"
  git checkout $TAG
  echo "baseurl: /$NAME" > config_override.yml
  bundle exec jekyll build --config _config.yml,config_override.yml
  rm config_override.yml
  rm -rf ../public/$NAME
  mv _site ../public/$NAME
done
