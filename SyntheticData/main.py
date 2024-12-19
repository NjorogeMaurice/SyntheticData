from SyntheticData.data_generation import generate_synthetic_data
from SyntheticData.metadata_creation import create_metadata


def gen_synthetic_data(data):
    metadata = create_metadata(data)
    synthetic_data=generate_synthetic_data(metadata,data)

    return synthetic_data