from elasticsearch import Elasticsearch
import os
from extract_features import extract_features

es = Elasticsearch(["http://localhost:9200"])

index_name = "image_search"

# Correct index settings with dense_vector
index_settings = {
    "mappings": {
        "properties": {
            "image_vector": {
                "type": "dense_vector",
                "dims": 512,  # Must match your feature vector size
                "index": True,
                "similarity": "l2_norm"
            },
            "image_path": {
                "type": "keyword"  # Changed from text to keyword for exact matching
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "filename": {"type": "keyword"},
                    "size": {"type": "long"}
                }
            }
        }
    }
}

# Create the index with proper settings
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

es.indices.create(
    index=index_name,
    mappings=index_settings["mappings"]
)

# Index your images (same as before)
image_dir = "E:\Projects\Image search\images"
for img_file in os.listdir(image_dir):
    if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
        img_path = os.path.join(image_dir, img_file)
        features = extract_features(img_path)
        
        if features:
            doc = {
                "image_vector": features,
                "image_path": img_path,
                "metadata": {
                    "filename": img_file,
                    "size": os.path.getsize(img_path)
                }
            }
            es.index(index=index_name, document=doc)
            print(f"Indexed: {img_file}")

print("Indexing complete!")