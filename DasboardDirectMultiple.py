import customtkinter as ctk
import tkintermapview as tkmap
import os
import sys
import time
import threading
import json
from PIL import Image, ImageTk

# Import the Dron class
from Drone import Drone as Dron

# Night mode
ctk.set_appearance_mode("dark")

# Create App class
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create the app
        self.geometry("900x600")
        self.title("Dashboard Direct Multiple")
        self.resizable(False, False)

        # CLASS VARIABLES
        self.mission_waypoints = []
        self.mission_markers = []

        self.geofence_points = []
        self.geofence_markers = []
        self.geofence_enabled = False
        
        # Drone selector
        self.drone_selector_id = 1

        # Drone selected
        self.dron = None

        # Drones
        self.drones = []

        # Load images
        current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        self.plane_circle_1_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "images", "drone_circle.png")).resize((35, 35)))
        self.logo = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "images", "logo.jpg")).resize((400, 400)))

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
        self.info_textbox.insert("1.0", "Welcome to DashboardDirect Multiple.\nThis version of Dashboard Direct allows you to\ncontrol several drones simultaneously (10 maximum).\n\nPlease, click the 'Connect' button to start.")
        # Add a version number to the textbox
        self.info_textbox.insert("end", "\n\nPATCH NOTES:\n\n- Version: 0.1.0: Initial release\n\n- Version: 0.1.1: Connect and telemetry info added.\n\n- Version: 0.1.2: Control and pad buttons added.\n\n- Version: 1.0.0: All basic functions operative.\n\n- Version: 1.0.1: Map added.\n\n- Version: 1.0.2: Bug fixes.\n\n- Version: 2.0.0: Dron selector added (for multiple drones).\n\n- Version: 2.0.1: Arm all and take off all added.\n\n- Version: 3.0.0: Final release.")
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

        # Create a option selector for the number of drones (1 to 10)
        self.id_drone_number = ctk.CTkOptionMenu(self.main_frame, values=["Select swarm size...", "2","3", "4", "5","6", "7", "8","9", "10" ], width=130, fg_color="#457b9d", dropdown_fg_color="#457b9d", button_color="#457b9d")
        self.id_drone_number.grid(row=6, column=6, padx=10, pady=0, ipady=0, columnspan=1, sticky="we")

        # Create a option selector for the mode (real or simulation)
        self.mode_selector = ctk.CTkOptionMenu(self.main_frame, values=["Simulation", "Real"], width=130, fg_color="#457b9d", dropdown_fg_color="#457b9d", button_color="#457b9d")
        self.mode_selector.grid(row=6, column=7, padx=10, pady=0, ipady=0, columnspan=1, sticky="we")



    # FUNCTIONS (FRONTEND)

    def on_button_connect_click(self):
        # If the swarm size is not selected, show an error message
        if self.id_drone_number.get() == "Select swarm size...":
            self.info_textbox.configure(state="normal")
            self.info_textbox.delete("1.0", "end")
            self.info_textbox.insert("1.0", "Error: Please, select the swarm size.")
            self.info_textbox.configure(state="disabled")
            self.info_textbox.configure(text_color="red")
            return
        else:
            # Create the drones (1 to 10 depending on the selection) [i is the ID of the drone]
            for i in range(1, int(self.id_drone_number.get()) + 1):
                self.drones.append(Dron(i))

            # Before finishing, select the first drone as the selected drone
            self.dron = self.drones[0]
            print("Drone selected: " + str(self.dron))
            
            # Make the button invisible and substitute it with a label
            self.connect_button.grid_forget()
            self.id_drone_number.grid_forget()
            self.mode_selector.grid_forget()
            self.connect_label = ctk.CTkLabel(self.main_frame, text="Connecting...")
            self.connect_label.grid(row=7, column=6, padx=10, pady=0, sticky="nswe", columnspan=2)


            # Connect to the autopilot 1000ms later
            self.after(1000, self.connect)

    def set_main_page(self):
        # Create the main page view

        # Add a map to the main frame
        self.map_widget = tkmap.TkinterMapView(self.main_frame)
        self.map_widget.grid(row=0, column=0, padx=10, pady=10, rowspan=6, columnspan=6, sticky="nswe")
        # Change the map style to satellite
        x = -35.3633515
        y = 149.1652412
        z = 15
        self.map_widget.set_tile_server("https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", max_zoom=22)
        self.map_widget.set_position(x, y)
    
        # Create the main_frame_telemetry (for telemetry info)
        self.frame_telemetry = ctk.CTkFrame(self.main_frame, height=60)
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
        


        # Create a 1 row frame to select the drone that is being controlled

        self.frame_drone_selector = ctk.CTkFrame(self.main_frame, height=25)
        self.frame_drone_selector.grid(row=1, column=6, padx=10, pady=10, rowspan=1, columnspan=2, sticky="we")
        # Color the frame
        self.frame_drone_selector.configure(fg_color="#1f1f1f")
        # frame_telemetry can't be resized
        self.frame_drone_selector.grid_propagate(False)

        # Separate the frame_telemetry into 3 vertical sections
        self.frame_drone_selector.columnconfigure(0, weight=1)
        self.frame_drone_selector.columnconfigure(1, weight=1)
        self.frame_drone_selector.columnconfigure(2, weight=1)

        # Create the drone selector (1 button left, 1 label center, 1 button right)
        self.drone_selector_left = ctk.CTkButton(self.frame_drone_selector, text="<", fg_color="#457b9d", hover_color="#3a5f7d", command=self.select_previous_drone, height=15, width=15)
        self.drone_selector_left.grid(row=0, column=0, padx=2, pady=2, sticky="w")

        self.drone_selector_label = ctk.CTkLabel(self.frame_drone_selector, text="Drone ID: 1", font=("TkDefaultFont", 10), height=15)
        self.drone_selector_label.grid(row=0, column=1, padx=0, pady=2, sticky="we")

        self.drone_selector_right = ctk.CTkButton(self.frame_drone_selector, text=">", fg_color="#457b9d", hover_color="#3a5f7d", command=self.select_next_drone, height=15, width=15)
        self.drone_selector_right.grid(row=0, column=2, padx=2, pady=2, sticky="e")


        
        # Create the main_frame_control_pad (for control pad)
        
        self.main_frame_control_pad = ctk.CTkFrame(self.main_frame)
        self.main_frame_control_pad.grid(row=2, column=6, padx=10, pady=10, rowspan=1, columnspan=2, sticky="nswe")
        # Color the frame
        self.main_frame_control_pad.configure(fg_color="#1f1f1f")
        # frame_telemetry can't be resized
        self.main_frame_control_pad.grid_propagate(False)

        # Separate the frame_telemetry into 3 vertical sections
        self.main_frame_control_pad.columnconfigure(0, weight=1)
        self.main_frame_control_pad.columnconfigure(1, weight=1)
        self.main_frame_control_pad.columnconfigure(2, weight=1)

        # Separate the frame_telemetry into 3 horizontal section
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
        self.main_frame_control_buttons.grid(row=3, column=6, padx=10, pady=10, rowspan=1, columnspan=2, sticky="we")
        # Color the frame
        self.main_frame_control_buttons.configure(fg_color="#1f1f1f")
        # frame_telemetry can't be resized
        self.main_frame_control_buttons.grid_propagate(False)

        # Separate the frame_telemetry into 3 vertical sections
        self.main_frame_control_buttons.columnconfigure(0, weight=1)
        self.main_frame_control_buttons.columnconfigure(1, weight=1)
        self.main_frame_control_buttons.columnconfigure(2, weight=1)

        # Separate the frame_telemetry into 2 horizontal section
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
        
        self.control_input_altitude = ctk.CTkEntry(self.main_frame_control_buttons, border_color="#457b9d", text_color="gray", placeholder_text="Altitude...", width=130)
        self.control_input_altitude.grid(row=1, column=2, padx=5, pady=5, sticky="we")

        self.control_button_arm_all = ctk.CTkButton(self.main_frame_control_buttons, text="Arm All", command=self.arm_all, fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_button_arm_all.grid(row=1, column=0, padx=5, pady=5, sticky="we", ipady=10)

        self.control_button_take_off_all = ctk.CTkButton(self.main_frame_control_buttons, text="Take Off All", command=self.take_off_all, fg_color="#457b9d", hover_color="#3a5f7d")
        self.control_button_take_off_all.grid(row=1, column=1, padx=5, pady=5, sticky="we", ipady=10)

        # Create the disconnect button (Red)
        self.info_textbox_drones = ctk.CTkButton(self.main_frame, height=60 , text="Disconnect", command=self.disconnect, fg_color="#c1121f", hover_color="#a00f1c")
        self.info_textbox_drones.grid(row=4, column=6, padx=10, pady=10, rowspan=1, columnspan=2, sticky="nswe")

        

    # UPDATE CONTROL BUTTONS
    def update_control_buttons(self):
        while True:
            # print("Drone ID: " + str(self.drone_selector_id) + " - State: " + self.dron.state)
            # Update the control buttons depending on the state of the drone (for the selected drone)
            if self.dron.state == "connected":
                # Change the color of the arm button to blue
                self.control_button_arm.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="normal")
                self.control_button_arm_all.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="normal")
                # The other buttons are disabled
                self.control_button_take_off.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_RTL.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_take_off_all.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
            if self.dron.state == "armed":
                # Change the color of the arm button to green
                self.control_button_arm.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_arm_all.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                # The take off button is enabled and the RTL button is disabled
                self.control_button_take_off.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="normal")
                self.control_button_RTL.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_take_off_all.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="normal")
            if self.dron.state == "takingOff":
                # Change the color of the take off button to orange
                self.control_button_take_off.configure(fg_color="#fcbf49", hover_color="#fcbf49", state="disabled")
                self.control_button_take_off_all.configure(fg_color="#fcbf49", hover_color="#fcbf49", state="disabled")
                # The arm button is disabled and the RTL button is disabled
                self.control_button_arm.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_RTL.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="disabled")
                self.control_button_arm_all.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
            if self.dron.state == "flying":
                # Change the color of the take off button to green
                self.control_button_take_off.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_take_off_all.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                # The arm button is disabled and the RTL button is enabled
                self.control_button_arm.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_RTL.configure(fg_color="#457b9d", hover_color="#3a5f7d", state="normal")
                self.control_button_arm_all.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
            if self.dron.state == "returningHome":
                # Change the color of the RTL button to orange
                self.control_button_RTL.configure(fg_color="#fcbf49", hover_color="#fcbf49")
                # The arm button is disabled and the take off button is disabled
                self.control_button_arm.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_take_off.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_arm_all.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
                self.control_button_take_off_all.configure(fg_color="#80ed99", hover_color="#4ea167", state="disabled")
            time.sleep(0.5)



    # FUNCTIONS (BACKEND)
        
    def connect(self):
        # The connection ports are the following [10 possible drones]:
        self.ports = [5763, 5773, 5783, 5793, 5803, 5813, 5823, 5833, 5843, 5853]

        # Depending if real time or simulation mode is selected, the connection string will be different
        mode_selector = str(self.mode_selector.get())

        if mode_selector == "Simulation":
            print('Simulation mode selected')
            # Connect every drone to the autopilot
            for dron in self.drones:
                dron.connect_trigger( "tcp:127.0.0.1:" + str(self.ports[dron.ID - 1]), True)
                # Wait 1 second and check if the drone is connected
                time.sleep(1)
                if dron.state == "connected":
                    print("Drone " + str(dron.ID) + " connected.")
                else:
                    print("Error: Drone " + str(dron.ID) + " couldn't connect.")
        else:
            # A MODIFICAR (CUANDO SEPA COMO SE HACE DESDE EL AUTOPILOT SERVICE)
            print ('Real mode selected')
            # connection_string = "/dev/ttyS0"
            connection_string = "com7"
            # connection_string = "udp:127.0.0.1:14550"

        # Check that every drone is connected
        verification = True
        for dron in self.drones:
            if dron.state !="connected":
                verification = False
                break
        if verification:
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

            # Create a list for the markers of the drones
            self.drones_markers = [None] * len(self.drones)

            # Start the telemetry info for every drone
            for dron in self.drones:
                dron.send_telemetry_info_trigger(self.telemetry, False)

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
        for dron in self.drones:
            dron.disconnect()

        # Restart the application
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def telemetry(self, telemetry_info, drone_id):
        # Callback function to update the telemetry info in the main page view
        # Check if the drone ID is the same as the selected drone
        if drone_id == self.drone_selector_id:
            # Update the telemetry info
            #self.label_telemetry_lat_value.configure(text=telemetry_info['lat'])
            #self.label_telemetry_lon_value.configure(text=telemetry_info['lon'])
            self.label_telemetry_alt_value.configure(text=telemetry_info['altitude'])
            self.label_telemetry_hea_value.configure(text=telemetry_info['heading'])
            self.label_telemetry_gs_value.configure(text=telemetry_info['groundSpeed'])
            self.label_telemetry_bat_value.configure(text=telemetry_info['battery'])

        # Check if a marker for the drone has been created previously
        if self.drones_markers[drone_id - 1] != None:
            # Delete the previous marker
            self.drones_markers[drone_id - 1].delete()

        # Print the drone on the map
        marker = self.map_widget.set_marker(telemetry_info['lat'], telemetry_info['lon'], text="Drone " + str(drone_id), icon=self.plane_circle_1_image, marker_color_circle="green", marker_color_outside="black", text_color="black")

        # Add the marker to the list
        self.drones_markers[drone_id - 1] = marker

    def arm(self):
        # Arm the drone
        if self.dron.state == "connected":
            self.dron.arm_trigger(False)
            print("Vehicle armed.")
        else:
            print("The vehicle is not connected.")

        # the vehicle will disarm automatically is takeOff does not come soon, the arm function does this automatically

    def arm_all(self):
        # Arm all the drones
        for dron in self.drones:
            dron.arm_trigger(False)

    def take_off(self):
        # Take off the drone
        if self.dron.state == "armed":
            # Make the border of the entry white
            self.control_input_altitude.configure(border_color="white")
            altitude = self.control_input_altitude.get()
            if altitude != "" and int(altitude) > 0:
                self.dron.take_off_trigger(int(self.control_input_altitude.get()), False)
            else:
                # Make the border of the entry red
                self.control_input_altitude.configure(border_color="red")
                print("Error: The altitude must be a positive number.")
        else:
            print("The vehicle is not armed.")

    def take_off_all(self):
        # Take off all the drones
        # Make the border of the entry white
        self.control_input_altitude.configure(border_color="white")
        altitude = self.control_input_altitude.get()
        if altitude != "" and int(altitude) > 0:
            for dron in self.drones:
                dron.take_off_trigger(int(self.control_input_altitude.get()), False)
        else:
            # Make the border of the entry red
            self.control_input_altitude.configure(border_color="red")
            print("Error: The altitude must be a positive number.")

    def go(self, direction):
        # Go to a direction
        if self.dron.state == "flying":
            self.dron.go_order(direction)
        else:
            print("The vehicle is not flying.")

    def rtl(self):
        # Return to launch
        if self.dron.state == "flying":
            self.dron.return_to_launch_trigger(False)

    # DRONE SELECTOR:

    def select_previous_drone(self):
        # Select the previous drone
        if self.drone_selector_id > 1:
            self.drone_selector_id -= 1
            self.drone_selector_label.configure(text="Drone ID: " + str(self.drone_selector_id))
            self.dron = self.drones[self.drone_selector_id - 1]
        else:
            self.drone_selector_id = len(self.drones)
            self.drone_selector_label.configure(text="Drone ID: " + str(self.drone_selector_id))
            self.dron = self.drones[self.drone_selector_id - 1]

    def select_next_drone(self):
        # Select the next drone
        if self.drone_selector_id < len(self.drones):
            self.drone_selector_id += 1
            self.drone_selector_label.configure(text="Drone ID: " + str(self.drone_selector_id))
            self.dron = self.drones[self.drone_selector_id - 1]
        else:
            self.drone_selector_id = 1
            self.drone_selector_label.configure(text="Drone ID: " + str(self.drone_selector_id))
            self.dron = self.drones[self.drone_selector_id - 1]
 

# Run the app
app = App()
app.mainloop()