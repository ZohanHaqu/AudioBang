import sys
import pygame
import pyttsx3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout, QMenuBar, QMainWindow, QAction, QLabel, QLineEdit, QDialog, QDialogButtonBox, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QIcon

class AudioBang(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('AudioBang')
        self.setGeometry(100, 100, 400, 200)
        
        # Set the window icon to 'icon.png'
        self.setWindowIcon(QIcon('icon.png'))
        
        # Initialize Pygame mixer for audio playback
        pygame.mixer.init()
        
        # Initialize pyttsx3 for TTS
        self.tts_engine = pyttsx3.init()
        
        self.is_playing = False
        self.is_muted = False
        self.current_audio = None
        
        # Current audio list (can be expanded to create a playlist)
        self.audio_list = []
        self.history = []  # Tracks playback history
        self.history_index = -1  # Index for navigating history

        self.initUI()
        
    def initUI(self):
        # Create menu bar with Open, TTS, and Help options
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_audio)
        file_menu.addAction(open_action)

        # TTS menu
        tts_menu = menubar.addMenu('TTS')
        tts_action = QAction('Text To Speech', self)
        tts_action.triggered.connect(self.open_tts_dialog)
        tts_menu.addAction(tts_action)

        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.about_dialog)
        help_menu.addAction(about_action)
        
        how_to_use_action = QAction('How to Use', self)
        how_to_use_action.triggered.connect(self.how_to_use_dialog)
        help_menu.addAction(how_to_use_action)

        # Create Play/Pause, Mute, Next, and Previous buttons
        layout = QVBoxLayout()
        
        self.label = QLabel('No audio playing', self)
        layout.addWidget(self.label)
        
        button_layout = QHBoxLayout()
        
        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.toggle_play)
        button_layout.addWidget(self.play_button)
        
        self.pause_button = QPushButton('Pause', self)
        self.pause_button.clicked.connect(self.pause_audio)
        button_layout.addWidget(self.pause_button)
        
        self.mute_button = QPushButton('Mute', self)
        self.mute_button.clicked.connect(self.toggle_mute)
        button_layout.addWidget(self.mute_button)
        
        self.next_button = QPushButton('Next', self)
        self.next_button.clicked.connect(self.next_audio)
        self.next_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.next_button)
        
        self.previous_button = QPushButton('Previous', self)
        self.previous_button.clicked.connect(self.previous_audio)
        self.previous_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.previous_button)
        
        layout.addLayout(button_layout)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def open_audio(self):
        # Open audio file using QFileDialog
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Open Audio Files", "", "Audio Files (*.mp3 *.wav *.ogg);;All Files (*)", options=options)
        
        if files:
            self.audio_list = files
            self.history = []  # Reset history whenever a new set of audio files is opened
            self.history_index = -1  # Reset history index
            self.play_audio(self.audio_list[0])

    def play_audio(self, audio_file):
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        self.is_playing = True
        self.label.setText(f'Playing: {audio_file}')
        self.play_button.setText('Pause')
        self.mute_button.setText('Mute')

        # Update history
        if self.history_index == len(self.history) - 1 or not self.history:
            self.history.append(audio_file)
            self.history_index += 1
        else:
            # If the current audio is in the middle of the history, remove forward items in history
            self.history = self.history[:self.history_index + 1]
            self.history.append(audio_file)
            self.history_index += 1

        # Enable/disable Next and Previous buttons based on history
        self.update_navigation_buttons()

    def toggle_play(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_button.setText('Play')
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.play_button.setText('Pause')
    
    def pause_audio(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_button.setText('Play')
        self.label.setText('No audio playing')
        self.update_navigation_buttons()
    
    def toggle_mute(self):
        if self.is_muted:
            pygame.mixer.music.set_volume(1.0)
            self.is_muted = False
            self.mute_button.setText('Mute')
        else:
            pygame.mixer.music.set_volume(0.0)
            self.is_muted = True
            self.mute_button.setText('Unmute')
    
    def next_audio(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.play_audio(self.history[self.history_index])
            self.update_navigation_buttons()

    def previous_audio(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.play_audio(self.history[self.history_index])
            self.update_navigation_buttons()

    def update_navigation_buttons(self):
        # Enable/disable Next and Previous buttons based on history
        self.next_button.setEnabled(self.history_index < len(self.history) - 1)
        self.previous_button.setEnabled(self.history_index > 0)

    def open_tts_dialog(self):
        dialog = TTSDialog(self, self.tts_engine)  # Pass the tts_engine to the dialog
        dialog.exec_()

    def about_dialog(self):
        # Show about dialog
        QMessageBox.information(self, "About AudioBang", "AudioBang is an audio and text-to-speech utility.\n\nDeveloped with PyQt5 and Pygame.\nEnjoy using AudioBang!")

    def how_to_use_dialog(self):
        # Show how to use dialog
        QMessageBox.information(self, "How to Use AudioBang", 
            "1. Open audio files using File > Open.\n"
            "2. Play, pause, mute, and navigate through the audio with the respective buttons.\n"
            "3. Use Text-to-Speech under TTS > Text To Speech to generate speech from text.\n\nEnjoy!"
        )

    def closeEvent(self, event):
        # Stop any playing audio when the window is closed
        pygame.mixer.music.stop()
        self.tts_engine.stop()
        event.accept()

class SplashScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Splash Screen")
        self.setGeometry(150, 150, 600, 400)  # Set a window size for the splash screen

        # Layout for the splash screen
        layout = QVBoxLayout()
        
        # Add Image (resized)
        self.image_label = QLabel(self)
        pixmap = QPixmap("icon.png").scaled(600, 400)  # Resize the image to fit
        self.image_label.setPixmap(pixmap)
        layout.addWidget(self.image_label)

        self.setLayout(layout)
        
        # Timer to close the splash screen and show the welcome window after 3 seconds
        QTimer.singleShot(3000, self.close)

class WelcomeWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Welcome to AudioBang")
        self.setGeometry(150, 150, 400, 250)

        # Layout for the welcome window
        layout = QVBoxLayout()
        
        # Add Image (Resized)
        self.image_label = QLabel(self)
        pixmap = QPixmap("icon.png").scaled(200, 200, aspectRatioMode=1)  # Resize image to fit better
        self.image_label.setPixmap(pixmap)
        layout.addWidget(self.image_label)

        # Add Text
        self.text_label = QLabel("Welcome to AudioBang, an open-source audio player from Zohan Haque!\nTo use this app, go to the Help menu.", self)
        layout.addWidget(self.text_label)

        self.setLayout(layout)

class TTSDialog(QDialog):
    def __init__(self, parent=None, tts_engine=None):
        super().__init__(parent)
        
        self.tts_engine = tts_engine  # Store the TTS engine
        self.setWindowTitle('Text to Speech')
        self.setGeometry(200, 200, 400, 250)
        
        layout = QVBoxLayout()

        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Enter text to speak")
        layout.addWidget(self.text_input)

        self.output_text = QLabel(self)
        layout.addWidget(self.output_text)

        self.speak_button = QPushButton('Speak', self)
        self.speak_button.clicked.connect(self.speak_text)
        layout.addWidget(self.speak_button)

        self.setLayout(layout)

    def speak_text(self):
        text = self.text_input.text()
        if text:
            try:
                self.output_text.setText("Speaking...")
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                self.output_text.setText("TTS played successfully!")
            except Exception as e:
                self.output_text.setText(f"Error: {e}")
        else:
            self.output_text.setText("Please enter text.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    splash = SplashScreen()
    splash.exec_()
    
    welcome = WelcomeWindow()
    welcome.exec_()

    window = AudioBang()
    window.show()
    
    sys.exit(app.exec_())
