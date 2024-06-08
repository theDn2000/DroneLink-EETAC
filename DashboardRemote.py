import customtkinter as ctk
import tkintermapview as tkmap
import os
import sys
import time
import threading
import json
import base64
import io
import asyncio
import websockets
from paho.mqtt.client import ssl
from paho.mqtt import client as mqtt
import cv2 as cv
import numpy as np
from PIL import Image, ImageTk

# Night mode
ctk.set_appearance_mode("dark")

# Create App class
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create the app
        self.geometry("900x600")
        self.title("Dashboard Remote")
        self.resizable(False, False)

        # CLASS VARIABLES
        self.mission_waypoints = []
        self.mission_markers = []

        self.geofence_points = []
        self.geofence_markers = []
        self.geofence_enabled = False

        # Initialize the drone and camera id variables (1 by default)
        self.drone_id = 1
        self.camera_id = 1

        # Dashboard State
        self.connected = False

        # Dron marker variable
        self.dron_marker = None

        # Load images
        current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        self.plane_circle_1_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "images", "drone_circle.png")).resize((35, 35)))
        self.logo = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "images", "logo.jpg")).resize((400, 400)))

        # Go to point
        self.go_to_point_coords = None

        # Video stream parameters
        self.streaming = False
        self.video_connection_type = "broker" # Broker is the default option

        # WebSocket client parameters
        self.websocket = None
        self.url = "ws://localhosting:8765" # Url to stablish the connection (it is replaced automatically by the IP of the server when the connection is stablished)
        self.ws_connected = False
        self.loop = None

        # Map variables
        self.map_centered = False

        # MAIN FRAME
        # Create the main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Separate the main_frame into 8 vertical sections
        self.column0 = self.main_frame.columnconfigure(0, weight=1)
        self.column1 = self.main_frame.columnconfigure(1, weight=1)
        self.column2 = self.main_frame.columnconfigure(2, weight=1)
        self.column3 = self.main_frame.columnconfigure(3, weight=1)
        self.column4 = self.main_frame.columnconfigure(4, weight=1)
        self.column5 = self.main_frame.columnconfigure(5, weight=1)
        self.column6 = self.main_frame.columnconfigure(6, weight=1)
        self.column7 = self.main_frame.columnconfigure(7, weight=1)

        # Separate the main_frame into 8 horizontal sections
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        self.main_frame.rowconfigure(4, weight=1)
        self.main_frame.rowconfigure(5, weight=1)
        self.main_frame.rowconfigure(6, weight=1)
        self.main_frame.rowconfigure(7, weight=1)



        # BUTTONS
        # Create the connect_button
        self.connect_button = ctk.CTkButton(self.main_frame, text="Connect", command=self.on_button_connect_click, fg_color="#457b9d", hover_color="#3a5f7d")
        self.connect_button.grid(row=7, column=6, padx=10, pady=10, sticky="nswe", ipady=0, columnspan=2)

        # TEXTBOXES
        # Create the info_textbox (read-only)
        self.info_textbox = ctk.CTkTextbox(self.main_frame, width=350)
        self.info_textbox.grid(row=0, column=6, padx=10, pady=10, rowspan=6, columnspan=2, sticky="nswe")
        self.info_textbox.insert("1.0", "Welcome to DashboardRemote. This tool allows you to\ninteract with the autopilot functions using a broker.\n\nPlease, click the 'Connect' button to start.")
        # Add a version number to the textbox
        self.info_textbox.insert("end", "\n\nPATCH NOTES:\n\n- Version: 0.1.0: Initial release\n\n- Version: 0.1.1: Connect and telemetry info added.\n\n- Version: 0.1.2: Control and pad buttons added.\n\n- Version: 1.0.0: All basic functions operative.\n\n- Version: 1.0.1: Map with basic functions added.\n\n- Version: 1.0.2: Geofence functions added.\n\n- Version: 1.0.3: Mission functions added.\n\n- Version: 1.0.4: Parameters functions added.\n\n- Version: 2.0.0: Video stream added (via broker).\n\n- Version: 2.0.1: Video stream added (via websocket).\n\n- Version: 2.0.1: Bug fixes.\n\n- Version: 3.0.0: Visual update.\n\n- Version: 3.0.1: Bug fixes.\n\n- Version: 3.1.0: Final release.")
        # Disable the textbox
        self.info_textbox.configure(state="disabled")

        # Create the logo frame
        self.logo_frame = ctk.CTkFrame(self.main_frame, height=250, width=400)
        self.logo_frame.grid(row=0, column=0, padx=10, pady=10, rowspan=8, columnspan=5, sticky="nswe")
        # Color the frame
        self.logo_frame.configure(fg_color="#fdf0d5")
        # Create label for photo (no text, just the photo)
        self.label_logo = ctk.CTkLabel(self.logo_frame, text="", font=("TkDefaultFont", 11))
        # Center the label in the frame
        self.label_logo.place(relx=0.5, rely=0.5, anchor="center")
        # Insert image
        self.label_logo.configure(image=self.logo)

        # Create a option selector for the broker selection
        self.broker_selector = ctk.CTkOptionMenu(self.main_frame, values=["Select External Broker...", "hivemq","hivemq (certificate)", "classpip (credentials)"],  width=130, fg_color="#457b9d", dropdown_fg_color="#457b9d", button_color="#457b9d")
        self.broker_selector.grid(row=6, column=6, padx=10, pady=0, ipady=0, columnspan=1, sticky="we")

        # Create a option selector for the id of the drone
        self.drone_id_selector = ctk.CTkOptionMenu(self.main_frame, values=["Drone ID...", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], width=130, fg_color="#457b9d", dropdown_fg_color="#457b9d", button_color="#457b9d")
        self.drone_id_selector.grid(row=6, column=7, padx=10, pady=0, ipady=0, columnspan=1, sticky="we")



    # FUNCTIONS (FRONTEND)

    def on_button_connect_click(self):
        # If the broker is not selected, show an error message
        if  self.broker_selector.get() == "Select External Broker...":
            self.info_textbox.configure(state="normal")
            self.info_textbox.delete("1.0", "end")
            self.info_textbox.insert("1.0", "Error: Please select broker")
            self.info_textbox.configure(state="disabled")
            self.info_textbox.configure(text_color="red")
            return
        if self.drone_id_selector.get() == "Drone ID...":
            self.info_textbox.configure(state="normal")
            self.info_textbox.delete("1.0", "end")
            self.info_textbox.insert("1.0", "Error: Please select drone ID")
            self.info_textbox.configure(state="disabled")
            self.info_textbox.configure(text_color="red")
            return
        else:
            # Execute configuration
            self.configure()

            # Make the button invisible and substitute it with a label
            self.connect_button.grid_forget()
            self.broker_selector.grid_forget()
            self.drone_id_selector.grid_forget()
            self.connect_label = ctk.CTkLabel(self.main_frame, text="Connecting...")
            self.connect_label.grid(row=7, column=6, padx=10, pady=0, sticky="nswe", columnspan=2)

            # Get the ip of the websocket server
            self.get_ip()

            # Connect to the autopilot 1000ms later
            self.after(1000, self.connect)

    def set_main_page(self):
        # Create the main page view

        # Add a map to the main frame
        self.map_widget = tkmap.TkinterMapView(self.main_frame)
        self.map_widget.grid(row=0, column=0, padx=10, pady=10, rowspan=6, columnspan=6, sticky="nswe")
        # Change the map style to satellite
        x = -40.3633515
        y = 149.1652412
        z = 15
        self.map_widget.set_tile_server("https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", max_zoom=22)
        self.map_widget.set_position(x, y)
        # Add a right click menu to add mission waypoints
        self.map_widget.add_right_click_menu_command(label="Add Mission Waypoint", command=self.add_mission_waypoint_event, pass_coords=True)
        # Add a right click menu to add geofence points
        self.map_widget.add_right_click_menu_command(label="Add Geofence Point", command=self.add_geofence_point_event, pass_coords=True)
        # Add a right click menu to add a GO TO point
        self.map_widget.add_right_click_menu_command(label="Fly Here", command=self.go_to_point_event, pass_coords=True)

        # Insert tabview
        self.main_tabview = ctk.CTkTabview(self.main_frame, width=580, segmented_button_selected_color="#457b9d", segmented_button_unselected_hover_color="#3a5f7d", segmented_button_selected_hover_color="#3a5f7d")
        self.main_tabview.grid(row=6, column=0, padx=10, pady=10, rowspan=2, columnspan=6, sticky="nswe")
        # Create the tabs
        self.main_tabview.add("Parameters")
        self.main_tabview.add("Mission")
        self.main_tabview.add("Geofence")



        # Parameters tab:
        # Separate the tab into 2 vertical sections
        self.main_tabview.tab("Parameters").columnconfigure(0, weight=1)
        self.main_tabview.tab("Parameters").columnconfigure(1, weight=1)

        # Create a frame for get a parameter, with grey background
        self.get_parameter_frame = ctk.CTkFrame(self.main_tabview.tab("Parameters"), height=80, width=265)
        self.get_parameter_frame.grid(row=0, column=0, padx=10, pady=5, sticky="we")
        self.get_parameter_frame.configure(fg_color="#1f1f1f")
        # Separate the frame into 4 vertical sections
        self.get_parameter_frame.columnconfigure(0, weight=1)
        self.get_parameter_frame.columnconfigure(1, weight=1)
        self.get_parameter_frame.columnconfigure(2, weight=1)
        self.get_parameter_frame.columnconfigure(3, weight=1)
        # Separate the frame into 2 horizontal section
        self.get_parameter_frame.rowconfigure(0, weight=1)
        self.get_parameter_frame.rowconfigure(1, weight=1)
        
        # Add a button to get the value of a parameter
        self.get_parameter_button = ctk.CTkButton(self.get_parameter_frame, text="Get parameter", command=self.get_parameter, fg_color="#457b9d", hover_color="#3a5f7d", width=40)
        self.get_parameter_button.grid(row=0, column=1, padx=10, pady=5)
        # Add a entry to write the parameter ID
        self.parameter_id_input = ctk.CTkEntry(self.get_parameter_frame, border_color="#457b9d", text_color="gray", width=130, placeholder_text="type parameter ID...")
        self.parameter_id_input.grid(row=0, column=0, padx=10, pady=5)
        # Add a label to show the value of the parameter
        self.parameter_value_label = ctk.CTkLabel(self.get_parameter_frame, text="Value: ", font=("TkDefaultFont", 11))
        self.parameter_value_label.grid(row=3, column=0, padx=10, pady=5, sticky="w", columnspan=2)

        # Create a frame for set a parameter, with grey background
        self.set_parameter_frame2 = ctk.CTkFrame(self.main_tabview.tab("Parameters"), width=265, height=80)
        self.set_parameter_frame2.grid(row=0, column=1, padx=10, pady=5, sticky="we", columnspan=2)
        self.set_parameter_frame2.configure(fg_color="#1f1f1f")
        # Separate the frame into 2 vertical sections
        self.set_parameter_frame2.columnconfigure(0, weight=1)
        self.set_parameter_frame2.columnconfigure(1, weight=1)
        # Separate the frame into 2 horizontal section
        self.set_parameter_frame2.rowconfigure(0, weight=1)
        self.set_parameter_frame2.rowconfigure(1, weight=1)

        # Add a button to set the value of a parameter
        self.set_parameter_button = ctk.CTkButton(self.set_parameter_frame2, text="Set parameter", command=self.set_parameter, fg_color="#457b9d", hover_color="#3a5f7d", width=40)
        self.set_parameter_button.grid(row=1, column=0, padx=10, pady=5, columnspan=2, sticky="we")
        # Add a entry to write the parameter ID
        self.parameter_id_input_set = ctk.CTkEntry(self.set_parameter_frame2, border_color="#457b9d", text_color="gray", placeholder_text="type ID...", width=120)
        self.parameter_id_input_set.grid(row=0, column=0, padx=10, pady=5)
        # Add a entry to write the parameter value
        self.parameter_value_input = ctk.CTkEntry(self.set_parameter_frame2, border_color="#457b9d", text_color="gray", placeholder_text="type value...", width=100)
        self.parameter_value_input.grid(row=0, column=1, padx=10, pady=5)
        


        # Mission tab
        # Separate the tab into 2 horizontal sections
        self.main_tabview.tab("Mission").rowconfigure(0, weight=1)
        self.main_tabview.tab("Mission").rowconfigure(1, weight=1)

        # Separate the tab into 3 vertical sections
        self.main_tabview.tab("Mission").columnconfigure(0, weight=1)
        self.main_tabview.tab("Mission").columnconfigure(1, weight=1)
        self.main_tabview.tab("Mission").columnconfigure(2, weight=1)
        
        # Add a button to upload the flight plan
        self.upload_flight_plan_button = ctk.CTkButton(self.main_tabview.tab("Mission"), text="Upload Flight Plan", command=self.upload_flight_plan, fg_color="#457b9d", hover_color="#3a5f7d")
        self.upload_flight_plan_button.grid(row=0, column=0, padx=10, pady=10, sticky="we")

        # Add a button to execute the flight plan
        self.execute_flight_plan_button = ctk.CTkButton(self.main_tabview.tab("Mission"), text="Execute Flight Plan", command=self.execute_flight_plan, fg_color="#457b9d", hover_color="#3a5f7d")
        self.execute_flight_plan_button.grid(row=0, column=1, padx=10, pady=10, sticky="we")
        # This button is disabled by default
        self.execute_flight_plan_button.configure(state="disabled")

        # Add a button to clear the flight plan
        self.clear_flight_plan_button = ctk.CTkButton(self.main_tabview.tab("Mission"), text="Clear", command=self.clear_flight_plan, fg_color="#457b9d", hover_color="#3a5f7d")
        self.clear_flight_plan_button.grid(row=0, column=2, padx=10, pady=10, sticky="we")



        # Geofence tab
        # Separate the tab into 2 horizontal sections
        self.main_tabview.tab("Geofence").rowconfigure(0, weight=1)
        self.main_tabview.tab("Geofence").rowconfigure(1, weight=1)

        # Separate the tab into 3 vertical sections
        self.main_tabview.tab("Geofence").columnconfigure(0, weight=1)
        self.main_tabview.tab("Geofence").columnconfigure(1, weight=1)
        self.main_tabview.tab("Geofence").columnconfigure(2, weight=1)

        # Add a button to Enable the geofence
        self.enable_geofence_button = ctk.CTkButton(self.main_tabview.tab("Geofence"), text="Enable Geofence", command=self.enable_disable_geofence, fg_color="#457b9d", hover_color="#3a5f7d")
        self.enable_geofence_button.grid(row=0, column=0, padx=10, pady=10, sticky="we")

        # Add a button to upload the geofence
        self.upload_geofence_button = ctk.CTkButton(self.main_tabview.tab("Geofence"), text="Upload Fence", command=self.upload_geofence, fg_color="#457b9d", hover_color="#3a5f7d")
        self.upload_geofence_button.grid(row=0, column=1, padx=10, pady=10, sticky="we")

        # Add a selector to choose the geofence action
        self.geofence_action_selector = ctk.CTkOptionMenu(self.main_tabview.tab("Geofence"), values=["RTL", "Report", "Brake"], width=130, command=self.set_geofence_action, fg_color="#457b9d", dropdown_fg_color="#457b9d", button_color="#457b9d")
        self.geofence_action_selector.grid(row=0, column=2, padx=10, pady=10, sticky="we")

        # Add a button to clear the geofence and map
        self.clear_geofence_button = ctk.CTkButton(self.main_tabview.tab("Geofence"), text="Clear Geofence Points", command=self.clear_geofence, fg_color="#457b9d", hover_color="#3a5f7d")
        self.clear_geofence_button.grid(row=1, column=0, padx=10, pady=10, sticky="we", columnspan=3)



        # Right Panel
        # Create the main_frame_telemetry (for telemetry info)
        self.frame_telemetry = ctk.CTkFrame(self.main_frame, height=90)
        self.frame_telemetry.grid(row=0, column=6, padx=10, pady=10, rowspan=1, columnspan=2, sticky="we")
        # Color the frame
        self.frame_telemetry.configure(fg_color="#1f1f1f")
        # frame_telemetry can't be resized
        self.frame_telemetry.grid_propagate(False)

        # Separate the frame_telemetry into 2 vertical sections
        self.frame_telemetry.columnconfigure(0, weight=1)
        self.frame_telemetry.columnconfigure(1, weight=1)

        # Separate the frame_telemetry into 2 horizontal section
        self.frame_telemetry.rowconfigure(0, weight=1)
        self.frame_telemetry.rowconfigure(1, weight=1)

        # Create the labels for the telemetry info, 4 parameters (alt, heading, groundSpeed, battery)
        self.label_telemetry_alt = ctk.CTkLabel(self.frame_telemetry, text="Altitude: ",font=("TkDefaultFont", 11))
        self.label_telemetry_alt.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.label_telemetry_alt_value = ctk.CTkLabel(self.frame_telemetry, text="0.0", font=("TkDefaultFont", 11, "bold"))
        self.label_telemetry_alt_value.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.label_telemetry_hea = ctk.CTkLabel(self.frame_telemetry, text="Heading: ", font=("TkDefaultFont", 11))
        self.label_telemetry_hea.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.label_telemetry_hea_value = ctk.CTkLabel(self.frame_telemetry, text="0.0", font=("TkDefaultFont", 11, "bold"))
        self.label_telemetry_hea_value.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        self.label_telemetry_gs = ctk.CTkLabel(self.frame_telemetry, text="Ground Speed: ", font=("TkDefaultFont", 11))
        self.label_telemetry_gs.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.label_telemetry_gs_value = ctk.CTkLabel(self.frame_telemetry, text="0.0", font=("TkDefaultFont", 11, "bold"))
        self.label_telemetry_gs_value.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.label_telemetry_bat = ctk.CTkLabel(self.frame_telemetry, text="Battery: ", font=("TkDefaultFont", 11))
        self.label_telemetry_bat.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.label_telemetry_bat_value = ctk.CTkLabel(self.frame_telemetry, text="0.0", font=("TkDefaultFont", 11, "bold"))
        self.label_telemetry_bat_value.grid(row=1, column=1, padx=5, pady=5, sticky="e")


        # Create a frame for the video stream
        self.frame_stream = ctk.CTkFrame(self.main_frame, height=255)
        self.frame_stream.grid(row=1, column=6, padx=10, pady=10, rowspan=3, columnspan=2, sticky="we")
        # Color the frame
        self.frame_stream.configure(fg_color="#1f1f1f")
        # frame_telemetry can't be resized
        self.frame_stream.grid_propagate(False)

        # Create label for photo (no text, just the photo)
        self.label_photo = ctk.CTkLabel(self.frame_stream, text="", font=("TkDefaultFont", 11))
        self.label_photo.place(relx=0.5, rely=0.5, anchor="center")

        # Create the main_frame_control_pad (for control pad)
        self.main_frame_control_pad = ctk.CTkFrame(self.main_frame, height=150)
        self.main_frame_control_pad.grid(row=5, column=6, padx=10, pady=10, rowspan=1, columnspan=2, sticky="nswe")
        # Color the frame
        self.main_frame_control_pad.configure(fg_color="#1f1f1f")
        # frame can't be resized
        self.main_frame_control_pad.grid_propagate(False)

        # Separate the frame into 3 vertical sections
        self.main_frame_control_pad.columnconfigure(0, weight=1)
        self.main_frame_control_pad.columnconfigure(1, weight=1)
        self.main_frame_control_pad.columnconfigure(2, weight=1)

        # Separate the frame into 3 horizontal section
        self.main_frame_control_pad.rowconfigure(0, weight=1)
        self.main_frame_control_pad.rowconfigure(1, weight=1)
        self.main_frame_control_pad.rowconfigure(2, weight=1)
        

        # Create the control pad buttons
        self.control_pad_button_nw = ctk.CTkButton(self.main_frame_control_pad, text="NW", command=lambda : self.go("NorthWest"), fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_pad_button_nw.grid(row=0, column=0, padx=5, pady=5, sticky="we", ipady=10)

        self.control_pad_button_n = ctk.CTkButton(self.main_frame_control_pad, text="N", command=lambda : self.go("North"), fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_pad_button_n.grid(row=0, column=1, padx=5, pady=5, sticky="we", ipady=10)

        self.control_pad_button_ne = ctk.CTkButton(self.main_frame_control_pad, text="NE", command=lambda : self.go("NorthEast"), fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_pad_button_ne.grid(row=0, column=2, padx=5, pady=5, sticky="we", ipady=10)

        self.control_pad_button_w = ctk.CTkButton(self.main_frame_control_pad, text="W", command=lambda : self.go("West"), fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_pad_button_w.grid(row=1, column=0, padx=5, pady=5, sticky="we", ipady=10)

        self.control_pad_button_stop = ctk.CTkButton(self.main_frame_control_pad, text="STOP", command=lambda : self.go("Stop"), fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_pad_button_stop.grid(row=1, column=1, padx=5, pady=5, sticky="we", ipady=10)

        self.control_pad_button_e = ctk.CTkButton(self.main_frame_control_pad, text="E", command=lambda : self.go("East"), fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_pad_button_e.grid(row=1, column=2, padx=5, pady=5, sticky="we", ipady=10)

        self.control_pad_button_sw = ctk.CTkButton(self.main_frame_control_pad, text="SW", command=lambda : self.go("SouthWest"), fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_pad_button_sw.grid(row=2, column=0, padx=5, pady=5, sticky="we", ipady=10)

        self.control_pad_button_s = ctk.CTkButton(self.main_frame_control_pad, text="S", command=lambda : self.go("South"), fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_pad_button_s.grid(row=2, column=1, padx=5, pady=5, sticky="we", ipady=10)

        self.control_pad_button_se = ctk.CTkButton(self.main_frame_control_pad, text="SE", command=lambda : self.go("SouthEast"), fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_pad_button_se.grid(row=2, column=2, padx=5, pady=5, sticky="we", ipady=10)


        # Create the main_frame_control_buttons (for control buttons)
        self.main_frame_control_buttons = ctk.CTkFrame(self.main_frame, height=120)
        self.main_frame_control_buttons.grid(row=6, column=6, padx=10, pady=10, rowspan=1, columnspan=2, sticky="we")
        # Color the frame
        self.main_frame_control_buttons.configure(fg_color="#1f1f1f")
        # frame can't be resized
        self.main_frame_control_buttons.grid_propagate(False)

        # Separate the frame into 3 vertical sections
        self.main_frame_control_buttons.columnconfigure(0, weight=1)
        self.main_frame_control_buttons.columnconfigure(1, weight=1)
        self.main_frame_control_buttons.columnconfigure(2, weight=1)

        # Separate the frame into 2 horizontal section
        self.main_frame_control_buttons.rowconfigure(0, weight=1)
        self.main_frame_control_buttons.rowconfigure(1, weight=1)
        self.main_frame_control_buttons.rowconfigure(2, weight=1)

        # Create the control buttons
        self.control_button_arm = ctk.CTkButton(self.main_frame_control_buttons, text="Arm", command=self.arm, fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_button_arm.grid(row=0, column=0, padx=5, pady=5, sticky="we", ipady=10)

        self.control_button_take_off = ctk.CTkButton(self.main_frame_control_buttons, text="Take Off", command=self.take_off, fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_button_take_off.grid(row=0, column=1, padx=5, pady=5, sticky="we", ipady=10)

        self.control_button_RTL = ctk.CTkButton(self.main_frame_control_buttons, text="RTL", command=self.rtl, fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_button_RTL.grid(row=0, column=2, padx=5, pady=5, sticky="we", ipady=10)
        
        self.control_button_land = ctk.CTkButton(self.main_frame_control_buttons, text="Land", command=self.land, fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_button_land.grid(row=1, column=2, padx=5, pady=5, sticky="we", ipady=10)

        self.control_input_altitude = ctk.CTkEntry(self.main_frame_control_buttons, border_color="#457b9d", text_color="gray", placeholder_text="Altitude...", width=130)
        self.control_input_altitude.grid(row=1, column=0, padx=5, pady=5, sticky="we")

        self.control_button_change_altitude = ctk.CTkButton(self.main_frame_control_buttons, text="Change\nAltitude", command=self.change_altitude, fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_button_change_altitude.grid(row=1, column=1, padx=5, pady=5, sticky="we", ipady=10)
        
        # Create a frame for the camera functions (take picture, start stream, broker/websocket)
        self.frame_camera_buttons = ctk.CTkFrame(self.main_frame, height=75, width=265)
        self.frame_camera_buttons.grid(row=4, column=6, padx=10, pady=10, rowspan=1, columnspan=2, sticky="nswe")
        # Color the frame
        self.frame_camera_buttons.configure(fg_color="#1f1f1f")
        # frame_telemetry can't be resized
        self.frame_camera_buttons.grid_propagate(False)
        
        # Separate the frame_camera_buttons into 3 vertical sections
        self.frame_camera_buttons.columnconfigure(0, weight=1)
        self.frame_camera_buttons.columnconfigure(1, weight=1)
        self.frame_camera_buttons.columnconfigure(2, weight=1)
        
        self.button_picture = ctk.CTkButton(self.frame_camera_buttons, text="Picture", command=self.take_picture, fg_color="#457b9d", hover_color="#3a5f7d")
        self.button_picture.grid(row=0, column=0, padx=5, pady=3, sticky="nswe")

        self.button_stream = ctk.CTkButton(self.frame_camera_buttons, text="Stream", command=self.start_stream, fg_color="#457b9d", hover_color="#3a5f7d")
        self.button_stream.grid(row=0, column=1, padx=5, pady=3, sticky="nswe")

        self.button_broker = ctk.CTkButton(self.frame_camera_buttons, text="Broker", command=self.broker_websocket, fg_color="#457b9d", hover_color="#3a5f7d")
        self.button_broker.grid(row=0, column=2, padx=5, pady=3, sticky="nswe")
        
        # Create the disconnect button (Red)
        self.info_textbox_drones = ctk.CTkButton(self.main_frame, height=30 , text="Disconnect", command=self.disconnect, fg_color="#c1121f", hover_color="#a00f1c")
        self.info_textbox_drones.grid(row=7, column=6, padx=10, pady=10, rowspan=1, columnspan=2, sticky="nswe")

    def update_control_buttons(self):
        # Update the control buttons according to the state of the drone
        while True:
            if self.state == "connected":
                # connected: All buttons are disabled except for the arm button
                self.control_button_arm.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="normal")
                self.control_button_take_off.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_RTL.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_land.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_change_altitude.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
            if self.state == "armed":
                # armed: All buttons are disabled except for the take off button
                self.control_button_arm.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_take_off.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="normal")
                self.control_button_RTL.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_land.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_change_altitude.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
            if self.state == "takingOff" or self.state == "changingAltitude":
                # takingOff or changingAltitude: All buttons are disabled
                self.control_button_take_off.configure(fg_color="#fcbf49", hover_color="#fcbf49", state="disabled")
                self.control_button_arm.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_RTL.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_land.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_change_altitude.configure(fg_color="#fcbf49", hover_color="#fcbf49", state="disabled")
            if self.state == "flying":
                # flying: All buttons are disabled except for the RTL and land buttons
                self.control_button_take_off.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_arm.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_RTL.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="normal")
                self.control_button_land.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="normal")
                self.control_button_change_altitude.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="normal")
            if self.state == "returningHome" or self.state == "landing":
                # returnHome or landing: All the buttons are disabled
                self.control_button_RTL.configure(fg_color="#fcbf49", hover_color="#fcbf49", state="disabled")
                self.control_button_land.configure(fg_color="#fcbf49", hover_color="#fcbf49", state="disabled")
                self.control_button_arm.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_take_off.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_change_altitude.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
            if self.state == "onMission":
                # onMission: All buttons are disabled
                self.control_button_arm.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_take_off.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_RTL.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_land.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_change_altitude.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
            time.sleep(0.5)

    def telemetry(self, telemetry_info, drone_id):
        # Callback function to update the telemetry info in the main page view
        self.label_telemetry_alt_value.configure(text=telemetry_info['altitude'])
        self.label_telemetry_hea_value.configure(text=telemetry_info['heading'])
        self.label_telemetry_gs_value.configure(text=telemetry_info['groundSpeed'])
        self.label_telemetry_bat_value.configure(text=telemetry_info['battery'])
        self.state = telemetry_info['state']
        # Check if a marker for the drone has been created previously
        if self.dron_marker is not None:
            # Delete the marker
            self.dron_marker.delete()

        # Create a marker for the drone
        marker = self.map_widget.set_marker(telemetry_info['lat'], telemetry_info['lon'], text="Drone ", icon=self.plane_circle_1_image, marker_color_circle="green", marker_color_outside="black", text_color="black")
        # Center the map if is the first time
        if self.map_centered == False:
            self.centermap(telemetry_info['lat'], telemetry_info['lon'])
            self.map_centered = True
        # Update the marker
        self.dron_marker = marker

    def centermap(self, lat, lon):
        # Center the map in a specific location
        self.map_widget.set_position(lat, lon)
        print("Map centered.")



    # FUNCTIONS (BACKEND)

    def connect(self):
        # Connect to the autopilot service and to the drone
        self.client.publish("DashboardRemote/AutopilotService/connect/" + str(self.drone_id))

        if self.connected == True:
            time.sleep(1.5) # Wait for the connection to be established
            # Delete every element and start the main page view
            self.connect_label.grid_forget()
            self.info_textbox.grid_forget()
            self.label_logo.grid_forget()
            self.logo_frame.grid_forget()
            
            # Create the main page view
            self.set_main_page()

            # Start the update control buttons thread 
            t = threading.Thread(target=self.update_control_buttons)
            t.start()
            
        else:
            # Make the label invisible and show the button again
            self.connect_label.grid_forget()
            self.connect_button.grid(row=3, column=1, padx=10, pady=0, sticky="we", ipady=10)
            # Show an error message in the textbox, in red
            self.info_textbox.configure(state="normal")
            self.info_textbox.delete("1.0", "end")
            self.info_textbox.insert("1.0", "Error: Couldn't connect to the autopilot. Please, reset the application and try again.")
            self.info_textbox.configure(state="disabled")
            # The message should be in red
            self.info_textbox.configure(text_color="red")

    
    def disconnect(self):
        # Disconnect every drone
        self.client.publish("DashboardRemote/AutopilotService/disconnect/" + str(self.drone_id))

        # Restart the application
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def arm(self):
        # Arm the drone
        self.client.publish("DashboardRemote/AutopilotService/armDrone/" + str(self.drone_id))

    def take_off(self):
        # Take off the drone
        # Make the border of the entry white
        self.control_input_altitude.configure(border_color="white")
        # Take off the drone
        altitude = self.control_input_altitude.get()
        if altitude != "" and int(altitude) > 0:
            self.client.publish("DashboardRemote/AutopilotService/takeOff/" + str(self.drone_id), str(altitude))
        else:
            # Make the border of the entry red
            self.control_input_altitude.configure(border_color="red")
            print("Error: The altitude must be a positive number.")

    def change_altitude(self):
        # Change the altitude of the drone
        # Make the border of the entry white
        self.control_input_altitude.configure(border_color="white")
        # Change the altitude of the drone
        altitude = self.control_input_altitude.get()
        if altitude != "" and int(altitude) > 0:
            self.client.publish("DashboardRemote/AutopilotService/changeAltitude/" + str(self.drone_id), str(altitude))
        else:
            # Make the border of the entry red
            self.control_input_altitude.configure(border_color="red")
            print("Error: The altitude must be a positive number.")

    def go(self, direction):
        # Go to a direction
        if self.state == "flying":
            self.client.publish("DashboardRemote/AutopilotService/go/" + str(self.drone_id), str(direction))
        else:
            print("The vehicle is not flying.")

    def rtl(self):
        # Return to launch
        if self.state == "flying":
            self.client.publish("DashboardRemote/AutopilotService/returnToLaunch/" + str(self.drone_id))

    def land(self):
        # Land the drone
        if self.state == "flying":
            print("Landing...")
            self.client.publish("DashboardRemote/AutopilotService/land/" + str(self.drone_id))

    # Parameters:

    def get_parameter(self):
        # Get a parameter and show it in the label
        parameter_id = self.parameter_id_input.get()
        if parameter_id != "":
            # Make the border of the entry white
            self.parameter_id_input.configure(border_color="white")
            # Publish the message to get the parameter
            self.client.publish("DashboardRemote/AutopilotService/getParameter/" + str(self.drone_id), str(parameter_id))
            # Display that the parameter is being retrieved
            self.parameter_value_label.configure(text="Value: Loading...")
        else:
            # Make the border of the entry red
            self.parameter_id_input.configure(border_color="red")
            self.parameter_value_label.configure(text="Value: ")

    def set_parameter(self):
        # Set a parameter to a specific value
        parameter_id = str(self.parameter_id_input_set.get())
        parameter_value = str(self.parameter_value_input.get())
        message = parameter_id + "/" + parameter_value

        if parameter_id != "" and parameter_value != "":
            # Make the border of the entries white
            self.parameter_id_input_set.configure(border_color="white")
            self.parameter_value_input.configure(border_color="white")
            # Try to set the parameter, if it is not possible, show an error message
            try:
                self.client.publish("DashboardRemote/AutopilotService/setParameter/" + str(self.drone_id), str(message))
                print("Parameter set.")
            except:
                print("Error setting the parameter.")
        else:
            # Make the border of the entries red
            self.parameter_id_input_set.configure(border_color="red")
            self.parameter_value_input.configure(border_color="red")

    # Flight Plan:

    def upload_flight_plan(self):
        # Upload the flight plan
        if self.state == "connected" and len(self.mission_waypoints) > 0:
            # This button enables the execute flight plan button
            self.execute_flight_plan_button.configure(state="normal")

            # Upload the flight plan
            print("Uploading flight plan...")
            # Create a JSON string with the mission waypoints, with the following format:
            '''
            {
            "coordinates": [
                {"lat": 47.6205, "lon": -122.3493, "alt": 100},  // Coordinate 1
                {"lat": 47.6153, "lon": -122.3448, "alt": 150},  // Coordinate 2
                {"lat": 47.6102, "lon": -122.3425, "alt": 200}   // Coordinate 3
            ]
            }
            '''
            waypoints = {"coordinates": self.mission_waypoints}
            waypoints_json = json.dumps(waypoints)
            print(waypoints_json)
            
            self.client.publish("DashboardRemote/AutopilotService/uploadFlightPlan/" + str(self.drone_id), waypoints_json)

    def execute_flight_plan(self):
        # Execute the flight plan
        print("Executing flight plan...")
        self.client.publish("DashboardRemote/AutopilotService/executeFlightPlan/" + str(self.drone_id))

    def clear_flight_plan(self):
        # Clear the flight plan and the map
        # This button disables the execute flight plan button
        self.execute_flight_plan_button.configure(state="disabled")

        # Clear the flight plan
        print("Clearing flight plan...")
        # Delete every element from the mission waypoints list
        self.mission_waypoints = []
        # Delete every element from the mission markers list
        for marker in self.mission_markers:
            marker.delete()
        # Delete every element from the mission markers list
        self.mission_markers = []

    # GeoFence:

    def enable_disable_geofence(self):
        # Enable or disable the geofence
        # Check if the geofence is enabled or disabled
        if self.geofence_enabled:
            # Disable the geofence
            print("Disabling geofence...")
            # Publish the message to disable the geofence
            self.client.publish("DashboardRemote/AutopilotService/disableGeofence/" + str(self.drone_id))
            self.geofence_enabled = False

            # Make the button blue and change the text to "Enable Geofence"
            self.enable_geofence_button.configure(text="Enable Geofence", fg_color="#457b9d", hover_color="#3a5f7d")
        else:
            # Enable the geofence
            print("Enabling geofence...")
            # Publish the message to enable the geofence
            self.client.publish("DashboardRemote/AutopilotService/enableGeofence/" + str(self.drone_id))
            self.geofence_enabled = True

            # Make the button red and change the text to "Disable Geofence"
            self.enable_geofence_button.configure(text="Disable Geofence", fg_color="#c1121f", hover_color="#a00f1c")

    def upload_geofence(self):
        # Upload the geofence
        if len(self.geofence_points) < 3:
            print("Error: You need at least 3 points to create a geofence.")

        else:
            # Add the first point to the end of the list to close the geofence
            self.geofence_points.append(self.geofence_points[0])
            # Add the first point to the first position of the list, as the reference point
            self.geofence_points.insert(0, self.geofence_points[0])
            # Convert the list of points to a list of tuples
            fencelist = [(point["lat"], point["lon"]) for point in self.geofence_points]

            print(fencelist)
            # Convert the list fencelist to a JSON string
            fencelist = json.dumps(fencelist)

            # Publish the message to upload the geofence
            self.client.publish("DashboardRemote/AutopilotService/uploadGeofence/" + str(self.drone_id), fencelist)
            print("Uploading geofence...")
        
    def set_geofence_action(self, action):
        # Set the geofence action
        print("Geofence action set to:", action)
        if action == "RTL":
            action_id = 1
        elif action == "Report":
            action_id = 0
        elif action == "Brake":
            action_id = 4
        else:
            action_id = 1
        
        # Publish the message to upload the geofence
        self.client.publish("DashboardRemote/AutopilotService/actionGeofence/" + str(self.drone_id), str(action_id))
    
    def clear_geofence(self):
        # Clear the geofence points of the map
        print("Clearing geofence...")
        # Delete every element from the geofence points list
        self.geofence_points = []
        # Delete every element from the geofence markers list
        for marker in self.geofence_markers:
            marker.delete()
        # Delete every element from the geofence markers list
        self.geofence_markers = []

    # Map:

    def add_mission_waypoint_event(self, coords):
        # Add a mission waypoint to the map
        if self.control_input_altitude.get() == "" or int(self.control_input_altitude.get()) <= 0:
            # Make red the border of the entry
            self.control_input_altitude.configure(border_color="red")
        else:
            # Make the border color normal
            self.control_input_altitude.configure(border_color="#3117ea")
            # Add the altitude to the coords
            coords = (coords[0], coords[1], int(self.control_input_altitude.get()))
            print("Add Mission Waypoint:", coords)
            # Add the waypoint to the mission waypoints list
            entry = {"lat": coords[0], "lon": coords[1], "alt": int(self.control_input_altitude.get())}
            self.mission_waypoints.append(entry)
            new_marker = self.map_widget.set_marker(coords[0], coords[1], text=str(len(self.mission_waypoints)), marker_color_circle="red", marker_color_outside="black", text_color="red")
            # Add the new marker to the list
            self.mission_markers.append(new_marker)

    def add_geofence_point_event(self, coords):
        # Add a geofence point to the map
        print("Add Geofence Point:", coords)
        # Add the point to the geofence points list
        entry = {"lat": coords[0], "lon": coords[1]}
        self.geofence_points.append(entry)
        new_marker = self.map_widget.set_marker(coords[0], coords[1], text=str(len(self.geofence_points)), marker_color_circle="blue", marker_color_outside="black", text_color="blue")
        # Add the new marker to the list
        self.geofence_markers.append(new_marker)

    # Go to point:

    def go_to_point_event(self, coords):
        # Go to a point
        print("Go to:", coords)
        # Create the message to send to the autopilot
        message = str(coords[0]) + "/" + str(coords[1])
        # Go to a point
        self.client.publish("DashboardRemote/AutopilotService/goto/" + str(self.drone_id), str(message))
         
    # Camera:

    def take_picture(self):
        # Take a picture
        print("Taking picture...")
        self.client.publish("DashboardRemote/CameraService/takePicture/" + str(self.camera_id))

    def start_stream(self):
        # Start the video stream depending on the connection type (broker or socket)
        if self.video_connection_type == "broker":

            if self.streaming == False:

                # Start the video stream [via broker]
                self.button_stream.configure(text="Stop Stream", command=self.start_stream, fg_color="#c1121f", hover_color="#a00f1c")
                print("Starting stream...")
                self.client.publish("DashboardRemote/CameraService/startVideoStream/" + str(self.camera_id))
                self.streaming = True
                # Disable the broker_websocket button
                self.button_broker.configure(state="disabled")

            else:
                # Stop the video stream [via broker]
                self.button_stream.configure(text="Stream", command=self.start_stream, fg_color="#457b9d", hover_color="#3a5f7d")
                print("Stopping stream...")
                self.client.publish("DashboardRemote/CameraService/stopVideoStream/" + str(self.camera_id))
                self.streaming = False
                # Enable the broker_websocket button
                self.button_broker.configure(state="normal")

        elif self.video_connection_type == "websocket":

            # Start the video stream [via socket]
            if self.streaming == False:

                self.trigger_send_message(self.websocket, "DashboardRemote/CameraService/startVideoStream/" + str(self.camera_id))
                self.button_stream.configure(text="Stop Stream", command=self.start_stream, fg_color="#c1121f", hover_color="#a00f1c")
                print("Starting stream...")

                self.streaming = True

                # Disable the broker_websocket button
                self.button_broker.configure(state="disabled")

            else:
                # Stop the video stream [via websocket]
                self.button_stream.configure(text="Stream", command=self.start_stream, fg_color="#457b9d", hover_color="#3a5f7d")
                # Stop the loop
                self.client.publish("DashboardRemote/CameraService/stopVideoStream/" + str(self.camera_id))

                self.streaming = False

                # Enable the broker_websocket button
                self.button_broker.configure(state="normal")

    def broker_websocket(self):
        # Change the connection type
        if self.video_connection_type == "broker":
            self.video_connection_type = "websocket"
            # Change the button text to "Websocket"
            self.button_broker.configure(text="Websocket")
        else:
            self.video_connection_type = "broker"
            self.button_broker.configure(text="Broker")

    def process_frame(self, jpg_as_text):
        # Process the frame and show it in the image label
        # Convert to bytes
        image_bytes = base64.b64decode(jpg_as_text)

        # Create image PIL with the bytes
        image_pil = Image.open(io.BytesIO(image_bytes))
        # Resize the image
        image_pil = image_pil.resize((432, 234), Image.LANCZOS) # AR 1,85:1

        # Convert to custom tkinter image
        image_tk = ImageTk.PhotoImage(image_pil)

        # Show the image in the image label
        self.label_photo.configure(image=image_tk)



    # CONNECTIONS

    def configure(self):
        # Configure the drone and camera ids
        self.drone_id = int(self.drone_id_selector.get())
        self.camera_id = int(self.drone_id_selector.get())

        # Configure the connection to the broker
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "DashboardRemote", transport="websockets")
        self.client.on_connect = self.on_connect # Define the callback function for the connection
        self.client.on_message = self.on_message # Define the callback function for the message

        # Configure the external broker
        if self.broker_selector.get() == "hivemq":
            self.client.connect("broker.hivemq.com", 8000)
            print("Connected to broker.hivemq.com:8000")

        elif self.broker_selector.get() == "hivemq (certificate)":
            self.client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
            self.client.connect("broker.hivemq.com", 8884)
            print("Connected to broker.hivemq.com:8884")

        elif self.broker_selector.get() == "classpip (credentials)":
            self.client.username_pw_set(
                "classpip", "mimara00" # A CONFIRMAR
            )
            self.client.connect("classpip.upc.edu", 8000)
            print('- Autopilot Service: Connected to classpip.upc.edu:8000')

        else:
            print("Please, select a broker.")


        # Start the loop
        self.client.loop_start()
        self.client.subscribe("+/DashboardRemote/#")

    def on_connect(self, client, userdata, flags, rc):
        # Callback function for the connection
        if rc == 0:
            print("Connection OK")
            self.connected = True

        else:
            print("Bad connection")

    def on_message(self, client, userdata, message):
        # Callback function for the message
        # Process the message
        splitted = message.topic.split("/")
        # Extract the information of the message
        origin = splitted[0]
        destination = splitted[1]
        command = splitted[2]

        # If origin is CameraService:
        if origin == "CameraService":
            # Check the camera id
            camera_id = splitted[3]
            if camera_id == str(self.camera_id):
                # Process the message from the camera
                if command == "picture":
                    # Process the frame
                    self.process_frame(message.payload)
                
                if command == "videoFrame":
                    # Extract the jpg as text
                    img = base64.b64decode(message.payload)
                    # Convert into numpy array from buffer
                    npimg = np.frombuffer(img, dtype=np.uint8)
                    # Decode the image to Original Frame
                    img = cv.imdecode(npimg, 1)
                    # Show the image
                    img = cv.resize(img, (280, 135))
                    cv.imshow('Stream', img)
                    cv.waitKey(1)

                if command == "getCameraIP":
                    # Extract the camera ip
                    camera_ip = str(message.payload.decode("utf-8"))
                    # Change the ip of the websocket
                    print ("Cambio de ip: ", camera_ip)
                    self.ip = camera_ip
                    self.url = "ws://" + camera_ip + ":8765"

                    # Then, start the websocket
                    self.start_websocket()
                    

        # If origin is AutopilotService:
        if origin == "AutopilotService":
            # Check the drone id
            drone_id = splitted[3]
            if drone_id == str(self.drone_id):
                # Process the message from the autopilot
                if command == "telemetryInfo":
                    # Extract the telemetry info
                    telemetry_info = json.loads(message.payload)
                    # Call the telemetry function
                    self.telemetry(telemetry_info, self.drone_id)
                
                if command == "getParameterResponse":
                    # Extract the parameter value
                    parameter_value = message.payload.decode("utf-8")
                    # Show the parameter value in the label
                    self.parameter_value_label.configure(text="Value: " + str(parameter_value))



    # WEB SOCKET 
    
    def start_websocket(self):
        # Function to start the loop
        def start_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        # Create the loop
        self.loop = asyncio.new_event_loop()
        print ("Inicio con url: ", self.url)
        self.loop.create_task(self.listen(self.url))

        # Start the loop in a new thread
        t = threading.Thread(target=start_loop, args=(self.loop,))
        t.start()

    async def listen(self, url):
        # Listen to the websocket of the server
        self.websocket = await websockets.connect(url)
        async for message in self.websocket:
            # Receive the message
            if self.streaming == True:
                message = await self.websocket.recv()
                self.process_frame(message)

    async def send_message(self, message):
        # Send a message to the websocket
        print("Sending: ", message)
        await self.websocket.send(message)

    def trigger_send_message(self, websocket, message):
        # Trigger the send message function
        asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def get_ip(self):
        # Get the ip of the websocket server
        self.client.publish("DashboardRemote/CameraService/getCameraIP/" + str(self.camera_id))

# Run the app
app = App()
app.mainloop()