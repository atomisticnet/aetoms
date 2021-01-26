"""
Visualization styles.

"""

__author__ = "Alexander Urban"
__email__ = "aurban@atomistic.net"
__date__ = "2021-01-23"
__version__ = "0.1"


CPK = {
    'H': 'white',
    'C': 'black',
    'N': 'blue',
    'O': 'red',
    'F': 'green',
    'Cl': 'green',
    'Br': '0x8b0000',
    'I': '0x9400d3',
    'He': 'cyan',
    'Ne': 'cyan',
    'Ar': 'cyan',
    'Ce': 'cyan',
    'Kr': 'cyan',
    'P': 'orange',
    'S': 'yellow',
    'B': '0xffa07a',
    'Li': 'violet',
    'Na': 'violet',
    'K': 'violet',
    'Rb': 'violet',
    'Cs': 'violet',
    'Fr': 'violet',
    'Be': '0x2e8b57',
    'Mg': '0x2e8b57',
    'Ca': '0x2e8b57',
    'Sr': '0x2e8b57',
    'Ba': '0x2e8b57',
    'Ra': '0x2e8b57',
    'Ti': '0x808080',
    'Fe': '0xff8c00',
    'default': '0xda70d6'
}

DEFAULT_COLORS = CPK.copy()
DEFAULT_COLORS.update({
    'Li': '0x32cd32',
    'Sc': '0x6b8e23',
    'Ti': '0x48d1cc',
    'V': '0xC71585',
    'Cr': '0x87cefa',
    'Mn': '0x8b008b',
    'Co': '0x00008b',
    'Ni': 'blue',
    'Cu': '0x8b0000',
    'Zn': '0xadd8e6',
    'Pt': 'cyan',
    'Ir': 'violet'
})


class AtomStyle(object):
    def __init__(self, style, colors=DEFAULT_COLORS, **style_specs):
        """
        Arguments:
          style (str): line, cross, stick, sphere, cartoon, clicksphere
          colors (dict): element specific colors
          cell (bool): show unit cell?
          style_specs: other options for specific styles, such as sphere
            scales or bond radii.  See documentation for AtomStyleSpec

        """
        self.style = style
        self.colors = colors
        self.style_specs = style_specs

    def add_to_view(self, data, frmt, selection, view):
        view.addModel(data, frmt)
        sel = {'model': -1}
        if selection is not None:
            sel.update(selection)
        if 'default' in self.colors:
            view.setStyle(sel, {self.style: {'color': self.colors['default'],
                                             **self.style_specs}})
        else:
            view.setStyle(sel, {self.style: {**self.style_specs}})
        for species in self.colors:
            if species != 'default':
                view.setStyle({'elem': species, **sel},
                              {self.style: {'color': self.colors[species],
                                            **self.style_specs}})


class StickStyle(AtomStyle):
    def __init__(self, bond_radius=0.1, **kwargs):
        super(StickStyle, self).__init__(
            style='stick', radius=bond_radius, **kwargs)


class VanDerWaalsStyle(AtomStyle):
    def __init__(self, sphere_scale=1.0, **kwargs):
        super(VanDerWaalsStyle, self).__init__(
            style='sphere', scale=sphere_scale, **kwargs)


class BallAndStickStyle(AtomStyle):
    def __init__(self, sphere_scale=0.4, bond_radius=0.1, **kwargs):
        self.balls = AtomStyle('sphere', scale=sphere_scale, **kwargs)
        self.sticks = AtomStyle('stick', radius=bond_radius, **kwargs)

    def add_to_view(self, data, frmt, selection, view):
        self.balls.add_to_view(data, frmt, selection, view)
        self.sticks.add_to_view(data, frmt, selection, view)


class UnitCellStyle(dict):
    def __init__(self, linewidth=1.0, linecolor='black', showaxes=False,
                 showlabels=True):
        style = dict(
            box=dict(linewidth=linewidth, color=linecolor),
        )
        if not showaxes:
            style['astyle'] = {'hidden': True}
            style['bstyle'] = {'hidden': True}
            style['cstyle'] = {'hidden': True}
        if showaxes and showlabels:
            style['alabel'] = "a"
            style['blabel'] = "b"
            style['clabel'] = "c"
        super(UnitCellStyle, self).__init__(**style)
