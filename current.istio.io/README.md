# current.istio.io

This directory contains the source code to produce the [istio.io](https://istio.io) website from a branch of the
[istio.github.io](https://github.com/istio/istio.github.io).

To update istio.io, do the following:

- Edit `./build.sh` and set the BRANCH variable to the Git branch of istio/istio.github.io which you
want to publish as 'istio.io'.

- Run `./build.sh`. This will build a full copy of the site on your local system, in the public directory.

- Run `firebase deploy` to push the updated site content from your system to the live site. The
`build.sh` script includes a bit of info on prerequisites before you can run the script and run
firebase.

You're done!
