# sbuild Docker Images

This is an unofficial Docker image of
[sbuild](https://tracker.debian.org/pkg/sbuild).
You can run sbuild as a Docker container to build Debian binary packages
from Debian sources. It supports the releases; buster, stretch and unstable.
Moreover, two extensions of the sbuild image are provided to generate call
graphs. One using [svf](https://svf-tools.github.io/SVF/),
and the other one using
[CScout](https://www2.dmst.aueb.gr/dds/cscout/doc/mancscout.html).

Build
-----

```
docker build -t sbuild .
docker build -t sbuild-svf -f svf.Dockerfile .
docker build -t sbuild-cscout -f cscout.Dockerfile .
docker build -t sbuild-dynamic -f dynamic.Dockerfile .
```

Run
---

You should always pass the parameters `--privileged` and
`-v /path/to/folder:/callgraphs` where the first path is an absolute path
in the host machine in which the call graphs and logs will be saved.


* Run sbuild on `PACKAGE` from `buster` release.

```
docker run -it --rm --privileged -v /path/to/dir:/callgraphs sbuild \
    sbuild --apt-update --no-apt-upgrade --no-apt-distupgrade --batch \
    --stats-dir=/var/log/sbuild/stats --dist=buster --arch=amd64 PACKAGE
```

* The exact same command can be used with `sbuild_cscout` and `sbuild_svf`.

Logs
----

The logs from `sbuild_svf` and `sbuild_cscout` have the following format.
__All lines that start with `#` are comments.__

```
tool: [svf|cscout]
build: [success|failed]
detect_binaries: [success|failed]
# Per binary
analysis: <binary>: failed: [extract_bc|svf]
analysis: <binary>: success
produce_debs: [success|failed]
detect_packages: pkg1 pkg2 ...
# Per package
produce_callgraph: <package>: failed: [missing deb|empty|fcan]
produce_callgraph: <package>: success
```

Images in Dockerhub
-------------------

* **sbuild**: `schaliasos/sbuild`
* **sbuild-svf**: `schaliasos/sbuild-svf:latest`
* **sbuild-cscout**: `schaliasos/sbuild-cscout:latest`
* **sbuild-dynamic**: `schaliasos/sbuild-dynamic:latest`
