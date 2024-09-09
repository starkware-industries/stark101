
from merkle import verify_decommitment
from field import FieldElement
from channel import Channel

def next_fri_domain(domain):
  return [x**2 for x in domain[:len(domain)//2]]

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
  final_values: list[FieldElement]
  trace_domain: list[FieldElement]
  lde_domain: list[FieldElement]

  def __init__(self, x_proof: DecommitmentData, gx_proof: DecommitmentData, g2x_proof: DecommitmentData, cp_proof: list[DecommitmentData], final_values: list[FieldElement], trace_domain: list[FieldElement], lde_domain: list[FieldElement]):
    self.x_proof = x_proof
    self.gx_proof = gx_proof
    self.g2x_proof = g2x_proof
    self.cp_proof = cp_proof if cp_proof is not None else []
    self.final_values = final_values
    self.trace_domain = trace_domain
    self.lde_domain = lde_domain


  def verify(self, final_value: FieldElement,lde_tree, fri_merkles):
    # check merkle proofs
    merkle_proof_valid = []
    merkle_proof_valid.append(verify_decommitment(self.x_proof.index, self.x_proof.value, self.x_proof.authentication_path, self.x_proof.merkle_root) & (self.x_proof.merkle_root == lde_tree.root))
    merkle_proof_valid.append(verify_decommitment(self.gx_proof.index, self.gx_proof.value, self.gx_proof.authentication_path, self.gx_proof.merkle_root) & (self.gx_proof.merkle_root == lde_tree.root))
    merkle_proof_valid.append(verify_decommitment(self.g2x_proof.index, self.g2x_proof.value, self.g2x_proof.authentication_path, self.g2x_proof.merkle_root) & (self.g2x_proof.merkle_root == lde_tree.root))
    for i in range(len(self.cp_proof) // 2):
      proof = self.cp_proof[i*2]
      merkle_proof_valid.append(verify_decommitment(proof.index, proof.value, proof.authentication_path, proof.merkle_root) & (proof.merkle_root == fri_merkles[i].root))
      proof = self.cp_proof[i*2+1]
      merkle_proof_valid.append(verify_decommitment(proof.index, proof.value, proof.authentication_path, proof.merkle_root) & (proof.merkle_root == fri_merkles[i].root))

    # check same LDE root and same cp root for each layer
    same_lde_root = self.x_proof.merkle_root == self.gx_proof.merkle_root == self.g2x_proof.merkle_root
    same_cp_root = []
    for i in range(len(self.cp_proof) // 2):
      same_cp_root.append(self.cp_proof[i*2].merkle_root == self.cp_proof[i*2+1].merkle_root)

    # same final values
    same_final_values = []
    for i in range (len(self.final_values)):
      same_final_values.append(final_value == self.final_values[i])

    channel = Channel()
    channel.send(self.x_proof.merkle_root)
    alphas = channel.derive_alphas(3)

    # check cp0(x), f(x), f(g*x), f(g^2*x) relationship
    x_val = self.lde_domain[self.x_proof.index]  # x = lde_domain[index]
    p0_val = (self.x_proof.value - 1)/(x_val - 1)   # p0 = (f(x) - 1)/(x-g^0)
    p1_val = (self.x_proof.value - 2338775057)/(x_val - self.trace_domain[1022]) # p1 = (f(x) - 2338775057 )/(x-g^1022)

    p2_denominator = (x_val**1024 - 1)/((x_val - self.trace_domain[1021])*(x_val - self.trace_domain[1022])*(x_val - self.trace_domain[1023]))
    p2_val = (self.g2x_proof.value - self.gx_proof.value**2 - self.x_proof.value**2)/p2_denominator  # p2 = (f(g^2*x) - f(gx)^2 - f(x)^2)/[(x^1024 - 1)/((x-g^1021)*(x-g^1022)*(x-g^1023))]

    calculated_cp_val = p0_val * alphas[0] + p1_val * alphas[1] + p2_val * alphas[2]
    trace_cp_valid = calculated_cp_val == self.cp_proof[0].value

    # check cpi(x), cpi(-x), cp{i+1}(x^2) relationship
    domain = self.lde_domain
    cp_layers_valid = []
    for i in range(len(self.cp_proof)//2):
      if i < len(self.cp_proof)//2-1:
        next_cp_value = self.cp_proof[(i+1)*2].value  #
      else:
        next_cp_value = self.final_values[0]

      channel.send(self.cp_proof[i*2].merkle_root)
      beta = channel.receive_random_field_element()
      idx = self.cp_proof[i*2].index
      x_val = domain[idx]
      g_x_square_val = (self.cp_proof[i*2].value + self.cp_proof[i*2+1].value)/2
      h_x_square_val = (self.cp_proof[i*2].value - self.cp_proof[i*2+1].value)/(2*x_val)
      calculated_next_cp_eval = g_x_square_val + beta * h_x_square_val
      cp_layers_valid.append(calculated_next_cp_eval == next_cp_value)

      # update domain and next_cp_value
      domain = next_fri_domain(domain)

    # check sibling cp has same merkle root and lde_domain[idx]^2 == lde_domain[sibling_idx]^2
    same_sibling_square = []
    domain = self.lde_domain

    for i in range(len(self.cp_proof)//2):
      idx = self.cp_proof[i*2].index
      sibling_idx = self.cp_proof[i*2+1].index
      same_sibling_square.append(domain[idx] ** 2 == domain[sibling_idx] ** 2)

      domain = next_fri_domain(domain)

    valid = (all(merkle_proof_valid) & same_lde_root & all(same_cp_root) & all(same_final_values) &
             trace_cp_valid & all(cp_layers_valid) & all(same_sibling_square))
    return valid

