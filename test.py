#-*- coding: utf-8 -*-
import sqlite3
import time
import datetime
import pytz
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
conn = sqlite3.connect("RainbowFarm.db")
graphArray  = []
graphArray2 = []
graphArray3 = []
graphArray4 = []
graphArray5 = []
graphArray6 = []
graphArray7 = []
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}

matplotlib.rc('font', **font)
with conn:
    cur = conn.cursor()
    daybefore = '-'+sys.argv[1] +' day'
    cur.execute("select * from eggcount where dt  >= strftime('%Y-%m-%d %H:%M:%S', datetime('now','localtime'), '"+daybefore+"')")
    # cur.execute("INSERT INTO eggcount (name, eggnum) VALUES ('TEST2', 11)")
    rows = cur.fetchall()
    for row in rows:
        if(str(row[1]).replace('u\'','') == '1-Dong'):
            startingInfo=str(row).replace(')','').replace('(','').replace('u\'','').replace("'","")
            splitInfo = startingInfo.split(',')
            graphArrayAppend = splitInfo[3]+','+splitInfo[2]
            graphArray.append(graphArrayAppend)

        if(str(row[1]).replace('u\'','') == '2-Dong'):
            startingInfo=str(row).replace(')','').replace('(','').replace('u\'','').replace("'","")
            splitInfo = startingInfo.split(',')
            graphArrayAppend = splitInfo[3]+','+splitInfo[2]
            graphArray2.append(graphArrayAppend)

        if(str(row[1]).replace('u\'','') == '3-Dong'):
            startingInfo=str(row).replace(')','').replace('(','').replace('u\'','').replace("'","")
            splitInfo = startingInfo.split(',')
            graphArrayAppend = splitInfo[3]+','+splitInfo[2]
            graphArray3.append(graphArrayAppend)
        if(str(row[1]).replace('u\'','') == '4-Dong'):
            startingInfo=str(row).replace(')','').replace('(','').replace('u\'','').replace("'","")
            splitInfo = startingInfo.split(',')
            graphArrayAppend = splitInfo[3]+','+splitInfo[2]
            graphArray4.append(graphArrayAppend)

        if(str(row[1]).replace('u\'','') == '5-Dong'):
            startingInfo=str(row).replace(')','').replace('(','').replace('u\'','').replace("'","")
            splitInfo = startingInfo.split(',')
            graphArrayAppend = splitInfo[3]+','+splitInfo[2]
            graphArray5.append(graphArrayAppend)

        if(str(row[1]).replace('u\'','') == '6-Dong'):
            startingInfo=str(row).replace(')','').replace('(','').replace('u\'','').replace("'","")
            splitInfo = startingInfo.split(',')
            graphArrayAppend = splitInfo[3]+','+splitInfo[2]
            graphArray6.append(graphArrayAppend)
        if(str(row[1]).replace('u\'','') == '7-Dong'):
            startingInfo=str(row).replace(')','').replace('(','').replace('u\'','').replace("'","")
            splitInfo = startingInfo.split(',')
            graphArrayAppend = splitInfo[3]+','+splitInfo[2]
            graphArray7.append(graphArrayAppend)
    datestamp, value = np.loadtxt(graphArray, delimiter=',', unpack=True, converters={ 0: mdates.strpdate2num(' %Y-%m-%d %H:%M:%S')})
    datestamp2, value2 = np.loadtxt(graphArray2, delimiter=',', unpack=True, converters={ 0: mdates.strpdate2num(' %Y-%m-%d %H:%M:%S')})
    datestamp3, value3 = np.loadtxt(graphArray3, delimiter=',', unpack=True, converters={ 0: mdates.strpdate2num(' %Y-%m-%d %H:%M:%S')})
    datestamp4, value4 = np.loadtxt(graphArray4, delimiter=',', unpack=True, converters={ 0: mdates.strpdate2num(' %Y-%m-%d %H:%M:%S')})
    datestamp5, value5 = np.loadtxt(graphArray5, delimiter=',', unpack=True, converters={ 0: mdates.strpdate2num(' %Y-%m-%d %H:%M:%S')})
    datestamp6, value6 = np.loadtxt(graphArray6, delimiter=',', unpack=True, converters={ 0: mdates.strpdate2num(' %Y-%m-%d %H:%M:%S')})
    datestamp7, value7 = np.loadtxt(graphArray7, delimiter=',', unpack=True, converters={ 0: mdates.strpdate2num(' %Y-%m-%d %H:%M:%S')})
    fig = plt.figure()
    rect = fig.patch
    ax1 = fig.add_subplot(1,1,1)

    seoul=pytz.timezone('Asia/Seoul')
    plt.plot_date(x=datestamp, y=value, fmt='b-',tz=seoul, label = '1-dong', linewidth=2, color='red')
    plt.plot_date(x=datestamp2, y=value2, fmt='b-', tz=seoul,label = '2-dong', linewidth=2, color='green')
    plt.plot_date(x=datestamp3, y=value3, fmt='b-', tz=seoul,label = '3-dong', linewidth=2)
    plt.plot_date(x=datestamp4, y=value4, fmt='b-', tz=seoul,label = '4-dong', linewidth=2, color='olive')
    plt.plot_date(x=datestamp5, y=value5, fmt='b-', tz=seoul,label = '5-dong', linewidth=2, color='slateblue')
    plt.plot_date(x=datestamp6, y=value6, fmt='b-', tz=seoul,label = '6-dong', linewidth=2, color='blueviolet')
    plt.plot_date(x=datestamp7, y=value7, fmt='b-', tz=seoul,label = '7-dong', linewidth=2, color='peru')
    plt.legend(bbox_to_anchor=(1.0, 1), loc=2, borderaxespad=0., prop={'size': 18})
    cur.execute("select name, max(eggnum) from eggcount  where dt  >= date('now','"+daybefore+"') group by name")
    rows2 = cur.fetchall()

    columns = ('1-dong', '2-dong', '3-dong', '4-dong', '5-dong', '6-dong', '7dong')
    rows = ['No', 'net']

    # Get some pastel shades for the colors

    # Plot bars and create text labels for the table
    cell_body = []
    eggNum = []
    cell_text = []
    for row in rows2:
        cell_body.append(row[1])
        # print row
    for idx, val in enumerate(cell_body):
        if idx<len(cell_body)-1:
            print idx, (cell_body[idx]-cell_body[idx+1])
            eggNum.append(cell_body[idx]-cell_body[idx+1])
        else:
            print idx, val
            eggNum.append(val)
    cell_text.append(cell_body)
    cell_text.append(eggNum)
    # Reverse colors and text labels to display the last value at the top.


    # Add a table at the bottom of the axes
    the_table = plt.table(cellText=cell_text,
                          rowLabels=rows,
                          colLabels=columns,
                          loc='bottom',
                          bbox=[0, -0.13, 1, 0.08])
    the_table.set_fontsize(14)
    the_table.scale(1.2,1.2)
    plt.subplots_adjust(left=0.2, bottom=0.1)
    mng = plt.get_current_fig_manager()
    # mng.window.showMaximized()
    plt.show()
    cur.execute("delete from eggcount where dt < date('now','-30 days')")
