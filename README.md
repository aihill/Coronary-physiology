# Coronary-physiology

This simple program has two components

1) A 'pressure' component, which allows semi-automated calculation of the tension time index and diastolic time index. Beats are averaged or 'ensembled' using automatic ECG segmentation (gating).

![alt text](http://www.jamesphoward.com/pressure.PNG)

2) A 'flow' component, which allows semi-automated calculation and comparison of coronary flow states, namely mean velocity, peak diastolic velocity, and peak systolic velocity. Again, beats are averaged or 'ensembled' using automatic ECG segmentation (gating).

![alt text](http://www.jamesphoward.com/flow.PNG)

Data for both components should be supplied as separate files for each flow comparison (e.g. rest and exercise, pre- versus post PCI), in the following format:

Data should be supplied as separate rest and exercise files, in the format:

```
Patient: , Study: , Session: Default, Study date: 7/14/2017, 

Time	Pa	Pd	ECG	IPV	Pv	RWave	Tm

139.890	99.250	91.000	1.958	26.285	0.500		2:19:178

139.895	97.250	90.750	1.960	27.480	0.500		2:19:179
```

Each component can be run through its respective 'main_*.py' file, where configuration options are listed.
