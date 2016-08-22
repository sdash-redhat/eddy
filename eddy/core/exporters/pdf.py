# -*- coding: utf-8 -*-

##########################################################################
#                                                                        #
#  Eddy: a graphical editor for the specification of Graphol ontologies  #
#  Copyright (C) 2015 Daniele Pantaleone <pantaleone@dis.uniroma1.it>    #
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
#  #####################                          #####################  #
#                                                                        #
#  Graphol is developed by members of the DASI-lab group of the          #
#  Dipartimento di Ingegneria Informatica, Automatica e Gestionale       #
#  A.Ruberti at Sapienza University of Rome: http://www.dis.uniroma1.it  #
#                                                                        #
#     - Domenico Lembo <lembo@dis.uniroma1.it>                           #
#     - Valerio Santarelli <santarelli@dis.uniroma1.it>                  #
#     - Domenico Fabio Savo <savo@dis.uniroma1.it>                       #
#     - Daniele Pantaleone <pantaleone@dis.uniroma1.it>                  #
#     - Marco Console <console@dis.uniroma1.it>                          #
#                                                                        #
##########################################################################


from PyQt5.QtCore import QSizeF
from PyQt5.QtGui import QPainter, QPageSize
from PyQt5.QtPrintSupport import QPrinter

from eddy.core.datatypes.system import File
from eddy.core.exporters.common import AbstractDiagramExporter
from eddy.core.items.common import AbstractItem
from eddy.core.functions.path import openPath


class PdfDiagramExporter(AbstractDiagramExporter):
    """
    Extends AbstractDiagramExporter with facilities to export the structure of Graphol diagrams in PDF format.
    """
    def __init__(self, diagram, session=None):
        """
        Initialize the Pdf Exporter.
        :type session: Session
        """
        super(PdfDiagramExporter, self).__init__(diagram, session)

    #############################################
    #   INTERFACE
    #################################

    def export(self, path):
        """
        Perform PDF document generation.
        :type path: str
        """
        shape = self.diagram.visibleRect(margin=20)
        if shape:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            printer.setPaperSize(QPrinter.Custom)
            printer.setPageSize(QPageSize(QSizeF(shape.width(), shape.height()), QPageSize.Point))
            painter = QPainter()
            if painter.begin(printer):
                # TURN CACHING OFF
                for item in self.diagram.items():
                    if item.isNode() or item.isEdge():
                        item.setCacheMode(AbstractItem.NoCache)
                # RENDER THE DIAGRAM IN THE PAINTER
                self.diagram.render(painter, source=shape)
                # TURN CACHING ON
                for item in self.diagram.items():
                    if item.isNode() or item.isEdge():
                        item.setCacheMode(AbstractItem.DeviceCoordinateCache)
                # COMPLETE THE EXPORT
                painter.end()
                # OPEN THE DOCUMENT
                openPath(path)

    @classmethod
    def filetype(cls):
        """
        Returns the type of the file that will be used for the export.
        :return: File
        """
        return File.Pdf