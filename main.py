import os
import face_recognition
import pandas as pd
from datetime import datetime
import multiprocessing
from tqdm import tqdm
import pickle
from PIL import UnidentifiedImageError

# Configuration
IMAGE_DIR = "cctv_images"
THRESHOLD = 0.6
MODEL = "hog"  # Faster CPU model
NUM_PROCESSES = os.cpu_count()  # Match your 8 logical cores
BATCH_SIZE = 50  # Images per process
EMPLOYEE_ENCODINGS_PATH = "employee_encodings.pkl"  # Create this file first

def get_location(filename):
    return filename.split("_", 1)[0]

def process_image(args):
    filename, employee_encodings = args
    location = get_location(filename)
    image_path = os.path.join(IMAGE_DIR, filename)
    
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image, model=MODEL)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        # Filter out employees
        customer_encodings = []
        for encoding in face_encodings:
            if employee_encodings:
                matches = face_recognition.compare_faces(employee_encodings, encoding, THRESHOLD)
                if not any(matches):
                    customer_encodings.append(encoding)
            else:
                customer_encodings.append(encoding)
        
        return (location, customer_encodings)
    except (UnidentifiedImageError, Exception):
        return (location, [])

def process_images(image_dir):
    # Load employee encodings
    employee_encodings = []
    if os.path.exists(EMPLOYEE_ENCODINGS_PATH):
        with open(EMPLOYEE_ENCODINGS_PATH, "rb") as f:
            employee_encodings = pickle.load(f)

    # Prepare tasks
    image_files = [f for f in os.listdir(image_dir) if f.endswith(".jpg")]
    tasks = [(f, employee_encodings) for f in image_files]

    # Multiprocessing with progress bar
    unique_faces = {}
    with multiprocessing.Pool(NUM_PROCESSES) as pool:
        results = list(tqdm(pool.imap(process_image, tasks, chunksize=BATCH_SIZE), 
                        total=len(tasks), 
                        desc="Processing Images"))
        
    # Aggregate results
    for location, encodings in results:
        if location not in unique_faces:
            unique_faces[location] = []
        unique_faces[location].extend(encodings)

    # Deduplicate faces per location
    customer_counts = {}
    for loc, encodings in unique_faces.items():
        unique = []
        for enc in encodings:
            if not face_recognition.compare_faces(unique, enc, THRESHOLD):
                unique.append(enc)
        customer_counts[loc] = len(unique)

    # Generate report
    df = pd.DataFrame(
        {
            "System Time Stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Location": loc,
            "Customer Count in Images": count,
        }
        for loc, count in customer_counts.items()
    )
    
    df.to_excel("customer_count_report.xlsx", index=False)
    print("\n✅ Report generated with optimized processing!")

if __name__ == "__main__":
    process_images(IMAGE_DIR)























# import os
# import face_recognition
# import pandas as pd
# from datetime import datetime
# from tqdm import tqdm
# import warnings
# from PIL import UnidentifiedImageError  # <-- Add this

# # Configuration
# IMAGE_DIR = "cctv_images"  # Ensure this path is correct
# THRESHOLD = 0.6
# EMPLOYEE_ENCODINGS = []

# def get_location(filename):
#     return filename.split("_", 1)[0]

# def process_images(image_dir):
#     location_data = {}
#     corrupted_files = []  # Track problematic files

#     image_files = [f for f in os.listdir(image_dir) if f.endswith(".jpg")]
#     progress_bar = tqdm(image_files, desc="Processing Images", unit="image")

#     for filename in progress_bar:
#         location = get_location(filename)
#         if location not in location_data:
#             location_data[location] = {"encodings": [], "count": 0}

#         image_path = os.path.join(image_dir, filename)

#         try:
#             # Attempt to load the image
#             image = face_recognition.load_image_file(image_path)
#         except (UnidentifiedImageError, FileNotFoundError) as e:
#             corrupted_files.append(filename)
#             continue  # Skip this file

#         # Rest of your code for face detection...
#         face_locations = face_recognition.face_locations(image)
#         face_encodings = face_recognition.face_encodings(image, face_locations)

#         for encoding in face_encodings:
#             if EMPLOYEE_ENCODINGS:
#                 matches = face_recognition.compare_faces(EMPLOYEE_ENCODINGS, encoding, THRESHOLD)
#                 if any(matches):
#                     continue

#             matches = face_recognition.compare_faces(
#                 location_data[location]["encodings"], encoding, THRESHOLD
#             )
#             if not any(matches):
#                 location_data[location]["encodings"].append(encoding)
#                 location_data[location]["count"] += 1

#         progress_bar.set_postfix({"Location": location})

#     # Generate report
#     df = pd.DataFrame(
#         {
#             "System Time Stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "Location": loc,
#             "Customer Count in Images": data["count"],
#         }
#         for loc, data in location_data.items()
#     )
    
#     df.to_excel("customer_count_report.xlsx", index=False)

#     # Print corrupted files (if any)
#     if corrupted_files:
#         print("\n⚠️ Skipped corrupted/unreadable files:")
#         for file in corrupted_files:
#             print(f"  - {file}")

#     print("\n✅ Report generated: customer_count_report.xlsx")

# if __name__ == "__main__":
#     process_images(IMAGE_DIR)