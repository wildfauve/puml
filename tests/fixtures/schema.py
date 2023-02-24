from jobsworthy import structure as S
from pyspark.sql import types as Tfrom . import vocab


S.Table(vocab=vocab.vocab, vocab_directives=[S.VocabDirective.RAISE_WHEN_TERM_NOT_FOUND])
.column()  # Asset
.struct('heldInstrument.asset', False)
.string('heldInstrument.@id', False)
.string('heldInstrument.@type', False)
.string('heldInstrument.structuralType', False)
.string('heldInstrument.shortName', False)
.decimal('heldInstrument.pricingFactor', T.DecimalType(11, 5),  True)
.end_struct()


.column()  # State
.string('state.currentState', False)


.column()  # AppliedAt
.struct('timeDimension.appliedAt', False)
.string('timeDimension.hasTimeInstant', False)
.string('timeDimension.hasMonthDimension', False)
.string('timeDimension.hasYear', False)
.end_struct()


.column()  # CreatedAt
.struct('timeDimension.createdAt', False)
.string('timeDimension.hasTimeInstant', False)
.string('timeDimension.hasMonthDimension', False)
.string('timeDimension.hasYear', False)
.end_struct()


.column()  # Issuer
.struct('issuer.issuer', False)
.string('issuer.@id', False)
.string('issuer.@type', False)
.string('issuer.label', False)
.end_struct()


.column()  # CounterParty
.string('counterParty.label', False)


.column()  # IssuerClassification
.struct('issuerClassification.issuerClassification', False)
.string('issuerClassification.@id', False)
.string('issuerClassification.@type', False)
.string('issuerClassification.label', False)
.end_struct()


.column()  # CountryOfRisk
.struct('countryOfRisk.countryOfRisk', False)
.string('countryOfRisk.@id', False)
.string('countryOfRisk.label', False)
.end_struct()


.column()  # LegalJurisdiction
.struct('legalJurisdiction.legalJurisdiction', False)
.string('legalJurisdiction.@id', False)
.string('legalJurisdiction.label', False)
.end_struct()


.column()  # Classification
.struct('classification.classification', False)
.string('classification.@id', False)
.string('classification.@type', False)
.string('classification.label', False)
.end_struct()


.column()  # Rating
.struct('rating.rating', False)
.string('rating.@id', False)
.string('rating.@type', False)
.string('rating.label', False)
.end_struct()


.column()  # Identifier
.struct('identity.identifier', False)
.string('identity.@id', False)
.string('identity.@type', False)
.string('identity.label', False)
.end_struct()

