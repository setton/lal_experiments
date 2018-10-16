import os
import libadalang as lal
import GPS

all_entities = {}
# All entities.
# keys: node
# values: set of references (file, line, col)


def loc_error(n, message):
    """emit error message at the location of n"""
    print "{}:{}:{}: {}".format(
        os.path.basename(n.unit.filename),
        n.sloc_range.start.line,
        n.sloc_range.start.column,
        message)


def execute():
    project = GPS.Project.root()
    project_file = project.file().name()
    provider = lal.UnitProvider.for_project(project_file)

    ctx = lal.AnalysisContext(unit_provider=provider)

    mains = project.get_attribute_as_list('main')

    success_count = 0
    fail_count = 0

    for source in project.sources(recursive=True):
        if source.language().lower() != "ada":
            continue

        filename = source.name()

        unit = ctx.get_from_file(filename)
        for d in unit.diagnostics:
            print('{}: error: {}'.format(filename, d))
        if unit.diagnostics:
            continue

        unit.populate_lexical_env()
        for node in unit.root.findall(lal.Identifier):
            if node.parent.is_a(lal.DefiningName):
                if node.parent not in all_entities:
                    all_entities[node.parent] = set()
            else:
                xref = None
                try:
                    xref = node.p_xref
                    success_count += 1
                except Exception:
                    fail_count += 1
                    loc_error(node, "exception when computing xref")

                if xref:
                    # print "got xref", node.text, xref.unit, xref
                    key = xref
                    val = (node.unit.filename,
                           node.sloc_range.start.line,
                           node.sloc_range.start.column)
                    # print key, val

                    if key in all_entities:
                        if val in all_entities[key]:
                            # This could happen for package specs
                            pass
                        else:
                            if val:
                                all_entities[key].add(val)
                    else:
                        if val:
                            all_entities[key] = set([val])
                        else:
                            all_entities[key] = set()

    print "nodes successfully xref'ed: {}".format(success_count)
    print "nodes not xref'ed: {}".format(fail_count)

    # OK now do something

    for k in all_entities:
        if not all_entities[k]:
            print "{}:{}:{}: entity {} not referenced".format(
                os.path.basename(k.unit.filename),
                k.sloc_range.start.line,
                k.sloc_range.start.column,
                k.text)
