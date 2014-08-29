import sys, string, math
from xml.dom import minidom, Node
import urllib
from pygooglechart import Chart
from pygooglechart import SimpleLineChart
from pygooglechart import XYLineChart
from pygooglechart import SparkLineChart
from pygooglechart import StackedHorizontalBarChart
from pygooglechart import StackedVerticalBarChart
from pygooglechart import GroupedHorizontalBarChart
from pygooglechart import GroupedVerticalBarChart
from pygooglechart import Axis


def getFeedData(dom):
    feeds = dom.getElementsByTagName("feed")
    for feed in feeds:
        name = feed.getAttribute("name")
        print "Found Feed %s" % (name,)
        lineGraphFeed(feed)
        barGraphFeed(feed)

    #lineGraphFeed(feeds[1])
    #barGraphFeed(feeds[1])

def barGraphFeed(feed):
    name = feed.getAttribute("name")
    observations = feed.getElementsByTagName("observation")
    print "  Feed %s has %d observations" % (name,len(observations))
    data = []
    for obs in observations:
        value = int(obs.getAttribute("value"))
        #print "   val:%s (%s)" % (value, type(value))
        data.insert(0,value/10)

    #data.reverse  # remeber the feed is reversed
    print "Max Data: %s" % max(data)

    max_y = int(math.ceil(max(data)/100.0))*100
    print "Max_y : %s" % max_y
    chart = StackedVerticalBarChart(180, 120, y_range=[0, max_y])
    chart.set_bar_width(100.0/len(observations))
    chart.set_bar_width(1.2)

    chart.add_data(data)

    lftAxisMax = max_y/100;
    print "lftAxisMax %s"%lftAxisMax
    #left_axis = range(0, lftAxisMax,(lftAxisMax/4.0))
    left_axis = []
    right_axis = []
    for i in range(0,4+1):
        kw = (i*lftAxisMax/4.0)
        left_axis.append(kw)
        right_axis.append(kw*24)

    left_axis[0] = 'kW' # remove the first label
    right_axis[0] = 'kWh/d' # remove the first label
    chart.set_axis_labels(Axis.LEFT, left_axis)
    #chart.set_axis_labels(Axis.LEFT, right_axis)
    #chart.set_axis_labels(Axis.RIGHT, right_axis)

    chart.set_axis_labels(Axis.BOTTOM, ['','','','','','-18h','','','','','','-12h','','','','','','-6h','','','','','','*'])

    chart.set_title(name)

    # facebook colors
    chart.set_title_style('7f93bc',16)
    #chart.set_colours(['7f93bc'])
    chart.set_colours(['3b5998']) #darker blue

    #Colors
    colors=False
    if (colors):
        # Set the line colour to ...
        chart.set_colours(['FFFFFF'])
        # 0 here is the axis index ? 0 works for now
        chart.set_title_style('FFFFFF',16)
        chart.set_axis_style(0,'FFFFFF')
        chart.set_axis_style(1,'FFFFFF')
        chart.fill_linear_gradient(Chart.BACKGROUND,90,'000000',0.9,'007700',0.1)


    print chart.get_url()
    chart.download('%s-bar.png'%name)

def lineGraphFeed(feed):
    name = feed.getAttribute("name")
    observations = feed.getElementsByTagName("observation")
    print "  Feed %s has %d observations" % (name,len(observations))
    data = []
    for obs in observations:
        value = int(obs.getAttribute("value"))
        #print "   val:%s (%s)" % (value, type(value))
        data.insert(0,value/10)

    #data.reverse  # remeber the feed is reversed
    print "Max Data: %s" % max(data)

    max_y = int(math.ceil(max(data)/100.0))*100
    print "Max_y : %s" % max_y
    chart = SimpleLineChart(180, 120, y_range=[0, max_y])
    chart.add_data(data)

    lftAxisMax = max_y/100;
    print "lftAxisMax %s"%lftAxisMax
    #left_axis = range(0, lftAxisMax,(lftAxisMax/4.0))
    left_axis = []
    right_axis = []
    for i in range(0,4+1):
        kw = (i*lftAxisMax/4.0)
        left_axis.append(kw)
        right_axis.append(kw*24)

    left_axis[0] = 'kW' # remove the first label
    right_axis[0] = 'kWh/d' # remove the first label
    chart.set_axis_labels(Axis.LEFT, left_axis)
    #chart.set_axis_labels(Axis.RIGHT, right_axis)

    chart.set_title(name)

    # facebook colors
    chart.set_title_style('7f93bc',16)
    #chart.set_colours(['7f93bc'])
    chart.set_colours(['3b5998']) #darker blue

    #Colors
    colors=False
    if (colors):
        # Set the line colour to ...
        chart.set_colours(['FFFFFF'])
        # 0 here is the axis index ? 0 works for now
        chart.set_title_style('FFFFFF',16)
        chart.set_axis_style(0,'FFFFFF')
        chart.set_axis_style(1,'FFFFFF')
        chart.fill_linear_gradient(Chart.BACKGROUND,90,'000000',0.9,'007700',0.1)


    print chart.get_url()
    chart.download('%s-line.png'%name)


def run(urlOrFile):
    try:
        doc = minidom.parse(urlOrFile)
    except IOError:
        doc = minidom.parse(urllib.urlopen(urlOrFile))
    getFeedData(doc)

def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print 'usage: python %s <file|url>' % sys.argv[0]
        sys.exit(-1)
    run(args[0])


if __name__ == '__main__':
    main()
