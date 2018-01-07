#! /bin/bash
#
# Build the archive sites
#
# Assumes you have jekyll bundle installed (one time setup
# https://github.com/istio/istio.github.io#localnative-jekyll-install
#)
# And you've setup firebase (npm install -g firebase-tools; firebase login)
# After running this script, push to archive.istio.io with "firebase deploy"
#

# List of name:tagOrBranch - could be read from a file too
TOBUILD=(
  v0.1:release-0.1
  v0.2:2863aff3e633e6047e9758be5272f894badaa259
  v0.3:12577b7bba1de2f7265b0db7041192a7e04c10ce
  v0.4:4eeb1699fd464522a2b6dfe64e1fd404a2530ce1
  v0.5:master
)

GITDIR=istio.github.io

if [ -d $GITDIR ]; then
  cd $GITDIR
  git fetch
else
  git clone https://github.com/istio/istio.github.io.git
  cd $GITDIR
fi

FILESTOPATCH=(_includes/nav.html _includes/header.html index.html)
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
  for f in "${FILESTOPATCH[@]}"
  do
    mv  $f $f.orig 2> /dev/null && \
    sed -e "s/>Istio/>Istio <span style='font-size: 0.6em;'>Archive $NAME<\/span>/" < $f.orig > $f && \
    echo "*** Succesfully patched $f for $NAME"
  done
  bundle exec jekyll build --config _config.yml,config_override.yml
  git checkout -- .
  git clean -f
  rm -rf ../public/$NAME
  mv _site ../public/$NAME
  echo $NAME >> ../public/versions.txt
done
echo "All done!"
