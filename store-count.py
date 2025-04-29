import os

def extract_store_names(folder_path):
    store_names = set()
    num_of_images = 0
    store_names_obj = {}  # Format: {location: {"name": [], "images": 0}}
    
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            store_name = filename.split('_')[0].strip()
            store_names.add(store_name)

            if store_name not in store_names_obj:
                store_names_obj[store_name] = {"count": 0}
                store_names_obj[store_name]["count"] += 1
                continue

            if store_name in store_names_obj:
                store_names_obj[store_name]["count"] += 1

    sorted_stores = sorted(store_names)
    for idx, name in enumerate(sorted_stores, start=1):
        print(f"{idx}. {name} => Image Count: {store_names_obj[name]["count"]}")

# Example usage
folder_path = 'cctv_images'  # Replace this with the actual path
extract_store_names(folder_path)
