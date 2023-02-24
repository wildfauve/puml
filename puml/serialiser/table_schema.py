from __future__ import annotations
from typing import List, Callable, Optional, Dict, Union
import re
from functools import reduce, partial

from puml.model import class_model
from puml.util import fn, error

STRING_TYPE_PARSER = re.compile(r'\s*(Optional)?\[?(StringType)\]?')
DECIMAL_TYPE_PARSER = re.compile(r'\s*(Optional)?\[?(DecimalType\([\d,\s*]*\))\]?')


def serialise(model: class_model.Model, writer: Callable):
    table = model.find_class_by_type(class_model.Table)
    if not table:
        return model
    result = reduce(_column_generator, table.find_class_relations_by_type(class_model.Column,
                                                                          class_model.Column.sort_by_column_position),
                    _template(table))
    return writer(result)


def _column_generator(definition: List, column: class_model.Column):
    defn, vocab = definition
    defn.append(f".column()  # {column.name}")

    vocab_ns_meta = column.meta_by_name("vocabNamespace")

    vocab_ns = _to_camel_case(vocab_ns_meta.value) if vocab_ns_meta else None

    if column.is_struct():
        defn.append(f".struct('{_vocab_namespace(_to_camel_case(column.name), vocab_ns)}', False)")
        _extend_vocab(vocab, vocab_ns, column, _to_camel_case)

    if not column.properties:
        breakpoint()

    reduce(partial(_property_definition, vocab_ns), column.properties, definition)

    if column.is_struct():
        defn.append(".end_struct()")

    defn.append("\n")
    return definition


def _property_definition(vocab_ns: Optional[class_model.Meta], definition: List, prop: class_model.Property):
    matches = fn.remove_none(map(partial(_re_predicate, prop.type_of), type_matches))
    if not matches:
        raise error.TableSchemaException(f"No matching type function for type {prop.type_of}")
    return matches[0][0](vocab_ns, definition, prop)


def _string_type(vocab_ns: class_model.Meta, definition: List, prop: class_model.Property):
    defn, vocab = definition
    optional, type_def = STRING_TYPE_PARSER.search(prop.type_of).groups()

    optional = True if optional == "Optional" else False

    defn.append(f".string('{_vocab_namespace(prop.name, vocab_ns)}', {optional})")
    _extend_vocab(vocab, vocab_ns, prop)
    return definition


def _decimal_type(vocab_ns: class_model.Meta, definition: List, prop: class_model.Property):
    """
    .decimal("constituent.position.unitsHeld", T.DecimalType(22, 6), False)
    """
    defn, vocab = definition
    optional, type_def = DECIMAL_TYPE_PARSER.search(prop.type_of).groups()

    optional = True if optional == "Optional" else False

    defn.append(f".decimal('{_vocab_namespace(prop.name, vocab_ns)}', T.{type_def},  {optional})")
    _extend_vocab(vocab, vocab_ns, prop)
    return definition


def _vocab_namespace(element: str, vocab_ns: str = None) -> str:
    if not vocab_ns:
        return element
    return f"{vocab_ns}.{element}"


def _extend_vocab(vocab: Dict,
                  vocab_ns: str,
                  prop: Union[class_model.Property, class_model.Column],
                  formatter: Callable = fn.identity) -> Dict:
    return _add_term(formatter(_vocab_namespace(prop.name, vocab_ns)), vocab, prop.name, formatter)


def _re_predicate(target: str, rx):
    regex, func = rx
    match = regex.search(target)
    if not match:
        return None
    return (func, match)


def _to_camel_case(string: str) -> str:
    s = re.sub(r"(_|-)+",
               " ",
               re.sub(r'([A-Z])', r'-\1', string)).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])


def _term_finder(path, vocab):
    path_array = path.split(".")
    term = fn.deep_get(vocab, path_array)
    return path_array, term


def _add_term(path, vocab, prop_name, formatter: Callable = fn.identity):
    fst, rest = fn.fst_rst(path.split("."))
    if not rest:
        vocab[formatter(fst)] = {'term': formatter(prop_name)}
        return vocab
    if not vocab.get(fst):
        vocab[formatter(fst)] = {}
    return _add_term(".".join(rest), vocab[fst], prop_name, formatter)


def _template(table):
    return (
        [
            "from jobsworthy import structure as S",
            "from pyspark.sql import types as T"
            "from . import vocab",
            "\n",
            "S.Table(vocab=vocab.vocab, vocab_directives=[S.VocabDirective.RAISE_WHEN_TERM_NOT_FOUND])"
        ],
        dict()
    )


type_matches = {
    (re.compile(r'StringType'), _string_type),
    (re.compile(r'DecimalType'), _decimal_type)
}
