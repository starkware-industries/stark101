# Tips 

## Stark Verifer 
a stark verifer is created, which is defined on proof.py

DecommitmentData defines decommit record.

```python
class DecommitmentData:
  def __init__(self, index, value, authentication_path, merkle_root):
    self.index = index
    self.value = value
    self.authentication_path = authentication_path
    self.merkle_root = merkle_root
```


Proof collects x, g*x, g^2 * x, cp layers proof, trace_domain, lde_domain. *verify()* will check
- all merkle proofs
- check same LDE root and final values
- check cp0(x), f(x), f(g*x), f(g^2*x) relationship
- check cpi(x), cpi(-x), cp{i+1}(x^2) relationships
- check sibling cps have same merkle root, lde_domain[idx]^2 == lde_domain[sibling_idx]^2

```python
class Proof:
  x_proof: DecommitmentData
  gx_proof : DecommitmentData
  g2x_proof : DecommitmentData
  cp_proof : list[DecommitmentData]
  final_values: list[FieldElement]
  trace_domain: list[FieldElement]
  lde_domain: list[FieldElement]
```


run the following commands to check
```
python3 fibonacci_square.py 
python3 fibonacci_square_claimed_degree_less_than_512.py
```




## Issue in original [stark101](https://github.com/starkware-industries/stark101)
1. in Stark101-part2.ipynb, an uninitalized channel is used, whjch result alpha0=0 in *get_CP()* function, 
   ```python
   def get_CP(channel):
    alpha0 = channel.receive_random_field_element()
    alpha1 = channel.receive_random_field_element()
    alpha2 = channel.receive_random_field_element()
    return alpha0*p0 + alpha1*p1 + alpha2*p2
   ```
   ```
   
    test_channel = Channel()  #uninitalized channel 
    CP_test = get_CP(test_channel)
    assert CP_test.degree() == 1023, f'The degree of cp is {CP_test.degree()} when it should be 1023.'
    assert CP_test(2439804) == 838767343, f'cp(2439804) = {CP_test(2439804)}, when it should be 838767343'
    print('Success!')
   ```
   beside that, in turorial_seesions.py channel is initialied corrrect 
    ```
    def part1():
        ... ... 
        ch = Channel()
        ch.send(mt.root) #channel initialied corrrect 
        return t, g, points, h_gen, h, domain, p, ev, mt, ch
    ```

2. p2's denominator in Stark101-part2.ipynb is different from that in turorial_seesions.py
   ```
    denom2 = (X**1024 - 1) / ((X - g**1021) * (X - g**1022) * (X - g**1023)) # x^1024 -1 
   ```
  
   in turorial_seesions.py

    ```
    def part2():
        ... ... 
        coef = [FieldElement(1)] + [FieldElement(0)] * 1023 + [FieldElement(-1)] # 1-x^1024
        ... ... 
        return cp, cp_ev, cp_mt, ch, domain
    ```
 The above issuses cause part3's test fail(https://github.com/starkware-industries/stark101/issues/8), in this repo the second issue is fixed.



# STARK 101

## About

A tutorial for a basic STARK (**S**calable **T**ransparent **AR**gument of **K**nowledge) protocol
to prove the calculation of a Fibonacci-Square sequence, as designed for StarkWare
Sessions, and authored by the
[StarkWare](https://starkware.co) team.

Note that it was written assuming that the user has reviewed and understood the presentations at the
beginning of each part.

### Video Lessons

This tutorial has a series of videos
[available here](https://starkware.co/stark-101/)
to review. Slides and links (to this repositories' content) are also included.

## Run Online

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/starkware-industries/stark101/master?urlpath=lab%2Ftree%2Ftutorial%2FNotebookTutorial.ipynb)

## Run Locally

1. Install [Jupyter lab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html)
2. `cd tutorial`
3. `jupyter lab NotebookTutorial.ipynb`

## Math Background

During the tutorial you’ll generate a STARK proof for the 1023<sup>rd</sup> element of the
FibonacciSq sequence over a finite field. In this section, we explain what this last sentence means.

### Finite Fields

In the tutorial we will work with a finite field of prime size. This means we take a prime number
_p_, and then work with integers in the domain {0, 1, 2, …, _p_ – 1}. The idea is that we can treat
this set of integers in the same way we treat real numbers: we can add them (but we need to take the
result modulo _p_, so that it will fall back in the set), subtract them, multiply them and divide
them. You can even define polynomials such as _f_ ( _x_ ) = _a_+ _bx_<sup>2</sup> where the
coefficients _a_,_b_ and the input _x_ are all numbers in this finite set. Since the addition and
multiplication are done modulo _p_, the output _f _ ( _x_ ) will also be in the finite set. One
interesting thing to note about finite fields, which is different from real numbers, is that there
is always an element, _g_, called the generator (in fact there is more than one), for which the
sequence 1, _g_, _g_<sup>2</sup>, _g_<sup>3</sup>, _g_<sup>4</sup>, ... , _g_<sup>p-2</sup> (whose
length is _p_ - 1 ) covers all the numbers in the set but 0 (modulo _p_, of course). Such a
geometric sequence is called a cyclic group. We will supply you with python classes that implement
these things so you don’t have to be familiar with how these are implemented (though the algorithm
for division in a finite field is not that trivial).

### FibonacciSq

For the tutorial we define a sequence that resembles the well known Fibonacci sequence. In this
sequence any element is the sum of squares of the two previous elements. Thus the first elements
are:

1, 1, 2, 5, 29, 866, ...

All the elements of the sequence will be from the finite field (which means that both squaring and
addition is computed modulo p).

### STARK Proof

We will create a proof for the claim “The 1023<sup>rd</sup> element of the FibonacciSq sequence is
…”. By “proof” we don’t mean a mathematical proof with logical deductions. Instead, we mean some
data which can convince whomever reads it that the claim is correct. To make it more formal we
define two entities: **Prover** and **Verifier**. The Prover generates this data (the proof). The
Verifier gets this data and checks for its validity. The requirement is that if the claim is false,
the Prover will not be able to generate a valid proof (even if it deviates from the protocol).

STARK is a specific protocol which describes the structure of such proof and defines what the Prover
and Verifier have to do.

### Some Other Things You Should Know

We recommend you take a look at our [STARK math blog
posts](https://medium.com/starkware/tagged/stark-math) (Arithmetization
[I](https://medium.com/starkware/arithmetization-i-15c046390862) &
[II](https://medium.com/starkware/arithmetization-ii-403c3b3f4355) specifically). You don’t need to
read them thoroughly before running through the tutorial, but it can give you better context on what
things you can create proofs for, and what a STARK proof looks like. You should definitely give them
a read after you have completed this tutorial in full.

### Division of Polynomials

For every two polynomials _f_ ( _x_ ) and _g_ ( _x_ ), there exist two polynomials _q_ ( _x_ ) and
_r_ ( _x_) called the quotient and remainder of the division _f_ ( _x_ ) by _g_ ( _x_ ). They
satisfy _f_ ( _x_ ) = _g_ ( _x_ ) \* _q_ ( _x_ ) + _r_ ( _x_ ) and the degree of _r_ ( _x_ ) is
smaller than the degree of _g_ ( _x_ ).

For example, if _f_ ( _x_ ) = _x_<sup>3</sup> + _x_ + 1 and _g_ ( _x_ ) = _x_<sup>2</sup> + 1 then
_q_ ( _x_ ) = _x_ and _r_ ( _x_ ) = 1. Indeed, _x_<sup>3</sup> + _x_ + 1 = ( _x_<sup>2</sup> + 1 )
\* _x_ + 1.

### Roots of Polynomials

When a polynomial satisfies _f_ (_a_) = 0 for some specific value a (we say that _a_ is a root of _f_
), we don’t have remainder (_r_ ( _x_ ) = 0) when dividing it by (_x_ - _a_) so we can write _f_ (
_x_ ) = (_x_ - _a_) \* _q_ ( _x_ ), and deg( _q_ ) = deg( _f_ ) - 1. A similar fact is true for _k_
roots. Namely, if _a_<sub>_i_</sub> is a root of _f_ for all _i_ = 1, 2, …, _k_, then there exists a
polynomial _q_ of degree deg(_f_) - _k_ for which _f_ ( _x_ ) = ( _x_ - _a_<sub>1</sub> )( _x_ -
_a_<sub>2</sub> ) … ( _x_ - _a_<sub>_k_</sub> ) \* _q_ ( _x_ ) .

### Want to Know More?

1. Nigel Smart’s [“Cryptography Made Simple”](https://www.cs.umd.edu/~waa/414-F11/IntroToCrypto.pdf)
   – Chapter 1.1: Modular Arithmetic.

2. Arora and Barak’s [“Computational Complexity: A Modern
   Approach”](http://theory.cs.princeton.edu/complexity/book.pdf) – Appendix: Mathematical
   Background, sections A.4 (Finite fields and Groups) and A.6 (Polynomials).
