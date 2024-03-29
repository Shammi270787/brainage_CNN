"""Brain age prediction."""

# %% External package import

# %% Internal package import

from brainage.data import DataLoader
from brainage.preprocessing import DataPreprocessor
from brainage.models import DataModelPredictor

# %% Class definition


class BrainAgePredictor():
    """
    Brain age prediction class.

    This class provides ...

    Parameters
    ----------
    data_path : ...
        ...

    age_filter : ...
        ...

    image_dimensions : ...
        ...

    steps : ...
        ...

    learning_rate : ...
        ...

    number_of_epochs : ...
        ...

    batch_size : ...
        ...

    train_all_layers : ...
        ...

    architecture : ...
        ...

    optimizer : ...
        ...

    pretrained_weights : ...
        ...

    Attributes
    ----------
    data_loader : ...
        ...

    data_preprocessor : ...
        ...

    data_model_predictor : ...
        ...

    Methods
    -------
    ...
    """

    def __init__(
            self,
            data_path,
            age_filter,
            image_dimensions,
            steps,
            learning_rate=0.0001,
            number_of_epochs=240,
            batch_size=3,
            train_all_layers=False,
            architecture='sfcn',
            optimizer='adam',
            pretrained_weights=None):

        self.data_loader = DataLoader(data_path, age_filter)
        self.data_preprocessor = DataPreprocessor(
            image_dimensions, steps)
        self.data_model_predictor = DataModelPredictor(
            data_loader=self.data_loader,
            data_preprocessor=self.data_preprocessor,
            learning_rate=learning_rate,
            number_of_epochs=number_of_epochs,
            batch_size=batch_size,
            train_all_layers=train_all_layers,
            architecture=architecture,
            optimizer=optimizer,
            pretrained_weights=pretrained_weights)

    def predict(
            self,
            image):
        """Predict the brain age from an image."""
        return self.data_model_predictor.run_prediction_model(image)
