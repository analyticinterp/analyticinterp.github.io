---
title: "On the Universality of Transformer Representations"
author: "No one"
date: "2025-01-15"
description: "We prove that transformer networks with sufficient width and depth can approximate any continuous sequence-to-sequence function, extending classical universality results to the attention mechanism."
---

The universal approximation theorem for feedforward networks tells us that sufficiently wide networks can approximate any continuous function. But what about transformers? In this post, we extend these classical results to architectures with attention.

## The Classical Result

The universal approximation theorem (Cybenko, 1989; Hornik, 1991) states that feedforward networks with a single hidden layer can approximate any continuous function on a compact set to arbitrary accuracy:

**Theorem 1** (Universal Approximation). Let $\sigma: \mathbb{R} \to \mathbb{R}$ be a non-polynomial activation function. Then the set of functions

$$\mathcal{F} = \left\{ x \mapsto \sum_{i=1}^{N} \alpha_i \sigma(w_i^T x + b_i) : N \in \mathbb{N}, \alpha_i, b_i \in \mathbb{R}, w_i \in \mathbb{R}^d \right\}$$

is dense in $C(K)$ for any compact $K \subset \mathbb{R}^d$.

## Extending to Transformers

For transformers, we need to consider sequence-to-sequence mappings. Let $\mathcal{X} = \mathbb{R}^{n \times d}$ be the space of input sequences of length $n$ with $d$-dimensional embeddings.

**Theorem 2** (Transformer Universality). Any continuous function $f: \mathcal{X} \to \mathcal{X}$ can be approximated to arbitrary precision by a transformer with sufficient width and depth.

*Proof sketch*: The key insight is that attention can implement arbitrary pairwise interactions between sequence elements, while the feedforward layers provide universal approximation within each position.

## Implications

This theoretical result has several important implications:

1. **Expressivity**: Transformers are at least as expressive as any other continuous sequence model
2. **Depth vs Width**: Unlike feedforward networks, transformers benefit from both depth and width
3. **Attention is Sufficient**: The attention mechanism alone can implement complex computational patterns

## Open Questions

Several questions remain:
- What is the sample complexity of learning these universal approximators?
- Can we characterize which functions are "easy" vs "hard" for transformers?
- How does the inductive bias of attention affect learning dynamics?

In future work, we plan to explore these questions through both theoretical analysis and empirical investigation. 