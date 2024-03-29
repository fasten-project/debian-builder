# sbuild Docker Images

This is an unofficial Docker image of
[sbuild](https://tracker.debian.org/pkg/sbuild).
You can run sbuild as a Docker container to build Debian binary packages
from Debian sources. It supports the releases;bullseye, buster, stretch and unstable.
Moreover, two extensions of the sbuild image are provided to generate call
graphs. One using [svf](https://svf-tools.github.io/SVF/),
and the other one using
[CScout](https://www2.dmst.aueb.gr/dds/cscout/doc/mancscout.html).

Build
-----

```
docker build --no-cache -t sbuild_buster .
docker build -t sbuild-svf -f svf.Dockerfile .
docker build -t sbuild-cscout -f cscout_buster.Dockerfile .
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

Produce Fasten Call Graphs
--------------------------

To produce call graphs for Debian C packages in
[Fasten's format](https://github.com/fasten-project/fasten/wiki/Extended-Revision-Call-Graph-format#c),
you should use the `schaliasos/sbuild-cscout` image.
For example, to produce the call graph for the package `zlib1g-dev` of
Debian buster release and for amd64 architecture, you should
analyze the source of `zlib`.
You should use the following command.

```
docker run -it --rm --privileged -v $(pwd)/callgraphs:/callgraphs \
    schaliasos/sbuild-cscout sbuild --apt-update --no-apt-upgrade \
    --no-apt-distupgrade --batch --stats-dir=/var/log/sbuild/stats \
    --dist=buster --arch=amd64 zlib
```

The call graph will be generated in the following file.

```
callgraphs/zlib/buster/1\:1.2.11.dfsg-1/amd64/zlib1g-dev/fcg.json
```

Images in Dockerhub
-------------------

* **sbuild**: `schaliasos/sbuild`
* **sbuild-svf**: `schaliasos/sbuild-svf:latest`
* **sbuild-cscout**: `schaliasos/sbuild-cscout:latest`
* **sbuild-dynamic**: `schaliasos/sbuild-dynamic:latest`
