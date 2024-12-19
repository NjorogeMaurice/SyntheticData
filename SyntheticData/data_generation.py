from sdv.single_table import GaussianCopulaSynthesizer


def generate_synthetic_data(metadata,data):
    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(data)
    synthetic_data = synthesizer.sample(num_rows=len(data))
    return synthetic_data