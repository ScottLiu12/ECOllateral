import pytest

from src.demo import training_data
from src.models.regression import train_model


@pytest.fixture(scope="session")
def training_records():
    return training_data()


@pytest.fixture(scope="session")
def fitted_model(training_records):
    return train_model(training_records, data_kind="synthetic")
