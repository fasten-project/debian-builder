Produce Dynamic Call Graphs
===========================

Docker
------

```bash
docker build -t dynamic .
```

**Example**

```bash
docker run -it --rm -v $(pwd)/callgraph:/callgraph dynamic /bin/bash
apt source zlib
cd zlib-1.2.11.dfsg
./configure && make
echo hello world | valgrind --tool=callgrind --callgrind-out-file=minigzip.txt ./minigzip
gprof2dot -f callgrind -n 0.0 -e 0.0 -o graph.dot minigzip.txt
dot2fasten minigzip graph.dot res.json zlib1g-dev
cp res.json /callgraph/minigzip.json
```

Debian
------

```bash
apt install graphviz libgraphviz-dev valgrind binutils
pip3 install networkx pydot gprof2dot setuptools pygraphviz
```

**Example**

```bash
valgrind --tool=callgrind --callgrind-out-file=exec.txt ./exec
gprof2dot -f callgrind -n 0.0 -e 0.0 -o graph.dot minigzip.txt
dot2fasten minigzip graph.dot res.json package
```

Run with make test/check
------------------------

You can declare the following variable in the beginning of a Makefile,
and then use that variable (as follows) to create the call graph of a 
specific test case.

```Makefile
VALGRIND = valgrind --tool=callgrind --callgrind-out-file=

...

teststatic: static
        @TMPST=tmpst_$$; \
        if echo hello world | $(VALGRIND)static1.txt ./minigzip | \
            $(VALGRIND)static2.txt ./minigzip -d && \
            $(VALGRIND)static3.txt ./example $$TMPST ; then \
          echo '                *** zlib test OK ***'; \
        else \
          echo '                *** zlib test FAILED ***'; false; \
        fi; \
        rm -f $$TMPST
```

dot2fasten
-----------

```
usage: Convert dot graph to FASTEN JSON format [-h] [-s [STATIC_LIBRARIES ...]] [-r [SELF_REGEX ...]]
                                               binary input_dot output_json

positional arguments:
  binary                Analyzed binary
  input_dot
  output_json

optional arguments:
  -h, --help            show this help message and exit
  -s [STATIC_LIBRARIES ...], --static-libraries [STATIC_LIBRARIES ...]
                        Space separated paths of linked static libraries
  -r [SELF_REGEX ...], --self-regex [SELF_REGEX ...]
                        Regex to identify libraries of analyzed product (default: pwd)
```

Output format
-------------

```json
[
  ["//libc6/ld-linux-x86-64.so;C/calloc()", "//libc6/ld-linux-x86-64.so;C/malloc()"], 
  ["//zlib/minigzip;C/deflateEnd()", "//zlib/minigzip;C/zcfree()"], 
  ["//zlib/minigzip;C/deflateInit2_()", "//zlib/minigzip;C/deflateResetKeep()"], 
  ["//zlib/minigzip;C/gz_compress()", "//libc6/libc.so;C/ferror()"],
  ["//zlib/minigzip;C/zcfree()", "//libc6/ld-linux-x86-64.so;C/free()"]
]
```
