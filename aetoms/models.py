"""
Atomic structure models.

"""

try:
    import ase
    import ase.io
    ase_loaded = True
except ImportError:
    ase_loaded = False

from .styles import (BallAndStickStyle, StickStyle, VanDerWaalsStyle,
                     UnitCellStyle)


__author__ = "Alexander Urban"
__email__ = "aurban@atomistic.net"
__date__ = "2021-01-23"
__version__ = "0.1"


atom_styles = {
    'bs': BallAndStickStyle(),
    'ballsticks': BallAndStickStyle(),
    's': StickStyle(),
    'sticks': StickStyle(),
    'vdw': VanDerWaalsStyle(),
    'vanderwaals': VanDerWaalsStyle(),
    'default': BallAndStickStyle()
}


def pdb(coords, types, a, b, c, alpha, beta, gamma, model=1):
    """
    Return string in the protein databank atomic structure format.

    Arguments:
      coords[i, j] (float): j-th Cartesian coordinate of the i-th atom
      types[i] (str): chemical symbol of atom i
      a, b, c (float): lenghts of the three lattice vectors
      alpha, beta, gamma (float): cell angles in degrees
      model (int): model number for multi-model files

    """
    header = ("CRYST1 {:8.3f} {:8.3f} {:8.3f} "
              "{:6.2f} {:6.2f} {:6.2f} P 1\nMODEL     {:d}\n")
    atom = ("ATOM {0:6d}   {1:2s} MOL     1     {2:7.3f} {3:7.3f} {4:7.3f} "
            "{5:5.2f}  0.00          {1:2s}\n")
    out = ""
    out += header.format(a, b, c, alpha, beta, gamma, model)
    for i, coo in enumerate(coords):
        out += atom.format(i, types[i], coo[0], coo[1], coo[2], 0.0)
    out += "ENDMOL\n"
    return out


class Model(object):

    def __init__(self, frames, show_cell=True, style='default'):
        self.frames = frames
        self._active_frame = -1
        self.representations = []
        self.add_representation(style=style)
        self.frmt = "pdb"
        self.show_cell = show_cell
        self.cell_style = UnitCellStyle()
        self.model_id = None
        self._view = None
        self._model = None

    @classmethod
    def from_ase_atoms(cls, atoms, **kwargs):
        frames = []
        if hasattr(atoms, "positions"):
            trajec = [atoms]
        else:
            trajec = atoms
        for i, frame in enumerate(trajec):
            a, b, c = frame.cell.lengths()
            alpha, beta, gamma = frame.cell.angles()
            coords = frame.positions
            types = frame.get_chemical_symbols()
            frames.append(pdb(coords, types, a, b, c, alpha, beta,
                              gamma, model=(i+1)))
        return cls(frames, **kwargs)

    @classmethod
    def from_pymatgen_structures(cls, structures, **kwargs):
        frames = []
        if hasattr(structures, "cart_coords"):
            trajec = [structures]
        else:
            trajec = structures
        for i, frame in enumerate(trajec):
            coords = frame.cart_coords
            a, b, c, alpha, beta, gamma = frame.lattice.parameters
            types = [s.symbol for s in frame.species]
            frames.append(pdb(coords, types, a, b, c, alpha, beta,
                              gamma, model=(i+1)))
        return cls(frames, **kwargs)

    @classmethod
    def from_file(cls, filename, frmt=None, **kwargs):
        if not ase_loaded:
            raise ValueError("`ase` package not found.")
        if frmt is not None and frmt not in ase.io.formats.ioformats:
            raise ValueError("File format not supported: {}".format(frmt))
        atoms = ase.io.read(filename=filename, format=frmt, index=":")
        return cls.from_ase_atoms(atoms, **kwargs)

    @property
    def num_frames(self):
        return len(self.frames)

    @property
    def active_frame(self):
        return self._active_frame

    @active_frame.setter
    def active_frame(self, frame):
        i = max(-self.num_frames, min(frame, self.num_frames-1))
        self._active_frame = i
        if self._model is not None:
            if i < 0:
                i = self.num_frames + i
            self._model.setFrame(i)

    def add_representation(self, style, selection=None):
        """
        Add a visual representaion of the atomic structure, i.e., a a
        visualization format.

        Arguments:
          style (AtomStyle or str): a visualization style
          selection (dict): an AtomSelectionSpec; if none is given, all
            atoms in the structure will be selected

        """
        sel = {'model': -1}
        if selection is not None:
            sel.update(selection)
        if style in atom_styles:
            style = atom_styles[style]
        self.representations.append((sel, style))

    def update_representation(self, style, selection=None, representation=-1):
        """
        Replace a representation with another one.

        Arguments:
          style (AtomStyle or str): a visualization style
          selection (dict): an AtomSelectionSpec; if none is given, all
            atoms in the structure will be selected
          representation (int): the ID of the representation to be replaced

        """
        if self.model_id is not None:
            sel = {'model': self.model_id}
        else:
            sel = {'model': -1}
        if selection is not None:
            sel.update(selection)
        if style in atom_styles:
            style = atom_styles[style]
        self.representations[representation] = (sel, style)
        self.update()

    def add_to_view(self, view, model_id):
        """
        Arguments:
          view (py3Dmol.view): py3Dmol view object
          model_id (int): the ID of the current model

        """
        self.model_id = model_id
        self._view = view
        data = "\n".join(self.frames)
        view.addModelsAsFrames(data, self.frmt)
        self._model = view.getModel(-1)
        for sel, style in self.representations:
            style.apply(self._model, selection=sel)
        self._model.setFrame(self.active_frame)
        if self.show_cell:
            view.addUnitCell({'model': self.model_id}, self.cell_style)

    def update(self):
        if self._model is None:
            raise ValueError(
                "Model has to be added to a view before it can be updated.")
        else:
            for sel, style in self.representations:
                style.apply(self._model, selection=sel)
        self._model.setFrame(self.active_frame)
