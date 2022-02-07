"""Define Pydantic Class models for VRSATILE models."""
from __future__ import annotations
from enum import Enum
from typing import List, Optional, Union, Any, Literal

from pydantic import BaseModel, Extra, StrictInt, StrictStr, \
    root_validator, validator, Field

from ga4gh.vrsatile.pydantic import return_value
from ga4gh.vrsatile.pydantic.vrs_models import CURIE, Allele, Haplotype, \
    CopyNumber, Text, VariationSet, SequenceLocation, ChromosomeLocation,\
    Sequence, Gene, Variation


class VODClassName(str, Enum):
    """Define VOD class names."""

    VARIATION_DESCRIPTOR = "VariationDescriptor"
    LOCATION_DESCRIPTOR = "LocationDescriptor"
    SEQUENCE_DESCRIPTOR = "SequenceDescriptor"
    GENE_DESCRIPTOR = "GeneDescriptor"


class VRSATILETypes(str, Enum):
    """Define types used in VRSATILE."""

    EXTENSION = "Extension"
    EXPRESSION = "Expression"


class MoleculeContext(str, Enum):
    """The structural variant type associated with this variant."""

    GENOMIC = "genomic"
    TRANSCRIPT = "transcript"
    PROTEIN = "protein"


class Extension(BaseModel):
    """The Extension class provides VODs with a means to extend descriptions
    with other attributes unique to a content provider. These extensions are
    not expected to be natively understood under VRSATILE, but may be used
    for pre-negotiated exchange of message attributes when needed.
    """

    class Config:
        """Class configs."""

        extra = Extra.forbid

    type: Literal[VRSATILETypes.EXTENSION] = VRSATILETypes.EXTENSION
    name: StrictStr
    value: Any


class Expression(BaseModel):
    """The Expression class is designed to enable descriptions based on a
    specified nomenclature or syntax for representing an object. Common
    examples of expressions for the description of molecular variation include
    the HGVS and ISCN nomenclatures.
    """

    class Config:
        """Class configs."""

        extra = Extra.forbid

    type: Literal[VRSATILETypes.EXPRESSION] = VRSATILETypes.EXPRESSION
    syntax: CURIE
    value: StrictStr
    version: Optional[StrictStr]

    _get_syntax_val = validator('syntax', allow_reuse=True)(return_value)


class ValueObjectDescriptor(BaseModel):
    """The root class of all VODs is the abstract Value Object Descriptor
    class. All attributes of this parent class are inherited by child classes.
    """

    class Config:
        """Class configs."""

        extra = Extra.allow

    id: CURIE
    type: StrictStr
    label: Optional[StrictStr]
    description: Optional[StrictStr]
    xrefs: Optional[List[CURIE]]
    alternate_labels: Optional[List[StrictStr]]
    extensions: Optional[List[Extension]]

    _get_id_val = validator('id', allow_reuse=True)(return_value)
    _get_xrefs_val = validator('xrefs', allow_reuse=True)(return_value)


class SequenceDescriptor(ValueObjectDescriptor):
    """This descriptor is intended to reference VRS Sequence value objects."""

    class Config:
        """Class configs."""

        extra = Extra.forbid

    type: Literal[VODClassName.SEQUENCE_DESCRIPTOR] = \
        VODClassName.SEQUENCE_DESCRIPTOR
    sequence_id: Optional[CURIE]
    sequence: Optional[Sequence]
    residue_type: Optional[CURIE]

    @root_validator(pre=True)
    def check_sequence_or_sequence_id_present(cls, values):
        """Check that at least one of {`sequence`, `sequence_id`} is set."""
        msg = 'Must give values for either `sequence`, `sequence_id`, or both'
        value, value_id = values.get('sequence'), values.get('sequence_id')
        assert value or value_id, msg
        return values

    _get_sequence_id_val = \
        validator('sequence_id', allow_reuse=True)(return_value)
    _get_sequence_val = validator('sequence', allow_reuse=True)(return_value)
    _get_residue_type_val = \
        validator('residue_type', allow_reuse=True)(return_value)


class LocationDescriptor(ValueObjectDescriptor):
    """This descriptor is intended to reference VRS Location value objects."""

    class Config:
        """Class configs."""

        extra = Extra.forbid

    type: Literal[VODClassName.LOCATION_DESCRIPTOR] = \
        VODClassName.LOCATION_DESCRIPTOR
    location_id: Optional[CURIE]
    location: Optional[Union[SequenceLocation, ChromosomeLocation]]

    @root_validator(pre=True)
    def check_location_or_location_id_present(cls, values):
        """Check that at least one of {`location`, `location_id`} is set."""
        msg = 'Must give values for either `location`, `location_id`, or both'
        value, value_id = values.get('location'), values.get('location_id')
        assert value or value_id, msg
        return values

    _get_location_id_val = \
        validator('location_id', allow_reuse=True)(return_value)


class GeneDescriptor(ValueObjectDescriptor):
    """This descriptor is intended to reference VRS Gene value objects."""

    class Config:
        """Class configs."""

        extra = Extra.forbid

    type: Literal[VODClassName.GENE_DESCRIPTOR] = VODClassName.GENE_DESCRIPTOR
    gene_id: Optional[CURIE]
    gene: Optional[Gene]

    @root_validator(pre=True)
    def check_gene_or_gene_id_present(cls, values):
        """Check that at least one of {`gene`, `gene_id`} is set."""
        msg = 'Must give values for either `gene`, `gene_id`, or both'
        value, value_id = values.get('gene'), values.get('gene_id')
        assert value or value_id, msg
        return values

    _get_gene_id_val = validator('gene_id', allow_reuse=True)(return_value)


class VCFRecord(BaseModel):
    """This data class is used when it is desirable to pass data as expected
    from a VCF record.
    """

    class Config:
        """Class configs."""

        extra = Extra.forbid

    genome_assembly: StrictStr
    chrom: StrictStr
    pos: StrictInt
    id: Optional[StrictStr]
    ref: StrictStr
    alt: StrictStr
    qual: Optional[StrictStr]
    filter: Optional[StrictStr]
    info: Optional[StrictStr]


class VariationDescriptor(ValueObjectDescriptor):
    """This descriptor is intended as an class for describing VRS Variation
    value objects.
    """

    class Config:
        """Class configs."""

        extra = Extra.forbid

    type: Literal[VODClassName.VARIATION_DESCRIPTOR] = \
        VODClassName.VARIATION_DESCRIPTOR
    variation_id: Optional[CURIE]
    variation: Optional[Union[Allele, Haplotype, CopyNumber,
                              Text, VariationSet]]
    molecule_context: Optional[MoleculeContext]
    structural_type: Optional[CURIE]
    expressions: Optional[List[Expression]]
    vcf_record: Optional[VCFRecord]
    gene_context: Optional[Union[CURIE, GeneDescriptor]]
    vrs_ref_allele_seq: Optional[Sequence]
    allelic_state: Optional[CURIE]

    _get_variation_id_val = \
        validator('variation_id', allow_reuse=True)(return_value)
    _get_structural_type_val = \
        validator('structural_type', allow_reuse=True)(return_value)
    _get_gene_context_val = \
        validator('gene_context', allow_reuse=True)(return_value)
    _get_vrs_allele_ref_seq_val = \
        validator('vrs_ref_allele_seq', allow_reuse=True)(return_value)
    _get_allelic_state_val = \
        validator('allelic_state', allow_reuse=True)(return_value)


class CategoricalVariationClassName(str, Enum):

    CANONICAL_VARIATION = "CanonicalVariation"
    COMPLEX_VARIATION = "ComplexVariation"


class CategoricalVariation(BaseModel):
    """A representation of a categorically-defined `functional domain
    <https://en.wikipedia.org/wiki/Domain_of_a_function>`_ for variation, in
    which individual variation instances may be members.
    """

    id: Optional[CURIE] = Field(..., alias="_id")
    type: CategoricalVariationClassName
    complement: bool

    _get_id_val = validator("id", allow_reuse=True)(return_value)


class CanonicalVariation(CategoricalVariation):
    """A categorical variation domain characterized by a representative
    Variation context to which members lift-over, project, translate, or
    otherwise directly align.
    """

    type: Literal[CategoricalVariationClassName.CANONICAL_VARIATION] = \
        CategoricalVariationClassName.CANONICAL_VARIATION
    variation: Optional[Union[Allele, Haplotype, CopyNumber,
                              Text, VariationSet]]


class ComplexVariationOperator(str, Enum):
    """Possible values for the Complex Variation's `operator` field."""

    AND = "AND"
    OR = "OR"


class ComplexVariation(CategoricalVariation):
    """A categorical variation domain jointly characterized by two or more
    other categorical variation domains.
    """

    type: Literal[CategoricalVariationClassName.COMPLEX_VARIATION] = \
        CategoricalVariationClassName.COMPLEX_VARIATION
    operands: List[CategoricalVariation]
    operator: ComplexVariationOperator
