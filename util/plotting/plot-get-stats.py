from optparse import OptionParser
import plotly
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *
import os

this_directory = os.path.dirname(os.path.realpath(__file__)) + "/"

import sys
sys.path.insert(0,os.path.join(this_directory,"..","job_launching"))
import common

import numpy as np  # (*) numpy for math functions and arrays
import csv


def get_csv_data(filepath):
    all_stats = {}
    apps = []
    data = {}
    with open(filepath, 'r') as data_file:
        reader = csv.reader(data_file)        # define reader object
        state = "start"
        for row in reader:                    # loop through rows in csv file
            if len(row) != 0 and row[0].startswith("----"):
                state = "find-stat"
                continue
            if state == "find-stat":
                current_stat = row[0]
                state = "find-apps"
                continue
            if state == "find-apps":
                apps = [item[:4].upper() for item in row[1:]]
                state = "process-cfgs"
                continue
            if state == "process-cfgs":
                if len(row) == 0:
                    all_stats[current_stat] = apps,data
                    apps = []
                    data = {}
                    state = "start"
                    continue
                temp = []
                for x in row[1:]:
                    try:
                        temp.append(float(x))
                    except ValueError:
                        temp.append(0)
                data[row[0]] = np.array(temp)

    return all_stats

parser = OptionParser()
parser = OptionParser()
parser.add_option("-n", "--basename", dest="basename",
                  help="Basename for plot generation",
                  default="gpgpu-sim")
parser.add_option("-c", "--csv_file", dest="csv_file",
                  help="File to parse",
                  default="")
(options, args) = parser.parse_args()
options.csv_file = common.file_option_test( options.csv_file, "", this_directory )

all_stats = get_csv_data(options.csv_file)

colors= ['#0F8C79','#BD2D28','#E3BA22']
stat_count = 0
for stat,value in all_stats.iteritems():
    traces = []
    cfg_count = 0
    apps, data = value
    for k,v in data.iteritems():
        traces.append(Bar(
            x= apps,
            y= v,
            name=k,
            marker=Marker(color=colors[cfg_count]),
            xaxis='x1',
            yaxis='y{}'.format(stat_count+1)
            )
        )
        cfg_count += 1

    data = Data(traces)
    layout = Layout(
        title=stat,
        barmode='group',
        bargroupgap=0,
        bargap=0.25,
        showlegend=True,
        yaxis=YAxis(
            title="test",
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    )
    fig = Figure(data=data, layout=layout)
    figure_name = options.basename+"--"+stat
    print "plotting: " + figure_name
    outdir = (os.path.join(this_directory,"htmls"))
    if not os.path.exists( outdir ):
        os.makedirs(outdir)
    plotly.offline.plot(fig, filename=os.path.join(outdir,figure_name + ".html"),auto_open=False)
    stat_count += 1
