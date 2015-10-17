# -*- coding: utf-8 -*-

##########################################################################
#                                                                        #
#  Grapholed: a diagramming software for the Graphol language.           #
#  Copyright (C) 2015 Daniele Pantaleone <danielepantaleone@me.com>      #
#                                                                        #
#  This program is free software: you can redistribute it and/or modify  #
#  it under the terms of the GNU General Public License as published by  #
#  the Free Software Foundation, either version 3 of the License, or     #
#  (at your option) any later version.                                   #
#                                                                        #
#  This program is distributed in the hope that it will be useful,       #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
#  GNU General Public License for more details.                          #
#                                                                        #
#  You should have received a copy of the GNU General Public License     #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.  #
#                                                                        #
##########################################################################
#                                                                        #
#  Graphol is developed by members of the DASI-lab group of the          #
#  Dipartimento di Informatica e Sistemistica "A.Ruberti" at Sapienza    #
#  University of Rome: http://www.dis.uniroma1.it/~graphol/:             #
#                                                                        #
#     - Domenico Lembo <lembo@dis.uniroma1.it>                           #
#     - Marco Console <console@dis.uniroma1.it>                          #
#     - Valerio Santarelli <santarelli@dis.uniroma1.it>                  #
#     - Domenico Fabio Savo <savo@dis.uniroma1.it>                       #
#                                                                        #
##########################################################################


from grapholed.fields import SpinBox
from grapholed.functions import connect
from grapholed import __appname__ as appname, __organization__ as organization

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QDialogButtonBox, QTabWidget, QFormLayout


class PreferencesDialog(QDialog):
    """
    This class implements the 'Preferences' dialog.
    """
    def __init__(self, parent=None):
        """
        Initialize the preferences dialog.
        :param parent: the parent widget.
        """
        super().__init__(parent)

        self.settings = QSettings(organization, appname)

        ############################################### APPEARANCE TAB #################################################

        # TODO: make size dependent from DiagramScene constants
        self.sceneSizeField = SpinBox(self)
        self.sceneSizeField.setRange(2000, 1000000)
        self.sceneSizeField.setSingleStep(100)
        self.sceneSizeField.setValue(self.settings.value('scene/size', 5000, int))

        self.appearanceWidget = QWidget()
        self.appearanceLayout = QFormLayout(self.appearanceWidget)
        self.appearanceLayout.addRow('Scene size', self.sceneSizeField)

        ################################################ MAIN WIDGET ###################################################

        self.mainWidget = QTabWidget(self)
        self.mainWidget.addTab(self.appearanceWidget, QIcon(':/icons/appearance.png'), 'Appearance')

        ################################################# BUTTON BOX ###################################################

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close, Qt.Horizontal, self)

        ################################################ MAIN LAYOUT ###################################################

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.mainWidget)
        self.mainLayout.addWidget(self.buttonBox, 0, Qt.AlignRight)

        self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Preferences')

        ################################################# SIGNALS ######################################################

        connect(self.buttonBox.accepted, self.accept)
        connect(self.buttonBox.rejected, self.reject)
        connect(self.finished, self.handleFinished)

    ################################################# SIGNAL HANDLERS ##################################################

    def handleFinished(self, code):
        """
        Executed when the dialog is terminated.
        :param code: the result code.
        """
        if code == QDialog.Accepted:
            self.settings.setValue('scene/size', self.sceneSizeField.value())