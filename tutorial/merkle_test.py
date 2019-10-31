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


from hashlib import sha256
from random import randint

from field import FieldElement
from merkle import MerkleTree, verify_decommitment


def test_merkle_get_authentication_path():
    for _ in range(10):
        data_length = randint(0, 2000)
        data = [FieldElement.random_element() for _ in range(data_length)]
        m = MerkleTree(data)
        leaf_id = randint(0, data_length - 1)
        decommitment = m.get_authentication_path(leaf_id)
        # Check a correct decommitment.
        content = data[leaf_id]
        assert verify_decommitment(leaf_id, content, decommitment, m.root)
        # Check that altering the decommitment causes verification to fail.
        altered = decommitment[:]
        random_index = randint(0, len(altered) - 1)
        altered[random_index] = sha256(altered[random_index].encode()).hexdigest()
        assert not verify_decommitment(leaf_id, content, altered, m.root)
        # Check that altering the content causes verification to fail.
        other_content = data[randint(0, data_length - 1)]
        assert not verify_decommitment(
            leaf_id, other_content, decommitment, m.root) or other_content == content
