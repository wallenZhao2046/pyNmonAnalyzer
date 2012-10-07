#!/usr/bin/env python
'''
Copyright (c) 2012 Matthias Lee

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
import numpy as np

class pyNmonPlotter:
	# Holds final 2D arrays of each stat
	processedData = {}
	plotCols = {"DISKBUSY":["sda","xvdf"],"NET":["eth0"]}
	
	def __init__(self, processedData, outdir="./data/", overwrite=False, debug=False):
		# TODO: check input vars or "die"
		self.imgPath = os.path.join(outdir,"img")
		self.debug = debug
		self.processedData = processedData
		if not (os.path.exists(self.imgPath)):
			try:
				os.makedirs(self.imgPath)
			except:
				print "[ERROR] creating results dir:",self.imgPath
				exit()
		
	def plotStats(self, todoList):
		outFiles=[]
		if len(todoList) <= 0:
			print "Error: nothing to plot"
			exit()
		
		for stat in todoList:
			if "CPU" in stat:
				# parse NMON date/timestamps and produce datetime objects
				times = [datetime.datetime.strptime(d, "%d-%b-%Y %H:%M:%S") for d in self.processedData["CPU_ALL"][0][1:]]
				values=[]
				values.append((self.processedData["CPU_ALL"][1][1:],"usr"))
				values.append((self.processedData["CPU_ALL"][2][1:],"sys"))
				values.append((self.processedData["CPU_ALL"][3][1:],"wait"))
				
				data=(times,values)
				fname = self.plotStat(data, xlabel="Time", ylabel="CPU load (%)", title="CPU vs Time", isPrct=True, stacked=True)
				outFiles.append(fname)
				
			elif "DISKBUSY" in stat:
				# parse NMON date/timestamps and produce datetime objects
				times = [datetime.datetime.strptime(d, "%d-%b-%Y %H:%M:%S") for d in self.processedData["DISKBUSY"][0][1:]]
				
				values=[]
				for i in self.processedData["DISKBUSY"]:
					colTitle = i[:1][0]
					for col in self.plotCols["DISKBUSY"]:
						if col in colTitle:
							read = np.array([float(x) for x in i[1:]])
							values.append((read,colTitle))
				
				data=(times,values)
				fname = self.plotStat(data, xlabel="Time", ylabel="Disk Busy (%)", title="Disk Busy vs Time", yrange=[0,105])
				outFiles.append(fname)
				
			elif "MEM" in stat:
				# TODO: implement using Stacked graphs for this
				# parse NMON date/timestamps and produce datetime objects
				times = [datetime.datetime.strptime(d, "%d-%b-%Y %H:%M:%S") for d in self.processedData["CPU_ALL"][0][1:]]
				values=[]
				
				mem=np.array(self.processedData["MEM"])
				
				# used = total - free - buffers - chache
				total = np.array([float(x) for x in mem[1][1:]])
				free = np.array([float(x) for x in mem[5][1:]])
				cache = np.array([float(x) for x in mem[10][1:]])
				buffers = np.array([float(x) for x in mem[13][1:]])

				used = total - free - cache - buffers
				values.append((used,"used mem"))
				values.append((total,"total mem"))
				
				data=(times,values)
				fname = self.plotStat(data, xlabel="Time", ylabel="Memory in MB", title="Memory vs Time", isPrct=False, yrange=[0,max(total)*1.2])
				outFiles.append(fname)
				
			elif "NET" in stat:
				# parse NMON date/timestamps and produce datetime objects
				times = [datetime.datetime.strptime(d, "%d-%b-%Y %H:%M:%S") for d in self.processedData["CPU_ALL"][0][1:]]
				values=[]
				
				read=np.array([])
				write=np.array([])
				for i in self.processedData["NET"]:
					colTitle = i[:1][0]
					for iface in self.plotCols["NET"]:
						if iface in colTitle and "read" in colTitle:
							read = np.array([float(x) for x in i[1:]])
							values.append((read,colTitle))
							
						elif iface in colTitle and "write" in colTitle:
							write = np.array([float(x) for x in i[1:]])
							values.append((write,colTitle))
				
				data=(times,values)
				fname = self.plotStat(data, xlabel="Time", ylabel="Network KB/s", title="Net vs Time", yrange=[0,max(max(read),max(write))*1.2])
				outFiles.append(fname)
		return outFiles
			
		
	def plotStat(self, data, xlabel="time", ylabel="", title="title", isPrct=False, yrange=[0,105], stacked=False):
		
		# figure dimensions
		fig = plt.figure(figsize=(13,4), frameon=True)
		# risizing to hack the legend in the right location
		fig.subplots_adjust(right=.8)
		ax = fig.add_subplot(1,1,1)
		
		# retrieve timestamps and datapoints
		times, values = data 
		
		if stacked:
			# TODO: parameterize out so that it can be more versitile
			a = np.array([float(x) for x in values[0][0]])
			b = np.array([float(x) for x in values[1][0]])
			c = np.array([float(x) for x in values[2][0]])
			y = np.row_stack((a,b,c))
			y_ax = np.cumsum(y, axis=0)
			ax.fill_between(times, 0, y_ax[0,:], facecolor="green", label="usr")
			ax.fill_between(times, y_ax[0,:], y_ax[1,:], facecolor="red", label="sys")
			ax.fill_between(times, y_ax[1,:], y_ax[2,:], facecolor="blue", label="wait")
			
			# hack for getting around missing legend
			p1 = plt.Rectangle((0, 0), 1, 1, fc="g")
			p2 = plt.Rectangle((0, 0), 1, 1, fc="r")
			p3 = plt.Rectangle((0, 0), 1, 1, fc="b")
			ax.legend([p1, p2, p3],["usr","sys","wait"], fancybox=True, loc='center left', bbox_to_anchor=(1, 0.5))

		else:
			# plot
			for v,label in values:
				ax.plot_date(times, v, "-", label=label)
				
			ax.legend(fancybox=True, loc='center left', bbox_to_anchor=(1, 0.5))
		
		
		# format axis
		ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(10))
		ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%m-%d %H:%M:%S"))
		ax.xaxis.set_minor_locator(mpl.ticker.MaxNLocator(100))
		ax.autoscale_view()
		if isPrct:
			ax.set_ylim([0,105])
		else:
			ax.set_ylim(yrange)
		ax.grid(True)

		fig.autofmt_xdate()
		ax.set_ylabel(ylabel)
		ax.set_xlabel(xlabel)
		if self.debug:
			plt.show()
		else:
			outFilename = os.path.join(self.imgPath,title.replace (" ", "_")+".png")
			plt.savefig(outFilename)
			return outFilename

