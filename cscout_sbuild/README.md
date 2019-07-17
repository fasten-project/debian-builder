# sbuild image with CScout and fcan

The image has installed  [sbuild](https://tracker.debian.org/pkg/sbuild),
[CScout](https://www2.dmst.aueb.gr/dds/cscout/),
and [fcan](https://github.com/fasten-project/canonical-call-graph-generator/tree/master/fcan).
You can run a container with that image to produce FASTEN canonicalized call
graphs.

Build
-----

```
docker build -t sbuild_cscout .
```

Run
---

```
mkdir -p /path/to/dir/callgraphs
docker run -it --cap-add SYS_ADMIN -v /path/to/dir:/var/log/sbuild/ sbuild_cscout sbuild --apt-update --no-apt-upgrade --no-apt-distupgrade --batch --stats-dir=/var/log/sbuild/stats --dist=stretch --arch=amd64 PACKAGE
```

If CScout managed to produce a call graph then it dumped it at
`/path/to/folder/callgraphs/PACKAGE-VERSION/can_cgraph.json`
