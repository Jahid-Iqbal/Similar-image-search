from elasticsearch import Elasticsearch

import sys
from pathlib import Path
# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.extract_features import extract_features

es = Elasticsearch(["http://localhost:9200"])

def search_similar_images(query_img_path, k=5):
    """Finds 'k' similar images to the query image"""
    query_vector = extract_features(query_img_path)
    
    search_query = {
        "knn": {
            "field": "image_vector",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": 100
        },
        "_source": ["image_path", "metadata"]
    }
    
    results = es.search(
        index="image_search",
        knn=search_query["knn"],
        source=search_query["_source"]
    )
    
    return results['hits']['hits']

if __name__ == "__main__":
    query_image = "E:\Projects\Image search\images/0000000000613_i6IUdTS.jpg.jpeg"  # Replace with your query image
    similar_images = search_similar_images(query_image)
    
    print(f"Similar images to {query_image}:")
    for i, img in enumerate(similar_images, 1):
        print(f"{i}. {img['_source']['image_path']} (Score: {img['_score']:.3f})")