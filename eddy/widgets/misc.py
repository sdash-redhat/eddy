# -*- coding: utf-8 -*-

##########################################################################
#                                                                        #
#  Eddy: an editor for the Graphol ontology language.                    #
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
#  Dipartimento di Ingegneria Informatica, Automatica e Gestionale       #
#  A.Ruberti at Sapienza University of Rome: http://www.dis.uniroma1.it/ #
#                                                                        #
#     - Domenico Lembo <lembo@dis.uniroma1.it>                           #
#     - Valerio Santarelli <santarelli@dis.uniroma1.it>                  #
#     - Domenico Fabio Savo <savo@dis.uniroma1.it>                       #
#     - Marco Console <console@dis.uniroma1.it>                          #
#                                                                        #
##########################################################################


from time import time, sleep

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel


class SplashScreen(QLabel):
    """
    This class implements Eddy's splash screen.
    It can be used with the context manager, i.e:

    >>> import sys
    >>> from PyQt5.QtWidgets import QApplication
    >>> app = QApplication(sys.argv)
    >>> with SplashScreen(min_splash_time=5):
    >>>     app.do_something_heavy()

    will draw a 5 seconds (at least) splash screen on the screen.
    The with statement body can be used to initialize the application and process heavy stuff.
    """
    def __init__(self, min_splash_time=2):
        """
        Initialize the Eddy's splash screen.
        :param min_splash_time: the minimum amount of seconds the splash screen should be drawn.
        """
        super().__init__(None, Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SplashScreen)
        self.min_splash_time = time() + min_splash_time
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setPixmap(QPixmap(':/images/splash'))
        self.setMask(self.pixmap().mask())
        self.setFixedSize(self.pixmap().width(), self.pixmap().height())

    def __enter__(self):
        """
        Draw the splash screen.
        """
        self.show()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Remove the splash screen from the screen.
        This will make sure that the splash screen is displayed for at least min_splash_time seconds.
        """
        now = time()
        if now < self.min_splash_time:
            sleep(self.min_splash_time - now)
        self.close()


__all__ = [
    'SplashScreen',
]