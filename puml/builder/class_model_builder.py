from typing import Tuple, Any, Callable
import re
from functools import reduce, partial

from puml.model import class_model
from puml.util import fn, error

from rich.console import Console
from rich.text import Text
from rich.table import Table

console = Console()


def build(file_name: str, serialiser: Callable = None, writer: Callable = None):
    model, _ = reduce(_parse, _read_file(file_name).split("\n"), (class_model.Model(), None))
    _print_status(model)
    if serialiser:
        serialiser(model, writer)
    return model


def _parse(model: Tuple[class_model.Model, Any], line: str):
    console.print(line, style="magenta")
    func, match = _parser_finder(line)
    if not func:
        return model
    return func(model, match)


def _parser_finder(line: str):
    result = fn.remove_none(map(partial(_re_predicate, line), rx.items()))
    if not result:
        console.print(f"No Match for: {line}", style="#af00ff")
        return None, None
    # if len(result) > 1:
    #     breakpoint()
    return result[0]


def _re_predicate(target: str, rx):
    name, options = rx
    match = options['re'].search(target)
    if not match:
        return None
    return (options['fn'], match)


def _model_start(model: Tuple[class_model.Model, Any], match):
    klass_model, _ = model
    name, = match.groups()
    console.print(f"Model Start: {name}", style="green")
    klass_model.name = name
    return model


def _class_start(model: Tuple[class_model.Model, Any], match):
    klass_model, should_be_none = model
    if should_be_none:
        raise error.TableSchemaException(
            f"Problem with class definition {should_be_none.name} not completed before starting new class")
    name, stereotype = match.groups()
    console.print(f"Class Start: {name}, {stereotype}", style="blue")
    klass = klass_model.create_klass(name, stereotype)
    return klass_model, klass


def _class_end(model: Tuple[class_model.Model, Any], match):
    klass_model, klass = model
    console.print(f"Class End: {klass.name}", style="blue")
    klass.end_declaration()
    return klass_model, None


def _class_meta(model: Tuple[class_model.Model, Any], _match):
    klass_model, klass = model
    klass.start_meta()
    return model


def _class_behaviour(model: Tuple[class_model.Model, Any], _match):
    klass_model, klass = model
    klass.start_behaviour()
    return model


def _class_segment_end(model: Tuple[class_model.Model, Any], match):
    klass_model, klass = model
    klass.end_segment()
    return model


def _class_prop(model: Tuple[class_model.Model, Any], match):
    klass_model, klass = model
    name, prop_type = match.groups()
    if klass is None:
        breakpoint()
    klass.add_property(name.strip(), prop_type.strip() if prop_type else prop_type)
    return model


def _relation(model: Tuple[class_model.Model, Any], match):
    klass_model, _ = model
    side1, relation, _, cardinality, side2, *annotation = match.groups()
    console.print(f"Relation: {side1} {relation} {cardinality} {side2} {annotation}", style="cyan")
    klass_model.add_klass_relation(side1, relation, cardinality, side2, annotation)
    return model


def _noop(model: Tuple[class_model.Model, Any], match):
    console.print(f"Noop of {match}")
    return model


def _read_file(file_name):
    with open(file_name) as file:
        out = file.read()
    return out


def _print_status(model):
    table = Table(title="Parse Status")

    table.add_column("Metric", justify="right", style="cyan", no_wrap=True)
    table.add_column("Count", justify="center", style="magenta")

    kls_types = _number_of_klass_types(model)
    table.add_row("Number of Classes", str(len(model.klasses)))
    for name, ct in kls_types.items():
        table.add_row(f"Number of Class Type: {name}", str(ct))
    table.add_row("Number of Relations", str(_number_of_relations(model)))
    console.print(table)


def _number_of_relations(model):
    return reduce(_accumulate, model.klasses, 0)


def _number_of_klass_types(model):
    return reduce(_kls_types_ct, model.klasses, dict())


def _accumulate(ct, klass):
    return ct + len(klass.related_to)


def _kls_types_ct(ct, klass):
    name = klass.__class__.__name__
    if ct.get(name):
        ct[name] += 1
    else:
        ct[name] = 1
    return ct


rx = {
    "enduml": {"re": re.compile(r'@enduml'), "fn": _noop},
    "comment": {"re": re.compile(r"\s*'"), "fn": _noop},
    "!": {"re": re.compile(r'^!'), "fn": _noop},
    "startuml": {"re": re.compile(r'@startuml\s*(\w+)'), "fn": _model_start},
    "class_declaration": {"re": re.compile(r'^class\s*(\w+)\s*<{0,2}([\w-]*)>{0,2}'), "fn": _class_start},
    "class_declaration_end": {"re": re.compile(r'^\}'), "fn": _class_end},
    "class_meta": {"re": re.compile(r'\s*--meta--\s*'), "fn": _class_meta},
    "class_behaviour": {"re": re.compile(r'\s*--behaviour--\s*'), "fn": _class_behaviour},
    "relation": {
        "re": re.compile(r'(\w+)\s*(<[-.\|]+|[-.\|]+>)\s*("([\d\.\*]*)"|\s*)\s*(\w+):?\s*<{0,2}([\.\w:-]+)?>{0,2}'),
        "fn": _relation},
    "class_prop": {"re": re.compile(r'\s*([\w@-]+):?\s*([\[\]\(\),\w\/\.\s]+)?'), "fn": _class_prop},
    "class_segment_end": {"re": re.compile(r'\s*===\s*'), "fn": _class_segment_end}
}

"""
r'\s*([\w@-]+):\s*([\w\[\]]+)'


"""
