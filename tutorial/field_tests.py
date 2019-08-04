from field import FieldElement


def test_field_operations():
    # Check pow, mul, and the modular operations
    t = FieldElement(2).pow(30) * FieldElement(3) + FieldElement(1)
    assert t == FieldElement(0)
    # Check generator
    # Check inverse
    # Check hash via usage of set


def test_field_div():
    for _ in range(100):
        t = FieldElement.random_element(exclude_elements=[FieldElement.zero()])
        t_inv = FieldElement.one() / t
        assert t_inv == t.inverse()
        assert t_inv * t == FieldElement.one()
