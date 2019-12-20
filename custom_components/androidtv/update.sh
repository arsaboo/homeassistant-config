#!/bin/bash

# 1. Delete files
rm *.py
rm manifest.json
rm services.yaml
rm -rf androidtv

# 2. Download component files
wget https://raw.githubusercontent.com/home-assistant/home-assistant/dev/homeassistant/components/androidtv/__init__.py
wget https://raw.githubusercontent.com/home-assistant/home-assistant/dev/homeassistant/components/androidtv/manifest.json
wget https://raw.githubusercontent.com/home-assistant/home-assistant/dev/homeassistant/components/androidtv/media_player.py
wget https://raw.githubusercontent.com/home-assistant/home-assistant/dev/homeassistant/components/androidtv/services.yaml

# 3. Download `androidtv` package
mkdir -p androidtv
wget https://raw.githubusercontent.com/JeffLIrion/python-androidtv/master/androidtv/__init__.py -O androidtv/__init__.py
wget https://raw.githubusercontent.com/JeffLIrion/python-androidtv/master/androidtv/adb_manager.py -O androidtv/adb_manager.py
wget https://raw.githubusercontent.com/JeffLIrion/python-androidtv/master/androidtv/androidtv.py -O androidtv/androidtv.py
wget https://raw.githubusercontent.com/JeffLIrion/python-androidtv/master/androidtv/basetv.py -O androidtv/basetv.py
wget https://raw.githubusercontent.com/JeffLIrion/python-androidtv/master/androidtv/constants.py -O androidtv/constants.py
wget https://raw.githubusercontent.com/JeffLIrion/python-androidtv/master/androidtv/firetv.py -O androidtv/firetv.py

# 4. Download `adb-shell` package
mkdir -p androidtv/adb_shell/auth
mkdir -p androidtv/adb_shell/handle
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/__init__.py -O androidtv/adb_shell/__init__.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/adb_device.py -O androidtv/adb_shell/adb_device.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/adb_message.py -O androidtv/adb_shell/adb_message.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/constants.py -O androidtv/adb_shell/constants.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/exceptions.py -O androidtv/adb_shell/exceptions.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/handle/__init__.py -O androidtv/adb_shell/handle/__init__.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/handle/base_handle.py -O androidtv/adb_shell/handle/base_handle.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/handle/tcp_handle.py -O androidtv/adb_shell/handle/tcp_handle.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/auth/__init__.py -O androidtv/adb_shell/auth/__init__.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/auth/keygen.py -O androidtv/adb_shell/auth/keygen.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/auth/sign_cryptography.py -O androidtv/adb_shell/auth/sign_cryptography.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/auth/sign_pycryptodome.py -O androidtv/adb_shell/auth/sign_pycryptodome.py
wget https://raw.githubusercontent.com/JeffLIrion/adb_shell/master/adb_shell/auth/sign_pythonrsa.py -O androidtv/adb_shell/auth/sign_pythonrsa.py

# 5. Replace imports
sed -i "s|from androidtv|from .androidtv|g" media_player.py
sed -i "s|from adb_shell|from .androidtv.adb_shell|g" media_player.py
sed -i "s|from adb_shell|from .adb_shell|g" androidtv/adb_manager.py

# 6. Include pure-python-adb
rm -rf androidtv/ppadb
git clone https://github.com/Swind/pure-python-adb.git
mv pure-python-adb/ppadb androidtv/
rm -rf pure-python-adb
cd androidtv
grep -rl "from ppadb" . | xargs sed -i 's/from ppadb/from custom_components.androidtv.androidtv.ppadb/g'
sed -i "s|raise RuntimeError|pass  # raise RuntimeError|g" ppadb/utils/logger.py
