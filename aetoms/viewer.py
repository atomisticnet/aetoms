"""
Visualize atomic structures using py3Dmol and 3Dmol.js

"""

import py3Dmol
import IPython
from ipywidgets import (Button, Layout, IntSlider, Dropdown, Output,
                        Play, IntText, BoundedIntText,
                        VBox, HBox, interactive_output, jslink)

__author__ = "Alexander Urban"
__email__ = "aurban@atomistic.net"
__date__ = "2021-01-23"
__version__ = "0.1"


class Viewer(object):

    def __init__(self, model=None, width=600, height=400):
        self.width = width
        self.height = height
        if model is not None:
            self.models = [model]
            self._active_model = 0
        else:
            self.models = []
            self._active_model = None
        self.view = None

    def __str__(self):
        return

    @property
    def num_models(self):
        return len(self.models)

    @property
    def num_frames(self):
        return self.models[self.active_model].num_frames

    @property
    def active_frame(self):
        return self.models[self.active_model].active_frame

    @property
    def active_model(self):
        return self._active_model

    @active_model.setter
    def active_model(self, model):
        if self.num_models == 0:
            self._active_model = None
        else:
            self._active_model = max(
                -self.num_models, min(model, self.num_models-1))

    def add_model(self, model):
        """
        Arguments:
          model (StructureModel): the atomic structure model

        """
        self.models.append(model)

    def _set_hoverable(self):
        """
        Set javascript function that is called when hovering over atoms.
        Only to be called after the 3Dmol view is created with `show()`
        and needs to be followed by a call to `self.view.update()`.

        """
        if self.view is None:
            return
        self.view.setHoverable(
            {}, True,
            '''function(atom, viewer, event, container) {
                 if(!atom.label) {
                   atom.label = viewer.addLabel(
                     atom.serial + " " + atom.atom,
                     {position: atom,
                      backgroundColor: 'mintcream',
                      fontColor:'black'});
                  }
                }''',
            '''function(atom, viewer) {
                 if(atom.label) {
                   viewer.removeLabel(atom.label);
                   delete atom.label;
                 }
               }'''
        )

    def show(self, **kwargs):
        """
        Display 3Dmol.js output using IPython/Jupyter notebook display.

        If called with keyword arguments, those will be passed on to
        `update()`.

        """
        self.view = py3Dmol.view(width=self.width, height=self.height)
        for i, m in enumerate(self.models):
            m.add_to_view(self.view, i)
        self.view.zoomTo()
        self._set_hoverable()
        self.view.show()
        if len(kwargs) > 0:
            self.update(**kwargs)

    def update(self, model=None, frame=None, style=None):
        if self.view is None:
            self.show()
        if model is not None:
            self.active_model = model
        if frame is not None:
            self.models[self.active_model].active_frame = frame
        if style is not None:
            self.models[self.active_model].update_representation(style)
        for m in self.models:
            m.update()
        self._set_hoverable()
        self.view.update()

    def app(self):
        self._out = Output(layout=Layout(width="{}px".format(self.width+2),
                                         height="{}px".format(self.height+2),
                                         border='1px solid black'))
        sld_frame = IntSlider(description="Frame",
                              min=0, max=self.num_frames-1,
                              step=1, value=self.active_frame,
                              layout=Layout(width="{}px".format(self.width)))
        btn_play = Play(description="Animate",
                        min=0, max=self.num_frames-1,
                        step=1, value=self.active_frame,
                        interval=200)
        btn_fwrd = Button(description="▶▶", layout=Layout(width="auto"))
        btn_revs = Button(description="◀◀", layout=Layout(width="auto"))
        drd_model = Dropdown(description="Model",
                             options=list(range(self.num_models)),
                             value=self.active_model)
        drd_style = Dropdown(description="Style",
                             options=['sticks', 'ballsticks', 'vanderwaals',
                                      'default'],
                             value='default')
        int_delay = IntText(description="Delay (ms)", value=100,
                            layout=Layout(max_width="150px"))
        int_step = BoundedIntText(description="Step", value=1,
                                  min=1, max=self.num_frames,
                                  layout=Layout(max_width="150px"))
        ui = VBox([HBox([drd_model, drd_style]),
                   self._out,
                   HBox([VBox([int_step, int_delay]),
                         VBox([sld_frame,
                               HBox([btn_revs, btn_play, btn_fwrd])],
                              layout=Layout(align_items='center'))])],
                  layout=Layout(align_items='center'))

        def frame_fwrd(btn):
            if (sld_frame.value < sld_frame.max):
                sld_frame.value += 1

        def frame_revs(btn):
            if (sld_frame.value > sld_frame.min):
                sld_frame.value -= 1

        def frame_change(model, frame, style):
            with self._out:
                self.update(model=model, frame=frame, style=style)

        btn_fwrd.on_click(frame_fwrd)
        btn_revs.on_click(frame_revs)
        jslink((btn_play, "value"), (sld_frame, "value"))
        jslink((int_delay, "value"), (btn_play, "interval"))
        jslink((int_step, "value"), (btn_play, "step"))
        interactive_output(frame_change, {'model': drd_model,
                                          'style': drd_style,
                                          'frame': sld_frame})

        IPython.display.display(ui)
