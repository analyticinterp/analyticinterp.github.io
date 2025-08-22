---
title: "Introduction: what do you want to understand?"
author: "[long list of authors]"
date: "2025-09-01"
sequence: "quickstart"
sequence_order: 1
---

The mathematical science of deep learning has had many successes over the past decade in the quest to bring principle to practical neural networks. It has also had many failures. There is now so much literature that it is difficult for newcomers to know where to start. This needn’t be the case: our successes are notable but few, experts are converging on useful ideas and methodologies, and we should summarize in plain language the things that have definitively worked so we can better build on them. This post is a summary of what we see as the “essentials of deep learning theory” as of 2025: the parts of the story so far that seem to us inevitable, indispensable, and part of the final picture we expect to one day find.

***For newcomers:*** welcome to the science of learning mechanics! It is our belief that neural networks have a great deal of mathematical principle behind them, we just haven’t found most of it yet. The field is currently conducting a scientific search for these principles, and if you want to contribute, we can use your help. Our hope is that this post can serve as a quickstart guide to the field, summarizing the ideas we’re quite confident will stick around, so you can get up to speed and become conversant. We’ll focus on important *ideas* more than important *papers,* and we’ll tell you what you should get out of reading the papers we do share. We will not go into much technical detail here, as our intent is just to give you a useful map of the essential territory. We’ll highlight open questions — the big stuff we’re really curious about, not just problems that are technically open — as we go. Please feel free to adopt them as your own, and tell us what you find.

Throughout, we’ll assume familiarity with basic math and basic deep learning, but if you find something unduly confusing (especially if you want to fix it yourself), let us know.

***For experts in deep learning theory:*** in any scientific enterprise, it’s useful every once in a while to stop, look backwards, and assess our progress. Fields tend to sprawl as they advance, and so it is periodically valuable to reflect and notice that the important results are rather simpler than the path by which we got there. (You will recognize many such cases in this guide.) It's useful to look backwards and simplify, to smooth over the path, to find the simple stories we will one day canonize in textbooks. This helps us grizzled veterans as much as newcomers, for we’re all on the same team here, and when we agree on our history and goals, we can better work together.

It’s the job of all experienced scientists to help teach and train the generations below us. It’s easy to forget with experience how hard it is to learn. We’d like you to share this with your younger students and collaborators. It is meant for them. If you see ways to make this a better resource, we’d like to hear them.

Science is an edifice of ideas, each supporting those above it. While each idea is contributed by one or more people, and these contributors deserve credit, here we focus on the ideas. Nonetheless, if you feel we have made any attribution errors, do inform us. Furthermore, while this list is intended to be minimal, not comprehensive, if we have missed anything essential, please tell us.

## Asking a specific question

Deep learning is complicated. Training a neural network involves choosing an architecture, choosing a dataset, selecting numerous hyperparameters, and running a long iterated training procedure until, eventually, the loss goes down and learning has occurred. There will be no simple theory encompassing all of these variables — there are simply too many. For the time being, it’s important to be clear we’re asking questions simple and specific enough to be answered. As we make progress, we can hope to widen each pocket of understanding, eventually linking them together into a unified picture! As of 2025, though, our progress lies primarily in a few disjoint islands that are yet to be linked.

A good way to go about research in this or any field is to narrow in on a specific enough question that it might actually be answered. "Understanding deep learning" in the abstract (or "solving" it, etc.) is largely a mirage. By the same token, a good way to organize this field's findings so far is in terms of the part of the deep learning process they help you understand. We’ll structure our summary of the highlights in this way, clustering results according to the type of question they help you answer. This clustering is neither definitive nor static: these topic questions weren’t the obvious choices five years ago, and they’ll probably be different a few years down the line! Nonetheless, the best learning is propelled by genuine curiosity, and organizing ideas around questions lets the reader quickly find and sink their teeth into the material that seems most enticing.

Without further ado, here’s this guide's table of contents, structured as a list of topic questions. We follow this rough ordering: the higher the topic on the list, the more we know about it, and the more important those findings are when studying later topics.


