"""SFCN model."""

# %% External package import

from numpy import exp
from torch import as_tensor, device, float32, load, no_grad
from torch.nn import Conv3d, DataParallel, init, Module
from torch.optim import Adam, SGD

# %% Internal package import

from brainage.models.architectures import SFCN
from brainage.tools import get_bin_centers

# %% Class definition


class SFCNModel(Module):
    """
    SFCN model class.

    This class provides ...

    Parameters
    ----------
    pretrained_weights : ...
        ...

    comp_device : ...
        ...

    age_filter : ...
        ...

    Attributes
    ----------
    comp_device : ...
        ...

    age_filter : ...
        ...

    architecture : ...
        ...

    Methods
    -------
    - ``freeze_inner_layers()`` : ...
    - ``adapt_output_layer(age_range)`` : ...
    - ``set_optimizer(optimizer, learning_rate)`` : ...
    - ``fit(data, number_of_epochs, batch_size)`` : ...
    - ``forward(image)`` : ...
    """

    def __init__(
            self,
            pretrained_weights,
            comp_device,
            age_filter):

        # Call the superclass constructor
        super(SFCNModel, self).__init__()

        # Get the attributes from the arguments
        self.comp_device = comp_device
        self.age_filter = age_filter

        # Initialize the model architecture
        self.architecture = SFCN()

        # Parallelize the model
        self.architecture = DataParallel(self.architecture)

        # Load the pretrained weights if applicable
        if pretrained_weights:
            self.architecture.load_state_dict(load(
                pretrained_weights, map_location=device(comp_device)))

    def freeze_inner_layers(self):
        """Freeze the parameters of the input and hidden layers."""
        # Get all and the output layer parameters
        all_params = self.parameters()
        out_params = self.architecture.module.classifier.conv_6.parameters()

        # Set the gradient calculation for all parameters to False
        for param in all_params:
            param.requires_grad = False

        # Set the gradient calculation for the output layer to True
        for param in out_params:
            param.requires_grad = True

    def adapt_output_layer(
            self,
            age_range):
        """Adapt the output layer for the age range."""
        self.module.classifier.conv_6 = Conv3d(64, age_range, padding=0,
                                               kernel_size=1)
        init.kaiming_normal_(self.module.classifier.conv_6.weight)

    def set_optimizer(
            self,
            optimizer,
            learning_rate):
        """Set the optimizer for the model training."""
        if optimizer == 'adam':
            self.optimizer = Adam(filter(lambda p: p.requires_grad,
                                         self.parameters()),
                                  lr=learning_rate,
                                  betas=(0.9, 0.999),
                                  eps=1e-08,
                                  weight_decay=0,
                                  amsgrad=False)
        elif optimizer == 'sgd':
            self.optimizer = SGD(filter(lambda p: p.requires_grad,
                                        self.parameters()),
                                 lr=learning_rate,
                                 momentum=0.9,
                                 weight_decay=0.001)

    def fit(
            self,
            data,
            number_of_epochs,
            batch_size):
        """Fit the SFCN model."""
        print('This is where the fitting will be done - someday ...')

    def forward(
            self,
            image):
        """Perform a single forward pass through the model."""
        # Get the bin centers
        centers = get_bin_centers(self.age_filter, 1)

        # Get the image shape
        dims = image.shape

        # Reshape the image to 5D (with batch size 1)
        image = image.reshape(1, dims[0], dims[1], dims[2], dims[3])

        # Convert the image to a tensor
        image = as_tensor(image, dtype=float32, device=self.comp_device)

        # Set the architecture into evaluation mode (affects BatchNorm)
        self.architecture.eval()

        # Get the model output with gradient calculation disabled
        with no_grad():
            output = self.architecture(image)

        # Shift the output back to the CPU
        out = output[0].cpu().reshape([1, -1])

        # Convert the output to a numpy array
        out = out.numpy()

        # Calculate the probabilities
        prob = exp(out)

        # Get the prediction with the bin centers
        pred = prob @ centers

        return pred
