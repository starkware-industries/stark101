from collections import Counter
from functools import reduce
from math import sqrt
from random import randint

from channel import Channel


def test_reproducability():
    c = Channel()
    c.send("Yes")
    r = c.receive_random_int(0, 2 ** 20)
    d = Channel()
    d.send("Yes")
    assert r == d.receive_random_int(0, 2 ** 20)


def test_uniformity():
    range_size = 10
    c = Channel()
    c.send(str(randint(0, 2 ** 20)))
    num_tries = 2 ** 10
    dist = Counter(c.receive_random_int(0, range_size - 1) for i in range(num_tries))
    dist_rand = Counter(randint(0, range_size - 1) for i in range(num_tries))
    mean = num_tries / range_size
    normalized_stdv_channel = sqrt(sum((y-mean)**2 for y in dist.values())) / range_size
    normalized_stdv_random = sqrt(sum((y-mean)**2 for y in dist_rand.values())) / range_size
    assert abs(normalized_stdv_channel - normalized_stdv_random) < 4
