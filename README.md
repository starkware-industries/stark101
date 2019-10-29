# Stark 101

## About
A tutorial for a basic STARK (Scalable Transparent Argument of Knowledge) protocol to prove the calculation of a Fibonacci-Square sequence, as designed for [StarkWare Sessions](https://starkware.co/starkware-sessions/), and authored by the [StarkWare](https://starkware.co) team.
Note that it was written assuming that the user has reviewed and understood the presentations at the beginning of each part.

## Run Online
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/starkware-industries/stark101/master?urlpath=lab%2Ftree%2Ftutorial%2FNotebookTutorial.ipynb)

## Run Locally
1. Install [Jupyter lab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html) 
2. `cd tutorial`
3. `jupyter lab NotebookTutorial.ipynb`

## Math Background
During the tutorial you’ll generate a STARK proof for the 1023th element of the FibonacciSq sequence over a finite field. In this section, we explain what this last sentence means.
### Finite Fields
In the tutorial we will work with a finite field of prime size. This means we take a prime number p, and then work with integers in the domain {0, 1, 2, …, p – 1}. The idea is that we can treat this set of integers in the same way we treat real numbers: we can add them (but we need to take the result modulo p, so that it will fall back in the set), subtract them, multiply them and divide them. You can even define polynomials such as f(x)=a+bx<sup>2</sup> where the coefficients a,b and the input x are all numbers in this finite set. Since the addition and multiplication are done modulo p, the output f(x) will also be in the finite set. One interesting thing to note about finite fields, which is different from real numbers, is that there is always an element, g, called the generator (in fact there is more than one), for which the sequence 1, g, g<sup>2</sup>, g<sup>3</sup>, g<sup>4</sup>, …, g<sup>p-2</sup> (whose length is p-1) covers all the numbers in the set but 0 (modulo p, of course). Such a geometric sequence is called a cyclic group. We will supply you with python classes that implement these things so you don’t have to be familiar with how these are implemented (though the algorithm for division in a finite field is not that trivial).
### FibonacciSq
For the tutorial we define a sequence that resembles the well known Fibonacci sequence. In this sequence any element is the sum of squares of the two previous elements. Thus the first elements are:

1, 1, 2, 5, 29, 866, …

All the elements of the sequence will be from the finite field (which means that both squaring and addition is computed modulo p).

### STARK Proof
We will create a proof for the claim “The 1023th element of the FibonacciSq sequence is …”. By “proof” we don’t mean a mathematical proof with logical deductions. Instead, we mean some data which can convince whomever reads it that the claim is correct. To make it more formal we define two entities: Prover and Verifier. The Prover generates this data (the proof). The Verifier gets this data and checks for its validity. The requirement is that if the claim is false, the Prover will not be able to generate a valid proof (even if it deviates from the protocol).
STARK is a specific protocol which describes the structure of such proof and defines what the Prover and Verifier have to do.

### Some Other Things You Should Know
We recommend you take a look at our math blog posts ([Arithmetization I](https://medium.com/starkware/arithmetization-i-15c046390862), [Arithmetization II](https://medium.com/starkware/arithmetization-ii-403c3b3f4355)). You don’t need to read them thoroughly before running through the tutorial, but it can give you better context on what things you can create proofs for, and what a STARK proof looks like. You should definitely give them a read after you have completed this tutorial in full.

### Division of Polynomials
For every two polynomials f(x) and g(x), there exist two polynomials q(x) and r(x) called the quotient and remainder of the division f(x) by g(x). They satisfy f(x) = g(x) * q(x) + r(x) and the degree of r(x) is smaller than the degree of g(x). For example, if f(x)=x<sup>3</sup>+x+1 and g(x)=x<sup>2</sup>+1 then q(x)=x and r(x)=1. Indeed, x<sup>3</sup>+x+1 = (x<sup>2</sup>+1)*x + 1.
### Roots of Polynomials
When a polynomial satisfies f(a) = 0 for some specific value a (we say that a is a root of f), we don’t have remainder (r(x)=0) when dividing it by (x-a) so we can write f(x) = (x-a)*q(x), and deg(q)=deg(f)-1. A similar fact is true for k roots. Namely, if a<sub>i</sub> is a root of f for all i=1, 2, …, k, then there exists a polynomial q of degree deg(f)-k for which f(x) = (x-a<sub>1</sub>)(x-a<sub>2</sub>) … (x-a<sub>k</sub>)*q(x).
