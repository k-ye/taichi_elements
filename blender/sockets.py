import bpy


# socket colors
cols = {
    'INT': (0.25, 0.25, 0.25, 1.0),
    'FLOAT': (0.5, 0.5, 0.5, 1.0),
    'VECTOR': (0.25, 0.25, 0.8, 1.0),
    'STRUCT': (0.0, 1.0, 0.0, 1.0),
    'ADD': (0.0, 0.0, 0.0, 0.25),
    'STRING': (1.0, 0.5, 0.0, 1.0),
    'COLOR': (0.8, 0.8, 0.0, 1.0)
}


# get reroute input socket
def get_socket(socket):
    node = socket.node
    for input_socket in node.inputs:
        for link in input_socket.links:
            from_node = link.from_node
            from_socket = link.from_socket
            if from_node:
                if from_node.bl_idname == 'NodeReroute':
                    from_socket = get_socket(from_socket)
                return from_socket


class ElementsBaseSocket(bpy.types.NodeSocket):
    bl_idname = 'elements_base_socket'

    split_factor = 0.5

    def get_value(self):
        if not self.is_output and len(self.links):
            from_socket = self.links[0].from_socket
            if from_socket.node.bl_idname == 'NodeReroute':
                from_socket = get_socket(from_socket)
                if from_socket is None:
                    return self.value
            if from_socket.bl_idname == self.bl_idname:
                if hasattr(from_socket, 'get_value'):
                    return from_socket.get_value()
            else:
                return self.value
        else:
            return self.value

    def draw(self, context, layout, node, text):
        if not len(self.links) or self.is_output:
            if self.text:
                row = layout.split(factor=self.split_factor)
                row.label(text=self.text)
                row.prop(self, 'value', text='')
            else:
                row = layout.split(factor=1.0)
                row.prop(self, 'value', text='')
        else:
            layout.label(text=self.text)


class ElementsIntegerSocket(ElementsBaseSocket):
    bl_idname = 'elements_integer_socket'

    value: bpy.props.IntProperty(default=0)
    text: bpy.props.StringProperty(default='Integer')

    def draw_color(self, context, node):
        return cols['INT']


class ElementsFloatSocket(ElementsBaseSocket):
    bl_idname = 'elements_float_socket'

    value: bpy.props.FloatProperty(default=0.0)
    text: bpy.props.StringProperty(default='Float')

    def draw_color(self, context, node):
        return cols['FLOAT']


class ElementsVectorSocket(ElementsBaseSocket):
    bl_idname = 'elements_vector_socket'

    value: bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), size=3)
    text: bpy.props.StringProperty(default='Float')

    def draw_color(self, context, node):
        return cols['VECTOR']


class ElementsStructSocket(ElementsBaseSocket):
    bl_idname = 'elements_struct_socket'

    text: bpy.props.StringProperty(default='Value')

    def get_value(self):
        if not self.is_output and len(self.links):
            from_socket = self.links[0].from_socket
            if from_socket.node.bl_idname == 'NodeReroute':
                from_socket = get_socket(from_socket)
            if from_socket.bl_idname == self.bl_idname:
                return from_socket.links[0].from_node.get_class()
            else:
                return None
        else:
            return None

    def draw_color(self, context, node):
        return cols['STRUCT']

    def draw(self, context, layout, node, text):
        layout.label(text=self.text)


class ElementsAddSocket(bpy.types.NodeSocket):
    bl_idname = 'elements_add_socket'

    text: bpy.props.StringProperty(default='')

    def draw_color(self, context, node):
        return cols['ADD']

    def draw(self, context, layout, node, text):
        layout.label(text=self.text)


class ElementsFolderSocket(ElementsBaseSocket):
    bl_idname = 'elements_folder_socket'

    value: bpy.props.StringProperty(subtype='DIR_PATH')
    text: bpy.props.StringProperty(default='Folder')

    split_factor = 0.35

    def draw_color(self, context, node):
        return cols['STRING']


class ElementsColorSocket(ElementsBaseSocket):
    bl_idname = 'elements_color_socket'

    value: bpy.props.FloatVectorProperty(
        subtype='COLOR', min=0.0, max=1.0, size=3, default=(0.8, 0.8, 0.8)
    )
    text: bpy.props.StringProperty(default='Float')

    def draw_color(self, context, node):
        return cols['COLOR']


socket_classes = [
    ElementsIntegerSocket,
    ElementsFloatSocket,
    ElementsVectorSocket,
    ElementsColorSocket,
    ElementsStructSocket,
    ElementsAddSocket,
    ElementsFolderSocket
]


def register():
    for socket_class in socket_classes:
        bpy.utils.register_class(socket_class)


def unregister():
    for socket_class in reversed(socket_classes):
        bpy.utils.unregister_class(socket_class)
