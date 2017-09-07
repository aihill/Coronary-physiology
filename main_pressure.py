from pressure import Aup

filename = './data/1.rest.txt' #File location
sample_rate = 1 / 200 #Frequency of samples e.g. 200 Hz = 1/200
ecg_sens = 100 #Alter this to tweak R wave under-sensing/T wave over-sensing

pressureplot = Aup(filename=filename,sample_rate=sample_rate,ecg_sens=ecg_sens)
pressureplot.load()
pressureplot.gate()
pressureplot.init_plots()
pressureplot.app.instance().exec_()