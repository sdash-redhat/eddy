# -*- coding: utf-8 -*-

##########################################################################
#                                                                        #
#  Eddy: a graphical editor for the construction of Graphol ontologies.  #
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
#  #####################                          #####################  #
#                                                                        #
#  Graphol is developed by members of the DASI-lab group of the          #
#  Dipartimento di Ingegneria Informatica, Automatica e Gestionale       #
#  A.Ruberti at Sapienza University of Rome: http://www.dis.uniroma1.it/ #
#                                                                        #
#     - Domenico Lembo <lembo@dis.uniroma1.it>                           #
#     - Valerio Santarelli <santarelli@dis.uniroma1.it>                  #
#     - Domenico Fabio Savo <savo@dis.uniroma1.it>                       #
#     - Marco Console <console@dis.uniroma1.it>                          #
#                                                                        #
##########################################################################


import sys

from math import sin, cos, radians, pi as M_PI

from PyQt5.QtCore import QPointF, QLineF, Qt
from PyQt5.QtGui import QPainter, QPen, QPolygonF, QColor, QPixmap, QPainterPath
from PyQt5.QtWidgets import QMenu

from eddy.core.datatypes import Font, DiagramMode, Item, Identity
from eddy.core.items.edges.common.base import AbstractEdge
from eddy.core.items.edges.common.label import Label


class InstanceOfEdge(AbstractEdge):
    """
    This class implements the InstanceOf edge.
    """
    item = Item.InstanceOfEdge
    name = 'instanceOf'
    xmlname = 'instance-of'

    def __init__(self, **kwargs):
        """
        Initialize the InstanceOf edge.
        """
        super().__init__(**kwargs)
        self.label = Label('instanceOf', centered=True, parent=self)

    ####################################################################################################################
    #                                                                                                                  #
    #   INTERFACE                                                                                                      #
    #                                                                                                                  #
    ####################################################################################################################

    def contextMenu(self, pos):
        """
        Returns the basic edge context menu.
        :type pos: QPointF
        :rtype: QMenu
        """
        menu = QMenu()
        scene = self.scene()
        breakpoint = self.breakpointAt(pos)
        if breakpoint is not None:
            action = scene.mainwindow.actionRemoveEdgeBreakpoint
            action.setData((self, breakpoint))
            menu.addAction(action)
        else:
            menu.addAction(scene.mainwindow.actionDelete)
        return menu

    def copy(self, scene):
        """
        Create a copy of the current edge.
        :type scene: DiagramScene
        """
        kwargs = {
            'scene': scene,
            'id': self.id,
            'source': self.source,
            'target': self.target,
            'breakpoints': self.breakpoints[:],
        }

        return self.__class__(**kwargs)

    def isValid(self, source, target):
        """
        Tells whether this edge is valid when being added between the given source and target nodes.
        :type source: AbstractNode
        :type target: AbstractNode
        :rtype: bool
        """
        if source is target:
            # Self connection is not valid.
            return False

        if source.identity not in {Identity.Individual, Identity.Link}:
            # The source of the edge must be one of Individual or Link.
            return False

        if len(source.outgoingNodes(lambda x: x.isItem(Item.InstanceOfEdge) and x is not self)) > 0:
            # The source node MUST be instanceOf at most of one construct.
            return False

        if source.identity is Identity.Individual and target.identity is not Identity.Concept:
            # If the source of the edge is an Individual it means that we are trying to construct a ClassAssertion
            # construct, and so the target of the edge MUST be an axiom identified as Concept (Atomic or General).
            # OWL 2 syntax: ClassAssertion(axiomAnnotations ClassExpression Individual)
            return False

        if source.identity is Identity.Link:

            if not target.isItem(Item.RoleNode, Item.RoleInverseNode, Item.AttributeNode):
                # If the source of the edge is a Link then the target of the edge MUST be the
                # OWL 2 equivalent of ObjectPropertyExpression and DataPropertyExpression.
                return False

            if target.isItem(Item.RoleNode, Item.RoleInverseNode):
                # If the target of the edge is a Role expression then we need to check
                # not to have Literals in input to the source node (which is a Link).
                # OWL 2 syntax: ObjectPropertyAssertion(axiomAnnotations ObjectPropertyExpression Individual Individual)
                if len(source.incomingNodes(filter_on_edges=lambda x: x.isItem(Item.InputEdge),
                                            filter_on_nodes=lambda x: x.identity is Identity.Literal)) > 0:
                    return False

            if target.isItem(Item.AttributeNode):
                # If the target of the edge is an Attribute expression then we need to check
                # not to have 2 Individuals as input to the source node (which is a link).
                # OWL 2 syntax: DataPropertyAssertion(axiomAnnotations DataPropertyExpression Individual Literal)
                if len(source.incomingNodes(filter_on_edges=lambda x: x.isItem(Item.InputEdge),
                                            filter_on_nodes=lambda x: x.identity is Identity.Individual)) > 1:
                    return False

        return True

    def updateLabelPos(self, points):
        """
        Update the label text position.
        :type points: T <= tuple | list
        """
        self.label.updatePos(points)

    ####################################################################################################################
    #                                                                                                                  #
    #   IMPORT / EXPORT                                                                                                #
    #                                                                                                                  #
    ####################################################################################################################

    @classmethod
    def fromGraphol(cls, scene, E):
        """
        Create a new item instance by parsing a Graphol document item entry.
        :type scene: DiagramScene
        :type E: QDomElement
        :rtype: AbstractEdge
        """
        points = []

        # extract all the breakpoints from the edge children
        children = E.elementsByTagName('line:point')
        for i in range(0, children.count()):
            P = children.at(i).toElement()
            point = QPointF(int(P.attribute('x')), int(P.attribute('y')))
            points.append(point)

        kwargs = {
            'scene': scene,
            'id': E.attribute('id'),
            'source': scene.node(E.attribute('source')),
            'target': scene.node(E.attribute('target')),
            'breakpoints': points[1:-1],
        }

        edge = cls(**kwargs)

        # set the anchor points only if they are inside the endpoint shape: users can modify the .graphol file manually,
        # changing anchor points coordinates, which will result in an edge floating in the scene without being bounded
        # by endpoint shapes. Not setting the anchor point will make the edge use the default one (node center point)

        path = edge.source.painterPath()
        if path.contains(edge.source.mapFromScene(points[0])):
            edge.source.setAnchor(edge, points[0])

        path = edge.target.painterPath()
        if path.contains(edge.target.mapFromScene(points[-1])):
            edge.target.setAnchor(edge, points[-1])

        # map the edge over the source and target nodes
        edge.source.addEdge(edge)
        edge.target.addEdge(edge)
        edge.updateEdge()
        return edge

    def toGraphol(self, document):
        """
        Export the current item in Graphol format.
        :type document: QDomDocument
        :rtype: QDomElement
        """
        ## ROOT ELEMENT
        edge = document.createElement('edge')
        edge.setAttribute('source', self.source.id)
        edge.setAttribute('target', self.target.id)
        edge.setAttribute('id', self.id)
        edge.setAttribute('type', self.xmlname)

        ## LINE GEOMETRY
        source = self.source.anchor(self)
        target = self.target.anchor(self)

        for p in [source] + self.breakpoints + [target]:
            point = document.createElement('line:point')
            point.setAttribute('x', p.x())
            point.setAttribute('y', p.y())
            edge.appendChild(point)

        return edge

    ####################################################################################################################
    #                                                                                                                  #
    #   GEOMETRY                                                                                                       #
    #                                                                                                                  #
    ####################################################################################################################

    def boundingRect(self):
        """
        Returns the shape bounding rect.
        :rtype: QRectF
        """
        path = QPainterPath()
        path.addPath(self.selection)
        path.addPolygon(self.head)

        for shape in self.handles.values():
            path.addEllipse(shape)
        for shape in self.anchors.values():
            path.addEllipse(shape)

        return path.controlPointRect()

    def painterPath(self):
        """
        Returns the current shape as QPainterPath (used for collision detection).
        :rtype: QPainterPath
        """
        path = QPainterPath()
        path.addPath(self.path)
        path.addPolygon(self.head)

        return path

    def shape(self):
        """
        Returns the shape of this item as a QPainterPath in local coordinates.
        :rtype: QPainterPath
        """
        path = QPainterPath()
        path.addPath(self.selection)
        path.addPolygon(self.head)

        if self.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
            for shape in self.anchors.values():
                path.addEllipse(shape)

        return path

    ####################################################################################################################
    #                                                                                                                  #
    #   GEOMETRY UPDATE                                                                                                #
    #                                                                                                                  #
    ####################################################################################################################

    def updateEdge(self, target=None):
        """
        Update the edge painter path and the selection polygon.
        :type target: QPointF
        """
        boxSize = self.selectionSize
        headSize = self.headSize
        sourceNode = self.source
        targetNode = self.target
        sourcePos = self.source.anchor(self)
        targetPos = target or self.target.anchor(self)

        self.updateAnchors()
        self.updateHandles()

        ################################################################################################################
        #                                                                                                              #
        #   UPDATE EDGE PATH, SELECTION BOX AND HEAD                                                                   #
        #                                                                                                              #
        ################################################################################################################

        # get the list of visible subpaths for this edge
        collection = self.computePath(sourceNode, targetNode, [sourcePos] + self.breakpoints + [targetPos])

        def createSelectionBox(pos1, pos2, angle, size):
            """
            Constructs the selection polygon between pos1 and pos2 according to the given angle.
            :type pos1: QPointF
            :type pos2: QPointF
            :type angle: float
            :type size: int
            :rtype: QPolygonF
            """
            rad = radians(angle)
            x = size / 2 * sin(rad)
            y = size / 2 * cos(rad)
            a = QPointF(+x, +y)
            b = QPointF(-x, -y)
            return QPolygonF([pos1 + a, pos1 + b, pos2 + b, pos2 + a])

        def createHead(pos1, angle, size):
            """
            Create the head polygon.
            :type pos1: QPointF
            :type angle: float
            :type size: int
            :rtype: QPolygonF
            """
            rad = radians(angle)
            pos2 = pos1 - QPointF(sin(rad + M_PI / 3.0) * size, cos(rad + M_PI / 3.0) * size)
            pos3 = pos1 - QPointF(sin(rad + M_PI - M_PI / 3.0) * size, cos(rad + M_PI - M_PI / 3.0) * size)
            return QPolygonF([pos1, pos2, pos3])

        self.path = QPainterPath()
        self.selection = QPainterPath()

        points = [] # will store all the points defining the edge not to recompute the path to update the label
        append = points.append  # keep this shortcut and the one below since it saves a lot of computation
        extend = points.extend  # more: http://blog.cdleary.com/2010/04/efficiency-of-list-comprehensions/

        if len(collection) == 0:

            self.head = QPolygonF()

        elif len(collection) == 1:

            subpath = collection[0]
            p1 = sourceNode.intersection(subpath)
            p2 = targetNode.intersection(subpath) if targetNode else subpath.p2()
            if p1 is not None and p2 is not None:
                self.path.moveTo(p1)
                self.path.lineTo(p2)
                self.selection.addPolygon(createSelectionBox(p1, p2, subpath.angle(), boxSize))
                self.head = createHead(p2, subpath.angle(), headSize)
                extend((p1, p2))

        elif len(collection) > 1:

            subpath1 = collection[0]
            subpathN = collection[-1]
            p11 = sourceNode.intersection(subpath1)
            p22 = targetNode.intersection(subpathN)

            if p11 and p22:

                p12 = subpath1.p2()
                p21 = subpathN.p1()

                self.path.moveTo(p11)
                self.path.lineTo(p12)
                self.selection.addPolygon(createSelectionBox(p11, p12, subpath1.angle(), boxSize))
                extend((p11, p12))

                for subpath in collection[1:-1]:
                    p1 = subpath.p1()
                    p2 = subpath.p2()
                    self.path.moveTo(p1)
                    self.path.lineTo(p2)
                    self.selection.addPolygon(createSelectionBox(p1, p2, subpath.angle(), boxSize))
                    append(p2)

                self.path.moveTo(p21)
                self.path.lineTo(p22)
                self.selection.addPolygon(createSelectionBox(p21, p22, subpathN.angle(), boxSize))
                append(p22)

                self.head = createHead(p22, subpathN.angle(), headSize)

        self.updateZValue()
        self.updateLabelPos(points)
        self.update()

    ####################################################################################################################
    #                                                                                                                  #
    #   DRAWING                                                                                                        #
    #                                                                                                                  #
    ####################################################################################################################

    @classmethod
    def image(cls, **kwargs):
        """
        Returns an image suitable for the palette.
        :rtype: QPixmap
        """
        lineWidth = 54
        headSize = 8  # length of the head side
        headSpan = 4  # offset between line end and head end (this is needed
                      # to prevent artifacts to be visible on low res screens)

        # Initialize the pixmap
        pixmap = QPixmap(kwargs['w'], kwargs['h'])
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        # Initialize the line
        line_p1 = QPointF(((kwargs['w'] - lineWidth) / 2), kwargs['h'] / 2)
        line_p2 = QPointF(((kwargs['w'] - lineWidth) / 2) + lineWidth - (headSpan / 2), kwargs['h'] / 2)
        line = QLineF(line_p1, line_p2)

        angle = radians(line.angle())

        # Calculate head coordinates
        p1 = QPointF(line.p2().x() + (headSpan / 2), line.p2().y())
        p2 = p1 - QPointF(sin(angle + M_PI / 3.0) * headSize, cos(angle + M_PI / 3.0) * headSize)
        p3 = p1 - QPointF(sin(angle + M_PI - M_PI / 3.0) * headSize, cos(angle + M_PI - M_PI / 3.0) * headSize)

        # Initialize edge head
        head = QPolygonF([p1, p2, p3])

        # Draw the polygon
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(0, 0, 0), 1.1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(line)

        # Draw the head
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(0, 0, 0), 1.1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(0, 0, 0))
        painter.drawPolygon(head)

        # Draw the text on top of the edge
        space = 2 if sys.platform.startswith('darwin') else 0
        painter.setFont(Font('Arial', 9, Font.Light))
        painter.drawText(line_p1.x() + space, (kwargs['h'] / 2) - 4, 'instanceOf')

        return pixmap

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        :type painter: QPainter
        :type option: int
        :type widget: QWidget
        """
        if self.canDraw():

            scene = self.scene()

            # Draw the selection path if needed
            if scene.mode in (DiagramMode.Idle, DiagramMode.NodeMove) and self.isSelected():
                painter.setRenderHint(QPainter.Antialiasing)
                painter.fillPath(self.selection, self.selectionBrush)

            # Draw the edge path
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(self.shapePen)
            painter.drawPath(self.path)

            # Draw the head polygon
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(self.headPen)
            painter.setBrush(self.headBrush)
            painter.drawPolygon(self.head)

            if self.isSelected():

                # Draw breakpoint handles
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setPen(self.handlePen)
                painter.setBrush(self.handleBrush)
                for rect in self.handles.values():
                    painter.drawEllipse(rect)

                # Draw anchor points
                if self.target:
                    painter.setRenderHint(QPainter.Antialiasing)
                    painter.setPen(self.handlePen)
                    painter.setBrush(self.handleBrush)
                    for rect in self.anchors.values():
                        painter.drawEllipse(rect)