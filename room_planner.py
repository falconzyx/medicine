import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from collections import defaultdict

class RoomPlanner:
    def __init__(self):
        # NLP synonyms for room types to improve recognition
        self.room_type_synonyms = {
            "icu": ["icu", "intensive care", "intensive care unit", "critical care"],
            "operating room": ["operating room", "or", "surgery room", "surgical suite", "operation theater"],
            "emergency room": ["emergency room", "er", "emergency department", "ed", "a&e", "accident and emergency", "trauma room"],
            "patient room": ["patient room", "hospital room", "inpatient room", "ward room", "recovery room"],
            "laboratory": ["laboratory", "lab", "clinical lab", "testing lab", "diagnostic lab"],
            "radiology": ["radiology", "imaging", "diagnostic imaging", "x-ray room", "mri room", "ct room"],
            "pharmacy": ["pharmacy", "drug dispensary", "medication room", "dispensary"],
            "physical therapy": ["physical therapy", "pt room", "rehabilitation", "rehab room", "therapy room"]
        }
        
        # Detailed equipment specifications by room type
        self.room_equipment = {
            "ICU": {
                "min_area": 250,
                "recommended_area": 400,
                "equipment": [
                    {
                        "name": "Patient Bed",
                        "specs": "Electric adjustable ICU bed with side rails",
                        "dimensions": "7.5ft x 3.3ft",
                        "placement": "Center of room, head against wall",
                        "clearance": "4ft on all sides"
                    },
                    {
                        "name": "Patient Monitor",
                        "specs": "Multi-parameter vital signs monitor",
                        "dimensions": "1.5ft x 1ft",
                        "placement": "Wall-mounted at head of bed",
                        "clearance": "1ft around monitor"
                    },
                    {
                        "name": "Ventilator",
                        "specs": "ICU-grade mechanical ventilator",
                        "dimensions": "2ft x 2ft",
                        "placement": "Right side of bed head",
                        "clearance": "2ft for access"
                    },
                    {
                        "name": "Infusion Pumps",
                        "specs": "Multiple channel smart pumps",
                        "dimensions": "1ft x 1ft each",
                        "placement": "Left side of bed",
                        "quantity": "3-4 units",
                        "clearance": "1.5ft for access"
                    },
                    {
                        "name": "Supply Cart",
                        "specs": "Mobile medical supply cart",
                        "dimensions": "3ft x 2ft",
                        "placement": "Along wall, easy access",
                        "clearance": "3ft in front"
                    },
                    {
                        "name": "Code Cart",
                        "specs": "Emergency resuscitation cart",
                        "dimensions": "2.5ft x 2ft",
                        "placement": "Near room entrance",
                        "clearance": "4ft for emergency access"
                    }
                ],
                "layout_guidelines": [
                    "Maintain 4ft clearance around bed for 360° patient access",
                    "Position bed to allow direct line of sight from nurse station",
                    "Keep emergency equipment (code cart) near entrance for quick access",
                    "Group infusion pumps and monitors on patient's left side",
                    "Ensure adequate space for family seating area",
                    "Maintain clear path to head of bed for emergency procedures"
                ]
            },
            "Operating Room": {
                "min_area": 400,
                "recommended_area": 600,
                "equipment": [
                    {
                        "name": "Operating Table",
                        "specs": "Electric surgical table with articulation",
                        "dimensions": "6.5ft x 2.5ft",
                        "placement": "Center of room",
                        "clearance": "6ft on all sides"
                    },
                    {
                        "name": "Surgical Lights",
                        "specs": "Dual-head LED surgical lights",
                        "dimensions": "Ceiling mounted, 2ft diameter each",
                        "placement": "Ceiling mounted over table",
                        "clearance": "Height adjustable"
                    },
                    {
                        "name": "Anesthesia Machine",
                        "specs": "Complete anesthesia workstation",
                        "dimensions": "2.5ft x 2.5ft",
                        "placement": "At head of table",
                        "clearance": "3ft for anesthesiologist"
                    },
                    {
                        "name": "Surgical Equipment Cart",
                        "specs": "Sterile instrument cart",
                        "dimensions": "4ft x 2ft",
                        "placement": "Right side of table",
                        "clearance": "3ft for scrub nurse"
                    },
                    {
                        "name": "Imaging Equipment",
                        "specs": "Mobile C-arm X-ray unit",
                        "dimensions": "6ft x 3ft when deployed",
                        "placement": "Parked at foot of table when needed",
                        "clearance": "5ft swing radius"
                    },
                    {
                        "name": "Supply Cabinets",
                        "specs": "Wall-mounted medical supply storage",
                        "dimensions": "6ft x 2ft",
                        "placement": "Along walls",
                        "clearance": "4ft in front"
                    }
                ],
                "layout_guidelines": [
                    "Position table to allow 360° access with 6ft clearance",
                    "Ensure adequate overhead lighting coverage",
                    "Maintain sterile field boundaries",
                    "Plan for equipment power and gas connections",
                    "Allow space for mobile imaging equipment",
                    "Create separate clean and dirty utility areas"
                ]
            },
            "Emergency Room": {
                "min_area": 250,
                "recommended_area": 350,
                "equipment": [
                    {
                        "name": "Trauma/Resuscitation Bed",
                        "specs": "Specialized emergency treatment bed with X-ray capability",
                        "dimensions": "7ft x 3ft",
                        "placement": "Center of room with 360° access",
                        "clearance": "5ft on all sides"
                    },
                    {
                        "name": "Defibrillator/Monitor",
                        "specs": "Combined defibrillator with multi-parameter vital signs monitoring",
                        "dimensions": "1.5ft x 1.5ft",
                        "placement": "Wall-mounted or on mobile stand at head of bed",
                        "clearance": "2ft for quick access"
                    },
                    {
                        "name": "Crash Cart",
                        "specs": "Emergency medication and equipment cart",
                        "dimensions": "3ft x 2ft",
                        "placement": "Near head of bed",
                        "clearance": "3ft for rapid access in emergencies"
                    },
                    {
                        "name": "Suction Equipment",
                        "specs": "Wall-mounted medical suction unit",
                        "dimensions": "1ft x 1ft",
                        "placement": "Wall-mounted at head of bed",
                        "clearance": "1ft for access"
                    },
                    {
                        "name": "Oxygen Supply System",
                        "specs": "Medical gas outlets with flow regulators",
                        "dimensions": "Wall-mounted system",
                        "placement": "Head wall near bed",
                        "clearance": "1.5ft for connections"
                    },
                    {
                        "name": "Supply Storage",
                        "specs": "Cabinets with immediate access supplies",
                        "dimensions": "5ft x 2ft",
                        "placement": "Along wall opposite to bed",
                        "clearance": "3ft in front"
                    },
                    {
                        "name": "Mobile X-ray Unit",
                        "specs": "Portable diagnostic imaging equipment",
                        "dimensions": "4ft x 2ft",
                        "placement": "Parked in corner when not in use",
                        "clearance": "Access pathway of 4ft"
                    }
                ],
                "layout_guidelines": [
                    "Central placement of bed with 360° access for resuscitation efforts",
                    "Critical equipment (defibrillator, suction) must be within arm's reach",
                    "Maintain clear pathway from door to bed for rapid access",
                    "Equipment organization must follow resuscitation protocols",
                    "All monitoring equipment must be visible from main work area",
                    "Ensure trauma team has adequate space to work (minimum 5-7 providers)",
                    "Maintain separate clean and contaminated areas"
                ]
            }
        }
        self.room_equipment_mapping = {
            'ICU': ['Patient Monitor', 'Ventilator', 'Infusion Pump', 'Defibrillator', 'Vital Signs Monitor'],
            'Operating Room': ['Anesthesia Machine', 'Surgical Table', 'Surgical Lights', 'Patient Monitor', 'Electrosurgical Unit'],
            'Emergency Room': ['Patient Monitor', 'Defibrillator', 'ECG Machine', 'Crash Cart', 'Portable X-ray'],
            'Patient Room': ['Hospital Bed', 'Patient Monitor', 'Infusion Pump', 'Over-bed Table', 'Blood Pressure Monitor'],
            'Laboratory': ['Centrifuge', 'Microscope', 'Analyzer', 'Refrigerator', 'Lab Information System'],
            'Radiology': ['X-ray Machine', 'CT Scanner', 'MRI Machine', 'Ultrasound Machine', 'PACS Workstation'],
            'Pharmacy': ['Medicine Cabinet', 'Refrigerator', 'Laminar Flow Hood', 'Pill Counter', 'Label Printer'],
            'Physical Therapy': ['Treadmill', 'Exercise Bike', 'Parallel Bars', 'Ultrasound Therapy', 'TENS Unit']
        }
        self.room_dimensions = {
            'ICU': {'min_area': 250, 'recommended_area': 300},
            'Operating Room': {'min_area': 400, 'recommended_area': 600},
            'Emergency Room': {'min_area': 200, 'recommended_area': 250},
            'Patient Room': {'min_area': 180, 'recommended_area': 200},
            'Laboratory': {'min_area': 300, 'recommended_area': 400},
            'Radiology': {'min_area': 350, 'recommended_area': 450},
            'Pharmacy': {'min_area': 200, 'recommended_area': 300},
            'Physical Therapy': {'min_area': 400, 'recommended_area': 500}
        }

    def standardize_room_type(self, input_room_type):
        """Match user input to standardized room type using NLP matching."""
        if not input_room_type:
            return None
            
        input_room_type = input_room_type.lower().strip()
        
        # Direct match to standard name
        if input_room_type in self.room_equipment:
            return input_room_type
        
        # Check synonyms
        for standard_name, synonyms in self.room_type_synonyms.items():
            if input_room_type in synonyms:
                return standard_name
        
        # Partial matching (if user enters partial name)
        for standard_name, synonyms in self.room_type_synonyms.items():
            for synonym in synonyms:
                if synonym in input_room_type or input_room_type in synonym:
                    return standard_name
        
        return None
                
    def get_equipment_recommendations(self, room_type, area=None):
        # Standardize the room type using NLP matching
        std_room_type = self.standardize_room_type(room_type)
        
        if not std_room_type or std_room_type not in self.room_equipment:
            # Suggest possible room types if not found
            room_types = list(self.room_equipment.keys())
            return {
                'room_type': room_type,
                'area_status': f'Room type "{room_type}" not recognized. Available room types: {", ".join(room_types)}',
                'recommendations': [],
                'layout_guidelines': []
            }
        
        room_info = self.room_equipment[std_room_type]
        
        # Area analysis
        area_status = None
        if area:
            if area < room_info['min_area']:
                area_status = f'WARNING: The provided area of {area} sq ft is below the minimum recommended area of {room_info["min_area"]} sq ft for a {room_type}.'
            elif area < room_info['recommended_area']:
                area_status = f'The provided area of {area} sq ft meets minimum requirements but is below the recommended {room_info["recommended_area"]} sq ft for optimal {room_type} layout.'
            else:
                area_status = f'The provided area of {area} sq ft is adequate for a {room_type}.'
        else:
            area_status = f'Recommended minimum area: {room_info["min_area"]} sq ft, Optimal area: {room_info["recommended_area"]} sq ft'
        
        # Format equipment details
        equipment_details = []
        for equip in room_info['equipment']:
            details = f"{equip['name']}:\n"
            details += f"  • Specifications: {equip['specs']}\n"
            details += f"  • Dimensions: {equip['dimensions']}\n"
            details += f"  • Placement: {equip['placement']}\n"
            details += f"  • Required Clearance: {equip['clearance']}"
            if 'quantity' in equip:
                details += f"\n  • Quantity: {equip['quantity']}"
            equipment_details.append(details)
        
        return {
            'room_type': std_room_type,
            'area_status': area_status,
            'recommendations': equipment_details,
            'layout_guidelines': room_info['layout_guidelines']
        }

    def get_layout_guidelines(self, room_type):
        """Get layout guidelines for a specific room type."""
        guidelines = {
            'ICU': [
                "Place patient monitor at head of bed for clear visibility",
                "Position ventilator on the head wall",
                "Keep defibrillator easily accessible near the entrance",
                "Arrange infusion pumps on either side of the bed",
                "Ensure 360-degree access around the bed"
            ],
            'Operating Room': [
                "Center surgical table in the room",
                "Mount surgical lights directly above the table",
                "Position anesthesia machine at head of table",
                "Keep surgical equipment on mobile carts for flexibility",
                "Ensure adequate space for staff movement around table"
            ],
            'Emergency Room': [
                "Position bed against the wall with access from three sides",
                "Keep crash cart near the entrance",
                "Mount patient monitor on wall at head of bed",
                "Ensure easy access to medical gas outlets",
                "Maintain clear path to entrance/exit"
            ],
            'Patient Room': [
                "Place bed against wall with window view if possible",
                "Position over-bed table on the dominant hand side",
                "Mount patient monitor on wall at head of bed",
                "Keep visitor seating away from medical equipment",
                "Ensure clear path to bathroom"
            ]
            # Add more room types as needed
        }
        return guidelines.get(room_type, ["No specific layout guidelines available for this room type."])

    def analyze_room_compatibility(self, room_type, equipment_list):
        """Analyze if the provided equipment list is compatible with the room type."""
        if room_type not in self.room_equipment_mapping:
            return {
                'status': 'error',
                'message': f'Room type {room_type} not recognized',
                'analysis': None
            }
        
        recommended_equipment = set(self.room_equipment_mapping[room_type])
        provided_equipment = set(equipment_list)
        
        missing_essential = recommended_equipment - provided_equipment
        extra_equipment = provided_equipment - recommended_equipment
        
        compatibility_score = len(provided_equipment.intersection(recommended_equipment)) / len(recommended_equipment) * 100
        
        return {
            'status': 'success',
            'compatibility_score': round(compatibility_score, 2),
            'missing_equipment': list(missing_essential),
            'extra_equipment': list(extra_equipment),
            'recommendations': self.get_equipment_recommendations(room_type)
        }
