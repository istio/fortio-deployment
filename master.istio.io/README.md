# master.istio.io

This directory contains the source code for the [master.istio.io](https://master.istio.io) website,
which generates a website with the master branch of [istio.github.io](https://github.com/istio/istio.github.io).

To create a new snapshot of the master branch from istio.github.io, you need to follow these steps:

- Run `./build.sh`. This will build a full copy of the master.istio.io site on your local
system, in the public directory.

- Run `firebase deploy` to push the updated master.istio.io from your system to the live site. The
`build.sh` script includes a bit of info on prerequisites before you can run the script and run
firebase.

You're done!

