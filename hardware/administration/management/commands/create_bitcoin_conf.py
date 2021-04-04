#
# Copyright (c) Addy Yeow Chin Heng <ayeowch@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import loader
from django.utils.crypto import get_random_string


class Command(BaseCommand):
    help = "Creates bitcoin.conf in bitcoin directory."

    def handle(self, *args, **options):
        if not os.path.isfile(settings.BITCOIN_CONF):
            create_bitcoin_conf()


def create_bitcoin_conf():
    if not os.path.isdir(settings.BITCOIN_DIR):
        make_bitcoin_dirs()
    context = {
        'datadir': settings.BITCOIN_DIR,
        'port': str(settings.BITCOIN_PORT),
        'maxconnections': str(settings.BITCOIN_MAX_CONNECTIONS),
        'rpcbind': settings.RPC_HOST,
        'rpcallowip': settings.RPC_HOST,
        'rpcport': str(settings.RPC_PORT),
        'rpcuser': get_random_string(100, settings.SECRET_CHARS),
        'rpcpassword': get_random_string(100, settings.SECRET_CHARS),
        'prune': str(settings.BITCOIN_PRUNE),
    }
    conf = loader.render_to_string('bitcoin.conf.tmpl', context)
    with open(settings.BITCOIN_CONF, 'w') as f:
        f.write(conf)
    print('{} created'.format(settings.BITCOIN_CONF))
    try:
        os.chmod(settings.BITCOIN_CONF, 600)
    except OSError as err:
        pass


def make_bitcoin_dirs():
    os.makedirs(settings.BITCOIN_DIR)
    # Symlink ~/.bitcoin to the actual bitcoin directory as it is used by
    # default when running command such as `bitcoin-cli getinfo` without
    # additional arguments.
    default_bitcoin_dir = os.path.expanduser('~/.bitcoin')
    if not os.path.exists(default_bitcoin_dir):
        os.symlink(settings.BITCOIN_DIR, default_bitcoin_dir)
