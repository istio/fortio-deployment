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

FILESTOPATCH=(_includes/nav.html index.html)
VERSIONS_LIST=""
for rel in "${TOBUILD[@]}"
do
  NAME=$(echo $rel | cut -d : -f 1)
  TAG=$(echo $rel | cut -d : -f 2)
	echo "Building '$NAME' from $TAG"
  git checkout $TAG
  echo "baseurl: /$NAME" > config_override.yml
  for f in "${FILESTOPATCH[@]}"
  do
    mv  $f $f.orig
    sed -e "s/>Istio/>Istio Archive $NAME/" < $f.orig > $f
  done
  bundle exec jekyll build --config _config.yml,config_override.yml
  rm config_override.yml
  git checkout -- .
  rm -rf ../public/$NAME
  mv _site ../public/$NAME
  VERSIONS_LIST="${VERSIONS_LIST}<li><a href='$NAME\/'>$NAME<\/a><\/li>"
done
sed -e "s/VERSIONS_LIST/$VERSIONS_LIST/" < ../index.html.in > ../public/index.html
echo "All done!"
