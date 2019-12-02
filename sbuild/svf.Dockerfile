FROM schaliasos/sbuild

USER root

ENV build_deps="wget python python-pip cmake g++"
ENV svf_deps="zlib1g-dev libncurses5-dev libssl-dev libpcre2-dev zip"
ENV llvm_deps="libllvm-7-ocaml-dev libllvm7 llvm-7 llvm-7-dev llvm-7-doc llvm-7-examples llvm-7-runtime"
ENV clang_deps="clang-7 clang-tools-7 clang-7-doc libclang-common-7-dev libclang-7-dev libclang1-7 clang-format-7 python-clang-7"
ENV llvm_linker_etc="libfuzzer-7-dev lldb-7 lld-7 libc++-7-dev libc++abi-7-dev libomp-7-dev"

# INSTALL PACKAGES
RUN apt -yqq update && apt -yqq upgrade && \
    apt install -yqq $build_deps $svf_deps $llvm_deps $clang_deps $llvm_linker_etc

WORKDIR /root

# INSTALL SVF
ENV LLVM_SRC=/usr/local/installations/llvm-7.0.0.src
ENV LLVM_OBJ=/usr/lib/llvm-7/build
ENV LLVM_DIR=/usr/lib/llvm-7/build
RUN mkdir -p /usr/local/installations
WORKDIR /usr/local/installations
RUN wget http://llvm.org/releases/7.0.0/llvm-7.0.0.src.tar.xz && \
    tar xf llvm-7.0.0.src.tar.xz && \
    git clone https://github.com/SVF-tools/SVF.git SVF
WORKDIR SVF
RUN mkdir Release-build
WORKDIR Release-build
RUN cmake ../ && make -j4
ENV SVF_HOME=/usr/local/installations/SVF/
ENV PATH=$SVF_HOME/Release-build/bin:$PATH
RUN pip install wllvm

WORKDIR /root

# SCRIPT TO RUN TOOLS
COPY ./scripts/svf/analyzer /usr/local/bin/analyzer

# CONFIG FILES
COPY ./config/svf/sbuildrc /root/.sbuildrc
COPY ./config/svf/sbuildrc /home/builder/.sbuildrc
COPY ./config/svf/fstab /etc/schroot/sbuild/fstab

# DIRECTORY TO SAVE CALL-GRAPHS
run mkdir -p /callgraphs
RUN chown -R builder /callgraphs
RUN chmod o+w /callgraphs/

USER builder
WORKDIR /home/builder
