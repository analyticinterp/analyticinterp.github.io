---
title: "Want to understand the average size of hidden representations?"
toc_title: "...the average size of hidden representations?"
author: "[long list of authors]"
date: "2025-09-01"
description: "Exploring the mathematical properties of hidden layer representations and their average magnitudes."
sequence: "quickstart"
sequence_title: "A Quickstart Guide to Learning Mechanics"
sequence_description: "A comprehensive guide to understanding the mathematical foundations of deep learning, from optimization to generalization."
sequence_order: 2
---

You should! This is foundational for understanding everything else about the dynamics of neural networks.

Historically, the first questions people tried to answer about neural networks dealt with their performance and representations: how can we characterize how well our network performs, and what hidden representations do they learn as they train? We’ll revisit these questions later in a modern light, but suffice it to say that they are hard and it’s unclear where to start. In rigorous science, it’s usually a good idea to be humble about what you can understand and to start with the dumbest, simplest question you think you can answer, working up from there. It turns out that the simplest useful theoretical question you can ask about neural networks is: *as you forward-propagate your signal and backprop your gradient, roughly how big are the (pre)activations and gradients on average?*

More precisely: suppose we have an input vector $\mathbf{x}$ (an image, token, set of features, etc.), and we start propagating forward through our network, stopping part way. Denote by $\mathbf{h}_\ell(\mathbf{x})$ the hidden representations after applying the $\ell$-th linear layer. What’s the typical size of an element of $\mathbf{h}_\ell(\mathbf{x})$? If you want a mathematical metric for this, you might study the root-mean-squared size

$$
q_\ell(\mathbf{x}) := \frac{|\!|{\mathbf{h}_\ell(\mathbf{x})}|\!|}{\sqrt{\text{size}[\mathbf{h}_\ell(\mathbf{x})]}}.
$$

You don't want $q_\ell(\mathbf{x})$ to either blow up or vanish as you propagate forwards through the network. If either happens, you'll be feeding very large or very small arguments to your activation function^[…or feeding very large or small values to a norm layer, or representing them in finite precision and losing bits, or some other malady.], which is generally a bad idea. In a neural network of many layers, problems like this tend to get worse as you propagate through more and more layers, so you want to avoid them from the get go.

### First steps: LeCun initialization and large width

The first people to address this question seriously were practitioners in the 1990s. If you initialize a neural network’s weight parameters with unit variance — that is, $W_{ij} \sim \mathcal{N}(0,1)$ — then your preactivations tend to blow up. If instead you initialize with

$$
W_{ij} \sim \mathcal{N}(0, \sigma^2),
$$

where $\sigma^2 = \frac{1}{\text{[fan in]}}$. By a central limit theorem calculation, this ensures that well-behaved activations in the previous layer mean well-behaved preactivations in the following layer, at least at initialization.

- This scheme is now called LeCun initialization after [[LeCun et al. (1996)]](https://link.springer.com/chapter/10.1007/978-3-642-35289-8_3).

This is the first calculation any new deep learning scientist should be able to perform! Get comfortable with this kind of central limit theorem argument.

The central limit theorem works best as the number of added terms grows. This suggests that, when studying any sort of signal propagation problem, it’s a good and useful idea to consider the case of large width. **This is the consideration that motivates the study of infinite-width networks, which are now central in the mathematical science of deep learning.** It’s very important to think about this enough to have intuition for why the large-width limit is useful.

### Infinite-width nets at init: signal propagation and the NNGP

A natural next question is: *what else can you say about wide neural networks at initialization?* The answer unfolds in the following sequence.

First, you can perform a close study of the “signal sizes” $q_\ell(\mathbf{x})$ as well as the correlations $c_\ell(\mathbf{x}, \mathbf{x}') := \langle \mathbf{h}_\ell(\mathbf{x}), \mathbf{h}_\ell(\mathbf{x}') \rangle$. You can actually calculate both of these exactly at infinite width using Gaussian integrals.

- See [[Poole et al. (2016)]](https://arxiv.org/abs/1606.05340) for a derivation physicists will like and [[Daniely et al. (2016)]](https://arxiv.org/abs/1602.05897) for a more formal treatment mathematicians will like.
    - It’s worth getting to the point where you understand either Eqns (1-5) from [[Poole et al. (2016)]](https://arxiv.org/abs/1606.05340)  or Sections 5 and 8 from [Daniely et al (2016)]. The other stuff — chaos, computational graphs, and so on — is cool but not essential.
- See [[Schoenholz et al. (2016)]](https://arxiv.org/abs/1611.01232) for a similar size analysis for the backpropagated gradients.

Next, you can study not only the *averages* of these quantities but also their complete *distributions*. It turns out they’re Gaussian at initialization (surprise, surprise) and the network function value itself is a “Gaussian process” with a covariance kernel that you can obtain in closed form.

- This was first worked out for shallow networks by [[Neal (1996)]](https://glizen.com/radfordneal/ftp/pin.pdf). It took another two decades before it was extended to deep networks by [[Lee et al. (2017)]](https://arxiv.org/abs/1711.00165).

It’s very worth working through the neural network Gaussian process (NNGP) idea and getting intuition for both GPs and the forward-prop statistics that give a GP in this context. Notice that MLPs have NNGPs with rotation-invariant kernels.

At this point in our discussion, we already have papers that have calculated average-case quantities exactly which agree well with experiments using networks with widths in the hundreds or thousands. Look at how good the agreement is in these plots:

<div class="full-width-figure">
<img src="../static/great_dl_th-exp_plots.png" alt="Theory-experiment agreement plots">
<div class="figure-caption">Left: signal propagation of layerwise correlations from <a href="https://arxiv.org/abs/1606.05340">Poole et al. (2016)</a>. Right: performance vs. ordered/chaotic regimes from <a href="https://arxiv.org/abs/1711.00165">Lee et al. (2017)</a>. Now <em>that's</em> a theory-experiment match.</div>
</div>

It’s worth appreciating that extremely good agreement with experiment is possible if we’re studying the right objects in the right regimes. Most deep learning theory work that can’t get agreement this good eventually fades or is replaced by something that does. It’s usually wise to insist on a quantitative match from your theory and be satisfied with nothing less.

### Infinite-width nets under gradient descent: the NTK

Now that we understand initialization in wide networks, we’re ready to study training. The first milestone on this path is the “neural tangent kernel” (NTK). The main result here is that if you *train* a neural network in the NNGP infinite-width setting, its functional evolution is described by a particular kernel which remains static for all time. This kernel is the inner product of parameter gradient vectors:

$$
\text{NTK}(\mathbf{x}, \mathbf{x}') := \left\langle \nabla_{\boldsymbol{\theta}} f_{\boldsymbol{\theta}}(\mathbf{x}), \nabla_{\boldsymbol{\theta}} f_{\boldsymbol{\theta}}(\mathbf{x}') \right\rangle.
$$

The primary consequence is that, in this limit, the learning dynamics of a neural networks is, by the “kernel trick,” equivalent to the dynamics of a linear model. The final learned function is given by *kernel (ridge) regression.*

- The original NTK paper is that of [[Jacot et al. (2018)]](https://arxiv.org/abs/1806.07572). The subsequent presentation of [[Lee et al. (2019)]](https://arxiv.org/abs/1902.06720) is less formal and may be easier for beginners.
    - The NTK idea is a bit too technical to explain here (though we sure want to), but it’s all but essential to understand it before moving on to feature learning. It’s worth allocating some time, working through one of these papers, and making sure you’ve extracted the simple core idea. It’s also worth thinking carefully about linear models and kernel regression, as these will return later as first models for other learning phenomena.
    - Notice that one can make accurate *quantitative* predictions for the learning of wide nets using the NTK. See, for example, Figure 2 of [[Lee et al. (2019)]](https://arxiv.org/abs/1902.06720).

### The dynamics of feature learning: the maximal update parameterization ($\mu$P)

After the development of the NTK, people quickly noticed that networks in this limit don’t exhibit feature learning. That is, at infinite width, the hidden neurons of a network represent the same functions after training as they did at initialization. At large-but-finite width, the change is finite but negligible. This is a first clue that the wonderful, analytically tractable NTK limit isn’t the end of the story.

For a few years, it seemed like we might have to give up on infinite-width networks. Fortunately, it turned out that there’s *another* coherent infinite-width limit in which things scale differently, and the network *does* actually undergo feature learning. This is the limit in which most deep learning theory now takes place.

Here’s the evolution of ideas, some key papers, and key takeaways:

- [[Chizat and Bach (2018)]](https://arxiv.org/abs/1812.07956) gave a “lazy” vs. “rich” dichotomy of gradient descent dynamics, using “lazy” to mean “kernel dynamics” and “rich” to mean “anything else.”
    - It’s worth understanding what “lazy” training is, and how an output multiplier can make any neural network train lazily.
- [[Mei et al (2018)]](https://arxiv.org/abs/1804.06561) pointed out a “mean-field” parameterization that allows infinite-width shallow neural nets to learn features.
    - This may be an easier place to start than $\mu$P, but if you understand $\mu$P, you can skip mean-field nets for now.
- [[Yang and Hu (2021)]](https://proceedings.mlr.press/v139/yang21c.html) pointed out a way that layerwise init sizes + learning rates can scale with network width so that the network learns features to leading order *even at infinite width.* They call this the “maximal update parameterization” (muP, or $\mu$P).
    - The core idea here is extremely important and can be understood in simple terms. Their “Tensor Programs” and “abc-param” frameworks are fairly complicated — you don’t need to understand either to get the main gist. [[Yang et al. (2023)]](https://arxiv.org/abs/2310.17813) gives a simpler framing of the big idea here.
- [[Yang et al. (2022)]](https://arxiv.org/abs/2203.03466) showed that this parameterization is practically useful: it lets one scale up neural networks while preserving network hyperparameters. (More on this in [our discussion of hyperparameters](LINK).)
    - This is widely hailed as the first practically impactful achievement of deep learning theory.

These “rich,” feature learning, $\mu$P dynamics led to a paradigm shift in deep learning theory. Most later work uses or relates to it in some way. It’s thus very important to understand. Any deep learning theorist should be able to sit down and derive the $\mu$P parameterization, or something equivalent to it, from first principles. It’s difficult to do relevant work in 2025 without it!

It’s worth noting that, unlike the NTK limit, the $\mu$P limit is very difficult to study analytically. In the NTK limit, we have kernel behavior, simple gradient descent dynamics, a convex loss surface (using squared loss), and lots of older theoretical tools that we can bring to bear. In the $\mu$P limit, we have none of this. To our knowledge, nobody’s even shown a general result that a deep network in the $\mu$P limit *converges,* let alone characterized the solution that’s found!

<div class="question-box">

**Open question:** when does a network in the $\mu$P limit converge under gradient descent?

</div>

In the NTK limit, we can study the model with the well-established math of kernel theory (which has been developed further expressly for the study of the NTK). In the $\mu$P limit, the best we have so far are rather complex calculational frameworks:

- The dynamical mean-field theory (DMFT) frameworks of [[Bordelon and Pehlevan (2022)]](https://arxiv.org/abs/2205.09653) and [[Dandi et al. (2024)]](https://arxiv.org/abs/2402.03220) let one compute feature distributions of infinite-width networks in the rich regime, but it is quite complicated, and it is difficult to extract analytical insight. (It is nonetheless useful for scaling calculations.) The Tensor Programs framework of [[Yang and Hu (2021)]](https://proceedings.mlr.press/v139/yang21c.html) allows one to perform the same calculations with random matrix theory language.
    - These are specialized tools and are not essential on a first pass through deep learning theory.

<div class="question-box">

**Open question:** is there a simple calculational framework — potentially making realistic simplifying assumptions — that allows us to quantitatively study feature evolution in the rich regime?

</div>

### Onwards: towards infinite depth

Early in this chapter, we took width to infinity, which allowed us a host of useful calculational tools. We can also take depth to infinity. There are several ways to do this, but the upshot is that one quickly encounters stability problems, so a ResNet formulation in which each layer gets a small premultiplier seems like the most promising choice.

- [[Bordelon et al. (2023)]](https://arxiv.org/abs/2309.16620) and [[Yang et al. (2023)]](https://arxiv.org/abs/2310.02244) give treatments of $\mu$P at large depth. They conclude with slightly different scaling recommendations for layerwise premultipliers.
    - This is probably useful to understand for the future but is not yet essential knowledge. As with $\mu$P, the most important thing to get out of either paper is the scaling calculation that gives the hyperparameter prescription.

<div class="question-box">

**Open question:** is there a simple calculational framework for studying the feature evolution of an infinite-depth network?

</div>