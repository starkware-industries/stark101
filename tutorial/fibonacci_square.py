

from field import FieldElement
from polynomial import Polynomial, interpolate_poly, X, prod
from hashlib import sha256
from channel import serialize
from merkle import MerkleTree
from channel import Channel

def build_trace_eval():
  a = [FieldElement(1), FieldElement(3141592)]
  for _ in range(1021):
      v = a[-2]**2 + a[-1]**2
      a.append(v)
  assert a[-1] == FieldElement(2338775057)
  assert len(a) == 1023
  print("success generate trace")
  return a


# build x_coordinates
def build_trace_domain(n):
  assert n % 2 == 0  # n must be even
  g = FieldElement.generator() ** ((FieldElement.k_modulus - 1) // n)
  assert g.is_order(n)

  print(f'Generator of the field {n} is: {g}')
  # Fill G with the elements of G such that G[i] := g ** i
  G = [g ** i for i in range(n)]

  assert G[0] == FieldElement(1)
  assert G[1] == g
  for i in range(n//2):
    assert g * G[i] * G[-i-1] == FieldElement(1)

  print("success build x_coordinates")
  return G

def build_polynomial(xs, ys):
  f = interpolate_poly(xs, ys)
  v = f(2)
  assert v == FieldElement(1302089273)
  print("success build polynomial")
  return f


# build the larger evaluation domain x_coordinates
def build_lde_domain(n):
  assert n % 2 == 0  # n must be even
  H = build_trace_domain(n)
  lde_domain = [H[i] * FieldElement.generator() for i in range(n)]

  assert len(set(lde_domain)) == len(lde_domain)
  w = FieldElement.generator()
  w_inv = w.inverse()
  assert '55fe9505f35b6d77660537f6541d441ec1bd919d03901210384c6aa1da2682ce' == sha256(
    str(H[1]).encode()).hexdigest(), \
    'H list is incorrect. H[1] should be h (i.e., the generator of H).'
  for i in range(n):
    assert ((w_inv * lde_domain[1]) ** i) * w == lde_domain[i]
  print('Success build evaluation x_coordinates in the larger domain!')
  return lde_domain

def build_lde_eval(f, lde_domain):
  lde_eval = [f(x) for x in lde_domain]

  assert '1d357f674c27194715d1440f6a166e30855550cb8cb8efeb72827f6a1bf9b5bb' == sha256(
    serialize(lde_eval).encode()).hexdigest()
  print('success evaluation!')
  return lde_eval

def commit(data):
    tree = MerkleTree(data)
    return tree

def constraint_0(f):
    #constraint 1: f(x) = 1
    assert f.eval(1) == 1
    numerator = f -1
    denomator = X -1
    p0 = numerator / denomator
    r0 = numerator % denomator

    assert r0 == 0
    assert p0.eval(2718) == 2509888982
    assert p0.degree() == 1021
    print('Success build p0!')
    return p0

def constraint_1(f, x):
  assert f.eval(x) == 2338775057
  numerator = f - 2338775057
  denomator = X - x
  p1 = numerator / denomator
  r1 = numerator % denomator
  # q = (f - 2338775057) / (X - x)
  # r = (f - 2338775057) % (X - x)

  assert r1 == 0
  assert p1.eval(5772) == 232961446
  assert p1.degree() == 1021
  print('Success build p1!')
  return p1

def constraint_2(f,G):
  g = G[1]
  # lst = [(X - e) for e in range(G)]
  # prod(lst)
  numerator = f.compose(g ** 2 * X) - f.compose(g * X) ** 2 - f ** 2
  denomator = (X**1024-1)/((X-g**1021)*(X-g**1022)*(X-g**1023))
  p2 = numerator / denomator
  r2 = numerator % denomator

  assert r2 ==0
  assert numerator(g ** 1020) == 0
  assert numerator.eval(g ** 1021) != 0

  assert p2.degree() == 1023, f'The degree of the third constraint is {p2.degree()} when it should be 1023.'
  assert p2.eval(31415) == 2090051528
  assert p2.degree() == 1023
  print('Success build p2!')
  return p2

# alpha0 = 0, alpha1 = 787618507, alpha2 = -1067186547
# alpha0 = 787618507, alpha1 = -1067186547, alpha2 = -839323826
def build_compostion_polynomial(p0, p1, p2, channel):
  alpha0 = channel.receive_random_field_element()
  alpha1 = channel.receive_random_field_element()
  alpha2 = channel.receive_random_field_element()

  print(f'alpha0 = {alpha0}, alpha1 = {alpha1}, alpha2 = {alpha2}')
  cp = p0 * alpha0 + p1 * alpha1 + p2 * alpha2

  assert cp.degree() == 1023, f'The degree of cp is {cp.degree()} when it should be 1023.'
  print(f'cp(2439804) = {cp(2439804)}')
  assert cp.eval(2439804) == 1136940269, f'cp(2439804) = {cp(2439804)}, when it should be -197666696'
  print('success build composition polynomial!')
  return cp

def next_fri_domain(domain):
  return [x**2 for x in domain[:len(domain)//2]]


if __name__ == "__main__":
    trace_eval = build_trace_eval()            #[y0,y1,y2,...,y1022]
    trace_domain = build_trace_domain(1024)    #[g^0,g^1,g^2,...,g^1023]

    f =build_polynomial(trace_domain[:-1], trace_eval)
    lde_domain = build_lde_domain(1024*8)
    lde_eval = build_lde_eval(f, lde_domain)
    tree = commit(lde_eval)
    assert tree.root == '6c266a104eeaceae93c14ad799ce595ec8c2764359d7ad1b4b7c57a4da52be04'
    print('success commit lde evaluation!')

    channel = Channel()
    channel.send(tree.root)

    p0 = constraint_0(f)
    p1 = constraint_1(f, trace_domain[-2])
    p2 = constraint_2(f,trace_domain)
    cp =build_compostion_polynomial(p0, p1, p2, Channel())
    cp_eval_ys = [cp(x) for x in lde_domain]

    cp_tree = commit(cp_eval_ys)
    print(cp_tree.root)
    assert cp_tree.root == '96d8b67edd866c276d7bff9ab9e46d4465c47e2383c70ff34e5cecdfea4722c6'
    print('success commit!')



