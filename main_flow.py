from flow import PrePost

pre_filename = './data/2.pre.txt' #File location
post_filename = './data/2.post.txt' #File location

sample_rate = 1 / 200 #Frequency of samples e.g. 200 Hz = 1/200
ecg_sens = 100 #Alter this to tweak R wave under-sensing/T wave over-sensing

flowplot = PrePost(prefilename=pre_filename,postfilename=post_filename,sample_rate=sample_rate,ecg_sens=ecg_sens)
flowplot.load()
flowplot.gate()
flowplot.init_plots()
flowplot.app.instance().exec_()