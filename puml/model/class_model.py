from __future__ import annotations
from typing import Tuple, Any, Union, Callable, List
from functools import partial
from dataclasses import dataclass, field

from puml.util import fn, error


@dataclass
class Model:
    name: str = None
    klasses: list = field(default_factory=list)

    def create_klass(self, name, stereotype):
        klass = Klass.factory(name=name, stereotype=stereotype)
        self.klasses.append(klass)
        return klass

    def add_klass_relation(self, leftname, relation, cardinality, rightname, annotation):
        left_klass, right_klass = self.find_left_right_klasses(leftname, rightname)
        if not left_klass or not right_klass:
            return self
        if ">" in relation:
            left_klass.has_relation_to(right_klass, cardinality, annotation)
        elif "<" in relation:
            right_klass.has_relation_to(left_klass, cardinality, annotation)
        return self

    def find_class_by_type(self, klass_type: Union[Table, Column, Klass]):
        return fn.find(partial(self.klass_type_predicate, klass_type), self.klasses)

    def find_left_right_klasses(self, left, right) -> Tuple:
        return (fn.find(partial(self.klass_name_predicate, left), self.klasses),
                fn.find(partial(self.klass_name_predicate, right), self.klasses))

    def klass_name_predicate(self, name, klass):
        return klass.name == name

    def klass_type_predicate(self, klass_type: Any, klass):
        return isinstance(klass, klass_type)


@dataclass
class Klass:
    name: str
    stereotype: str
    meta: list = field(default_factory=list)
    properties: list = field(default_factory=list)
    related_to: list = field(default_factory=list)
    behaviours: list = field(default_factory=list)
    collecting_meta: bool = None
    collecting_behaviour: bool = None
    in_declaration: bool = field(default=True)

    @classmethod
    def factory(cls, name, stereotype):
        kls = cls.klass_definitions().get(stereotype)
        if not kls:
            return cls(name, stereotype)
        return kls(name, stereotype)

    @classmethod
    def klass_definitions(cls):
        return {"table": Table, "column": Column}

    def __eq__(self, other):
        return self.name == other.nam

    def not_accepting_properties(self):
        return not self.in_declaration or self.collecting_behaviour or self.collecting_meta

    def end_declaration(self):
        self.in_declaration = False
        return self

    def start_meta(self):
        self.collecting_meta = True

    def start_behaviour(self):
        self.collecting_behaviour = True

    def end_segment(self):
        if self.collecting_meta:
            self.collecting_meta = False
        if self.collecting_behaviour:
            self.collecting_behaviour = False
        return self

    def add_property(self, name, term):
        if self.collecting_meta:
            self.meta.append(Meta(name=name, value=term))
            return self
        if self.collecting_behaviour:
            self.behaviours.append(name)
            return self
        self.properties.append(Property(name=name, type_of=term))
        return self

    def has_relation_to(self, klass, cardinality, annotation):
        self.related_to.append(Relation(klass, cardinality, annotation))
        return self

    def find_class_relations_by_type(self, klass_type: Union[Table, Column, Klass], sort_fn: Callable = fn.identity):
        return (sort_fn(
            map(self.klass_for_relation, fn.select(partial(self.klass_type_predicate, klass_type), self.related_to)))
        )

    def klass_type_predicate(self, klass_type, rel: Relation):
        return isinstance(rel.klass, klass_type)

    def klass_for_relation(self, relation: Relation):
        return relation.klass


@dataclass
class Table(Klass):
    pass


@dataclass
class Column(Klass):

    @classmethod
    def sort_by_column_position(self, klasses: List[Column]):
        return sorted(klasses, key=lambda k: k.column_position())

    def column_position(self):
        return int(self.meta_by_name("isAtColumnPosition", True).value)

    def meta_by_name(self, name, fail_when_not_found: bool = False, formatter: Callable = fn.identity):
        meta = Meta.find_by_name(name, self.meta)
        if not meta and fail_when_not_found:
            raise error.TableSchemaException(f"Column: {self.name} has no isAtColumnPosition meta value")
        return meta

    def is_struct(self):
        return len(self.properties) > 1


@dataclass
class Property:
    name: str
    type_of: str


@dataclass
class Meta:
    name: str
    value: str
    formatter: Callable = None

    @classmethod
    def find_by_name(cls, name, meta_pairs: List[Meta]):
        return fn.find(partial(cls.meta_name_predicate, name), meta_pairs)

    @classmethod
    def meta_name_predicate(cls, name, meta: Meta):
        return meta.name == name


@dataclass
class Relation:
    klass: Klass
    cardinality: str
    annotation: list
