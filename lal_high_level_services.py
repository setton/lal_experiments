import os
import libadalang as lal

NOT_APPLICABLE = 1
IN_SOURCE = 2
IN_STANDARD = 3
NOT_FOUND = 4


def identifier_to_first_part(node):
    """Return the definition (first part) of the node denoted by
       the Identifier node node.

       The result is a tuple (status, reference) where
         status is:
             NOT_APPLICABLE if the identifier is not an entity
                (for instance an attribute name, a pragma parameter)
             IN_SOURCE if this resolves to an entity in the sources
             IN_STANDARD if this resolved to an entity in the standard
             NOT_FOUND if no reference was found

          reference is the Defining_Name in the canonical_part, or None.
    """
    if not node.is_a(lal.Identifier):
        raise Exception(
            "the parameter to identifier_to_first_part must be an Identifier")

    parent = node.parent
    if parent and (parent.is_a(lal.AttributeRef) or
                   parent.is_a(lal.PragmaNode) or
                   parent.is_a(lal.PragmaArgumentAssoc)):
        return (NOT_APPLICABLE, None)

    if node.p_is_defining:
        ref = node.p_enclosing_defining_name.p_canonical_part
    else:
        ref = node.p_referenced_decl().p_canonical_part.p_defining_name

    if not ref:
        return (NOT_FOUND, None)

    if ref.unit.filename.endswith('__standard'):
        return (IN_STANDARD, ref)

    return (IN_SOURCE, ref)
