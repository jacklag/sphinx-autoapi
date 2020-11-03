import json
import subprocess
import os
from collections import defaultdict

from sphinx.util.console import bold
import sphinx.util.logging

from .base import PythonMapperBase, SphinxMapperBase

LOGGER = sphinx.util.logging.getLogger(__name__)

ESDOC_MAP = {
    "cls_type": "kind",
    "children": "children",
    "doc_string": "description",
    "scope": "scope",
}


class JavaScriptSphinxMapper(SphinxMapperBase):

    """Auto API domain handler for Javascript

    Parses directly from Javascript files.

    :param app: Sphinx application passed in as part of the extension
    """

    def read_file(self, path, **kwargs):
        """Read file input into memory, returning deserialized objects

        :param path: Path of file to read
        """
        # TODO support JSON here
        # TODO sphinx way of reporting errors in logs?
        subcmd = "jsdoc"
        if os.name == "nt":
            subcmd = ".".join([subcmd, "cmd"])

        try:
            parsed_data = json.loads(subprocess.check_output([subcmd, "-X", path]))
            return parsed_data
        except json.decoder.JSONDecodeError:
            LOGGER.warning("Error reading file: {0}".format(path))
        except IOError:
            LOGGER.warning("Error reading file: {0}".format(path))
        except TypeError:
            LOGGER.warning("Error reading file: {0}".format(path))
        return None

    # Subclassed to iterate over items
    def map(self, options=None):
        """Trigger find of serialized sources and build objects"""
        for _, data in sphinx.util.status_iterator(
            self.paths.items(),
            bold("[AutoAPI] ") + "Mapping Data... ",
            length=len(self.paths),
            stringify_func=(lambda x: x[0]),
        ):
            by_path = {}
            for item in data:
                obj = self.create_class(item, options)
                if obj:
                    if type(obj) in IGNORED_CLASSES:
                        continue
                    obj.jinja_env = self.jinja_env
                    by_path[obj.id] = obj

            parents = set()
            children = set()
            missing_parents = {}
            for _, obj in by_path.items():
                # parent_path = None
                try:
                    if obj.memberof:
                        parent = by_path[obj.memberof]
                        if obj.type == "method":
                            methods = getattr(parent, "methods", [])
                            methods.append(obj)
                            parent.methods = methods
                        else:
                            parent.children.append(obj)
                            children.add(obj)
                        if parent not in children:
                            parents.add(parent)
                        if obj in parents:
                            parents.remove(obj)
                except KeyError:
                    missing_parents[obj.memberof] = obj
                    LOGGER.warning(f"Parent {obj.memberof} not found for : {obj.id}")

            for parent in parents:
                self.add_object(parent)

    def create_class(self, data, options=None, **kwargs):
        """Return instance of class based on Javascript data

        Data keys handled here:

            type
                Set the object class

            consts, types, vars, funcs
                Recurse into :py:meth:`create_class` to create child object
                instances

        :param data: dictionary data from godocjson output
        """
        obj_map = dict((cls.type, cls) for cls in ALL_CLASSES)
        try:
            data_type = data[ESDOC_MAP["cls_type"]]
            scope = data.get(ESDOC_MAP["scope"], None)
            if data_type == "function" and scope == "instance":
                data_type = "method"
        except KeyError:
            LOGGER.warning("Type error: %s" % data)

        obj = None
        try:
            cls = obj_map[data_type]
            obj = cls(data, jinja_env=self.jinja_env, app=self.app)
        except KeyError as err:
            LOGGER.warning(err)
            LOGGER.warning("Type not found: %s" % data)
        except TypeError as err:
            LOGGER.warning(err)
            LOGGER.warning("Type class not found: %s" % data)

        return obj


class JavaScriptPythonMapper(PythonMapperBase):

    language = "javascript"

    def __init__(self, obj, **kwargs):
        """
        Map JSON data into Python object.

        This is the standard object that will be rendered into the templates,
        so we try and keep standard naming to keep templates more re-usable.
        """

        super(JavaScriptPythonMapper, self).__init__(obj, **kwargs)
        self.name = obj.get("name")
        self.id = tuple(
            obj.get("longname", self.name)
            .replace("~", ".")
            .replace("#", ".")
            .split(".")
        )
        self.memberof = tuple(
            obj.get("memberof", "").replace("~", ".").replace("#", ".").split(".")
        )
        self.memberof = obj.get("memberof", None)
        if self.memberof:
            self.memberof = tuple(
                self.memberof.replace("~", ".").replace("#", ".").split(".")
            )

        # Second level
        self.docstring = obj.get(ESDOC_MAP["doc_string"], "")
        # self.docstring = obj.get('comment', '')

        self.imports = obj.get("imports", [])
        self.children = []
        self.parameters = self._get_params(obj)
        self.args = [p["name"] for p in self.parameters]
        self.access = obj.get("access", "public")

    def _get_params(self, obj):
        params = []
        for orig_param in obj.get("params", []):
            param = {
                "defaultvalue": None,
                "description": None,
                "name": None,
                "nullable": False,
                "optional": False,
                "type": None,
                "variable": False,
            }
            param.update(orig_param)
            if param["type"]:
                param["type"] = param["type"]["names"][0]
            params.append(param)
        return params

    @property
    def is_private(self):
        return self.access != "public"


class JavaScriptModule(JavaScriptPythonMapper):
    type = "module"
    # ref_directive = "module"
    top_level_object = True

    @property
    def item_map(self):
        item_map = defaultdict(list)
        for child in self.children:
            item_map[child.type].append(child)
        return item_map


class JavaScriptClass(JavaScriptPythonMapper):
    type = "class"
    # top_level_object = True


class JavaScriptMethod(JavaScriptPythonMapper):
    type = "method"


class JavaScriptFunction(JavaScriptPythonMapper):
    type = "function"
    # ref_type = "func"


class JavaScriptData(JavaScriptPythonMapper):
    type = "data"


class JavaScriptMember(JavaScriptPythonMapper):
    type = "member"
    # ref_type = "data"
    # ref_directive = "data"


class JavaScriptAttribute(JavaScriptPythonMapper):
    type = "attribute"
    # ref_directive = "attr"


class JavaScriptTypedef(JavaScriptPythonMapper):
    type = "typedef"
    # ref_directive = "data"


class JavaScriptPackage(JavaScriptPythonMapper):
    type = "package"


class JavaScriptNamespace(JavaScriptPythonMapper):
    type = "namespace"
    # ref_directive = "ns"


class JavaScriptConstant(JavaScriptPythonMapper):
    type = "constant"
    # ref_directive = "data"


class JavaScriptEvent(JavaScriptPythonMapper):
    type = "event"


class JavaScriptExternal(JavaScriptPythonMapper):
    type = "external"


class JavaScriptFile(JavaScriptPythonMapper):
    type = "file"


class JavaScriptInterface(JavaScriptPythonMapper):
    type = "interface"


class JavaScriptMixin(JavaScriptPythonMapper):
    type = "mixin"


class JavaScriptParam(JavaScriptPythonMapper):
    type = "param"


REPRESENTED_CLASSES = [
    JavaScriptFunction,
    JavaScriptMethod,
    JavaScriptClass,
    JavaScriptData,
    JavaScriptAttribute,
    JavaScriptMember,
    JavaScriptModule,
]

IGNORED_CLASSES = [
    JavaScriptPackage,
    JavaScriptParam,
    JavaScriptTypedef,
    JavaScriptEvent,
    JavaScriptNamespace,
    JavaScriptConstant,
    JavaScriptExternal,
    JavaScriptFile,
    JavaScriptInterface,
    JavaScriptMixin,
]

ALL_CLASSES = REPRESENTED_CLASSES + IGNORED_CLASSES
