# sbuild Docker Image

This is an unofficial Docker image of
[sbuild](https://tracker.debian.org/pkg/sbuild).
You can run sbuild as an Docker container to build Debian binary packages
from Debian sources. It supports stretch and unstable.

Build
-----

```
docker build -t sbuild .
```

Run
---
You should always pass the parameters `--cap-add SYS_ADMIN` and
`-v /path/to/folder:/var/log/sbuild` where the first path is an absolute path
in your file system where logs will be saved.

* Interactive container with bash

```
docker run -it --cap-add SYS_ADMIN -v /path/to/folder:/var/log/sbuild sbuild bash
```

* Run sbuild on PACKAGE using stretch

```
docker run -it --cap-add SYS_ADMIN -v /path/to/dir:/var/log/sbuild/ sbuild sbuild --apt-update --no-apt-upgrade --no-apt-distupgrade --batch --stats-dir=/var/log/sbuild/stats --dist=stretch --arch=amd64 PACKAGE
```

* Run sbuild on PACKAGE using unstable and save the stdout in the logs
directory.

```
docker run -it --cap-add SYS_ADMIN -v /path/to/dir:/var/log/sbuild/ sbuild sbuild --apt-update --no-apt-upgrade --no-apt-distupgrade --batch --stats-dir=/var/log/sbuild/stats --dist=unstable --arch=amd64 PACKAGE && cp *.build /var/log/sbuild/
```
