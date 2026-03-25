FROM ubuntu:20.04
WORKDIR /app

# install tools needed for eigenstrat installation
RUN apt-get update \
    && apt-get install -y --no-install-recommends liblapacke-dev libc6-dev gcc ca-certificates git make libgsl-dev liblapack3 libopenblas-base liblapack-dev libopenblas-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # clone github
    && git clone https://github.com/DReichLab/EIG.git \
    # install eigensoft
    && cd EIG/src/ \
    && make LDLIBS="-llapacke" \
    && make install \
    # move scripts to path
    && cd /app \
    && mv EIG/bin/* /usr/bin/
    

