

from field import FieldElement
from polynomial import Polynomial, interpolate_poly, X, prod
from hashlib import sha256
from channel import serialize
from merkle import MerkleTree, verify_decommitment
from channel import Channel
from proof import Proof, DecommitmentData, next_fri_domain
from random import randint

def build_trace_eval():
  a = [FieldElement(1), FieldElement(3141592)]
  for _ in range(1021):
      v = a[-2]**2 + a[-1]**2
      a.append(v)
  assert a[-1] == FieldElement(2338775057)
  assert len(a) == 1023
  print("success generate trace")
  return a


# build trace domain
def build_domain(n):
  assert n % 2 == 0  # n must be even
  g = FieldElement.generator() ** ((FieldElement.k_modulus - 1) // n)
  assert g.is_order(n)

  # Fill G with the elements of G such that G[i] := g ** i
  G = [g ** i for i in range(n)]

  assert G[0] == FieldElement(1)
  assert G[1] == g
  for i in range(n//2):
    assert g * G[i] * G[-i-1] == FieldElement(1)

  print("success build trace domain")
  return G


def build_trace_domain():
  n = 1024
  G = build_domain(n)
  return G


def build_polynomial(xs, ys):
  f = interpolate_poly(xs, ys)
  v = f(2)
  assert v == FieldElement(1302089273)
  print("success build polynomial")
  return f


# build the larger evaluation domain x_coordinates
def build_lde_domain():
  n = 8192
  H = build_domain(n)
  lde_domain = [H[i] * FieldElement.generator() for i in range(n)]

  assert len(set(lde_domain)) == len(lde_domain)
  w = FieldElement.generator()
  w_inv = w.inverse()
  assert '55fe9505f35b6d77660537f6541d441ec1bd919d03901210384c6aa1da2682ce' == sha256(
    str(H[1]).encode()).hexdigest(), \
    'H list is incorrect. H[1] should be h (i.e., the generator of H).'
  for i in range(n):
    assert ((w_inv * lde_domain[1]) ** i) * w == lde_domain[i]
  print('success build lde domain!')
  return lde_domain

def build_lde_value(f, lde_domain):
  lde_value = [f.eval(x) for x in lde_domain]

  assert '1d357f674c27194715d1440f6a166e30855550cb8cb8efeb72827f6a1bf9b5bb' == sha256(
    serialize(lde_value).encode()).hexdigest()
  print('success build lde evaluation!')
  return lde_value

def commit(data):
    tree = MerkleTree(data)
    return tree

def constraint_0(f):
    #constraint 1: f(x) = 1
    assert f.eval(1) == 1
    numerator = f - 1
    denominator = X - 1
    p0 = numerator / 	denominator
    r0 = numerator % 	denominator

    assert r0 == 0
    assert p0.eval(2718) == 2509888982
    assert p0.degree() == 1021
    print('Success build p0!')
    return p0

def constraint_1(f, x):
  assert f.eval(x) == 2338775057
  numerator = f - 2338775057
  denominator = X - x
  p1 = numerator / 	denominator
  r1 = numerator % 	denominator

  assert r1 == 0
  assert p1.eval(5772) == 232961446
  assert p1.degree() == 1021
  print('Success build p1!')
  return p1

def constraint_2(f,G):
  g = G[1]
  numerator = f.compose(g ** 2 * X) - f.compose(g * X) ** 2 - f ** 2
  denominator = (X**1024-1)/((X-g**1021)*(X-g**1022)*(X-g**1023))
  p2 = numerator / denominator
  r2 = numerator % denominator

  assert r2 ==0
  assert numerator(g ** 1020) == 0
  assert numerator.eval(g ** 1021) != 0

  assert p2.degree() == 1023, f'The degree of the third constraint is {p2.degree()} when it should be 1023.'
  assert p2.eval(31415) == 2090051528
  assert p2.degree() == 1023
  print('Success build p2!')
  return p2



def build_compostion_polynomial(p0, p1, p2, alpha0, alpha1, alpha2):
  cp = p0 * alpha0 + p1 * alpha1 + p2 * alpha2
  return cp



def next_fri_polynomial(poly, beta):
  odd_coeffs = poly.poly[1::2]
  even_coeffs = poly.poly[::2]
  odd = beta * Polynomial(odd_coeffs)
  even = Polynomial(even_coeffs)
  return odd + even

def next_fri_layer(poly, domain, beta):
  next_domain = next_fri_domain(domain)
  next_poly = next_fri_polynomial(poly, beta)
  next_eval = [next_poly(x) for x in next_domain]
  return next_poly, next_domain, next_eval

def fri_commit(cp, lde_domain, cp_eval, cp_merkle, channel):
  fri_polys = [cp]
  fri_domains = [lde_domain]
  fri_layers = [cp_eval]
  fri_merkles = [cp_merkle]
  i = 0
  while fri_polys[-1].degree() > 0:
    beta = channel.receive_random_field_element()
    next_poly, next_domain, next_eval = next_fri_layer(fri_polys[-1], fri_domains[-1], beta)
    fri_polys.append(next_poly)
    fri_domains.append(next_domain)
    fri_layers.append(next_eval)
    fri_merkles.append(commit(next_eval))
    channel.send(fri_merkles[-1].root)  # record each layer's merkle root
    i += 1

  channel.send(str(fri_polys[-1].poly[0]))
  print(f'fold {i} times:')
  return fri_polys, fri_domains, fri_layers, fri_merkles

'''

  Importtant
  1. in stark101, sibling is only for check cpi(x), cpi(-x), cp{i+1}(x^2) relationships calculation, not for merkle tree building as shown in https://zk-learning.org/assets/lecture8.pdf page38, where sibling is also for merkle tree building, but they are different implementations, both are correct.
  2. channel.send should be used carefully, since it will change channel's state, so comparing to its original implemenation, channel.send() is deleted here.
 '''
def decommit_on_fri_layers(fri_layers, fri_merkles, idx, channel):
  cp_proof = []
  for layer, merkle in zip(fri_layers[:-1], fri_merkles[:-1]):
    length = len(layer)
    idx = idx % length
    sib_idx = (idx + length // 2) % length
    proof = DecommitmentData(idx, layer[idx], merkle.get_authentication_path(idx), merkle.root)
    cp_proof.append(proof)

    proof = DecommitmentData(sib_idx, layer[sib_idx], merkle.get_authentication_path(sib_idx), merkle.root)
    cp_proof.append(proof)

  return cp_proof, fri_layers[-1]


def decommit_on_query(trace_domain, lde_domain,lde_value, tree, fri_layers, fri_merkles, idx, channel):
  assert idx + 16 < len(lde_value), f'query index: {idx} is out of range. Length of layer: {len(lde_value)}.'

  x_proof = DecommitmentData(idx, lde_value[idx], tree.get_authentication_path(idx), tree.root)

  next_idx = idx + 8
  gx_proof = DecommitmentData(next_idx, lde_value[next_idx], tree.get_authentication_path(next_idx), tree.root)

  next_next_idx = idx + 16
  g2x_proof = DecommitmentData(next_next_idx, lde_value[next_next_idx], tree.get_authentication_path(next_next_idx), tree.root)

  cp_proof, final_values = decommit_on_fri_layers(fri_layers, fri_merkles, idx, channel)
  proof = Proof(x_proof, gx_proof, g2x_proof, cp_proof, final_values, trace_domain, lde_domain)
  return proof


def test_next_fri_layer():
  test_poly = Polynomial([FieldElement(2), FieldElement(3), FieldElement(0), FieldElement(1)])
  test_domain = [FieldElement(3), FieldElement(5)]
  beta = FieldElement(7)
  next_p, next_d, next_l = next_fri_layer(test_poly, test_domain, beta)
  assert next_p.poly == [FieldElement(23), FieldElement(7)]
  assert next_d == [FieldElement(9)]
  assert next_l == [FieldElement(86)]
  print('success verify next_fri_layer!')

def stark101_test():
  trace_value = build_trace_eval()  # [y0,y1,y2,...,y1022]
  trace_domain = build_trace_domain()  # [g^0,g^1,g^2,...,g^1023]

  f = build_polynomial(trace_domain[:-1], trace_value)
  lde_domain = build_lde_domain()
  lde_value = build_lde_value(f, lde_domain)
  lde_tree = commit(lde_value)
  assert lde_tree.root == '6c266a104eeaceae93c14ad799ce595ec8c2764359d7ad1b4b7c57a4da52be04'
  print('success commit lde evaluation!')

  channel = Channel()
  channel.send(lde_tree.root)

  p0 = constraint_0(f)
  p1 = constraint_1(f, trace_domain[-2])
  p2 = constraint_2(f, trace_domain)

  alphas = channel.derive_alphas(3)
  cp = build_compostion_polynomial(p0, p1, p2, alphas[0], alphas[1], alphas[2])
  cp_eval = [cp(x) for x in lde_domain]

  cp_tree = commit(cp_eval)
  assert cp_tree.root == 'd7e5200e990727c6da6bf711aeb496244b8b48436bd6f29066e1ddb64e22605b'
  print('success commit cp evaluation!')

  channel.send(cp_tree.root)
  fri_polys, fri_domains, fri_layers, fri_merkles = fri_commit(cp, lde_domain, cp_eval, cp_tree,
                                                               channel)
  print('success commit all proofs!')

  proof_1 = decommit_on_query(trace_domain, lde_domain, lde_value, lde_tree, fri_layers,
                              fri_merkles, 1, channel)
  proof_100 = decommit_on_query(trace_domain, lde_domain, lde_value, lde_tree, fri_layers,
                                fri_merkles, 100, channel)

  valid = proof_1.verify(proof_1.final_values[0])
  assert valid == True
  valid = proof_100.verify(proof_1.final_values[0])
  assert valid == True

  for i in range(10):
    idx = randint(0, 8192 - 16)
    proof = decommit_on_query(trace_domain, lde_domain, lde_value, lde_tree, fri_layers,
                              fri_merkles, idx, channel)
    valid = proof.verify(proof_1.final_values[0])
    assert valid == True

  print(f'final values:', proof_1.final_values)
  print('success verify proofs')

if __name__ == "__main__":
  stark101_test()


