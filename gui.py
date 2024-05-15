import tkinter as tk
from tkinter import ttk
import redis
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import threading

# Redis connection
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

class MedicalDataMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Data Monitoring System")

        self.patient_id_label = ttk.Label(root, text="Patient ID:")
        self.patient_id_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.patient_id_entry = ttk.Entry(root, width=15)
        self.patient_id_entry.grid(row=0, column=1, padx=10, pady=10)

        self.search_button = ttk.Button(root, text="Search", command=self.search_patient)
        self.search_button.grid(row=0, column=2, padx=10, pady=10)

        self.chart_frame = ttk.Frame(root)
        self.chart_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Start Redis Pub/Sub listener in a separate thread
        self.pubsub_thread = threading.Thread(target=self.redis_listener)
        self.pubsub_thread.daemon = True
        self.pubsub_thread.start()

    def search_patient(self):
        self.update_plot()

    def update_plot(self):
        patient_id = self.patient_id_entry.get()
        if patient_id:
            vital_signs_json = redis_client.get(f'patient:{patient_id}:vital_signs')
            if vital_signs_json:
                vital_signs = json.loads(vital_signs_json)

                # Plot data
                self.ax.clear()
                self.ax.plot(vital_signs,  color='blue')
                self.ax.set_xlabel('Time')
                self.ax.set_ylabel('Value')
                self.ax.set_title(f'Vital Signs for Patient {patient_id}')
                self.fig.tight_layout()
                self.canvas.draw()

    def redis_listener(self):
        pubsub = redis_client.pubsub()
        pubsub.subscribe('vital_signs_update')
        for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                patient_id = data['patient_id']
                if str(patient_id) == self.patient_id_entry.get():
                    self.update_plot()

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalDataMonitorApp(root)
    root.mainloop()
