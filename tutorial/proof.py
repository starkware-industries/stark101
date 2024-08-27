
from merkle import verify_decommitment
from field import FieldElement
from channel import Channel

class DecommitmentData:
  def __init__(self, index, value, authentication_path, merkle_root):
    self.index = index
    self.value = value
    self.authentication_path = authentication_path
    self.merkle_root = merkle_root

class Proof:
  x_proof: DecommitmentData
  gx_proof : DecommitmentData
  g2x_proof : DecommitmentData
  cp_proof : list[DecommitmentData]
  final_eval: FieldElement

  def __init__(self, x_proof: DecommitmentData, gx_proof: DecommitmentData, g2x_proof: DecommitmentData, cp_proof: list[DecommitmentData], final_eval: FieldElement):
    self.x_proof = x_proof
    self.gx_proof = gx_proof
    self.g2x_proof = g2x_proof
    self.cp_proof = cp_proof if cp_proof is not None else []
    self.final_eval = final_eval

  def add_to_cp(self, data: DecommitmentData):
    """Append a DecommitmentData object to the CP list."""
    self.CP.append(data)

  def verify(self, final_value: FieldElement):
    # check merkle proofs
    valid_x = verify_decommitment(self.x_proof.index, self.x_proof.value, self.x_proof.authentication_path, self.x_proof.merkle_root)
    valid_gx = verify_decommitment(self.gx_proof.index, self.gx_proof.value, self.gx_proof.authentication_path, self.gx_proof.merkle_root)
    valid_g2x = verify_decommitment(self.g2x_proof.index, self.g2x_proof.value, self.g2x_proof.authentication_path, self.g2x_proof.merkle_root)

    valid_cp = []
    for proof in self.cp_proof:
      v = verify_decommitment(proof.index, proof.value, proof.authentication_path, proof.merkle_root)
      valid_cp.append(v)

    merkle_valid = valid_x and valid_gx and valid_g2x and all(valid_cp)

    # check same LDE root and final evaluation
    same_lde_root = self.x_proof.merkle_root == self.gx_proof.merkle_root == self.g2x_proof.merkle_root
    same_final_eval = self.final_eval == final_value

    channel = Channel()
    channel.send(self.x_proof.merkle_root)
    alphas = channel.derive_alphas(3)
    print(f'alphas:',alphas)

    #FIXME check cp0(x), f(x), f(gx), f(g^2*x) relationships

    #FIXME cpi(x), cpi(-x), cp{i+1}(x^2) relationships


    #FIXME check sibling cp has same merkle root
    same_sibling_merle_root = []
    for i in range(len(self.cp_proof)//2):
      v =  self.cp_proof[i*2].merkle_root == self.cp_proof[i*2+1].merkle_root
      same_sibling_merle_root.append(v)

    valid = merkle_valid & same_lde_root & same_final_eval &all(same_sibling_merle_root)
    return valid

