from channel import Channel
from field import FieldElement
from merkle import MerkleTree
from polynomial import interpolate_poly, Polynomial


def part1():
    t = [FieldElement(1), FieldElement(3141592)]
    while len(t) < 1023:
        t.append(t[-2] * t[-2] + t[-1] * t[-1])
    g = FieldElement.generator() ** (3 * 2 ** 20)
    points = [g ** i for i in range(1024)]
    h_gen = FieldElement.generator() ** ((2 ** 30 * 3) // 8192)
    h = [h_gen ** i for i in range(8192)]
    domain = [FieldElement.generator() * x for x in h]
    p = interpolate_poly(points[:-1], t)
    ev = [p.eval(d) for d in domain]
    mt = MerkleTree(ev)
    ch = Channel()
    ch.send(mt.root)
    return t, g, points, h_gen, h, domain, p, ev, mt, ch


def part2():
    t, g, points, h_gen, h, domain, p, ev, mt, ch = part1()
    numer0 = p - Polynomial([FieldElement(1)])
    denom0 = Polynomial.gen_linear_term(FieldElement(1))
    q0, r0 = numer0.qdiv(denom0)
    numer1 = p - Polynomial([FieldElement(2338775057)])
    denom1 = Polynomial.gen_linear_term(points[1022])
    q1, r1 = numer1.qdiv(denom1)
    inner_poly0 = Polynomial([FieldElement(0), points[2]])
    final0 = p.compose(inner_poly0)
    inner_poly1 = Polynomial([FieldElement(0), points[1]])
    composition = p.compose(inner_poly1)
    final1 = composition * composition
    final2 = p * p
    numer2 = final0 - final1 - final2
    coef = [FieldElement(1)] + [FieldElement(0)] * 1023 + [FieldElement(-1)]
    numerator_of_denom2 = Polynomial(coef)
    factor0 = Polynomial.gen_linear_term(points[1021])
    factor1 = Polynomial.gen_linear_term(points[1022])
    factor2 = Polynomial.gen_linear_term(points[1023])
    denom_of_denom2 = factor0 * factor1 * factor2
    denom2, r_denom2 = numerator_of_denom2.qdiv(denom_of_denom2)
    q2, r2 = numer2.qdiv(denom2)
    cp0 = q0.scalar_mul(ch.receive_random_field_element())
    cp1 = q1.scalar_mul(ch.receive_random_field_element())
    cp2 = q2.scalar_mul(ch.receive_random_field_element())
    cp = cp0 + cp1 + cp2
    cp_ev = [cp.eval(d) for d in domain]
    cp_mt = MerkleTree(cp_ev)
    ch.send(mt.root)
    return cp, cp_ev, cp_mt, ch, domain

# from part 3


def next_fri_domain(domain):
    return [x ** 2 for x in domain[:len(domain) // 2]]


def next_fri_polynomial(poly, alpha):
    odd_coefficients = poly.poly[1::2]
    even_coefficients = poly.poly[::2]
    odd = Polynomial(odd_coefficients).scalar_mul(alpha)
    even = Polynomial(even_coefficients)
    return odd + even


def next_fri_layer(poly, dom, alpha):
    next_poly = next_fri_polynomial(poly, alpha)
    next_dom = next_fri_domain(dom)
    next_layer = [next_poly.eval(x) for x in next_dom]
    return next_poly, next_dom, next_layer


def part3():
    cp, cp_ev, cp_mt, ch, domain = part2()
    # FriCommit function
    fri_polys = [cp]
    fri_doms = [domain]
    fri_layers = [cp_ev]
    merkles = [cp_mt]
    while fri_polys[-1].degree() > 0:
        alpha = ch.receive_random_field_element()
        next_poly, next_dom, next_layer = next_fri_layer(fri_polys[-1], fri_doms[-1], alpha)
        fri_polys.append(next_poly)
        fri_doms.append(next_dom)
        fri_layers.append(next_layer)
        merkles.append(MerkleTree(next_layer))
        ch.send(merkles[-1].root)
    ch.send(str(fri_polys[-1].poly[0]))
    return fri_polys, fri_doms, fri_layers, merkles, ch
