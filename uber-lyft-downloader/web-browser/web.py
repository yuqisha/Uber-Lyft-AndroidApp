from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtNetwork import QNetworkCookie
import sys, os
import json
import sip


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.webview = QWebEngineView()
        profile = QWebEngineProfile(self.webview)
        profile.clearHttpCache()
        cookie_store = profile.cookieStore()
        cookie_store.deleteAllCookies()
        cookie_store.cookieAdded.connect(self.onCookieAdded)
        self.cookies = []
        webpage = QWebEnginePage(profile, self.webview)
        self.webview.setPage(webpage)
        self.webview.load(
            QUrl("https://partners.uber.com/p3/payments/weekly-earnings/"))
        self.setCentralWidget(self.webview)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Message",
            "Quit to finish log in process?",
            QMessageBox.Close | QMessageBox.Cancel, QMessageBox.Close)
        self.toJson()

        if reply == QMessageBox.Close:
            event.accept()
        else:
            event.ignore()

    def onCookieAdded(self, cookie):
        for c in self.cookies:
            if c.hasSameIdentifier(cookie):
                return
        new_cookie = QNetworkCookie(cookie)
        self.cookies.append(new_cookie)
        #print(bytearray(new_cookie.name()).decode(), bytearray(new_cookie.value()).decode())

    def toJson(self):
        cookies_list_info = {}
        for c in self.cookies:
            if bytearray(c.name()).decode() != '':
                cookies_list_info[bytearray(c.name()).decode()] = bytearray(c.value()).decode()
        #print("Cookie as list of dictionary:")
        #print(cookies_list_info)
        pre = os.path.expanduser('~')
        path = os.path.join(pre, 'UberLyftCookies')
        if not os.path.exists(path):
            os.mkdir(path)
        filename = os.path.join(path, 'data.json')
        with open(filename, 'w') as outfile:
            json.dump(cookies_list_info, outfile)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
