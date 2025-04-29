import cv2
import face_recognition
import numpy as np
import json
import os
import tkinter as tk
from tkinter import simpledialog

# File to store face encodings and names
data_file = 'face_data.json'
name_file = 'face_names.json'

# Load existing face data if it exists
if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        face_data = json.load(f)
else:
    face_data = {}

# Load existing names if it exists
if os.path.exists(name_file):
    with open(name_file, 'r') as f:
        face_names = json.load(f)
else:
    face_names = {}

# Initialize the camera
camera = cv2.VideoCapture(0)

# Function to save face data
def save_face_data():
    with open(data_file, 'w') as f:
        json.dump(face_data, f)

# Function to save face names
def save_face_names():
    with open(name_file, 'w') as f:
        json.dump(face_names, f)

# Function to add a new face
def add_new_face(face_encoding):
    identifier = str(len(face_data) + 1)  # Assign a new ID
    face_data[identifier] = face_encoding.tolist()  # Save as list for JSON serialization
    face_names[identifier] = "Unknown"  # Default name
    save_face_data()
    save_face_names()
    return identifier

# Function to input name for a detected face using a pop-up dialog
def input_name(identifier):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    name = simpledialog.askstring("Input", f"Enter name for ID {identifier}:", parent=root)
    if name:
        face_names[identifier] = name
        save_face_names()
    root.destroy()

# Keep looping
while True:
    # Grab the current frame
    grabbed, frame = camera.read()
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find all face locations and encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Loop through each face found in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Check if the face is already known
        matches = face_recognition.compare_faces([np.array(face_data[key]) for key in face_data.keys()], face_encoding)
        
        if True in matches:
            # If a match is found, get the index of the first match
            matched_idx = matches.index(True)
            identifier = list(face_data.keys())[matched_idx]
            name = face_names[identifier]
        else:
            # If no match is found, add the new face
            identifier = add_new_face(face_encoding)
            name = "Unknown"  # Default name for new faces

        # If the name is still "Unknown", prompt for a name
        if name == "Unknown":
            input_name(identifier)  # Prompt for name input
            name = face_names[identifier]  # Update name after input

        # Draw a rectangle around the face and label it
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow("Face Recognition", frame)

    # If the 'q' key is pressed, stop the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()