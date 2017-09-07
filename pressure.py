from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from scipy.integrate import simps
from numpy import trapz
import numpy as np
import peakutils #If missing 'pip install peakutils'
import inspect

class Aup:
    def __init__(self, filename, sample_rate, ecg_sens):
        self.ecg_sens = ecg_sens
        self.filename = filename
        self.sample_rate = sample_rate

    def load(self):
        self.raw_time = np.loadtxt(self.filename, skiprows=4, usecols=[0])
        self.raw_pa = np.loadtxt(self.filename, skiprows=4, usecols=[1])
        self.raw_pd = np.loadtxt(self.filename, skiprows=4, usecols=[2])
        self.raw_ecg = np.loadtxt(self.filename, skiprows=4, usecols=[3])

    def gate(self):
        self.rwaves = peakutils.indexes(self.raw_ecg, min_dist=self.ecg_sens)
        self.onset_pa, self.p1_pa, self.p2_pa, self.onset_pd, self.p1_pd, self.p2_pd = 10, 40, 100, 10, 40, 100 #Starting positions of sliders
        self.gated_pa, self.gated_pd, self.gated_ecg = [], [], []
        self.mean_pd, self.mean_pa, self.mean_ecg = [], [], []
        for wavenumber, rwave in enumerate(self.rwaves[0:-1]):
            self.gated_pa.append(self.raw_pa[rwave:self.rwaves[wavenumber + 1]])
            self.gated_pd.append(self.raw_pd[rwave:self.rwaves[wavenumber + 1]])
            shortestsegment = min([len(segment) for segment in self.gated_pa])
        for time in range(shortestsegment):
            self.mean_pa.append(np.mean([segment[time] for segment in self.gated_pa]))
            self.mean_pd.append(np.mean([segment[time] for segment in self.gated_pd]))

    def init_plots(self):
        # Instantiate the plot
        pg.setConfigOptions(antialias=True)
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title="AUP")
        self.win.setWindowTitle('AUP')
        self.win.nextRow()

        # Plot data
        self.p_pa = self.win.addPlot(title="PA", y=self.raw_pa, pen='r')
        self.p_pa_gated = self.win.addPlot(title="PA gated")
        for data in self.gated_pa:
            self.p_pa_gated.plot(y=data, pen='r')
        self.p_pa_averaged = self.win.addPlot(title="PA averaged", y=self.mean_pa, pen='r')
        self.region_average_pa = pg.LinearRegionItem()
        self.region_average_pa.setZValue(10)
        self.p_pa_averaged.addItem(self.region_average_pa, ignoreBounds=True)
        self.p_pa_averaged.setAutoVisible(y=True)
        self.vLine_pa = pg.InfiniteLine(pos=self.onset_pa, angle=90, movable=True)
        self.p_pa_averaged.addItem(self.vLine_pa, ignoreBounds=True)

        self.win.nextRow()

        self.p_pd = self.win.addPlot(title="PD", y=self.raw_pd, pen='y')
        self.p_pd_gated = self.win.addPlot(title="PD gated")
        self.p_pd_averaged = self.win.addPlot(title="PD averaged", y=self.mean_pd, pen='y')
        for data in self.gated_pd:
            self.p_pd_gated.plot(y=data, pen='y')
        self.region_average_pd = pg.LinearRegionItem()
        self.region_average_pd.setZValue(10)
        self.p_pd_averaged.addItem(self.region_average_pd, ignoreBounds=True)
        self.p_pd_averaged.setAutoVisible(y=True)
        self.vLine_pd = pg.InfiniteLine(pos=self.onset_pd, angle=90, movable=True)
        self.p_pd_averaged.addItem(self.vLine_pd, ignoreBounds=True)

        self.win.nextRow()

        self.p_ecg = self.win.addPlot(title="ECG", y=self.raw_ecg, pen='w')
        self.p_ecg.plot(x=self.rwaves, y=np.repeat(max(self.raw_ecg), len(self.rwaves)), pen=(200, 200, 200), symbolBrush=(255, 0, 0),
                   symbolPen='w')

        self.p_processed_pa = self.win.addPlot(title="PA segments")
        self.p_processed_pa.setAutoVisible(y=True)

        self.p_processed_pd = self.win.addPlot(title="PD segments")
        self.p_processed_pd.setAutoVisible(y=True)

        self.mean_pa = list(np.array(self.mean_pa) - np.array([min(self.mean_pa)]))
        self.mean_pd = list(np.array(self.mean_pd) - np.array([min(self.mean_pd)]))

        self.x_pa_tr = list(range(0, int(self.p1_pa) - int(self.onset_pa) + 1))
        self.x_pa_ttr_minus_tr = list(range(int(self.p1_pa) - int(self.onset_pa), int(self.p2_pa) - int(self.onset_pa) + 1))
        self.x_pa_dti = list(range(int(self.p2_pa) - int(self.onset_pa), len(self.mean_pa) - int(self.onset_pa))) + list(
            range(len(self.mean_pa) - int(self.onset_pa), len(self.mean_pa)))
        self.y_pa_tr = self.mean_pa[int(self.onset_pa):int(self.p1_pa) + 1]
        self.y_pa_ttr_minus_tr = self.mean_pa[int(self.p1_pa):int(self.p2_pa) + 1]
        self.y_pa_dti = self.mean_pa[int(self.p2_pa):] + self.mean_pa[:int(self.onset_pa)]
        self.p_seg_pa_tr = self.p_processed_pa.plot(x=self.x_pa_tr, y=self.y_pa_tr, pen='r')
        self.p_seg_pa_tti_minus_tr = self.p_processed_pa.plot(x=self.x_pa_ttr_minus_tr, y=self.y_pa_ttr_minus_tr, pen='y')
        self.p_seg_pa_dti = self.p_processed_pa.plot(x=self.x_pa_dti, y=self.y_pa_dti, pen='g')

        self.x_pd_tr = list(range(0, int(self.p1_pd) - int(self.onset_pd) + 1))
        self.x_pd_ttr_minus_tr = list(range(int(self.p1_pd) - int(self.onset_pd), int(self.p2_pd) - int(self.onset_pd) + 1))
        self.x_pd_dti = list(range(int(self.p2_pd) - int(self.onset_pd), len(self.mean_pd) - int(self.onset_pd))) + list(
            range(len(self.mean_pd) - int(self.onset_pd), len(self.mean_pd)))
        self.y_pd_tr = self.mean_pd[int(self.onset_pd):int(self.p1_pd) + 1]
        self.y_pd_ttr_minus_tr = self.mean_pd[int(self.p1_pd):int(self.p2_pd) + 1]
        self.y_pd_dti = self.mean_pd[int(self.p2_pd):] + self.mean_pd[:int(self.onset_pd)]
        self.p_seg_pd_tr = self.p_processed_pd.plot(x=self.x_pd_tr, y=self.y_pd_tr, pen='r')
        self.p_seg_pd_tti_minus_tr = self.p_processed_pd.plot(x=self.x_pd_ttr_minus_tr, y=self.y_pd_ttr_minus_tr, pen='y')
        self.p_seg_pd_dti = self.p_processed_pd.plot(x=self.x_pd_dti, y=self.y_pd_dti, pen='g')

        self.region_average_pa.setRegion([self.p1_pa, self.p2_pa])
        self.region_average_pd.setRegion([self.p1_pd, self.p2_pd])

        self.win.nextRow()

        self.label_blank = pg.LabelItem(justify='left')
        self.win.addItem(self.label_blank)

        self.label_pa = pg.LabelItem(
            text="<span style='color: white'>P1 =<br>P2 =</span><br><span style='color: red'>TR AUC =</span><br><span style='color: orange'>TTI AUC =</span><br><span style='color: green'>DTI AUC =</span>",
            justify='left')
        self.win.addItem(self.label_pa)

        self.label_pd = pg.LabelItem(
            text="<span style='color: white'>P1 =<br>P2 =</span><br><span style='color: red'>TR AUC =</span><br><span style='color: orange'>TTI AUC =</span><br><span style='color: green'>DTI AUC =</span>",
            justify='left')
        self.win.addItem(self.label_pd)

        self.region_average_pa.sigRegionChanged.connect(self.update_pa)
        self.region_average_pd.sigRegionChanged.connect(self.update_pd)

        self.vLine_pa.sigPositionChanged.connect(self.update_pa)
        self.vLine_pd.sigPositionChanged.connect(self.update_pd)

    def update_pa(self):
        self.p_processed_pa.clear()
        self.update(mean=self.mean_pa,line=self.vLine_pa,region=self.region_average_pa,p_seg_tr=self.p_seg_pa_tr,p_seg_tti_minus_tr=self.p_seg_pa_tti_minus_tr,p_set_dti=self.p_seg_pa_dti, label=self.label_pa, plot=self.p_processed_pa)

    def update_pd(self):
        self.p_processed_pd.clear()
        self.update(mean=self.mean_pd,line=self.vLine_pd,region=self.region_average_pd,p_seg_tr=self.p_seg_pd_tr,p_seg_tti_minus_tr=self.p_seg_pd_tti_minus_tr,p_set_dti=self.p_seg_pd_dti, label=self.label_pd, plot=self.p_processed_pd)

    def update(self, mean, line, region, p_seg_tr, p_seg_tti_minus_tr, p_set_dti, label, plot):
        onset = line.value()
        region.setZValue(10)
        p1, p2 = region.getRegion()

        x_tr = list(range(0, int(p1) - int(onset) + 1))
        x_ttr_minus_tr = list(range(int(p1) - int(onset), int(p2) - int(onset) + 1))
        x_dti = list(range(int(p2) - int(onset), len(mean) - int(onset))) + list(
            range(len(mean) - int(onset), len(mean)))
        y_tr = mean[int(onset):int(p1) + 1]
        y_ttr_minus_tr = mean[int(p1):int(p2) + 1]
        y_dti = mean[int(p2):] + mean[:int(onset)]

        p_seg_tr = plot.plot(x=x_tr, y=y_tr, pen='r')
        p_seg_tti_minus_tr = plot.plot(x=x_ttr_minus_tr, y=y_ttr_minus_tr, pen='y')
        p_seg_dti = plot.plot(x=x_dti, y=y_dti, pen='g')

        pressure_p1 = max(y_tr)
        pressure_p2 = max(y_ttr_minus_tr)
        simps_tr = simps(y_tr, dx=self.sample_rate)
        trapz_tr = trapz(y_tr, dx=self.sample_rate)
        simps_tti = simps(y_tr+y_ttr_minus_tr, dx=self.sample_rate)
        trapz_tti = trapz(y_tr+y_ttr_minus_tr, dx=self.sample_rate)
        simps_dti = simps(y_dti, dx=self.sample_rate)
        trapz_dti = trapz(y_dti, dx=self.sample_rate)

        label.setText(
            "<span style='color: white'>P1 = %0.1f<br>P2 = %0.1f</span><br><span style='color: red'>TR AUC = %0.1f</span><br><span style='color: orange'>TTI AUC = %0.1f</span><br><span style='color: green'>DTI AUC = %0.1f</span>" % (
                pressure_p1, pressure_p2, np.mean([simps_tr, trapz_tr]),np.mean([simps_tti, trapz_tti]),np.mean([simps_dti, trapz_dti])))

        print("\n\n\n===== {} =====\n".format("PA" if inspect.stack()[1][3] == "update_pa" else "PD"))
        print("P1: {} // P2: {}".format(pressure_p1,pressure_p2))
        print("TR AUC by Simps: {} // Trapz: {}".format(simps_tr,trapz_tr))
        print("TTI AUC by Simps: {} // Trapz: {}".format(simps_tti,trapz_tti))
        print("DTI AUC by Simps: {} // Trapz: {}".format(simps_dti,trapz_dti))