#!/usr/bin/python3

about = """Your Laptop Is Now A Typewriter (YLINAT)
A text "editor" for bashing out rough drafts
Copyright 2023 Bradley Allen

Version 1.0 "showtime!"
Created for Timasomo 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/."""

# Note: This code is tab-indented, set your editor appropriately if you want to make changes.

import sys, os, configparser, random
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QAction, QActionGroup, QFont, QIcon, QKeySequence, QTextCursor
from PyQt6.QtWidgets import QApplication, QFileDialog, QFontDialog, QHBoxLayout, QMainWindow, QMessageBox, QPlainTextEdit, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
	
	def __init__(self):
		super().__init__()
		self.config = configparser.ConfigParser()
		self.config.read("ylinat.ini")
		self.setWindowTitle("Your Laptop Is Now A Typewriter")
		self.setWindowIcon(QIcon("icon.png"))
		screenSpace = QApplication.primaryScreen().availableGeometry()
		self.resize(QSize(
			self.config.getint("YLINAT", "WindowWidth", fallback=int(screenSpace.width()*0.7)),
			self.config.getint("YLINAT", "WindowHeight", fallback=int(screenSpace.height()*0.7))
		))
		self.marginSize = self.config.getint("YLINAT", "MarginSize", fallback=4)
		self._createMenuActions()
		self._createMenuBar()
		self.page = WriteOnceTextEdit(
			self.config.get("YLINAT", "FontName", fallback="Courier"),
			self.config.getint("YLINAT", "FontSize", fallback=12),
			self.config.getint("YLINAT", "FontWeight", fallback=400),
			self.config.getboolean("YLINAT", "FontItalic", fallback=False),
			self.config.get("YLINAT", "CustomStartMessage", fallback="")
		)
		centralWidget = QWidget()
		hLayout = QHBoxLayout()
		vLayout = QVBoxLayout()
		centralWidget.setLayout(hLayout)
		hLayout.addLayout(vLayout)
		vLayout.addWidget(self.page)
		self.setCentralWidget(centralWidget)
		self.activeFilePath = ""
		self.wordCountOnOpen = 0
		self.autosaveTimer = QTimer()
		self.autosaveTimer.setInterval(180000)
		self.autosaveTimer.timeout.connect(self.autosave)
		self.adjustMargins()
		self.limitLineWidth()
		self.goldfishMode()
	
	def newFile(self):
		if self.autosaveOnCloseAction.isChecked():
			self.autosave()
		self.setWindowTitle("Your Laptop Is Now A Typewriter")
		self.page.setPlainText("")
		self.activeFilePath = ""
		self.wordCountOnOpen = 0
		self.autosaveTimer.stop()
	
	def openFile(self):
		startDir = os.path.dirname(self.activeFilePath)
		if not startDir:
			startDir = self.config.get("YLINAT", "LastOpenedDirectory", fallback="")
		path, fileTypeFilter = QFileDialog.getOpenFileName(self, "Open", startDir, "Text files (*.txt);;All files (*)", "Text files (*.txt)")
		if path:
			if self.autosaveOnCloseAction.isChecked():
				self.autosave()
			self.activeFilePath = path
			with open(self.activeFilePath, "r") as file:
				contents = file.read().rstrip()	# rstrip because some text editors will add a newline at the end, which is a problem if you can't backspace.
			self.page.setPlainText(contents)
			self.page.moveCursor(QTextCursor.MoveOperation.End)
			self.setWindowTitle("YLINAT - " + os.path.basename(self.activeFilePath))
			self.wordCountOnOpen = len(contents.split())
			self.autosaveTimer.start()
	
	def saveFile(self):
		if self.activeFilePath:
			self._writeOut(self.activeFilePath)
		else:
			self.saveFileAs()
	
	def saveFileAs(self):
		startDir = os.path.dirname(self.activeFilePath)
		if not startDir:
			startDir = self.config.get("YLINAT", "LastOpenedDirectory", fallback="")
		path, fileTypeFilter = QFileDialog.getSaveFileName(self, "Save as", startDir, "Text files (*.txt);;All files (*)", "Text files (*.txt)")
		if path:
			if fileTypeFilter == "Text files (*.txt)" and path[-4:] != ".txt":
				path += ".txt"
			self.activeFilePath = path
			self._writeOut(self.activeFilePath)
			self.setWindowTitle("YLINAT - " + os.path.basename(self.activeFilePath))
			self.autosaveTimer.start()
	
	def autosave(self):
		if self.activeFilePath:
			self._writeOut(self.activeFilePath)
	
	def quitApp(self):
		self.close()
	
	def closeEvent(self, event):
		if self.autosaveOnCloseAction.isChecked():
			self.autosave()
		self._writeOutConfig()
		event.accept()
	
	def wordCount(self):
		wordCountMsg = QMessageBox()
		wordCountMsg.setWindowTitle("Word count")
		currentCount = len(self.page.toPlainText().split())
		wordCountMsg.setText("Total word count: " + str(currentCount) + "\nWords this session: " + str(currentCount - self.wordCountOnOpen))
		wordCountMsg.exec()
	
	def changeFont(self):
		font, ok = QFontDialog.getFont(self.page.font(), self)
		if ok:
			self.page.setFont(font)
		self.adjustMargins()
		self.limitLineWidth()
		self.goldfishMode()
	
	def setMarginsNone(self):
		self.marginSize = 0
		self.adjustMargins()
	
	def setMarginsSmall(self):
		self.marginSize = 2
		self.adjustMargins()
	
	def setMarginsMedium(self):
		self.marginSize = 4
		self.adjustMargins()
	
	def setMarginsLarge(self):
		self.marginSize = 6
		self.adjustMargins()
	
	def adjustMargins(self):
		if self.marginSize:
			self.page.document().setDocumentMargin(self.page.fontMetrics().averageCharWidth() * self.marginSize)
		else:
			self.page.document().setDocumentMargin(4)	# default small value, used for "none"
		self.page.hide()
		self.page.show()	# hackish, but just calling update() or repaint() leaves a ghost behind
	
	def limitLineWidth(self):
		if self.limitLineWidthAction.isChecked():
			self.page.setMaximumWidth(int(self.page.fontMetrics().averageCharWidth() * 80))
		else:
			self.page.setMaximumWidth(16777215)	# default max
		self.page.verticalScrollBar().setValue(self.page.verticalScrollBar().maximum() - self.page.verticalScrollBar().singleStep())
	
	def goldfishMode(self):
		if self.goldfishModeAction.isChecked():
			self.page.setMaximumHeight(int(self.page.fontMetrics().height() * 3.5))
		else:
			self.page.setMaximumHeight(16777215)	# default max
		self.page.verticalScrollBar().setValue(self.page.verticalScrollBar().maximum() - self.page.verticalScrollBar().singleStep()) 
	
	def aboutApp(self):
		QMessageBox.about(self, "About YLINAT", about)
	
	def _writeOut(self, path):
		contents = self.page.toPlainText()
		with open(path, "w") as file:
			file.write(contents)
	
	def _writeOutConfig(self):
		if "YLINAT" not in self.config:
			self.config["YLINAT"] = {}
		self.config["YLINAT"]["Autosave"] = str(self.autosaveOnAction.isChecked())
		self.config["YLINAT"]["AutosaveOnClose"] = str(self.autosaveOnCloseAction.isChecked())
		self.config["YLINAT"]["FontItalic"] = str(self.page.font().italic())
		self.config["YLINAT"]["FontName"] = self.page.font().family()
		self.config["YLINAT"]["FontSize"] = str(self.page.font().pointSize())
		self.config["YLINAT"]["FontWeight"] = str(self.page.font().weight())
		self.config["YLINAT"]["GoldfishMode"] = str(self.goldfishModeAction.isChecked())
		self.config["YLINAT"]["LastOpenedDirectory"] = os.path.dirname(self.activeFilePath)
		self.config["YLINAT"]["LimitLineWidth"] = str(self.limitLineWidthAction.isChecked())
		self.config["YLINAT"]["MarginSize"] = str(self.marginSize)
		self.config["YLINAT"]["WindowHeight"] = str(self.size().height())
		self.config["YLINAT"]["WindowWidth"] = str(self.size().width())
		with open("ylinat.ini", "w") as configfile:
			self.config.write(configfile)
	
	def _createMenuActions(self):
		self.newFileAction = QAction("&New", self)
		self.newFileAction.setShortcut("Ctrl+N")
		self.newFileAction.triggered.connect(self.newFile)
		self.openFileAction = QAction("&Open", self)
		self.openFileAction.setShortcut("Ctrl+O")
		self.openFileAction.triggered.connect(self.openFile)
		self.saveFileAction = QAction("&Save", self)
		self.saveFileAction.setShortcut("Ctrl+S")
		self.saveFileAction.triggered.connect(self.saveFile)
		self.saveFileAsAction = QAction("Save &as", self)
		self.saveFileAsAction.setShortcut("Ctrl+Shift+S")
		self.saveFileAsAction.triggered.connect(self.saveFileAs)
		self.autosaveOnAction = QAction("&Every 3 minutes", self, checkable=True, checked=self.config.getboolean("YLINAT", "Autosave", fallback=True))	# these two don't have connections, their states are read directly for autosave enabled/disabled
		self.autosaveOnCloseAction = QAction("&On file close", self, checkable=True, checked=self.config.getboolean("YLINAT", "AutosaveOnClose", fallback=True))
		self.quitAppAction = QAction("&Quit", self)
		self.quitAppAction.setShortcut("Ctrl+Q")
		self.quitAppAction.triggered.connect(self.quitApp)
		self.wordCountAction = QAction("&Word count", self)
		self.wordCountAction.triggered.connect(self.wordCount)
		self.changeFontAction = QAction("&Font", self)
		self.changeFontAction.triggered.connect(self.changeFont)
		marginsGroup = QActionGroup(self)
		self.changeMarginsNoneAction = QAction("&None", self, checkable=True)
		self.changeMarginsNoneAction.triggered.connect(self.setMarginsNone)
		marginsGroup.addAction(self.changeMarginsNoneAction)
		self.changeMarginsSmallAction = QAction("&Small", self, checkable=True)
		self.changeMarginsSmallAction.triggered.connect(self.setMarginsSmall)
		marginsGroup.addAction(self.changeMarginsSmallAction)
		self.changeMarginsMediumAction = QAction("&Medium", self, checkable=True)
		self.changeMarginsMediumAction.triggered.connect(self.setMarginsMedium)
		marginsGroup.addAction(self.changeMarginsMediumAction)
		self.changeMarginsLargeAction = QAction("&Large", self, checkable=True)
		self.changeMarginsLargeAction.triggered.connect(self.setMarginsLarge)
		marginsGroup.addAction(self.changeMarginsLargeAction)
		if self.marginSize == 0:
			self.changeMarginsNoneAction.setChecked(True)
		elif self.marginSize == 2:
			self.changeMarginsSmallAction.setChecked(True)
		elif self.marginSize == 4:
			self.changeMarginsMediumAction.setChecked(True)
		elif self.marginSize == 6:
			self.changeMarginsLargeAction.setChecked(True)
		self.limitLineWidthAction = QAction("&Limit line width", self, checkable=True, checked=self.config.getboolean("YLINAT", "LimitLineWidth", fallback=True))
		self.limitLineWidthAction.triggered.connect(self.limitLineWidth)
		self.goldfishModeAction = QAction("&Goldfish mode", self, checkable=True, checked=self.config.getboolean("YLINAT", "GoldfishMode", fallback=False))
		self.goldfishModeAction.triggered.connect(self.goldfishMode)
		self.aboutAppAction = QAction("&About", self)
		self.aboutAppAction.triggered.connect(self.aboutApp)
	
	def _createMenuBar(self):
		menuBar = self.menuBar()
		fileMenu = menuBar.addMenu("&File")
		fileMenu.addAction(self.newFileAction)
		fileMenu.addAction(self.openFileAction)
		fileMenu.addAction(self.saveFileAction)
		fileMenu.addAction(self.saveFileAsAction)
		autosaveMenu = fileMenu.addMenu("A&utosave file")
		autosaveMenu.addAction(self.autosaveOnAction)
		autosaveMenu.addAction(self.autosaveOnCloseAction)
		fileMenu.addSeparator()
		fileMenu.addAction(self.quitAppAction)
		editMenu = menuBar.addMenu("&Edit")	# just for giggles
		editMenu.setDisabled(True)
		toolsMenu = menuBar.addMenu("&Tools")
		toolsMenu.addAction(self.wordCountAction)
		optionsMenu = menuBar.addMenu("&Options")
		optionsMenu.addAction(self.changeFontAction)
		marginsMenu = optionsMenu.addMenu("Display &margins")
		marginsMenu.addAction(self.changeMarginsNoneAction)
		marginsMenu.addAction(self.changeMarginsSmallAction)
		marginsMenu.addAction(self.changeMarginsMediumAction)
		marginsMenu.addAction(self.changeMarginsLargeAction)
		optionsMenu.addSeparator()
		optionsMenu.addAction(self.limitLineWidthAction)
		optionsMenu.addAction(self.goldfishModeAction)
		helpMenu = menuBar.addMenu("&Help")
		helpMenu.addAction(self.aboutAppAction)

class WriteOnceTextEdit(QPlainTextEdit):
	
	def __init__(self, fontName="Courier", fontSize=12, fontWeight=400, fontItalic=False, startText=""):
		super().__init__()
		self.setFont(QFont(fontName, fontSize, fontWeight, fontItalic))
		if startText:
			self.setPlaceholderText(startText)
		else:
			fortunes = [
				"You've got this. Just keep writing.",
				"Your inner critic has no power here.",
				"The journey of a thousand pages begins with a single keystroke.",
				"Trust your instincts, and watch your story unfold.",
				"The first draft is for you. Perfection can wait.",
				"Every word brings you one step closer to your goal.",
				"Don't look back. The magic is in moving forward.",
				"Your story is waiting to be told. Don't hold back!",
				"Embrace the blank page, and let the words flow.",
				"Today, you write without fear."
			]
			self.setPlaceholderText(random.choice(fortunes))
	
	def keyPressEvent(self, event):
		if event in [
			QKeySequence.StandardKey.Backspace,
			QKeySequence.StandardKey.Copy,
			QKeySequence.StandardKey.Cut,
			QKeySequence.StandardKey.Delete,
			QKeySequence.StandardKey.DeleteCompleteLine,
			QKeySequence.StandardKey.DeleteEndOfLine,
			QKeySequence.StandardKey.DeleteEndOfWord,
			QKeySequence.StandardKey.DeleteStartOfWord,
			QKeySequence.StandardKey.MoveToEndOfBlock,
			QKeySequence.StandardKey.MoveToEndOfLine,
			QKeySequence.StandardKey.MoveToNextChar,
			QKeySequence.StandardKey.MoveToNextLine,
			QKeySequence.StandardKey.MoveToNextPage,
			QKeySequence.StandardKey.MoveToNextWord,
			QKeySequence.StandardKey.MoveToPreviousChar,
			QKeySequence.StandardKey.MoveToPreviousLine,
			QKeySequence.StandardKey.MoveToPreviousPage,
			QKeySequence.StandardKey.MoveToPreviousWord,
			QKeySequence.StandardKey.MoveToStartOfBlock,
			QKeySequence.StandardKey.MoveToStartOfDocument,
			QKeySequence.StandardKey.MoveToStartOfLine,
			QKeySequence.StandardKey.Paste,
			QKeySequence.StandardKey.Redo,
			QKeySequence.StandardKey.Replace,
			QKeySequence.StandardKey.SelectAll,
			QKeySequence.StandardKey.SelectEndOfBlock,
			QKeySequence.StandardKey.SelectEndOfDocument,
			QKeySequence.StandardKey.SelectEndOfLine,
			QKeySequence.StandardKey.SelectNextChar,
			QKeySequence.StandardKey.SelectNextLine,
			QKeySequence.StandardKey.SelectNextPage,
			QKeySequence.StandardKey.SelectNextWord,
			QKeySequence.StandardKey.SelectPreviousChar,
			QKeySequence.StandardKey.SelectPreviousLine,
			QKeySequence.StandardKey.SelectPreviousPage,
			QKeySequence.StandardKey.SelectPreviousWord,
			QKeySequence.StandardKey.SelectStartOfBlock,
			QKeySequence.StandardKey.SelectStartOfDocument,
			QKeySequence.StandardKey.SelectStartOfLine,
			QKeySequence.StandardKey.Undo
		]:
			pass
		elif event.key() in [
			Qt.Key.Key_Backspace,
			Qt.Key.Key_Insert,
			Qt.Key.Key_Delete,
			Qt.Key.Key_Home,
			Qt.Key.Key_End,
			Qt.Key.Key_Left,
			Qt.Key.Key_Up,
			Qt.Key.Key_Right,
			Qt.Key.Key_Down,
			Qt.Key.Key_PageUp,
			Qt.Key.Key_PageDown
		]:
			pass
		else:
			super().keyPressEvent(event)
	
	def mousePressEvent(self, event):
		pass
	def mouseReleaseEvent(self, event):
		pass
	def mouseDoubleClickEvent(self, event):
		pass
	def mouseMoveEvent(self, event):
		pass
	def contextMenuEvent(self, event):
		pass

def main():
	app = QApplication(sys.argv)	# no args are used, but here they are anyway
	window = MainWindow()
	window.show()
	exitCode = app.exec()
	sys.exit(exitCode)

if __name__ == "__main__": main()

