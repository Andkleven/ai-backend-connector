## Link Gstreamer packages to virtual environment in Linux
If you are using virtual environment in Linux, link the gi Python package from system's Python to the virtual environment's Python 
[Gist](https://gist.github.com/jegger/10003813)
```
cd venv/lib/python3.6/site-packages
ln -s /usr/lib/python3/dist-packages/gi
cd ../../../..
```

## Install Python packages
`pip install --upgrade pip`
`pip install --upgrade setuptools`
`pip install -r requirements.txt`
**Note for Windows:** Download Shapely-package which has it's geos-dependency built in from link below. Choose the one which matches your system from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely). Install with `pip install Shapely‑1.7.0‑cp36‑cp36m‑win_amd64.whl` or what ever is your system's package name. After installing Shapely wheel comment out `shapely` from requirements.txt and run `pip install -r requirements.txt`.