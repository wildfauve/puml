from functools import partial

from puml.builder import class_model_builder
from puml.serialiser import table_schema
from puml import writer


def test_parse_puml_dataproduct_model():
    model = class_model_builder.build("tests/fixtures/held-instrument.puml")

    assert len(model.klasses) == 13

    expected = {'HeldInstrument', 'Asset', 'State', 'AppliedAt', 'CreatedAt', 'Issuer', 'CounterParty',
                'IssuerClassification', 'CountryOfRisk', 'LegalJurisdiction', 'Classification', 'Rating', 'Identifier'}

    assert {k.name for k in model.klasses} == expected


def test_parse_general_puml_class_model():
    model = class_model_builder.build("tests/fixtures/general_class_model.puml")
    breakpoint()


def test_table_schema_serialiser():
    model = class_model_builder.build("tests/fixtures/held-instrument.puml",
                                      serialiser=table_schema.serialise,
                                      writer=partial(writer.file_writer,
                                                     "tests/fixtures/schema.py",
                                                     "tests/fixtures/vocab.py"))
    breakpoint()
