
import cv2
import os
import pytesseract
from ultralytics import YOLO
import pandas as pd
from datetime import datetime
from shapely.geometry import Polygon, Point
import hashlib

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Define the folder containing your images
image_folder = "cctv_images"
output_excel = "Customer_Count.xlsx"

# Define the universal counter polygon boundary (adjusted for all stores)
COUNTER_POLYGON = Polygon([(230, 280), (850, 280), (850, 520), (230, 520)])

# Initialize result storage
data = []

# To avoid duplicate counts
last_seen_positions = []

def hash_position(xy, tolerance=30):
    return hashlib.md5(f"{round(xy[0]/tolerance)}-{round(xy[1]/tolerance)}".encode()).hexdigest()

def extract_datetime_from_filename(filename):
    try:
        parts = filename.split("_")[-1].split(".")[0]
        dt = datetime.strptime(parts, "%Y%m%d%H%M%S")
        return dt.date().isoformat(), dt.time().isoformat()
    except Exception as e:
        return "N/A", "N/A"

# Process each image
for filename in sorted(os.listdir(image_folder)):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        image_path = os.path.join(image_folder, filename)
        image = cv2.imread(image_path)

        # Get timestamp from filename
        snap_date, snap_time = extract_datetime_from_filename(filename)

        # Detect people
        results = model(image)
        boxes = results[0].boxes
        person_count = 0
        employee_count = 0
        current_positions = []

        for box in boxes:
            cls = int(box.cls[0])
            if cls == 0:  # person class
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                pos_hash = hash_position((center_x, center_y))

                if pos_hash not in last_seen_positions:
                    point = Point(center_x, center_y)
                    if COUNTER_POLYGON.contains(point):
                        employee_count += 1
                    else:
                        person_count += 1
                    current_positions.append(pos_hash)

        last_seen_positions = current_positions  # update memory

        # Get system timestamp
        system_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append data
        data.append([snap_date, snap_time, system_timestamp, filename, person_count, employee_count])

# Create DataFrame
df = pd.DataFrame(data, columns=["Snap Date", "Snap Time", "System Time Stamp", "Snapshot Name", "Customer Count in Image", "Employee Count"])

# Save to Excel
df.to_excel(output_excel, index=False)
print(f"Saved output to {output_excel}")
