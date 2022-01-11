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
