"""Additional functions for class support."""

# %% External package import

from numpy import arange, array, floor, isscalar, ndim, random, zeros
from random import seed
from scipy.stats import norm
from torch import manual_seed as torch_manual_seed
from torch.cuda import manual_seed as cuda_manual_seed
from torch.cuda import manual_seed_all
from torch.backends import cudnn

# %% Function definitions


def crop_center(data, out_sp):
    """
    Return the center part of volume data.

    crop: in_sp > out_sp
    Example:
    data.shape = np.random.rand(182, 218, 182)
    out_sp = (160, 192, 160)
    data_out = crop_center(data, out_sp)
    """
    in_sp = data.shape
    nd = ndim(data)
    x_crop = int((in_sp[-1] - out_sp[-1]) / 2)
    y_crop = int((in_sp[-2] - out_sp[-2]) / 2)
    z_crop = int((in_sp[-3] - out_sp[-3]) / 2)
    if nd == 3:
        data_crop = data[x_crop:-x_crop, y_crop:-y_crop, z_crop:-z_crop]
    elif nd == 4:
        data_crop = data[:, x_crop:-x_crop, y_crop:-y_crop, z_crop:-z_crop]
    elif nd == 5:
        data_crop = data[:, :, x_crop:-x_crop, y_crop:-y_crop, z_crop:-z_crop]
    else:
        raise ('Wrong dimension! dim=%d.' % nd)
    return data_crop


def get_batch(generator, batch_size):
    """Get a single batch from a generator."""
    batch = []
    for i in range(batch_size):
        try:
            element = next(generator)
            batch.append(element)
        except StopIteration:

            return batch, False

    return batch, True


def get_bin_centers(bin_range, bin_step):
    """Get the bin centers for prediction."""
    bin_start = bin_range[0]
    bin_end = bin_range[1]
    bin_length = bin_end - bin_start
    bin_number = int(bin_length / bin_step)
    bin_centers = bin_start + float(bin_step) / 2 + bin_step * arange(bin_number)

    return bin_centers


def num2vect(x, bin_range, bin_step, sigma):
    """
    v,bin_centers = number2vector(x,bin_range,bin_step,sigma).

    bin_range: (start, end), size-2 tuple
    bin_step: should be a divisor of |end-start|
    sigma:
    = 0 for 'hard label', v is index
    > 0 for 'soft label', v is vector
    < 0 for error messages.
    """
    bin_start = bin_range[0]
    bin_end = bin_range[1]
    bin_length = bin_end - bin_start
    if not bin_length % bin_step == 0:
        print("bin's range should be divisible by bin_step!")
        return -1
    bin_number = int(bin_length / bin_step)
    bin_centers = bin_start + float(bin_step) / 2 + bin_step * arange(bin_number)

    if sigma == 0:
        x = array(x)
        i = floor((x - bin_start) / bin_step)
        i = i.astype(int)
        return i, bin_centers
    elif sigma > 0:
        if isscalar(x):
            v = zeros((bin_number,))
            for i in range(bin_number):
                x1 = bin_centers[i] - float(bin_step) / 2
                x2 = bin_centers[i] + float(bin_step) / 2
                cdfs = norm.cdf([x1, x2], loc=x, scale=sigma)
                v[i] = cdfs[1] - cdfs[0]
            return v, bin_centers
        else:
            v = zeros((len(x), bin_number))

            for j in range(len(x)):
                for i in range(bin_number):
                    x1 = bin_centers[i] - float(bin_step) / 2
                    x2 = bin_centers[i] + float(bin_step) / 2
                    cdfs = norm.cdf([x1, x2], loc=x[j], scale=sigma)
                    v[j, i] = cdfs[1] - cdfs[0]

            return v, bin_centers


def random_seed(seed_value, device):
    """Set the random seed."""
    random.seed(seed_value)  # cpu vars
    torch_manual_seed(seed_value)  # cpu  vars
    seed(seed_value)  # Python
    if device == "cuda:0":
        cuda_manual_seed(seed_value)
        manual_seed_all(seed_value)  # gpu vars
        cudnn.deterministic = True   # needed
        cudnn.benchmark = False
