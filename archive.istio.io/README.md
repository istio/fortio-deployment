# archive.istio.io

This directory contains the source code for the [archive.istio.io](https://archive.istio.io) website.

We archive snapshots of [istio.io](https://istio.io) for every release, which allows our customers to time travel and review
older docs. This is very valuable if they're running older versions and need to look something up.
Archives are maintained at [archive.istio.io](https://archive.istio.io).

To create a new snapshot of istio.io, you need to follow these steps:

- Go to [google.com/cse](https://google.com/cse) and create a new search engine for the snapshot. After you've gone through the hoops necessary
to get access to CSE, you'll see there are many search engines already created, one per existing snapshot. Each search engine is
scoped to search an individual snapshot of archive.istio.io. You will need to create a new similar search engine for the new
snapshot:

  - Within the CSE site, create a new search engine and specify that you'd like to search the url https://archive.istio.io/vXX
    where XX is the version number of the new snapshot such as `https://archive.istio.io/v0.5` or `https://archive.istio.io/v1.2`.

  - Once the engine is created, navigate to the Advanced tab and download the CSE XML file.

  - Edit the downloaded file and change `nonprofit="false"` to `nonprofit="true"`

  - Upload the updated XML file back to CSE.

  - Hunt about within the CSE UI and find the search engine ID for the new search engine and write that down.

- Go to your clone of the the [istio/istio.github.io](https://github.com/istio/istio.github.io) repo and create
a new branch to represent the new snapshot:

   ```bash
   git checkout master
   git pull
   git checkout -b release-XX
   ```

  where XX is the version number of the snapshot such as 0.5 or 1.2

- Edit the file `_data/istio.yml` to set `archive:` to `true` and update the search
engine id to the value you copied from above.

- Save the file, commit the change, and submit a PR to push your changes into the repo.

- Once the PR is introduced, you then need to switch to your clone of the [istio/admin-sites](https://github.com/istio/admin-sites) repo.
In this repo, update the TOBUILD array in the `archive.istio.io/build.sh` file to include an entry for the new snapshot you've created above.

- Run `archive.istio.io/build.sh`. This will build a full copy of the archive.istio.io site on your local
system, in the public directory.

- Run `firebase deploy` to push the updated archive.istio.io from your system to the live site. The
`build.sh` script includes a bit of info on prerequisites before you can run the script and run
firebase.

- Once the site is deployed, go back to your clone of istio.io and add your snapshot to the top of the
`_data/archives.yml`. Commit this file to the repo.

You're done!

