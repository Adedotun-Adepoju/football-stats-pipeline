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

    echo -e "Removing anaconda installation script..."
    rm ./Anaconda3-2022.10-Linux-x86_64.sh

    # activate conda 
    eval "$(/home/$USER/bin/anaconda3/bin/conda shell.bash hook)"

    echo -e "Running conda init..."
    conda init 
    #use -y flag to auto-approve
    echo -e "running conda update"
    confa update -y conda 

    cd 
else 
    echo -e "anaconda a;ready installed."
fi 

echo -e "\nRunning sudo apt-get update...\n"
sudo apt-get update 

echo -e "\nInstalling Docker...\n"
sudo apt=get -y install docker.io 

echo -e "\nInstalling docker-compose...\n"
cd 
cd bin 

wget https://github.com/docker/compose/releases/download/v2.12.0/docker-compose-linux-x86_64 -O docker-compose
sudo chmod +x docker-compose 

echo -e "\nInstalling Terraform...\n"
wget https://releases.hashicorp.com/terraform/1.3.3/terraform_1.3.3_linux_amd64.zip
sudo apt-get install unzip
unzip terraform_1.3.3_linux_amd64.zip
rm terraform_1.3.3_linux_amd64.zip

echo -e "\nSetup .bashrc...\n"

echo -e ''>> ~/.bashrc
echo -e 'export PATH=${HOME}/bin:${PATH}' >> ~/.bashrc
echo -e ''>> ~/.bashrc
echo -e 'export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.google/credentials/google_credentials.json"' >> ~/.bashrc

terraform -version
sudo docker --version
docker-compose version 
echo "anaconda-navigator version $(anaconda-navigator --version)"
anaconda --version
conda --version

echo -e "\nSetting up Docker without sudo setup...\n"
sudo groupadd docker 
sudo usermod -aG docker $USER
newgrp docker