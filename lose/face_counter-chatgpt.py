import face_recognition
import os
import numpy as np
from sklearn.cluster import DBSCAN
from collections import Counter
import matplotlib.pyplot as plt

# === CONFIG ===
IMAGE_FOLDER = "cctv_images"  # path_to_your_image_folder
EMPLOYEE_THRESHOLD = 5  # Faces seen >= this many times are considered employees

# === STEP 1: Load all images ===
def load_images_from_folder(folder):
    return sorted([
        os.path.join(folder, filename) for filename in os.listdir(folder)
        if filename.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])

# === STEP 2: Encode faces ===
def encode_faces(image_paths):
    encodings = []
    timestamps = []
    for path in image_paths:
        try:
            image = face_recognition.load_image_file(path)
            face_encs = face_recognition.face_encodings(image)
            for face_enc in face_encs:
                encodings.append(face_enc)
                timestamps.append(path)
        except Exception as e:
            print(f"Error processing {path}: {e}")
    return np.array(encodings), timestamps

# === STEP 3: Cluster face encodings ===
def cluster_faces(encodings, eps=0.5, min_samples=2):
    if len(encodings) == 0:
        return []
    model = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
    labels = model.fit_predict(encodings)
    return labels

# === STEP 4: Count appearances ===
def count_faces_by_label(labels):
    return Counter(labels)

# === STEP 5: Split into employees/customers ===
def separate_roles(label_counts, threshold):
    employees = [label for label, count in label_counts.items() if label != -1 and count >= threshold]
    customers = [label for label, count in label_counts.items() if label != -1 and count < threshold]
    return employees, customers

# === STEP 6: Main ===
def main():
    image_paths = load_images_from_folder(IMAGE_FOLDER)
    print(f"Loaded {len(image_paths)} images")

    encodings, timestamps = encode_faces(image_paths)
    print(f"Detected {len(encodings)} faces")

    labels = cluster_faces(encodings)
    print(f"Clustered into {len(set(labels)) - (1 if -1 in labels else 0)} unique people")

    label_counts = count_faces_by_label(labels)

    employees, customers = separate_roles(label_counts, EMPLOYEE_THRESHOLD)

    print("\n=== Results ===")
    print(f"Total unique people: {len(set([l for l in labels if l != -1]))}")
    print(f"Employees (seen >= {EMPLOYEE_THRESHOLD} times): {employees}")
    print(f"Customers (seen < {EMPLOYEE_THRESHOLD} times): {customers}")

    # Optional: Plot frequency histogram
    plt.bar(label_counts.keys(), label_counts.values(), color="skyblue")
    plt.xlabel("Cluster Label")
    plt.ylabel("Appearance Count")
    plt.title("Frequency of Face Clusters")
    plt.show()

if __name__ == "__main__":
    main()
