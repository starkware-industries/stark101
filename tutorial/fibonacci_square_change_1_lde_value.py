

from field import FieldElement
from fibonacci_square import *


def stark101_change_1_lde_value():
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
  fri_polys, fri_domains, fri_layers, fri_merkles = fri_commit(cp, lde_domain, cp_eval,
                                                                    cp_tree, channel)
  print('success commit all proofs!')

  # fake 1 lde value
  fake_lde_value = lde_value
  fake_lde_value[1024] = fake_lde_value[1024] + FieldElement(1)

  proof_0 = decommit_on_query(trace_domain, lde_domain, fake_lde_value, lde_tree, fri_layers,
                              fri_merkles, 0, channel)
  valid = proof_0.verify(proof_0.final_values[0])
  assert valid == True

  nb_pass = 0
  nb_fail = 0
  for i in range(8192-16):
   proof = decommit_on_query(trace_domain, lde_domain, fake_lde_value, lde_tree, fri_layers,
                              fri_merkles, i, channel)
   valid = proof.verify(proof_0.final_values[0])
   if valid == True:
    nb_pass += 1
   else:
    nb_fail += 1
    print(f'failed on index {i}')
  print(f'nb_pass: {nb_pass}, nb_fail: {nb_fail}')


'''
修改一个[0,8191-16)之间的1个lde_value，会造成3次失败的query，[8191-16:8192)之间的1个lde_value，会造成1次失败的query。
success commit all proofs!
failed on index 1008
failed on index 1016
failed on index 1024
nb_pass: 8173, nb_fail: 3

'''
if __name__ == "__main__":
  stark101_change_1_lde_value()

