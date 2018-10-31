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

        all_sources = project.sources(recursive=True)
        counter = 0

        for source in all_sources:
            if source.language().lower() != "ada":
                continue

            counter += 1
            print "completed {} out of {} ({}%)...".format(
                counter,
                len(all_sources),
                int(counter * 100 / len(all_sources)))
            filename = source.name()
            self.inspect_file(filename)

        print "nodes successfully xref'ed: {}".format(self.success_count)
        print "nodes not xref'ed: {}".format(self.fail_count)

        # OK now print something

        for k in self.all_objects:
            if not self.all_objects[k].reads:
                print "{}:{}:{}: is never read".format(
                    os.path.basename(k[0]),
                    k[1].line,
                    k[1].column)

        for k in self.all_callables:
            if not self.all_callables[k].calls:
                print "{}:{}:{}: is never called".format(
                    os.path.basename(k[0]),
                    k[1].line,
                    k[1].column)

        # TODO: complete with other things

    def process_node(self, node):
        """Process one node"""

        if (len(node.parents) > 7 and
            node.parents[5].is_a(lal.Params) and
                node.parents[7].is_a(lal.SubpDecl)):
            # Ignore parameter definition in subprogram declarations
            # because they are not findable from the subprogram body (RA18-041)
            return

        ref = None
        try:
            status, ref = identifier_to_first_part(node)
            self.success_count += 1
        except Exception:
            self.fail_count += 1
            status = NOT_APPLICABLE
            loc_error(node, "exception when computing xref")

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

            loc = unique_loc(ref)

            if ref.sloc_range.start.line == node.sloc_range.start.line:
                # Figure out if this is a definition
                if ref.is_a(lal.SubpDecl):
                    if loc not in self.all_callables:
                        self.all_callables[loc] = AdaCallable([])
                else:
                    if loc not in self.all_objects:
                        self.all_objects[loc] = AdaObject([], [])

            elif ref.is_a(lal.SubpDecl):
                if False:
                    loc_error(node, "is a subprogram call")
                # We have a subprogram call

                if loc in self.all_callables:
                    self.all_callables[loc].calls.append(loc)
                else:
                    self.all_callables[loc] = AdaCallable([node])

            else:
                if False:
                    loc_error(node, "is a object ref")
                # We have an object reference
                if loc in self.all_objects:
                    self.all_objects[loc].reads.append(ref)
                else:
                    self.all_objects[loc] = AdaObject([node], [])

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
