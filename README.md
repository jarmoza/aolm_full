# The Art of Literary Modeling
**Python Package and Repository**

Code, data, and media for AOLM dissertation

## Environment Setup

### Installing Anaconda (OS-specific Instructions)

If you do not yet have Anaconda ('conda') installed on your system, run the following
commands in your terminal

**Windows**
- curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe
- start "" /wait Miniforge3-Windows-x86_64.exe /InstallationType=JustMe /AddToPath=1 /S
- conda --version
    
**macOS, Apple silicon**
- curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
- bash Miniforge3-MacOSX-arm64.sh -b
- source ~/miniforge3/bin/activate
- conda --version

**macOS, Intel**
- curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh
- bash Miniforge3-MacOSX-x86_64.sh -b
- source ~/miniforge3/bin/activate
- conda --version

**Linux**
- curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
- bash Miniforge3-Linux-x86_64.sh -b
- source ~/miniforge3/bin/activate
- conda --version

### Install the 'conda' environment for 'Art of Literary Modeling' 

In the aolm_full root folder in your terminal, run *conda env create -f environment.yml*

### Activate the 'conda' environment

Next, run *conda activate aolm*. Repeat *only* this last command when you want to re-run
the tutorial script again after exiting your terminal (or after deactivating the 'conda' environment via *conda deactivate*).