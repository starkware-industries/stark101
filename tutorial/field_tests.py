###############################################################################
# Copyright 2019 StarkWare Industries Ltd.                                    #
#                                                                             #
# Licensed under the Apache License, Version 2.0 (the "License").             #
# You may not use this file except in compliance with the License.            #
# You may obtain a copy of the License at                                     #
#                                                                             #
# https://www.starkware.co/open-source-license/                               #
#                                                                             #
# Unless required by applicable law or agreed to in writing,                  #
# software distributed under the License is distributed on an "AS IS" BASIS,  #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
# See the License for the specific language governing permissions             #
# and limitations under the License.                                          #
###############################################################################


from field import FieldElement


def test_field_operations():
    # Check pow, mul, and the modular operations
    t = FieldElement(2) ** 30 * FieldElement(3) + FieldElement(1)
    assert t == FieldElement(0)
    # Check generator
    # Check inverse
    # Check hash via usage of set
def test_field_add():
    res = FieldElement.zero()

    for i in range(100):
        res = res + FieldElement(i)

    assert res == FieldElement(4950)

def test_field_neg():
    v = FieldElement(100)
    negV = -v
    print(f"v:{v}, negV:{negV}")
    assert 0 == v + negV

def test_field_div():
    for _ in range(100):
        t = FieldElement.random_element(exclude_elements=[FieldElement.zero()])
        t_inv = FieldElement.one() / t
        assert t_inv == t.inverse()
        assert t_inv * t == FieldElement.one()


if __name__ == "__main__":
    #test_field_add()
    test_field_operations()
    test_field_neg()
    # test_field_div()
