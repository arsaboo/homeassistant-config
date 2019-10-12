#!/bin/bash

# Re-download this custom component

set -e

# get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# make sure we are in the right folder
if [[ "$DIR" != *"/custom_components/androidtv" ]]; then
  echo "This script is not in the 'custom_components/androidtv' directory. Exiting now."
  exit 1
fi

rm -f *.py
rm -f *.pyc
rm -f manifest.json
rm -f services.yaml
rm -rf androidtv
rm -rf __pycache__

# 1. Download component files
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/__init__.py -O "$DIR/__init__.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/manifest.json -O "$DIR/manifest.json"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/media_player.py -O "$DIR/media_player.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/services.yaml -O "$DIR/services.yaml"

# 2. Download `androidtv` package
mkdir -p "$DIR/androidtv"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/__init__.py -O "$DIR/androidtv/__init__.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_manager.py -O "$DIR/androidtv/adb_manager.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/androidtv.py -O "$DIR/androidtv/androidtv.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/basetv.py -O "$DIR/androidtv/basetv.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/constants.py -O "$DIR/androidtv/constants.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/firetv.py -O "$DIR/androidtv/firetv.py"

# 3. Download `adb-shell` package
mkdir -p "$DIR/androidtv/adb_shell/auth"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/__init__.py -O "$DIR/androidtv/adb_shell/__init__.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/adb_device.py -O "$DIR/androidtv/adb_shell/adb_device.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/adb_message.py -O "$DIR/androidtv/adb_shell/adb_message.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/constants.py -O "$DIR/androidtv/adb_shell/constants.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/exceptions.py -O "$DIR/androidtv/adb_shell/exceptions.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/tcp_handle.py -O "$DIR/androidtv/adb_shell/tcp_handle.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/auth/__init__.py -O "$DIR/androidtv/adb_shell/auth/__init__.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/auth/keygen.py -O "$DIR/androidtv/adb_shell/auth/keygen.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/auth/sign_cryptography.py -O "$DIR/androidtv/adb_shell/auth/sign_cryptography.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/auth/sign_pycryptodome.py -O "$DIR/androidtv/adb_shell/auth/sign_pycryptodome.py"
wget https://raw.githubusercontent.com/JeffLIrion/ha-androidtv/master/custom_components/androidtv/androidtv/adb_shell/auth/sign_pythonrsa.py -O "$DIR/androidtv/adb_shell/auth/sign_pythonrsa.py"
