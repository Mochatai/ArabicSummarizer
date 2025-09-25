import sys
import traceback
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QFrame
from PySide6.QtCore import QRunnable, QThreadPool, Signal, Slot, QObject
import TransSum as translator
import time
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display


class WorkerSignals(QObject):
    """Signals from a running worker thread.

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc())

    result
        object data returned from processing, anything

    progress
        float indicating % progress
    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(float)

class Worker(QRunnable):
    """Worker thread."""
    
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Add the callback to our kwargs
        #self.kwargs["progress_callback"] = self.signals.progress

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threadpool = QThreadPool()
        thread_count = self.threadpool.maxThreadCount()
        print(f"Multithreading with maximum {thread_count} threads")
        self.setWindowTitle("My app")
        self.resize(1000,600)
        mainLayout = QHBoxLayout()
        layoutOne = QVBoxLayout()
        layoutTwo = QVBoxLayout()
        layoutThree = QVBoxLayout()

        reshaper = ArabicReshaper()
        

        summarizeButton = QPushButton("Click to summrize")
        past = QPushButton("Past")
        copy = QPushButton("Copy")
        delete = QPushButton("Delete text")
        firstInput = QPlainTextEdit()
        ArOutput = QPlainTextEdit()
        ArOutput.setReadOnly(True)

        

        appInterface = QWidget()
        
        summarizeButton.setStyleSheet("""

        QPushButton { background-color: #FAFBFC; 
            border-radius: 5px;
            border: 1px solid black; 
            color: black;
            padding: 20px; }
        QPushButton:hover {
            border: 2px solid black;
        }
        QPushButton:pressed  {
           background-color: #BEBEBE;
        }
""")
        
        past.setStyleSheet("""

        QPushButton { background-color: #FAFBFC; 
            border-radius: 5px;
            border: 1px solid black; 
            color: black;
            padding: 20px; }
        QPushButton:hover {
            border: 2px solid black;
        }
        QPushButton:pressed  {
           background-color: #BEBEBE;
        }
""")
        
        copy.setStyleSheet("""

        QPushButton { background-color: #FAFBFC; 
            border-radius: 5px;
            border: 1px solid black; 
            color: black;
            padding: 20px; }
        QPushButton:hover {
            border: 2px solid black;
        }
        QPushButton:pressed  {
           background-color: #BEBEBE;
        }
""")
        
        delete.setStyleSheet("""

        QPushButton { background-color: #FAFBFC; 
            border-radius: 5px;
            border: 1px solid black; 
            color: black;
            padding: 20px; }
        QPushButton:hover {
            border: 2px solid black;
        }
        QPushButton:pressed  {
           background-color: #BEBEBE;
        }
""")

        firstInput.setStyleSheet(""" QPlainTextEdit {  background-color: #FFFFFF; border: 0.5px solid black}  QPlainTextEdit:focus  {border: 0.5px solid #000000;}""")
        ArOutput.setStyleSheet(""" QPlainTextEdit {  background-color: #FFFFFF; border: 0.5px solid black}  QPlainTextEdit:focus  {border: 0.5px solid #000000;}""")

        
        layoutOne.addWidget(firstInput)
        layoutOne.addWidget(past)
        layoutOne.addWidget(delete)
        layoutTwo.addWidget(summarizeButton)
        layoutThree.addWidget(ArOutput)
        layoutThree.addWidget(copy)

        mainLayout.addLayout(layoutOne)
        mainLayout.addLayout(layoutTwo)
        mainLayout.addLayout(layoutThree)
        appInterface.setLayout(mainLayout)
        appInterface.setStyleSheet("QWidget {background-color: #E1D9D1}")
        self.setCentralWidget(appInterface)

        
        def on_past_click():
            clipboard = QApplication.clipboard()
            clipboard_text = clipboard.text()
            firstInput.setPlainText(clipboard_text)

        def on_copy_click():
            clipboard = QApplication.clipboard()
            clipboard.setText(ArOutput.toPlainText())

        def on_delete_click():
            firstInput.setPlainText("")
        
        def on_summarize_click():
            print("running on_summarize")
            summarizeButton.setEnabled(False)
            longText = firstInput.toPlainText()
            arSummraized = translator.runFullOp(longText)
            shaped = reshaper.reshape(arSummraized)
            ArOutput.setPlainText(shaped)
            time.sleep(25)
            summarizeButton.setEnabled(True)
        
        def setResults(res):
            ArOutput.setPlainText(res)
            time.sleep(5)
            summarizeButton.setText("Click to summrize")
            summarizeButton.setEnabled(True)
            print(res)

        def textSummarizing(longText):
            arSummraized = translator.runFullOp(longText)
            shaped = reshaper.reshape(arSummraized)
            return shaped
            
            
        def on_summarize_click_th():
            summarizeButton.setEnabled(False)
            summarizeButton.setText("summarize in progress")
            longText = firstInput.toPlainText()
            worker = Worker(textSummarizing, longText)
            worker.signals.result.connect(setResults)
            self.threadpool.start(worker)
            
        
        summarizeButton.clicked.connect(on_summarize_click_th)
        past.clicked.connect(on_past_click)
        copy.clicked.connect(on_copy_click)
        delete.clicked.connect(on_delete_click)

def creat_run():

    app = QApplication.instance()
    if app is None:
        # If not, create a new one
        app = QApplication(sys.argv)
    else:
        # If it exists, quit it and potentially delete it
        print("Existing QApplication instance found. Quitting and creating a new one.")
        app.quit()
        # In some cases, you might need to explicitly delete it
        # del app
        app = QApplication(sys.argv) # Create a new one after quitting         

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


#app = QApplication(sys.argv)
#window = MainWindow()
#window.show()
#app.exec()

if __name__ == "__main__":
    creat_run()