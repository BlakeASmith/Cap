from abc import *
import re
import plugins

class ToDo(plugins.TextObject):
    @property
    def attr_checks(self):
        return {
                'text':lambda s:  self.pattern.search(s) is not None
        }

    @property
    def pattern(self):
        return re.compile('^TODO:.*$')


class MyPlug(plugins.Plugin):
    @property
    def TextObjectType(self):
        return ToDo
