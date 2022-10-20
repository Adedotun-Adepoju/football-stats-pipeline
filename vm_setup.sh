#!/bin/bash

# Run using ./setup.sh

if ! [ -d ./bin ];
then 
    echo -e '\nCreating ~/bin directory\n'
    mkdir -p bin
fi 

if ! [ -d ./bin/anaconda3 ];
then 
    cd bin 
    echo -e '\nInstalling anaconda3...\n'
    echo -e "Download anaconda3..."
    wget https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh -O ./Anaconda3-2022.10-Linux-x86_64.sh
    echo -e "Running anaconda3 script..."
    # -b run install in batch mode (without manual intervention), it is expected the license terms are agreed upon
    # -p install prefix, defaults to $PREFIX, must not contain spaces.
    bash ./Anaconda3-2022.10-Linux-x86_64.sh -b -p ~/bin/anaconda3