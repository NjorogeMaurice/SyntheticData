from sdv.metadata import Metadata

def create_metadata(data):
    data = data
    metadata = Metadata.detect_from_dataframe(
        data=data,
        table_name='housing')
    return metadata