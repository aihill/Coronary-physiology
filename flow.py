from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import peakutils #If missing 'pip install peakutils'

class PrePost:
    def __init__(self, prefilename, postfilename, sample_rate, ecg_sens):
        self.pre_filename = prefilename
        self.post_filename = postfilename
        self.sample_rate = sample_rate
        self.ecg_sens = ecg_sens

    def load(self):
        self.pre_raw_time = np.loadtxt(self.pre_filename, skiprows=4, usecols=[0])
        self.pre_raw_ecg = np.loadtxt(self.pre_filename, skiprows=4, usecols=[3])
        self.pre_raw_flow = np.loadtxt(self.pre_filename, skiprows=4, usecols=[4])

        self.post_raw_time = np.loadtxt(self.post_filename, skiprows=4, usecols=[0])
        self.post_raw_ecg = np.loadtxt(self.post_filename, skiprows=4, usecols=[3])
        self.post_raw_flow = np.loadtxt(self.post_filename, skiprows=4, usecols=[4])

    def gate(self):
        self.pre_rwaves = peakutils.indexes(self.pre_raw_ecg, min_dist=self.ecg_sens)
        self.post_rwaves = peakutils.indexes(self.post_raw_ecg, min_dist=self.ecg_sens)
        self.pre_rwaves = self.pre_rwaves[1:]  # Remove 1st to prevent issues with first t wave for example looking like a peak
        self.post_rwaves = self.post_rwaves[1:]

        self.pre_gated_flow, self.post_gated_flow, self.pre_mean_flow, self.post_mean_flow = [],[],[],[]

        for wavenumber, rwave in enumerate(self.pre_rwaves[:-1]): #Remove first and last R wave
            self.pre_gated_flow.append(self.pre_raw_flow[rwave:self.pre_rwaves[wavenumber + 1]])
            shortestsegment = min([len(segment) for segment in self.pre_gated_flow])
        for time in range(shortestsegment):
            self.pre_mean_flow.append(np.mean([segment[time] for segment in self.pre_gated_flow]))

        for wavenumber, rwave in enumerate(self.post_rwaves[:-1]):  # Remove first and last R wave
            self.post_gated_flow.append(self.post_raw_flow[rwave:self.post_rwaves[wavenumber + 1]])
            shortestsegment = min([len(segment) for segment in self.post_gated_flow])
        for time in range(shortestsegment):
            self.post_mean_flow.append(np.mean([segment[time] for segment in self.post_gated_flow]))

    def init_plots(self):
        # Instantiate the plot
        pg.setConfigOptions(antialias=True)
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title="Flow")
        self.win.setWindowTitle('Flow')
        self.win.nextRow()

        # Plot flow data
        self.plot_flow_pre = self.win.addPlot(title="Pre flow", x=self.pre_raw_time, y=self.pre_raw_flow, pen='r',colspan=2)
        self.plot_flow_post = self.win.addPlot(title="Post flow", x=self.post_raw_time, y=self.post_raw_flow, pen='r',colspan=2)

        self.win.nextRow()

        # Set up sliders indicating peaks
        self.line_pre_systolic = pg.InfiniteLine(pos=0, angle=0, movable=False, pen='g')
        self.line_pre_diastolic = pg.InfiniteLine(pos=np.amax(self.pre_mean_flow), angle=0, movable=False, pen='b')
        self.line_post_systolic = pg.InfiniteLine(pos=0, angle=0, movable=False, pen='g')
        self.line_post_diastolic = pg.InfiniteLine(pos=np.amax(self.post_mean_flow), angle=0, movable=False, pen='b')
        self.plot_flow_pre.addItem(self.line_pre_systolic, ignoreBounds=True)
        self.plot_flow_pre.addItem(self.line_pre_diastolic, ignoreBounds=True)
        self.plot_flow_post.addItem(self.line_post_systolic, ignoreBounds=True)
        self.plot_flow_post.addItem(self.line_post_diastolic, ignoreBounds=True)

        # Plot ECGs with R waves detected
        self.plot_ecg_pre = self.win.addPlot(title="Pre ECG", y=self.pre_raw_ecg,colspan=2)
        self.plot_ecg_pre.plot(x=self.pre_rwaves, y=np.repeat(max(self.pre_raw_ecg), len(self.pre_rwaves)), pen=(200, 200, 200),
                        symbolBrush=(255, 0, 0),
                        symbolPen='w')

        self.plot_ecg_pre = self.win.addPlot(title="Post ECG", y=self.post_raw_ecg,colspan=2)
        self.plot_ecg_pre.plot(x=self.post_rwaves, y=np.repeat(max(self.post_raw_ecg), len(self.post_rwaves)), pen=(200, 200, 200),
                               symbolBrush=(255, 0, 0),
                               symbolPen='w')

        self.win.nextRow()

        # Set up labels
        self.label_pre = pg.LabelItem(
            text="<br><br><span style='color: lightgreen'>Vmean = %0.1f<br><span style='color: blue'>Vdiastolic = %0.1f</span><br><span style='color: yellow'>Vsystolic =</span><br><span style='color: white'>Ratio =</span>" % (np.mean(self.pre_mean_flow),np.amax(self.pre_mean_flow)),
            justify='left')

        self.label_post = pg.LabelItem(
            text="<br><br><span style='color: lightgreen'>Vmean = %0.1f<br><span style='color: blue'>Vdiastolic = %0.1f</span><br><span style='color: yellow'>Vsystolic =</span><br><span style='color: white'>Ratio =</span>" % (np.mean(self.post_mean_flow),np.amax(self.post_mean_flow)),
            justify='left')

        # Plot gated plots
        self.plot_gated_pre = self.win.addPlot(title="Pre flow gated")
        self.win.addItem(self.label_pre)

        self.plot_gated_post = self.win.addPlot(title="Post flow gated")
        self.win.addItem(self.label_post)

        for data in self.pre_gated_flow:
            self.plot_gated_pre.plot(y=data)
        self.plot_gated_pre.plot(y=self.pre_mean_flow,pen='g',width=10)

        for data in self.post_gated_flow:
            self.plot_gated_post.plot(y=data)
        self.plot_gated_post.plot(y=self.post_mean_flow,pen='g',width=10)

        # Set up sliders

        self.slider_pre_systolic = pg.InfiniteLine(pos=20, angle=90, movable=True, pen='y')
        self.slider_pre_diastolic = pg.InfiniteLine(pos=np.argmax(self.pre_mean_flow), angle=90, movable=True, pen='b')
        self.plot_gated_pre.addItem(self.slider_pre_systolic, ignoreBounds=True)
        self.plot_gated_pre.addItem(self.slider_pre_diastolic, ignoreBounds=True)

        self.slider_post_systolic = pg.InfiniteLine(pos=20, angle=90, movable=True, pen='y')
        self.slider_post_diastolic = pg.InfiniteLine(pos=np.argmax(self.post_mean_flow), angle=90, movable=True, pen='b')
        self.plot_gated_post.addItem(self.slider_post_systolic, ignoreBounds=True)
        self.plot_gated_post.addItem(self.slider_post_diastolic, ignoreBounds=True)

        self.slider_pre_systolic.sigPositionChanged.connect(self.update_pre)
        self.slider_pre_diastolic.sigPositionChanged.connect(self.update_pre)
        self.slider_post_systolic.sigPositionChanged.connect(self.update_post)
        self.slider_post_diastolic.sigPositionChanged.connect(self.update_post)

    def update_pre(self):
        systolic = self.pre_mean_flow[int(self.slider_pre_systolic.value())]
        diastolic = self.pre_mean_flow[int(self.slider_pre_diastolic.value())]
        self.line_pre_systolic.setValue(systolic)
        self.line_pre_diastolic.setValue(diastolic)

        self.label_pre.setText(
            "<br><br><span style='color: lightgreen'>Vmean = %0.1f<br><span style='color: blue'>Vdiastolic = %0.1f</span><br><span style='color: yellow'>Vsystolic = %0.1f</span><br><span style='color: white'>Ratio = %0.1f</span>" % (
                np.mean(self.pre_mean_flow),diastolic,systolic,diastolic/systolic))

    def update_post(self):
        systolic = self.post_mean_flow[int(self.slider_post_systolic.value())]
        diastolic = self.post_mean_flow[int(self.slider_post_diastolic.value())]
        self.line_post_systolic.setValue(systolic)
        self.line_post_diastolic.setValue(diastolic)

        self.label_post.setText(
            "<br><br><span style='color: lightgreen'>Vmean = %0.1f<br><span style='color: blue'>Vdiastolic = %0.1f</span><br><span style='color: yellow'>Vsystolic = %0.1f</span><br><span style='color: white'>Ratio = %0.1f</span>" % (
                np.mean(self.post_mean_flow), diastolic, systolic, diastolic / systolic))

