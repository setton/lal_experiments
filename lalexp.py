import os
import libadalang as lal
import GPS


def loc_error(n, message):
    """emit error message at the location of n"""
    print "{}:{}:{}: {}".format(
        os.path.basename(n.unit.filename),
        n.sloc_range.start.line,
        n.sloc_range.start.column,
        message)


class LALElim(object):

    def __init__(self, project):
        """Look in the given project for unused entities"""

        project_file = project.file().name()
        provider = lal.UnitProvider.for_project(project_file)
        self.ctx = lal.AnalysisContext(unit_provider=provider)

        self.all_entities = {}
        # All entities.
        # keys: node
        # values: set of references (file, line, col)

        # TODO: process only the closure of mains?
        # mains = project.get_attribute_as_list('main')

        self.success_count = 0
        self.fail_count = 0

        for source in project.sources(recursive=True):
            if source.language().lower() != "ada":
                continue

            filename = source.name()
            self.inspect_file(filename)

        print "nodes successfully xref'ed: {}".format(self.success_count)
        print "nodes not xref'ed: {}".format(self.fail_count)

        # OK now do something

        for k in self.all_entities:
            if not self.all_entities[k]:
                print "{}:{}:{}: entity {} not referenced".format(
                    os.path.basename(k.unit.filename),
                    k.sloc_range.start.line,
                    k.sloc_range.start.column,
                    k.text)

    def inspect_file(self, filename):
        """Look at all the defining entities in one file"""

        unit = self.ctx.get_from_file(filename)
        for d in unit.diagnostics:
            print('{}: error: {}'.format(filename, d))
        if unit.diagnostics:
            return

        unit.populate_lexical_env()
        for node in unit.root.findall(lal.Identifier):
            if node.parent.is_a(lal.DefiningName):
                if node.parent not in self.all_entities:
                    self.all_entities[node.parent] = set()
            else:
                xref = None
                try:
                    xref = node.p_xref
                    self.success_count += 1
                except Exception:
                    self.fail_count += 1
                    loc_error(node, "exception when computing xref")

                if xref:
                    # print "got xref", node.text, xref.unit, xref
                    key = xref
                    val = (node.unit.filename,
                           node.sloc_range.start.line,
                           node.sloc_range.start.column)
                    # print key, val

                    if key in self.all_entities:
                        if val in self.all_entities[key]:
                            # This could happen for package specs
                            pass
                        else:
                            if val:
                                self.all_entities[key].add(val)
                    else:
                        if val:
                            self.all_entities[key] = set([val])
                        else:
                            self.all_entities[key] = set()


def execute():
    project = GPS.Project.root()
    LALElim(project)
