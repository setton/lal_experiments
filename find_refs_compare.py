"""Small utility for comparing 'find all references' between the old engine
   and the new engine.

   Invoke with:

       gps -P <your_project> --load=python:<path_to_this_file>
"""

import libadalang as lal
import GPS


def node_to_file_line_col(node):
    return (node.unit.filename, int(node.sloc_range.start.line),
            node.sloc_range.start.column)


def loc_to_file_line_col(loc):
    return (loc.file().name(), loc.line(), loc.column())


class Explorer(object):

    def __init__(self, project):
        project_file = project.file().name()
        provider = lal.UnitProvider.for_project(project_file)
        self.ctx = lal.AnalysisContext(unit_provider=provider)

        self.all_sources = set([f for f in project.sources(recursive=True)
                                if f.language().lower() == "ada"])
        self.all_ctx = [self.ctx.get_from_file(f.name())
                        for f in self.all_sources]

        while self.all_sources:
            self.browse_one_source(self.all_sources.pop())

    def browse_one_source(self, src):
        unit = self.ctx.get_from_file(src.name())
        for defining in unit.root.findall(lal.DefiningName):
            # We have a defining name
            # get the tuples for all LAL references
            lal_refs = set([node_to_file_line_col(r)
                            for r in defining.p_find_all_references(
                                self.all_ctx)])

            # ... add yourself to the LAL results
            lal_refs.add(node_to_file_line_col(defining))

            # get the tuples for all GPS entity references
            e = GPS.Entity(defining.text, src,
                           int(defining.sloc_range.start.line),
                           int(defining.sloc_range.start.column))

            gps_refs = set([loc_to_file_line_col(l) for l in e.references()])

            in_gps_only = gps_refs - lal_refs
            in_lal_only = lal_refs - gps_refs

            if in_lal_only or in_gps_only:
                name = defining.text
                (file, line, col) = node_to_file_line_col(defining)
                GPS.Console().write(
                    "*** {}:{}:{}:{} ***\n".format(
                        name, file, line, col))

                if in_gps_only:
                    GPS.Console().write(
                        "    found by GPS but not by LAL: {}\n".format(
                         " ".join(["{}:{}:{}".format(f[0], f[1], f[2])
                                   for f in in_gps_only])))
                if in_lal_only:
                    GPS.Console().write(
                        "    found by LAL but not by GPS: {}\n".format(
                         " ".join(["{}:{}:{}".format(f[0], f[1], f[2])
                                   for f in in_lal_only])))


def execute(hook):
    project = GPS.Project.root()
    Explorer(project)

GPS.Hook("gps_started").add(execute)
