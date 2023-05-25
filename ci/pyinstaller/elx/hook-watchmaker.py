# -*- coding: utf-8 -*-
"""Pyinstaller hook for watchmaker standalone."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
    copy_metadata,
)

datas = [
    ("src/watchmaker/static", "watchmaker/static"),
    (
        "src/watchmaker/_vendor/pypa/get-pip/public/2.7",
        "watchmaker/_vendor/pypa/get-pip/public/2.7",
    ),
    ('/usr/lib64/.libcrypto.so.*.hmac', '.'),
    ('/usr/lib64/.libssl.so.*.hmac', '.'),
]

binaries = [
    ('/usr/lib64/libcrypto.so.*', '.'),
    ('/usr/lib64/libssl.so.*', '.'),
]

hiddenimports = [
    "boto3",
]

datas += copy_metadata("watchmaker", recursive=True)
datas += collect_data_files("watchmaker")
binaries += collect_dynamic_libs("watchmaker")
hiddenimports += collect_submodules("watchmaker")
