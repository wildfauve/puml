from typing import Tuple, List, Dict
import json


def write(schema_file_name: str, vocab_file_name: str, serialised: Tuple[List, Dict]):
    schema, vocab = serialised
    _write_schema(schema_file_name, schema)
    _write_vocab(vocab_file_name, vocab)


def _write_schema(file, schema):
    with open(file, 'w') as writer:
        writer.writelines("\n".join(schema))


def _write_vocab(file, vocab):
    with open(file, 'w') as writer:
        writer.write(json.dumps(vocab, indent=4))
