#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update encrypted deploy password in Travis config file."""


from __future__ import print_function

import base64
import json
from getpass import getpass

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.serialization import load_pem_public_key

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen


GITHUB_REPO = 'plus3it/watchmaker'


def load_key(pubkey):
    """
    Load public RSA key, ensuring correct header/footer format.

    Read more about RSA encryption with cryptography:
    https://cryptography.io/latest/hazmat/primitives/asymmetric/rsa/
    """
    try:
        return load_pem_public_key(pubkey.encode(), default_backend())
    except ValueError:
        # workaround for https://github.com/travis-ci/travis-api/issues/196
        pubkey = pubkey.replace('BEGIN RSA', 'BEGIN').replace('END RSA', 'END')
        return load_pem_public_key(pubkey.encode(), default_backend())


def encrypt(pubkey, password):
    """
    Encrypt password using given RSA public key and encode it with base64.

    The encrypted password can only be decrypted by someone with the
    private key (in this case, only Travis).
    """
    key = load_key(pubkey)
    encrypted_password = key.encrypt(password, PKCS1v15())
    return base64.b64encode(encrypted_password)


def fetch_public_key(repo):
    """Download RSA public key Travis will use for this repo.

    Travis API docs: http://docs.travis-ci.com/api/#repository-keys
    """
    keyurl = 'https://api.travis-ci.org/repos/{0}/key'.format(repo)
    data = json.loads(urlopen(keyurl).read().decode())
    if 'key' not in data:
        errmsg = "Could not find public key for repo: {}.\n".format(repo)
        errmsg += "Have you already added your GitHub repo to Travis?"
        raise ValueError(errmsg)
    return data['key']


def main(args):
    """Get a secure string for travis deployment."""
    public_key = fetch_public_key(args.repo)
    password = args.password or getpass('PyPI password: ')
    encrypted = encrypt(public_key, password.encode())
    print("{0}".format(dict(secure=encrypted)))  # noqa: T003
    print(  # noqa: T003
        "\nUpdate the secure string in .travis.yml and you'll be ready to "
        "deploy!"
    )


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default=GITHUB_REPO,
                        help='GitHub repo (default: %s)' % GITHUB_REPO)
    parser.add_argument('--password',
                        help='PyPI password (will prompt if not provided)')

    args = parser.parse_args()
    main(args)
