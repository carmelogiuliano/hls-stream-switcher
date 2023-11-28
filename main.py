import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt, QEvent, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QFont
from pynput import keyboard
import subprocess

# Global variable to keep track of the currently playing stream
current_stream = None

# Dictionary to map hotkeys to stream URLs
stream_info = {
    '1': {'url': '', 'name': ''},
    '2': {'url': '', 'name': ''},
    '3': {'url': '', 'name': ''},
    # Add streams here
}

# Signal class to emit the hotkey signal
class HotkeySignal(QObject):
    hotkeyPressed = pyqtSignal(str)

# Function to launch or close VLC with a specific stream URL
def toggle_vlc(hotkey):
    global current_stream

    # Check if the pressed hotkey is in the stream_info dictionary
    if hotkey not in stream_info:
        return  # Do nothing if the hotkey is not registered

    if current_stream is not None:
        # Close the currently playing stream
        current_stream.terminate()
        current_stream = None

    # Open the new stream corresponding to the pressed hotkey
    stream = stream_info[hotkey]
    vlc_command = ['vlc', '--fullscreen', stream['url']]
    current_stream = subprocess.Popen(vlc_command)


class KeyboardListenerThread(QThread):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def run(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        try:
            hotkey = key.char  # Check if the pressed key is a character
            self.signal.hotkeyPressed.emit(hotkey)
        except AttributeError:
            pass  # Ignore non-character keys

class MainWindow(QWidget):
    def __init__(self, hotkey_signal):
        super().__init__()

        # Create labels for each stream
        labels = []
        for hotkey, info in stream_info.items():
            label = QLabel(f"Press {hotkey} for {info['name']}", self)
            label.setGeometry(10, len(labels) * 40, 300, 30)

            labels.append(label)

        hotkey_signal.hotkeyPressed.connect(self.handle_hotkey)

        # Start the keyboard listener thread
        keyboard_thread = KeyboardListenerThread(hotkey_signal)
        keyboard_thread.start()

        self.show()

    def handle_hotkey(self, hotkey):
        toggle_vlc(hotkey)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    hotkey_signal = HotkeySignal()
    window = MainWindow(hotkey_signal)
    sys.exit(app.exec_())
