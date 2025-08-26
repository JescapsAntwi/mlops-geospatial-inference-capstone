"""
Simplified Inference Worker Module for Testing
This version doesn't require rasterio for initial testing
"""

import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List, Any

class InferenceWorker:
    """
    Simplified worker class for running inference on GeoTIFF files
    
    This is a simplified implementation that simulates the Palm model.
    In production, this would call the actual Palm model Docker container.
    """
    
    def __init__(self):
        # Simulated class labels for the Palm model
        self.class_labels = [
            "palm_tree", "building", "road", "water", "vegetation", 
            "vehicle", "person", "agriculture", "forest", "urban"
        ]
    
    async def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single GeoTIFF file through the Palm model
        
        Args:
            file_path: Path to the GeoTIFF file
            
        Returns:
            Dictionary containing inference results
        """
        try:
            print(f"🔍 Processing {file_path}...")
            
            # Simulate processing time (in real implementation, this would be actual model inference)
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # For testing, we'll simulate image dimensions
            # In production, this would read the actual GeoTIFF metadata
            height, width = 512, 512  # Simulated dimensions
            
            # Simulate Palm model inference results
            detections = self._simulate_palm_detections(width, height)
            
            # Create result structure
            result = {
                "file_path": file_path,
                "file_name": file_path.split("/")[-1],
                "image_info": {
                    "width": width,
                    "height": height,
                    "crs": "EPSG:4326",  # Simulated CRS
                    "transform": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]  # Simulated transform
                },
                "detections": detections,
                "processing_time": datetime.now().isoformat(),
                "model_version": "palm_v1.0_simulated"
            }
            
            print(f"✅ Completed inference on {file_path}")
            return result
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            # Return error result
            return {
                "file_path": file_path,
                "file_name": file_path.split("/")[-1],
                "error": str(e),
                "processing_time": datetime.now().isoformat()
            }
    
    def _simulate_palm_detections(self, width: int, height: int) -> List[Dict[str, Any]]:
        """
        Simulate detection results from the Palm model
        
        This generates realistic-looking bounding boxes and detections.
        In production, this would be the actual output from the Palm model.
        """
        detections = []
        
        # Generate random number of detections (1-10 per image)
        num_detections = random.randint(1, 10)
        
        for i in range(num_detections):
            # Random class selection
            class_id = random.randint(0, len(self.class_labels) - 1)
            class_name = self.class_labels[class_id]
            
            # Generate random bounding box coordinates
            # Ensure boxes are within image boundaries
            box_width = random.randint(20, min(200, width // 4))
            box_height = random.randint(20, min(200, height // 4))
            
            x_min = random.randint(0, width - box_width)
            y_min = random.randint(0, height - box_height)
            x_max = x_min + box_width
            y_max = y_min + box_height
            
            # Generate confidence score (0.5 to 0.99)
            confidence = round(random.uniform(0.5, 0.99), 3)
            
            detection = {
                "id": i,
                "class_id": class_id,
                "class_name": class_name,
                "bbox": [x_min, y_min, x_max, y_max],
                "bbox_format": "xyxy",  # x_min, y_min, x_max, y_max
                "confidence": confidence,
                "area": box_width * box_height
            }
            
            detections.append(detection)
        
        return detections
