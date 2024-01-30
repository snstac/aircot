AirCOT is installed as a dependency for various other programs (see above) but can be installed and updated
independently.

## Debian, Ubuntu, Raspberry Pi

```sh linenums="1"
sudo apt update
wget https://github.com/snstac/aircot/releases/latest/download/python3-aircot_latest_all.deb
sudo apt install -f ./python3-aircot_latest_all.deb
```

## Windows, Linux

```sh
python3 -m pip install aircot
```

## Developers

```sh linenums="1"
git clone https://github.com/snstac/aircot.git
cd aircot/
python3 setup.py install
```