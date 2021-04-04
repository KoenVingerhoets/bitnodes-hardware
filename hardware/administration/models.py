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
import re
from hashlib import sha256

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save

from .tasks import register_node_task

B58CHARS = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def b58decode(value, length):
    b58base = len(B58CHARS)
    long_value = 0
    for (i, c) in enumerate(value[::-1]):
        long_value += B58CHARS.find(c) * (b58base**i)
    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    result = chr(long_value) + result
    nPad = 0
    for c in value:
        if c == B58CHARS[0]:
            nPad += 1
        else:
            break
    result = chr(0) * nPad + result
    if length is not None and len(result) != length:
        return None
    return result


def get_bitcoin_address_version(address):
    addr = b58decode(address, 25)
    if addr is None:
        return None
    version = addr[0]
    checksum = addr[-4:]
    vh160 = addr[:-4]
    h3 = sha256(sha256(vh160).digest()).digest()
    if h3[0:4] == checksum:
        return ord(version)
    return None


def validate_bitcoin_address(value):
    """
    Validates Bitcoin address. Testnet addresses are not allowed.
    """
    message = '{} is not a valid Bitcoin address.'.format(value)
    if len(value) == 0:
        return
    if re.match(r'^[%s]{26,35}$' % B58CHARS, value) is None:
        raise ValidationError(message)
    version = get_bitcoin_address_version(value)
    # version == 0 (public key hash)
    # version == 5 (pay to script hash/P2SH)
    if version not in (0, 5):
        raise ValidationError(message)


class BitcoinAddress(models.Model):
    """
    Only 1 instance of this model is allowed per site.
    """
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    bitcoin_address = models.CharField(max_length=35, unique=True, blank=True,
                                       validators=[validate_bitcoin_address])

    def __str__(self):
        return self.bitcoin_address


def register_node(sender, instance, **kwargs):
    register_node_task.delay(instance.bitcoin_address)
post_save.connect(register_node, sender=BitcoinAddress)


class Bandwidth(models.Model):
    """
    Only 1 instance of this model is allowed per site.
    """
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    max_uplink = models.PositiveIntegerField(default=0)
