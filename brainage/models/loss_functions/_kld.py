"""Kullback-Leibler divergence loss."""

# %% External package import

import torch.nn as nn

# %% Function definition


def KLDivLoss(x, y):
    """
    Return K-L Divergence loss.

    Different from the default PyTorch nn.KLDivLoss in that
    a) the result is averaged by the 0th dimension (Batch size)
    b) the y distribution is added with a small value (1e-16) to prevent \
    log(0) problem
    """
    loss_func = nn.KLDivLoss(reduction='sum')
    y += 1e-16
    n = y.shape[0]
    loss = loss_func(x, y) / n

    return loss
