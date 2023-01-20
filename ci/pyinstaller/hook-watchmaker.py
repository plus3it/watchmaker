from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [
    ("src/watchmaker/static", "watchmaker/static"),
    ("src/vendor/pypa/get-pip/public/2.7", "vendor/pypa/get-pip/public/2.7"),
]
binaries = []
hiddenimports = []
datas += copy_metadata("watchmaker", recursive=True)
tmp_ret = collect_all("watchmaker")
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]
