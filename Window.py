#This is a simple browser using pyQt and webkit engine
import sys
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
from PyQt4 import *
import os

class Browser(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(1366,768)
        self.centralwidget = QtGui.QWidget(self)

        self.mainLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setMargin(1)

        self.frame = QtGui.QFrame(self.centralwidget)

        self.gridLayout = QtGui.QVBoxLayout(self.frame)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.url_box = QtGui.QLineEdit(self.frame)
        self.back = QtGui.QPushButton(self.frame)
        self.forward = QtGui.QPushButton(self.frame)

        self.back.setIcon(QtGui.QIcon().fromTheme("go-previous"))
        self.forward.setIcon(QtGui.QIcon().fromTheme("go-next"))

        self.horizontalLayout.addWidget(self.back)
        self.horizontalLayout.addWidget(self.forward)
        self.horizontalLayout.addWidget(self.url_box)
        self.gridLayout.addLayout(self.horizontalLayout)

        self.html = QtWebKit.QWebView()
        self.gridLayout.addWidget(self.html)
        self.mainLayout.addWidget(self.frame)
        self.setCentralWidget(self.centralwidget)

        self.connect(self.url_box, QtCore.SIGNAL("returnPressed()"), self.browse)
        self.connect(self.back, QtCore.SIGNAL("clicked()"), self.html.back)
        self.connect(self.forward, QtCore.SIGNAL("clicked()"), self.html.forward)

        self.default_url = "http://google.co.ke/"
        self.url_box.setText(self.default_url)
        
        # proxy support
        if 'http_proxy' in os.environ:
            proxy_url = QtCore.QUrl(os.environ['http_proxy'])
            if unicode(self.proxy_url.scheme()).starstswith('http'):
                protocol = QtNetwork.QNetworkProxy.HttpProxy
            else:
                protocol = QtNetwork.QNetworkProxy.Socks5Proxy
            QtNetwork.QNetworkProxy.setApplicationProxy(
                QtNetwork.QNetworkProxy(
                    protocol,
                    proxy_url.host(),
                    proxy_url.port(),
                    proxy_url.userName(),
                    proxy_url.password()))
        
        self.browse()
    def browse(self):
        if self.url_box.text():
            url = self.url_box.text()
        else:
            self.default_url
        self.html.load(QtCore.QUrl(url))
        self.html.show()

if __name__ == "__main__":
    program = QtGui.QApplication(sys.argv)
    main = Browser()
    main.show()
    sys.exit(program.exec_())