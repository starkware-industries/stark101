

from field import FieldElement
from fibonacci_square import *


def fri_commit_fake(cp, lde_domain, cp_eval, cp_merkle, channel, n):
  fri_polys = [cp]
  fri_domains = [lde_domain]
  fri_layers = [cp_eval]
  fri_merkles = [cp_merkle]
  for _ in range(n):
    beta = channel.receive_random_field_element()
    next_poly, next_domain, next_eval = next_fri_layer(fri_polys[-1], fri_domains[-1], beta)
    fri_polys.append(next_poly)
    fri_domains.append(next_domain)
    fri_layers.append(next_eval)
    fri_merkles.append(commit(next_eval))
    channel.send(fri_merkles[-1].root)  # record each layer's merkle root
  channel.send(str(fri_polys[-1].poly[0]))
  return fri_polys, fri_domains, fri_layers, fri_merkles

  '''
  在 stark101_claimed_degree_less_than_512()中, 将一个实际degree为1022的多项式f(x), 宣称为degree(f)=511 <512的多项式,
  对于degree< 512 需要折叠 ceil(log2(degree(f)))  = 9 次, 将最后一层变成常数，
  prover 折叠9次，提供proof。
  verifier 验证proof，检查最后一层是否 为常数，如果是，说明f(x)的degree<512。
  fake_fri_commit() 用于生成模拟生成9层 cp layer。

  '''
def stark101_claimed_degree_less_than_512():
  trace_value = build_trace_eval()  # [y0,y1,y2,...,y1022]
  trace_domain = build_trace_domain()  # [g^0,g^1,g^2,...,g^1023]

  f = build_polynomial(trace_domain[:-1], trace_value)  #1023
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
  fri_polys, fri_domains, fri_layers, fri_merkles = fri_commit_fake(cp, lde_domain, cp_eval,
                                                                    cp_tree, channel, 9)
  print('success commit all proofs!')

  proof_1 = decommit_on_query(trace_domain, lde_domain, lde_value, lde_tree, fri_layers,
                              fri_merkles, 1, channel)
  valid = proof_1.verify(proof_1.final_values[0], lde_tree, fri_merkles)
  assert valid == False
  print(f'final values:', proof_1.final_values)


if __name__ == "__main__":
  stark101_claimed_degree_less_than_512()

