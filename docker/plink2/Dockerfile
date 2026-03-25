FROM continuumio/miniconda3

WORKDIR /app

RUN apt-get update \
    # install packages needed for PLINK, NEAT plots and biofilter installation
    && apt-get install -y --no-install-recommends libz-dev g++ gcc git wget tar unzip make \
    && rm -rf /var/lib/apt/lists/* \
    # install PLINK
    && wget https://s3.amazonaws.com/plink2-assets/alpha6/plink2_linux_x86_64_20250707.zip \
    && unzip plink2_linux_x86_64_20250707.zip \
    && rm -rf plink2_linux_x86_64_20250707.zip \
    # move plink2 executable to $PATH
    && mv plink2 /usr/bin \
    # install python packages needed for pipeline
    && conda install -y -n base -c conda-forge scikit-learn dominate wget libtiff conda-build scipy pandas seaborn matplotlib numpy apsw sqlite \
    && conda clean --all --yes \
    # install NEAT plots
    && git clone https://github.com/PMBB-Informatics-and-Genomics/NEAT-Plots.git \
    && mv NEAT-Plots/manhattan-plot/ /app/ \
    && conda develop /app/manhattan-plot/ \
    # remove NEAT-plots directory
    && rm -R NEAT-Plots

USER root
