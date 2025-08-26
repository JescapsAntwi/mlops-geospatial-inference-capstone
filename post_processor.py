"""
Post-Processor Module
Converts raw inference results into COCO format JSON
"""

import json
from datetime import datetime
from typing import Dict, List, Any

class PostProcessor:
    """
    Converts Palm model inference results to COCO format
    
    COCO format is a standard for object detection datasets that includes:
    - Images: metadata about each image
    - Annotations: bounding boxes, class labels, and confidence scores
    - Categories: class definitions
    """
    
    def __init__(self):
        # Define COCO categories based on our Palm model classes
        self.categories = [
            {"id": 0, "name": "palm_tree", "supercategory": "vegetation"},
            {"id": 1, "name": "building", "supercategory": "structure"},
            {"id": 2, "name": "road", "supercategory": "infrastructure"},
            {"id": 3, "name": "water", "supercategory": "natural"},
            {"id": 4, "name": "vegetation", "supercategory": "natural"},
            {"id": 5, "name": "vehicle", "supercategory": "transport"},
            {"id": 6, "name": "person", "supercategory": "living"},
            {"id": 7, "name": "agriculture", "supercategory": "land_use"},
            {"id": 8, "name": "forest", "supercategory": "vegetation"},
            {"id": 9, "name": "urban", "supercategory": "land_use"}
        ]
    
    def convert_to_coco(self, inference_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert inference results to COCO format
        
        Args:
            inference_results: List of inference results from the Palm model
            
        Returns:
            Dictionary in COCO format
        """
        print("🔄 Converting results to COCO format...")
        
        # Initialize COCO structure
        coco_data = {
            "info": self._create_info(),
            "licenses": self._create_licenses(),
            "categories": self.categories,
            "images": [],
            "annotations": []
        }
        
        annotation_id = 1
        
        # Process each inference result
        for result in inference_results:
            # Skip results with errors
            if "error" in result:
                print(f"⚠️ Skipping {result['file_name']} due to error: {result['error']}")
                continue
            
            # Create image entry
            image_entry = self._create_image_entry(result, len(coco_data["images"]))
            coco_data["images"].append(image_entry)
            
            # Create annotation entries for each detection
            if "detections" in result and result["detections"]:
                for detection in result["detections"]:
                    annotation_entry = self._create_annotation_entry(
                        detection, 
                        annotation_id, 
                        image_entry["id"]
                    )
                    coco_data["annotations"].append(annotation_entry)
                    annotation_id += 1
        
        print(f"✅ Converted {len(coco_data['images'])} images and {len(coco_data['annotations'])} annotations to COCO format")
        return coco_data
    
    def _create_info(self) -> Dict[str, Any]:
        """Create COCO info section"""
        return {
            "year": datetime.now().year,
            "version": "1.0",
            "description": "Palm Model Geospatial Inference Results",
            "contributor": "MLOps Pipeline",
            "url": "",
            "date_created": datetime.now().isoformat()
        }
    
    def _create_licenses(self) -> List[Dict[str, str]]:
        """Create COCO licenses section"""
        return [
            {
                "id": 1,
                "name": "Attribution-NonCommercial-ShareAlike License",
                "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
            }
        ]
    
    def _create_image_entry(self, result: Dict[str, Any], image_id: int) -> Dict[str, Any]:
        """Create a COCO image entry"""
        image_info = result.get("image_info", {})
        
        return {
            "id": image_id,
            "width": image_info.get("width", 0),
            "height": image_info.get("height", 0),
            "file_name": result.get("file_name", "unknown.tif"),
            "license": 1,
            "flickr_url": "",
            "coco_url": "",
            "date_captured": result.get("processing_time", datetime.now().isoformat()),
            "geospatial_info": {
                "crs": image_info.get("crs", ""),
                "transform": image_info.get("transform", [])
            }
        }
    
    def _create_annotation_entry(self, detection: Dict[str, Any], annotation_id: int, image_id: int) -> Dict[str, Any]:
        """Create a COCO annotation entry"""
        bbox = detection.get("bbox", [0, 0, 0, 0])
        
        # Convert from xyxy to xywh format (COCO standard)
        x, y, x_max, y_max = bbox
        width = x_max - x
        height = y_max - y
        
        return {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": detection.get("class_id", 0),
            "segmentation": [],  # No segmentation in this implementation
            "area": detection.get("area", width * height),
            "bbox": [x, y, width, height],  # COCO format: [x, y, width, height]
            "iscrowd": 0,
            "confidence": detection.get("confidence", 0.0),
            "bbox_format_original": detection.get("bbox_format", "xyxy")
        }
    
    def save_coco_file(self, coco_data: Dict[str, Any], output_path: str):
        """
        Save COCO data to a JSON file
        
        Args:
            coco_data: COCO format data
            output_path: Path to save the JSON file
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(coco_data, f, indent=2)
            print(f"💾 Saved COCO results to {output_path}")
        except Exception as e:
            print(f"❌ Error saving COCO file: {e}")
    
    def validate_coco_format(self, coco_data: Dict[str, Any]) -> bool:
        """
        Basic validation of COCO format
        
        Args:
            coco_data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ["info", "licenses", "categories", "images", "annotations"]
        
        # Check required top-level keys
        for key in required_keys:
            if key not in coco_data:
                print(f"❌ Missing required key: {key}")
                return False
        
        # Check if we have at least one image
        if len(coco_data["images"]) == 0:
            print("❌ No images in COCO data")
            return False
        
        # Check if categories are properly defined
        if len(coco_data["categories"]) == 0:
            print("❌ No categories defined")
            return False
        
        print("✅ COCO format validation passed")
        return True
