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
import datetime
import logging as log

htmlheader='''<html>
<head><title>pyNmonReport %s </title></head>
<body>
<table>	
''' % (datetime.datetime.now())
	
def createReport(outFiles, outPath, fname="report.html"):
	reportPath = os.path.join(outPath,fname)
	try:
		report = open(reportPath, "w")
	except:
		log.error("Could not open report file!")
		exit()
	
	# write out the html header
	report.write(htmlheader)
	
	for f in outFiles:
		report.write('''	<tr>
		<td><br /><br />
		<b><center>%s</center></b><br />
		<img src="%s" />
		</td>
	</tr>
		''' % ("".join(os.path.basename(f).split(".")[:-1]), os.path.relpath(f,outPath)))
	
	report.write('''</table>
</body>
</html>
''')
	report.close()

def createInteractiveReport(reportConfig, outPath, data=None, fname="interactiveReport.html", templateFile="interactiveReport.tpl.html"):
	if not os.path.exists(templateFile):
		log.error("Template file for interactive report went missing.. "+templateFile)
		exit()
		
	if data is None:
		log.error("createInteractiveReport was not passed any data to process.")
		exit()
	
	tplFile = open(templateFile,"r").readlines()
	
	reportPath = os.path.join(outPath,fname)
	try:
		report = open(reportPath, "w")
	except:
		log.error("Could not open report file!")
		exit()
	
	dataSources=[]
	displayCols=[]
	specialOpts=[]
	basepath=os.path.join(outPath,"csv")
	relpath="csv"
	for k in reportConfig:
		# check path relative to us running
		print k
		candidatePath=os.path.join(basepath,k[0]+".csv")
		if os.path.exists(candidatePath):
			# add path relative to where the output is
			dataSources.append(os.path.join(relpath,k[0]+".csv"))
			
			# add to display cols
			localMin=None
			localMax=None
			headings=[]
			for c in data[k[0]]:
				for i in k[1]:
					# match anything that contains a key from reportConfig
					if i.lower() in c[0].lower():
						headings.append(c[0])
						numericArray = [ float(x) for x in c[1:] ]
						if max(numericArray) > localMax or localMax == None:
							localMax = max(numericArray)
						if  min(numericArray) < localMin or localMin == None:
							localMin = min(numericArray)
			displayCols.append(headings)
			localMin = (0.0 if localMin==None else localMin)
			localMax = (0.0 if localMax==None else localMax)
			specialOpts.append(('valueRange', [str(0.0), str(localMax*1.05)]))
			
			# get min/max of columns
			#for h in headings:
			#	print max(data[k[0]][h])
	
	for l in tplFile:
		if "[__plots__]" in l:
			line = ""
			for i in range(len(dataSources)):
				line += '<div id="plot' + str(i) + '"  style="width:1000px; height:300px;"></div> </ br> \n'
		elif "[__dataSources__]" in l:
			line = ""
			for s in dataSources:
				if line == "":
					line += '"'+s+'"'
				else:
					line += ',\n"'+s+'"'
		elif "[__specialOpts__]" in l:
			line = ""
			for s,v in specialOpts:
				print s,v
				if line == "":
					line += '{' + s + ': [' + ','.join(v) + ']}'
				else:
					line += ',\n{' + s + ': [' + ','.join(v) + ']}'
		elif "[__displayCols__]" in l:
			line = ""
			for s in displayCols:
				if line == "":
					line += '["' + '","'.join(s) + '"]'
				else:
					line += ',\n["' + '","'.join(s) + '"]'
		else:
			line = l
					
		report.write(line)
		
	report.close()