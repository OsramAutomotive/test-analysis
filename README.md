# DV Station Test Analysis

This program analyzes raw environmental test data for automotive lighting systems. The tests expose lighting systems to various temperature profiles while the systems are powered. Each test system is comprised of many modules (e.g. - Turn, DRL, Park, Outage, etc.) and can be ran in different modes (e.g. - Park+Turn, Turn only, DRL+Park, etc.). These various modes are excited at different voltages throughout testing. The primary function of this project is to analyze the distributions of current for each temperature/mode/voltage condition and compare them to design current limits. 


## The DV Test Station
These test stations consist of 2 power supplies, 2 DAQ systems, and 6 pc boards. The test systems are wired to the boards and currents are measured across high precision shunt resistors. Each board is used for a single module in the system. For instance, a lighting project may be set up on the boards of a DV Test Station like this: 

```
Board 1 - Low Beam
Board 2 - High Beam
Board 3 - DRL
Board 4 - Park
Board 5 - Turn
Board 6 - Outage
```

A Labview program defines the functional cycle of testing (which modules are powered and when) and outputs raw DAQ voltage and current data of each system for each board. A single board's raw data looks like this: 
```
| Date     | Time       | Amb Temp TC1 | TC2    | TC3    | TC4    | VSetpoint | VSense 1 | VSense 2 | Board on/off | TP1: System 82 | TP2: System 83 | TP3: System 84 | TP4: System 85 | TP5: System 86 | TP6: System 87 | TP7: System 88 | TP8: System 89 | TP9: System 90 | TP10: System 91 | TP11: System 92 | TP12: System 93 |
|----------|------------|--------------|--------|--------|--------|-----------|----------|----------|--------------|----------------|----------------|----------------|----------------|----------------|----------------|----------------|----------------|----------------|-----------------|-----------------|-----------------|
| 2/2/2017 | 4:29:32 PM | 22.955       | 23.367 | 22.785 | 22.281 | 9         | 9.009    | 9.118    | 1            | 0.49788        | 0.49691        | 0.49941        | 0.48962        | 0.4949         | 0.49386        | 0.49448        | 0.49518        | 0.49372        | 0.49802         | 0.49865         | 0.48726         |
| 2/2/2017 | 4:29:33 PM | 22.943       | 23.364 | 22.764 | 22.266 | 9         | 9.012    | 9.019    | 1            | 0.49851        | 0.49754        | 0.50004        | 0.49011        | 0.49566        | 0.49441        | 0.4949         | 0.49587        | 0.49441        | 0.49851         | 0.49927         | 0.48775         |
| 2/2/2017 | 4:29:34 PM | 22.949       | 23.37  | 22.785 | 22.284 | 9         | 9.023    | 9.071    | 1            | 0.49879        | 0.49761        | 0.50011        | 0.49018        | 0.49573        | 0.49462        | 0.49511        | 0.49615        | 0.49455        | 0.49872         | 0.49927         | 0.48775         |
| 2/2/2017 | 4:29:35 PM | 22.943       | 23.391 | 22.776 | 22.272 | 9         | 9.015    | 9.122    | 1            | 0.49886        | 0.49775        | 0.50025        | 0.49025        | 0.49594        | 0.49469        | 0.49525        | 0.49608        | 0.49469        | 0.49879         | 0.4992          | 0.48789         |
| 2/2/2017 | 4:29:41 PM | 22.949       | 23.431 | 22.782 | 22.639 | 9         | 0.003    | 0.003    | 0            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF             | OFF             | OFF             |
| 2/2/2017 | 4:29:42 PM | 22.965       | 23.456 | 22.764 | 22.629 | 9         | 0.003    | 0.003    | 0            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF             | OFF             | OFF             |
| 2/2/2017 | 4:29:43 PM | 22.961       | 23.45  | 22.767 | 22.595 | 9         | 0.003    | 0.003    | 0            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF             | OFF             | OFF             |
| 2/2/2017 | 4:29:44 PM | 22.968       | 23.465 | 22.785 | 22.614 | 9         | 0.003    | 0.003    | 0            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF            | OFF             | OFF             | OFF             |

(and so on ...)

```

## Current Limits
For each lighting project current limits are established for the various temperature/mode/voltage conditions. These limits can be used for any particular environmental test. These limits are stored in an excel file and pulled by the program into a simple dictionary. Limits are excellent for comparing the measured currents to an expected/acceptable range. They also help recognize subtle failures. 

## Analysis

The analysis consists of 3 components:
1. Temporal Plotting
2. Current Histograms
3. Summary Tables with basic statisitcs and comparison to limits 

### 1) Temporal Plotting
Outputs a set of temporal subplots:
* Functional cycle
* Temperature profile
* Current draw for each mode that is present

Here's an example: 
```
![Example of temporal plot](https://raw.githubusercontent.com/OsramAutomotive/test-analysis/master/images/example-plot.png)
```

### 2) Current Histograms
Histograms can be created to visualize the distribution of currents at different test conditions. If provided, limits are drawn as vertical dashed lines. 

Here's an example: 
```
![Example of histogram](https://raw.githubusercontent.com/OsramAutomotive/test-analysis/master/images/example-histogram.png)
```

### 3) Summary Tables
An excel file is created with the basic statistics for the various temperature/mode/voltage conditions for each system. A new tab is created for each test temperature the user wishes to analyze. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

E2E testing is being added to validate accuracy of analysis

```
Examples...
```


## Built With

* [Pandas](http://pandas.pydata.org/) - Data wrangling and processing
* [Matplotlib](http://matplotlib.org/) - Plotting and histograms
* [XlsWriter](http://xlsxwriter.readthedocs.io/) - Used to generate analysis tables


## Authors

* **Sam Bruno** - *Initial work* - [Osram Automotive](https://github.com/OsramAutomotive)
