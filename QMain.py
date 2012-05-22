"""
Gui is based on Eli Bendersky's PyQt+matplotlib demo
"""
import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import math
import matplotlib as mpl
import matplotlib.pyplot as plot
import numpy as np

import Qharm as Qh

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Quantum harmonic oscillator')

        self.ex = Qh.Experiment()
        self.T = 0
        self.delta = 0.1

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.textbox.setText('1')
        self.on_draw()
        self.timer = self.startTimer(50)

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """ Software simulation of a quantum harmonic oscillator
        """
        QMessageBox.about(self, "About Qharm", msg.strip())
    
    def on_delta_changed(self):
        self.delta = float(self.slider.value())/100

    def state_toggle(self):
        if self.random.isChecked():
            text = unicode(self.textbox.text())
            self.ex.data = [float(s) for s in text.split()]
            self.ex.n = len(self.ex.data)
        if self.coherent.isChecked():
            self.ex.n = int(self.n.value())
        if self.squeezed.isChecked():
            self.ex.n = int(self.n.value())

        self.ex.random = self.random.isChecked()
        self.ex.coherent = self.coherent.isChecked()
        self.ex.squeezed = self.squeezed.isChecked()

    def change_n(self):
        self.ex.n = int(self.n.value())

    def prepare_to_draw(self):
        self.T = 0
        self.state_toggle()

        self.ex.m = float(self.m.text())
        self.ex.w = float(self.w.text())
        self.ex.a = float(self.a.text())
        self.ex.s = float(self.s.text())

    def parabola(self):
        self.plot = plot.plot(self.xs, self.ys, label=r'$x^2$', color='red')

    def psi2(self):
        self.plot = plot.plot(self.xs, self.zs, label=r'$\Psi^2(x, t)$', color = 'blue')

    def psi(self):
        self.plot = plot.plot(self.xs, self.zsr, self.zsi, label=r'$\Psi(x, t)$', color = 'blue')

    def draw2d(self):
        del self.axes.lines[1]
        self.psi2()

    def draw3d(self):
        del self.axes.lines[0]
        self.psi()

    def back_to_2d(self):
        self.fig.delaxes(self.axes)
        self.axes = self.fig.add_subplot(111)
        #self.axes.autoscale(False)
        self.axes.grid(True)

    def back_to_3d(self):
        self.fig.delaxes(self.axes)
        self.axes = self.fig.add_subplot(111, projection='3d')
        #self.axes.autoscale(False)
        self.axes.grid(True)

    def set2d(self):
        #self.fig.gca() # ???

        plot.xlabel('$x$')
        plot.ylabel('$U(x)$')
        plot.title(r'The curves $x^2$ and $\Psi^2(x, t)$')

        self.parabola()
        self.psi2()

        plot.legend(loc='upper right')

        self.draw = self.draw2d

    def set3d(self):
        #self.fig.gca(projection='3d')

        plot.xlabel('$x$')
        self.axes.set_ylabel('$Im(\Psi)$')
        self.axes.set_zlabel('$Re(\Psi)$')
        plot.title(r'The curve $\Psi(x, t)$')

        self.psi()

        plot.legend(loc='upper right')

        self.draw = self.draw3d

    def toggle_2d_3d(self):

        self.axes.clear()
        if (self.p3d.isChecked()):
            self.back_to_3d()
            self.set3d()
        else:
            self.back_to_2d()
            self.set2d()

    def on_draw(self):
        """ Redraws the figure
        """

        self.draw()
        
        self.canvas.draw()

    def timerEvent(self, evt):
        self.T += self.delta
        psi = [self.ex.Psi(x, self.T) for x in self.xs]

        self.zs  = [Qh.norm(x) for x in psi]
        self.zsr = [x.real for x in psi]
        self.zsi = [x.imag for x in psi]

        self.statusBar().showMessage('Time: %.2f' % self.T, 2000)
        self.on_draw()
        #self.fig.canvas.draw()

    def default(self):
        self.m.setText('1.0')
        self.w.setText('1.0')
        self.a.setText('1.0')
        self.s.setText('1.0')

    def create_main_frame(self):
        self.main_frame = QWidget()

        mpl.rcParams['legend.fontsize'] = 10

        self.fig = plot.figure()

        self.xs = [x for x in mpl.mlab.frange(-4, 4, 0.1)]
        self.ys = [0.5*x*x for x in self.xs]
        self.zs = [0 for x in self.xs]
        self.zsr = [0 for x in self.xs]
        self.zsi = [0 for x in self.xs]
         
        self.set2d()
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls
        # 
        m_label = QLabel('m (mass)')
        self.m = QLineEdit()
        self.m.setMinimumWidth(20)

        w_label = QLabel('w (freq)')
        self.w = QLineEdit()
        self.w.setMinimumWidth(20)

        a_label = QLabel('a (shift)')
        self.a = QLineEdit()
        self.a.setMinimumWidth(20)

        s_label = QLabel('s (squeeze)')
        self.s = QLineEdit()
        self.s.setMinimumWidth(20)

        self.default()

        self.textbox = QLineEdit()
        self.textbox.setMinimumWidth(200)
        
        self.draw_button = QPushButton("&Draw")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.prepare_to_draw)

        self.def_button = QPushButton("&Default")
        self.connect(self.def_button, SIGNAL('clicked()'), self.default)
        
        self.p3d = QCheckBox("2D/3D")
        self.p3d.setChecked(False)
        self.connect(self.p3d, SIGNAL('stateChanged(int)'), self.toggle_2d_3d)
        
        n_label = QLabel('n:')
        self.n = QSpinBox()
        self.n.setRange(3, 50)
        self.n.setValue(13)
        self.connect(self.n, SIGNAL('valueChanged(int)'), self.change_n)

        label = QLabel('delta: ')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(10)
        self.slider.setMaximumWidth(300)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_delta_changed)
        
        state_label = QLabel('state:')
        rand_label = QLabel('random')
        self.random = QRadioButton()
        self.connect(self.random, SIGNAL('toggled(bool)'), self.state_toggle)

        coh_label = QLabel('coherent')
        self.coherent = QRadioButton()
        self.coherent.setChecked(True)
        self.connect(self.coherent, SIGNAL('toggled(bool)'), self.state_toggle)

        squ_label = QLabel('squeezed')
        self.squeezed = QRadioButton()
        self.connect(self.squeezed, SIGNAL('toggled(bool)'), self.state_toggle)

        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        
        for w in [  m_label, self.m, w_label, self.w, 
                a_label, self.a, s_label, self.s ]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        hbox2 = QHBoxLayout()
        
        for w in [ state_label,
                   self.random, rand_label,
                   self.coherent, coh_label,  
                   self.squeezed, squ_label ]:
            hbox2.addWidget(w)
            hbox2.setAlignment(w, Qt.AlignVCenter)

        self.state = QGroupBox()
        self.state.setLayout(hbox2)

        hbox1 = QHBoxLayout()
        
        for w in [ self.state, self.p3d, n_label, self.n, 
                label, self.slider, self.draw_button, self.def_button]:
            hbox1.addWidget(w)
            hbox1.setAlignment(w, Qt.AlignVCenter)
        
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.textbox)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox3)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        
    def create_status_bar(self):
        self.status_text = QLabel("Time: "+str(self.T))
        self.statusBar().addWidget(self.status_text, 1)

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About Qharm')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
