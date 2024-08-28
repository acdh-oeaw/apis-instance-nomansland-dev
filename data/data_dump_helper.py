import pandas as pd


class DataDumpHelper:
    def __init__(self, json_dump):
        self.df = pd.read_json(json_dump)

    def get_base_vocab_data(self, vocab_pk):
        match = self.df[
            (self.df.model == "apis_vocabularies.vocabsbaseclass")
            & (self.df.pk == vocab_pk)
        ]
        if match.shape[0]:
            return {"name": match.iloc[0].fields["name"]}
        return {}
