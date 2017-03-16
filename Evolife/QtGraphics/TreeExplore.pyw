##############################################################################
# EVOLIFE  www.dessalles.fr/Evolife                    Jean-Louis Dessalles  #
#            Telecom ParisTech  2014                       www.dessalles.fr  #
##############################################################################


##############################################################################
#  Tree configuration editor                                                 #
##############################################################################
""" (Parameter, value) pairs can be set in a convenient way using this
	configuration editor. The editor reads a Tree structure (stored in
	a XML file). Users change values by clicking on parameter name.
	Text displayed at the bottom of the window explains the role of each parameter
"""

import PyQt4	# graphics
from PyQt4.QtCore import *
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QApplication, QColor, QMessageBox
from PyQt4.QtGui import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTreeWidgetItemIterator
from PyQt4.QtGui import QTextEdit, QTextBrowser, QFileDialog, QIcon
import sys
import re   # regular expressions
import os
import xml.dom.minidom  # for XML I/O
from  xml.parsers.expat import ExpatError
import webbrowser   # is user wants to export tree structure to html 

sys.path.append('..')
sys.path.append('../..')
sys.path.append('../../..')

import Evolife.Scenarii.Parameters as EvolParam

#	compatibility with python 2
if sys.version_info >= (3,0):	
	QString = lambda x: x
	str_ = lambda x: x
	def QStringList(s=None):
		if s: return [s]
		return []
else:
	str_ = lambda S: unicode(S, encoding='latin_1')		# to fix problems with accents 


DefaultTreeFileName = 'EvolifeConfigTree.xml'   # Where parameters are hierarchically described
DefaultCfgFileName = 'Evolife.evo'  # where parameter values are stored
DefaultTtitle = 'Configuration editor (starter)'

	
class ConfEditor(QWidget):
	" Containing window "
	def __init__(self, WTitle="Configuration editor", TreeFileName=DefaultTreeFileName):
		QWidget.__init__(self)
		self.setWindowTitle(WTitle)	

		self.setGeometry(150, 100, 400, 700)
		self.GlobalFrame = QVBoxLayout(self)
		self.ButtonFrame = QHBoxLayout()
		self.GlobalFrame.addLayout(self.ButtonFrame)
		self.TreeEditor = WTree(self, TreeFileName)
		self.GlobalFrame.addWidget(self.TreeEditor, stretch=2)
		self.LoadButton = QPushButton('&Load')
		self.ButtonFrame.addWidget(self.LoadButton)
		self.LoadButton.clicked.connect(self.TreeEditor.LoadConfig)
		self.SaveButton = QPushButton('&Save')
		self.ButtonFrame.addWidget(self.SaveButton)
		self.SaveButton.clicked.connect(self.TreeEditor.SaveConfig)
		self.RunButton = QPushButton('&Run')
		self.ButtonFrame.addWidget(self.RunButton)
		self.RunButton.clicked.connect(self.TreeEditor.Run)
		self.HtmlButton = QPushButton('&Html')
		self.ButtonFrame.addWidget(self.HtmlButton)
		self.HtmlButton.clicked.connect(self.TreeEditor.ExportToHtml)
		self.QuitButton = QPushButton('&Quit')
		self.ButtonFrame.addWidget(self.QuitButton)
		self.QuitButton.clicked.connect(self.close)		
		#self.TextZone = QTextEdit()
		self.TextZone = QTextBrowser()
		self.GlobalFrame.addStretch(0)
		self.GlobalFrame.addWidget(self.TextZone, stretch=1)

	def closeEvent(self, event):
		if self.TreeEditor.confirmExit():
			event.accept()
		else:
			event.ignore()		

	def keyPressEvent(self, e):
		if e.key() in [Qt.Key_Escape]:
			self.close()		 
		#print e.key()
		#self.TreeEditor.keyPressEvent(e)
		QWidget.keyPressEvent(self, e)
	
		
class WTree(QTreeWidget):
	" A tree that we can explore and edit "
	def __init__(self, parent=None, TreeFileName=DefaultTreeFileName):
		QTreeWidget.__init__(self, parent)
		self.parent = parent
		self.setGeometry(0,0, self.parent.width(), self.parent.height())
		self.setColumnCount(2)
		self.setColumnWidth(0,270)
		#self.header().setStretchLastSection(False)
		#self.resizeColumnToContents(1)
		headerTitles = QStringList()
		headerTitles.append(QString("Parameter"))
		headerTitles.append(QString("Value"))
		self.setHeaderLabels(headerTitles)
		self.setEditTriggers(QTreeWidget.DoubleClicked|QTreeWidget.EditKeyPressed)
		self.rootItems = []
		self.currentItemChanged.connect(self.visit)
		self.itemDoubleClicked.connect(self.edit_)
		self.editing = None
		self.expandAll()
		self.ScenarioName = ''
		self.NodeDescriptions = dict()  # textual parameter descriptions
		self.ParamScenario = dict()  # name of corresponding scenario for parameters
		self.changed = False
		self.ApplicationPath = ''
		self.TreeFileName = TreeFileName
		self.RunCfgFileName = DefaultCfgFileName
		self.load()
		self.parent.setWindowTitle(self.NodeValue('Title').replace('_',' ') + ' ' + DefaultTtitle)
		

	def visit(self, New, Old):
		" this function is executed when a new node becomes selected "
		#print 'Now in %s' % New.text(0),
		if self.editing is not None and self.editing != New:
			#self.closePersistentEditor(self.editing,1)
			self.editing = None
		if New is not None and str(New.text(0)) in self.NodeDescriptions:
			# the textual description is displayed in the text zone (in blue)
			NewDescription = '<p style="color: blue; font-family: courier">%s</p>' % self.NodeDescriptions[str(New.text(0))][2].strip()
			self.parent.TextZone.setHtml(QString(NewDescription))
		if Old and str(Old.text(0)) in ['ScenarioName', 'RunConfigFile']:
			# scenario name of Run cfg file name may have been edited
			if self.NodeValue('ScenarioName'):	self.ScenarioName = str(self.NodeValue('ScenarioName'))
			if self.NodeValue('RunConfigFile'):	self.RunCfgFileName = str(self.NodeValue('RunConfigFile'))
			self.highlightRelevantParameters()
			
	def edit_(self, ClickedItem, Col):
		" allows to edit the value of a node "
		self.editing = self.currentItem()
		#self.openPersistentEditor(self.editing,1)
		self.changed = True
		self.editItem(self.editing,1)
		
	def findNode(self, NodeName):
		" finds a node in the tree "
		NodeIterator = QTreeWidgetItemIterator(self)
		Node = NodeIterator.value()
		while Node:
			if Node.text(0) == NodeName:
				return Node
			NodeIterator += 1
			Node = NodeIterator.value()
		return None

	def findNodesByAttribute(self, Attribute='Scenario'):
		" returns all nodes in the tree that have this attribute "
		NodeIterator = QTreeWidgetItemIterator(self)
		Node = NodeIterator.value()
		# Found = dict()	# doesn't work anymore in python 3 !
		Found = []
		while Node:
			if str(Node.text(0)) in self.ParamScenario:
				Found.append((Node, self.ParamScenario[str(Node.text(0))]))
			NodeIterator += 1
			Node = NodeIterator.value()
		return Found

	def NodeValue(self, NodeName):
		" returns the value attached to a node name "
		Node = self.findNode(NodeName)
		if Node and str(Node.text(1)):	return str(Node.text(1))
		return ''
		
		
	def load(self):
		" Loads parameter definitions and documentation from xml file "

		# First, retrieve parameter definitions from XML file
		NodeDescriptionList = []
		try:
			Parameters = xml.dom.minidom.parse(self.TreeFileName).getElementsByTagName('Parameter')
		except (ExpatError, IOError):
			print('No xml description found in %s' % self.TreeFileName)
			return
		for P in Parameters:
			Name = P.getElementsByTagName('Name')[0].childNodes[0].data
			if P.getAttribute('Scenario'):
				# this parameter is stored as belonging to a scenario
				self.ParamScenario[str(Name)] = str(P.getAttribute('Scenario'))
			Description = Value = ''
			# Retrieve parameter description
			DescriptionNodes = P.getElementsByTagName('Description')
			if DescriptionNodes != [] and DescriptionNodes[0].parentNode == P:
				InfoNodes = DescriptionNodes[0].getElementsByTagName('info')
				if InfoNodes:
					Description = InfoNodes[0].childNodes[0].data
			# Retrieve parameter value
			ValueNodes = P.getElementsByTagName('Value')
			if ValueNodes != [] and ValueNodes[0].parentNode == P:
				Value = ValueNodes[0].childNodes[0].data
			# Store parameter in NodeDescriptionList
			if P.parentNode.tagName == 'Config':
				# root parameter node
				NodeDescriptionList.append((Name, 1, [Name], Description, Value))
			else:
				Parent = P.parentNode.getElementsByTagName('Name')[0].childNodes[0].data
				NodeDescriptionList.append((Name, 2, [Parent, Name], Description, Value))

		self.NodeDescriptions = dict(map(lambda x: (x[0],x[1:-1]), NodeDescriptionList))

		# Building the tree
		for NodeDescription in NodeDescriptionList:
			NodeName = NodeDescription[0]
			NodeValue = NodeDescription[4]
			if NodeDescription[1] <= 1:
				# root node
				Node = QTreeWidgetItem(None, QStringList(QString(NodeName)))
				self.addTopLevelItem(Node)
				Node.setText(1, QString(NodeValue))
				Node.setFlags(Node.flags()|Qt.ItemIsEditable)
			else:
				ParentName = NodeDescription[2][-2]
				Parent = self.findNode(ParentName)
				if Parent is not None:
					if EvolParam.isInZ(NodeName): # compatibility with the old system
						Parent.setText(1,QString(NodeName))
					else:
						Node = QTreeWidgetItem(QStringList(QString(NodeName)))
						Parent.addChild(Node)
						Node.setText(1, QString(NodeValue))				
						Node.setFlags(Node.flags()|Qt.ItemIsEditable)
				else:
					print('error: missing parent', ParentName, 'for', NodeDescription[0])
		
		# Checking Evolife Path
		ApplicationPathNode = self.findNode('ApplicationDir')
		self.ApplicationPath = self.NodeValue('ApplicationDir')
		if not self.ApplicationPath or not os.path.exists(self.ApplicationPath):
			# rescue attempt
			self.ApplicationPath = None
			for R in os.walk(os.path.abspath('.')[0:os.path.abspath('.').find('Evo')]):
				if os.path.exists(os.path.join(R[0],'Evolife','__init__.py')):
					self.ApplicationPath = os.path.join(R[0],'Evolife')
					break
			if ApplicationPathNode and self.ApplicationPath:
				# ApplicationPathNode.setText(1,QString(self.ApplicationPath))
				ApplicationPathNode.setText(1,QString(os.path.relpath(self.ApplicationPath)))
			else:	self.ApplicationPath = '.'
		self.ScenarioName = str(self.NodeValue('ScenarioName'))
		if self.NodeValue('RunConfigFile'):
			self.RunCfgFileName = self.NodeValue('RunConfigFile')
		if self.NodeValue('Icon'):
			self.parent.setWindowIcon(QIcon(os.path.join(self.ApplicationPath,self.NodeValue('Icon'))))
		self.highlightRelevantParameters()

	def highlightRelevantParameters(self):
		" Disable irrelevant parameter nodes (depending on the scenario) "
		ScenarioDependentParameters = self.findNodesByAttribute('Scenario')   # find all nodes that are known to pertain to a scenario
		for (Node, ScenarioRestriction) in ScenarioDependentParameters:
			Node.setDisabled(True)
		for (Node, ScenarioRestriction) in ScenarioDependentParameters:	# second loop, as there may be duplicates
			# if ScenarioDependentParameters[Node] == self.ScenarioName:
			# if self.ScenarioName in ScenarioDependentParameters[Node].split():
			if self.ScenarioName in ScenarioRestriction.split():
				Node.setDisabled(False)
		
	def xmlSave(self, Node, Level):
		" returns a xml definition of the node and of its children "
		Name = str(Node.text(0))	# name of the parameter
		Prefix = '\t' * Level
		if Name in self.ParamScenario:
			XmlStr = '%s<Parameter Scenario="%s">\n' % (Prefix, self.ParamScenario[Name])
		else:
			XmlStr = '%s<Parameter>\n' % Prefix
		XmlStr += '%s\t<Name>%s</Name>\n' % (Prefix, Name)
		if str(Node.text(0)) in self.NodeDescriptions:
			Description = self.NodeDescriptions[str(Node.text(0))][2].strip()
			if Description != '':
				XmlStr += '%s\t<Description><info><![CDATA[%s]]></info></Description>\n' % (Prefix, Description)
		if str(Node.text(1))!='':
			XmlStr += '%s\t<Value>%s</Value>\n' % (Prefix, str(Node.text(1)))
		for Child in range(Node.childCount()):
			XmlStr += self.xmlSave(Node.child(Child), Level+1)	  
		XmlStr += '%s</Parameter>\n' % Prefix
		return XmlStr

	def save(self):
		" Saves parameter definitions and documentation in XML form "
		XmlStr = "<Config>\n"   # Xml string to store the tree structure
		for TopNode in range(self.topLevelItemCount()):
			XmlStr += self.xmlSave(self.topLevelItem(TopNode),1)
		XmlStr += "</Config>\n"
		#CfgTreeFile = open(os.path.join(self.ApplicationPath, self.TreeFileName),'w')
		CfgTreeFile = open(self.TreeFileName,'w')
		CfgTreeFile.write(XmlStr)
		CfgTreeFile.close()

	def ExportToHtml(self):
		" Exports the tree structure (parameter definitions and documentation) to an HTML file "
		HtmlStr= "<html>\n"	 # Html string that is used to store the tree structure
		HtmlStr += '<h3><a href="http://www.dessalles.fr/Evolife">Goto Evolife documentation</a></h3>'
		NodeIterator = QTreeWidgetItemIterator(self)
		Node = NodeIterator.value()
		while Node:
			Ancestors = self.NodeAncestry(Node)
			HtmlStr += "\n\n<h%d>%s%s</h%d>\n" % (len(Ancestors), ' ==> '.join(map(lambda x: str(x.text(0)),Ancestors)),
												' --> ' * (str(Node.text(1))!='') + str(Node.text(1)),
												 len(Ancestors))
			if str(Node.text(0)) in self.NodeDescriptions:
				HtmlStr+= '<p style="color: blue; font-family: courier">%s</p>' % self.NodeDescriptions[str(Node.text(0))][2].strip()
			NodeIterator += 1
			Node = NodeIterator.value()
		HtmlStr += '\n\n<h2></h2></html>'
		HtmlTreeFileName = os.path.splitext(self.TreeFileName)[0]+ '.html'
		CfgTreeFile = open(HtmlTreeFileName,'w')
		CfgTreeFile.write(HtmlStr)
		CfgTreeFile.close()
		webbrowser.open('file:///' + os.path.abspath(HtmlTreeFileName))

	def NodeAncestry(self, Node):
		" returns the list of ancestors of a node "
		if Node is None:	return []
		return self.NodeAncestry(Node.parent())+ [Node] # nice lateral recursion


	def LoadConfig(self, e):
		" Loads parameter values from EVO file "
		# Get the name of the configuration file (where 'parameter value' pairs are stored)
		CfgFileName = self.NodeValue('ScenarioFileName')
		CfgFileName = QFileDialog.getOpenFileName(None,QString('Choose a configuration file'),
												  QString(CfgFileName), QString('(*.evo)'))
		if CfgFileName == '':   return False
		if os.path.splitext(str(CfgFileName))[1] != '.evo':	return False
		Params = EvolParam.Parameters(CfgFileName)
		#for PName in Params.ParamNames():	# processes only numerical parameters
		for PName in Params.Params:	# processes all parameters
			PNode = self.findNode(PName)
			if PNode is not None:
				PNode.setText(1,QString(str(Params.Parameter(PName))))
			elif PName.startswith('S_'):	
				# compatibility with older versions
				self.ScenarioName = PName[2:]
				SNameNode = self.findNode('ScenarioName')
				if SNameNode is not None:
					SNameNode.setText(1,QString(self.ScenarioName))
			else:
				print('Creating missing node:', PName)
				Node = QTreeWidgetItem(None, QStringList(QString(PName)))
				self.addTopLevelItem(Node)
				Node.setText(1,QString(str(Params.Parameter(PName))))
				Node.setFlags(Node.flags()|Qt.ItemIsEditable)
				self.NodeDescriptions[PName] = (1, [PName], PName)				
		# update the configuration file name node (priority over loaded node)
		FNameNode = self.findNode('ScenarioFileName')
		if FNameNode is not None:			
			FNameNode.setText(1,QString(os.path.relpath(str_(CfgFileName))))
		# get new parameter values
		# Special case for scenario name
		if 'ScenarioName' in Params.Params:
			self.ScenarioName = Params.Parameter('ScenarioName')
			SNameNode = self.findNode('ScenarioName')
			if SNameNode is not None:
				SNameNode.setText(1,QString(self.ScenarioName))
		# Update icon
		if self.NodeValue('Icon'):
			self.parent.setWindowIcon(QIcon(os.path.join(self.ApplicationPath,self.NodeValue('Icon'))))				
		self.highlightRelevantParameters()
		self.changed = False	# all parameters come from file
		return True

	def SaveConfig(self, CfgFileName):
		" Saves parameter values into EVO file "
		self.save()
		if not str(CfgFileName).endswith(self.RunCfgFileName):	# could be anything, as it is also called by a button
			CfgFileName = self.NodeValue('ScenarioFileName')
			CfgFileName = QFileDialog.getSaveFileName(None,QString('Write configuration to...'),
													  QString(CfgFileName), QString('*.evo'))
			if CfgFileName == '':   return  False   # user gives up
			self.changed = False
		NodeIterator = QTreeWidgetItemIterator(self)
		ParamValues = []
		Node = NodeIterator.value()
		while Node:
			#if not Node.isDisabled() and EvolParam.isInZ(str(Node.text(1))):
			if not Node.isDisabled() and str(Node.text(1)):
				ParamValues.append((Node.text(0),Node.text(1)))
			NodeIterator += 1
			Node = NodeIterator.value()
		#ParamValues.append(('S_%s' % self.ScenarioName, 1))
		#ParamValues.append(('S_%s' % str(self.NodeValue('ScenarioName')), 1))
		ParamValues.sort()
		CfgFile = open(CfgFileName,'w')
		CfgFile.write('\n'.join(["%s\t%s" % P for P in ParamValues]))
		CfgFile.close()
		return True

	def Run(self, e):
		" Generates an os command and executes it "
		self.SaveConfig(os.path.join(self.ApplicationPath, self.RunCfgFileName))
		Target = self.NodeValue('Target')
		if Target is not None:
			try:
				os.chdir(self.ApplicationPath)	
				os.startfile(os.path.join(self.ApplicationPath,Target))	# takes RunCfgFileName as default argument
			except AttributeError:
				os.spawnlp(os.P_NOWAIT, 'python', 'python', os.path.join(self.ApplicationPath,Target), self.RunCfgFileName)
	
	def keyPressEvent(self, e):
##		if e.key() in [Qt.Key_Escape]:
##			self.parent.close()		
		if e.key() in [Qt.Key_F2, Qt.Key_Space]:
			if self.editing is not None:
				#print "Error: already editing an item"
				pass
			else:
				self.edit_(self.currentItem(),0)
		QTreeWidget.keyPressEvent(self,e)

	def closeEvent(self, event):
		self.parent.close()
		event.ignore()
		
	def confirmExit(self):
		if self.changed:
			reply = QMessageBox.question(self, 'Exit', 'Configuration (EVO file) not saved. Quit ?',
				QString('No'), QString("Save and quit"), QString('Quit without saving'), 1, 0)
			if reply == 2:
				return True
			elif reply == 1:
				return self.SaveConfig(None)
			elif reply == 0:
				return False
		else:   return True


if __name__  == "__main__":

	if len(sys.argv) > 1 and sys.argv[-1].endswith('.xml'):
		TreeFileName = sys.argv.pop(-1)
	else:
		print('Using default configuration file')
		TreeFileName = DefaultTreeFileName
	MainApp = QApplication(sys.argv)

	WConf = ConfEditor(DefaultTtitle, TreeFileName=TreeFileName)

	WConf.show()

	MainApp.exec_()




__author__ = 'Dessalles'
