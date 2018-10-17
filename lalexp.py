import os
import libadalang as lal
import GPS
from ada_types import AdaObject, AdaCallable
from lal_high_level_services import identifier_to_first_part, \
    NOT_APPLICABLE, IN_SOURCE, IN_STANDARD, NOT_FOUND


DEBUG_MODE = False
# debug mode!


def loc_error(n, message):
    """emit error message at the location of n"""
    print "{}:{}:{}: {}".format(
        os.path.basename(n.unit.filename),
        n.sloc_range.start.line,
        n.sloc_range.start.column,
        message)


def unique_loc(node):
    return (node.unit.filename, node.sloc_range.start)


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

        self.all_objects = {}
        # All objects. Key: loc returned by unique_loc, value: AdaObject

        self.all_callables = {}
        # All callables. Key: loc returned by unique_loc, value: AdaCallable

        self.success_count = 0
        self.fail_count = 0

        for source in project.sources(recursive=True):
            if source.language().lower() != "ada":
                continue

            filename = source.name()
            self.inspect_file(filename)

        print "nodes successfully xref'ed: {}".format(self.success_count)
        print "nodes not xref'ed: {}".format(self.fail_count)

        # OK now print something

        for k in self.all_objects:
            if not self.all_objects[k].writes:
                print "{}:{}:{}: is never written".format(
                    os.path.basename(k.unit.filename),
                    k.line,
                    k.sloc_range.start.column,
                    self.all_objects[k].text)

        # TODO: complete with other things

    def process_node(self, node):
        """Process one node"""
        ref = None
        try:
            status, ref = identifier_to_first_part(node)
        except Exception:
            loc_error(node, "exception when computing xref")
            raise

        if status == NOT_APPLICABLE:
            # Nothing to do
            return
        elif status == IN_STANDARD:
            # Nothing to do either
            return
        elif status == NOT_FOUND:
            # Warn the user
            loc_error(node, "no xref found")
            return

        elif status == IN_SOURCE:
            # Debug: print a message
            if DEBUG_MODE:
                loc_error(node, "found xref at {}:{}:{}".format(
                    os.path.basename(ref.unit.filename),
                    ref.sloc_range.start.line,
                    ref.sloc_range.start.column))

            if ref.parent.is_a(lal.SubpSpec):
                # We have a subprogram call
                loc = unique_loc(ref)
                if loc in self.all_callables:
                    self.all_callables[loc].calls.append(loc)
                else:
                    self.all_callables[loc].calls = node

            else:
                print "TODO"  # TODO

        else:
            raise Exception("Add something to this case statement!")

    def inspect_file(self, filename):
        """Look at all the defining entities in one file"""

        unit = self.ctx.get_from_file(filename)
        for d in unit.diagnostics:
            print('{}: error: {}'.format(filename, d))
        if unit.diagnostics:
            return

        unit.populate_lexical_env()
        for node in unit.root.findall(lal.Identifier):
            self.process_node(node)


def execute():
    project = GPS.Project.root()
    LALElim(project)
