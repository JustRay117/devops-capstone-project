#!/bin/bash
echo "****************************************"
echo " Setting up Capstone Environment"
echo "****************************************"

# Check if Python 3.9.15 is already installed
python3.9 --version 2>&1 | grep 'Python 3.9.15'
if [ $? -eq 0 ]; then
    echo "Python 3.9.15 is already installed, skipping installation."
else
    echo "Installing Python 3.9 and Virtual Environment from source"
    sudo apt-get update
    sudo apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
    wget https://www.python.org/ftp/python/3.9.15/Python-3.9.15.tgz
    tar -xf Python-3.9.15.tgz
    cd Python-3.9.15
    ./configure --enable-optimizations
    make -j 4
    sudo make altinstall
fi

echo "Checking the Python version..."
python3.9 --version

echo "Creating a Python virtual environment"
python3.9 -m venv ~/venv

# Check if the virtual environment was created successfully
if [ ! -d "~/venv" ]; then
    echo "Failed to create virtual environment. Exiting."
    # exit 1
fi

echo "Configuring the developer environment..."
echo "# DevOps Capstone Project additions" >> ~/.bashrc
echo "export GITHUB_ACCOUNT=$GITHUB_ACCOUNT" >> ~/.bashrc
echo 'export PS1="\[\e]0;\u:\W\a\]${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u\[\033[00m\]:\[\033[01;34m\]\W\[\033[00m\]\$ "' >> ~/.bashrc
echo "source ~/venv/bin/activate" >> ~/.bashrc

echo "Installing Python dependencies..."
source ~/venv/bin/activate && python3.9 -m pip install --upgrade pip wheel
source ~/venv/bin/activate && pip install -r ./requirements.txt

echo "Starting the Postgres Docker container..."
make db

echo "Checking the Postgres Docker container..."
docker ps

echo "****************************************"
echo " Capstone Environment Setup Complete"
echo "****************************************"
echo ""
echo "Use 'exit' to close this terminal and open a new one to initialize the environment"
echo ""