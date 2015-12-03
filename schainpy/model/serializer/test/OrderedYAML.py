'''
A YAML Loader and Dumper which provide ordered dictionaries in place
of dictionaries (to keep the order of attributes as
found in the original YAML object file).

This module is modified from a submission on pyyaml.org:
http://pyyaml.org/attachment/ticket/161/use_ordered_dict.py

$Id$
'''

import yaml
import collections

class Loader(yaml.loader.Loader):
    """ YAML Loader producing OrderedDicts in place of dicts """
    
    def __init__(self, stream):
        yaml.loader.Loader.__init__(self, stream)
    
    def construct_ordered_mapping(self, node, deep=False):
        """ Replacement mapping constructor producing an OrderedDict """
        if not isinstance(node, yaml.MappingNode):
            raise yaml.constructor.ConstructorError(None, None,
                    "expected a mapping node, but found %s" % node.id,
                    node.start_mark)
        mapping = collections.OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, collections.Hashable):
                raise yaml.constructor.ConstructorError("while constructing a mapping", node.start_mark,
                        "found unhashable key", key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping
    # yaml.constructor.BaseConstructor.construct_mapping = construct_ordered_mapping
    
    def construct_mapping(self, node, deep=False):
        return self.construct_ordered_mapping(node, deep=deep)
    
    def construct_yaml_map_with_ordered_dict(self, node):
        data = collections.OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

class Dumper(yaml.dumper.Dumper):
    """ YAML Dumper producing documents from OrderedDicts """
    
    def __init__(self, stream, *args, **kwargs):
        yaml.dumper.Dumper.__init__(self, stream, *args, **kwargs)
    
    def represent_ordered_mapping(self, tag, mapping, flow_style=None):
        """ Replacement mapping representer for OrderedDicts """
        value = []
        node = yaml.MappingNode(tag, value, flow_style=flow_style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        if hasattr(mapping, 'items'):
            mapping = list(mapping.items())
        for item_key, item_value in mapping:
            node_key = self.represent_data(item_key)
            node_value = self.represent_data(item_value)
            if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style):
                best_style = False
            if not (isinstance(node_value, yaml.ScalarNode) and not node_value.style):
                best_style = False
            value.append((node_key, node_value))
        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node
    # yaml.representer.BaseRepresenter.represent_mapping = represent_ordered_mapping
    
    def represent_mapping(self, tag, mapping, flow_style=None):
        return self.represent_ordered_mapping(tag, mapping, flow_style=flow_style)

# Loader.add_constructor(
#         u'tag:yaml.org,2002:map',
#         Loader.construct_yaml_map_with_ordered_dict
# )
#  
# Dumper.add_representer(
#         collections.OrderedDict,
#         yaml.representer.SafeRepresenter.represent_dict
# )
