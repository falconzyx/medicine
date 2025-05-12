"""
Patient-Specific Equipment Recommendation Engine

This module provides personalized equipment recommendations based on patient characteristics,
medical conditions, and specific needs.
"""
import pandas as pd
import numpy as np
from collections import defaultdict

class PatientRecommender:
    def __init__(self):
        """Initialize the patient recommendation engine with clinical knowledge base."""
        # Map conditions to equipment needs with priority levels (1-5, with 5 being highest)
        self.condition_equipment_map = {
            # Respiratory conditions
            'pneumonia': [
                {'name': 'Oxygen Delivery System', 'priority': 5, 'rationale': 'Required for oxygen therapy to maintain adequate saturation'},
                {'name': 'Pulse Oximeter', 'priority': 5, 'rationale': 'Continuous monitoring of oxygen saturation'},
                {'name': 'Suction Device', 'priority': 4, 'rationale': 'Airway clearance for secretions'},
                {'name': 'Nebulizer', 'priority': 3, 'rationale': 'Delivery of bronchodilators if needed'}
            ],
            'copd': [
                {'name': 'BiPAP/CPAP Machine', 'priority': 5, 'rationale': 'Non-invasive ventilation for respiratory support'},
                {'name': 'Oxygen Delivery System', 'priority': 5, 'rationale': 'Low-flow oxygen as prescribed'},
                {'name': 'Pulse Oximeter', 'priority': 4, 'rationale': 'Monitoring of oxygen saturation'},
                {'name': 'Nebulizer', 'priority': 4, 'rationale': 'Administration of bronchodilators'}
            ],
            'asthma': [
                {'name': 'Peak Flow Meter', 'priority': 4, 'rationale': 'Monitoring lung function'},
                {'name': 'Nebulizer', 'priority': 4, 'rationale': 'Delivery of bronchodilators'},
                {'name': 'Oxygen Delivery System', 'priority': 3, 'rationale': 'Supplemental oxygen as needed'}
            ],
            'respiratory_failure': [
                {'name': 'Ventilator', 'priority': 5, 'rationale': 'Mechanical ventilation support'},
                {'name': 'Arterial Line Equipment', 'priority': 4, 'rationale': 'Continuous blood pressure monitoring and ABG sampling'},
                {'name': 'End-Tidal CO2 Monitor', 'priority': 4, 'rationale': 'Monitoring ventilation adequacy'}
            ],
            
            # Cardiovascular conditions
            'myocardial_infarction': [
                {'name': 'Cardiac Monitor', 'priority': 5, 'rationale': 'Continuous ECG monitoring'},
                {'name': 'Defibrillator', 'priority': 5, 'rationale': 'Ready for cardiac emergencies'},
                {'name': 'Oxygen Delivery System', 'priority': 4, 'rationale': 'Supplemental oxygen as needed'},
                {'name': 'IV Pump', 'priority': 4, 'rationale': 'Precise delivery of cardiac medications'}
            ],
            'heart_failure': [
                {'name': 'Cardiac Monitor', 'priority': 5, 'rationale': 'Monitoring for arrhythmias'},
                {'name': 'IV Pump', 'priority': 4, 'rationale': 'Diuretic and inotropic medication delivery'},
                {'name': 'Oxygen Delivery System', 'priority': 4, 'rationale': 'Supplemental oxygen therapy'},
                {'name': 'Digital Scale', 'priority': 3, 'rationale': 'Daily weight monitoring'}
            ],
            'hypertension': [
                {'name': 'Automated Blood Pressure Cuff', 'priority': 4, 'rationale': 'Regular BP monitoring'},
                {'name': 'IV Pump', 'priority': 3, 'rationale': 'For antihypertensive medications if needed'}
            ],
            'arrhythmia': [
                {'name': 'Cardiac Monitor', 'priority': 5, 'rationale': 'Continuous rhythm monitoring'},
                {'name': 'Defibrillator', 'priority': 5, 'rationale': 'Available for emergency cardioversion'},
                {'name': 'Temporary Pacemaker', 'priority': 4, 'rationale': 'For bradyarrhythmias if needed'}
            ],
            
            # Neurological conditions
            'stroke': [
                {'name': 'Neurological Assessment Tools', 'priority': 5, 'rationale': 'Regular neuro checks'},
                {'name': 'Swallow Evaluation Kit', 'priority': 4, 'rationale': 'Dysphagia screening'},
                {'name': 'Blood Pressure Monitor', 'priority': 4, 'rationale': 'Close BP management'},
                {'name': 'Oxygen Delivery System', 'priority': 3, 'rationale': 'As needed for hypoxia'}
            ],
            'seizure_disorder': [
                {'name': 'Padded Bed Rails', 'priority': 5, 'rationale': 'Prevention of injury during seizures'},
                {'name': 'Suction Device', 'priority': 4, 'rationale': 'Airway management during seizure'},
                {'name': 'Oxygen Delivery System', 'priority': 3, 'rationale': 'Post-ictal oxygen supplementation'}
            ],
            'traumatic_brain_injury': [
                {'name': 'ICP Monitoring Equipment', 'priority': 5, 'rationale': 'Intracranial pressure monitoring'},
                {'name': 'Neurological Assessment Tools', 'priority': 5, 'rationale': 'Frequent neuro checks'},
                {'name': 'Ventilator', 'priority': 4, 'rationale': 'If respiratory drive compromised'}
            ],
            
            # Gastrointestinal conditions
            'gi_bleed': [
                {'name': 'Suction Device', 'priority': 5, 'rationale': 'For hematemesis management'},
                {'name': 'IV Pump', 'priority': 5, 'rationale': 'Fluid and blood product administration'},
                {'name': 'Nasogastric Tube Kit', 'priority': 4, 'rationale': 'For gastric decompression and lavage'},
                {'name': 'Fluid Warmer', 'priority': 3, 'rationale': 'For prevention of hypothermia during resuscitation'}
            ],
            'inflammatory_bowel_disease': [
                {'name': 'IV Pump', 'priority': 4, 'rationale': 'For hydration and medication'},
                {'name': 'Patient-Controlled Analgesia Pump', 'priority': 3, 'rationale': 'Pain management'}
            ],
            
            # Endocrine conditions
            'diabetes': [
                {'name': 'Glucometer', 'priority': 5, 'rationale': 'Regular blood glucose monitoring'},
                {'name': 'IV Pump', 'priority': 4, 'rationale': 'For insulin infusions if needed'},
                {'name': 'Meal Delivery System', 'priority': 3, 'rationale': 'Consistent carbohydrate meal timing'}
            ],
            'diabetic_ketoacidosis': [
                {'name': 'IV Pump', 'priority': 5, 'rationale': 'Precise insulin and fluid administration'},
                {'name': 'Glucometer', 'priority': 5, 'rationale': 'Hourly glucose monitoring'},
                {'name': 'Cardiac Monitor', 'priority': 4, 'rationale': 'Monitoring for arrhythmias from electrolyte shifts'}
            ],
            
            # Renal conditions
            'acute_kidney_injury': [
                {'name': 'IV Pump', 'priority': 5, 'rationale': 'Precise fluid management'},
                {'name': 'Fluid Balance Chart', 'priority': 4, 'rationale': 'Strict input/output monitoring'},
                {'name': 'Digital Scale', 'priority': 4, 'rationale': 'Daily weight monitoring'}
            ],
            'chronic_kidney_disease': [
                {'name': 'Dialysis Access Care Kit', 'priority': 4, 'rationale': 'Maintenance of vascular access'},
                {'name': 'Blood Pressure Monitor', 'priority': 4, 'rationale': 'Regular BP monitoring'},
                {'name': 'Digital Scale', 'priority': 4, 'rationale': 'Daily weight monitoring'}
            ],
            
            # Surgical patients
            'post_surgical': [
                {'name': 'Wound Care Supplies', 'priority': 5, 'rationale': 'Surgical site management'},
                {'name': 'Patient-Controlled Analgesia Pump', 'priority': 4, 'rationale': 'Pain management'},
                {'name': 'Incentive Spirometer', 'priority': 4, 'rationale': 'Prevention of atelectasis'},
                {'name': 'Sequential Compression Devices', 'priority': 4, 'rationale': 'DVT prophylaxis'}
            ],
            
            # Infectious disease
            'sepsis': [
                {'name': 'Cardiac Monitor', 'priority': 5, 'rationale': 'Hemodynamic monitoring'},
                {'name': 'IV Pump', 'priority': 5, 'rationale': 'Fluid and vasopressor administration'},
                {'name': 'Temperature Management System', 'priority': 4, 'rationale': 'Fever management'}
            ],
            
            # Mobility/fall risk
            'fall_risk': [
                {'name': 'Bed Alarm', 'priority': 5, 'rationale': 'Alert for unauthorized bed exit'},
                {'name': 'Low Height Bed', 'priority': 4, 'rationale': 'Minimizing fall injury risk'},
                {'name': 'Gait Belt', 'priority': 4, 'rationale': 'Support during ambulation'}
            ],
            'mobility_impairment': [
                {'name': 'Mechanical Lift', 'priority': 5, 'rationale': 'Safe patient handling'},
                {'name': 'Pressure-Relieving Mattress', 'priority': 4, 'rationale': 'Prevention of pressure injuries'},
                {'name': 'Transfer Board', 'priority': 4, 'rationale': 'Assist with lateral transfers'}
            ]
        }
        
        # Demographics-based considerations (age, weight, etc.)
        self.demographic_equipment_map = {
            'pediatric': [
                {'name': 'Pediatric-Sized Equipment', 'priority': 5, 'rationale': 'Appropriately sized for children'},
                {'name': 'Child-Friendly Environment', 'priority': 3, 'rationale': 'Reduce stress and anxiety'}
            ],
            'geriatric': [
                {'name': 'Pressure-Relieving Mattress', 'priority': 4, 'rationale': 'Prevention of pressure injuries in thin skin'},
                {'name': 'Assistive Devices', 'priority': 4, 'rationale': 'Support mobility and independence'}
            ],
            'bariatric': [
                {'name': 'Bariatric Bed', 'priority': 5, 'rationale': 'Weight capacity and width requirements'},
                {'name': 'Bariatric Commode', 'priority': 4, 'rationale': 'Weight capacity requirements'},
                {'name': 'Ceiling Lift', 'priority': 5, 'rationale': 'Safe patient handling'}
            ]
        }
        
        # Additional equipment for specific clinical needs
        self.clinical_needs_map = {
            'isolation': [
                {'name': 'Negative Pressure Room', 'priority': 5, 'rationale': 'Airborne infection control'},
                {'name': 'PPE Station', 'priority': 5, 'rationale': 'Infection control supplies'}
            ],
            'immunocompromised': [
                {'name': 'HEPA Filter', 'priority': 5, 'rationale': 'Air filtration'},
                {'name': 'Positive Pressure Room', 'priority': 4, 'rationale': 'Protection from external contaminants'}
            ],
            'limited_mobility': [
                {'name': 'Ceiling Lift', 'priority': 4, 'rationale': 'Safe transfers'},
                {'name': 'Pressure-Relieving Mattress', 'priority': 4, 'rationale': 'Prevention of pressure injuries'}
            ],
            'visually_impaired': [
                {'name': 'Braille Signage', 'priority': 3, 'rationale': 'Navigation assistance'},
                {'name': 'Audible Alert Systems', 'priority': 4, 'rationale': 'Communication of important information'}
            ],
            'hearing_impaired': [
                {'name': 'Visual Alert System', 'priority': 4, 'rationale': 'Visual cues for alarms'},
                {'name': 'Communication Board', 'priority': 3, 'rationale': 'Alternative communication method'}
            ]
        }
        
        # Treatment-specific equipment needs
        self.treatment_equipment_map = {
            'chemotherapy': [
                {'name': 'Chemotherapy-Rated IV Pump', 'priority': 5, 'rationale': 'Safe administration of cytotoxic drugs'},
                {'name': 'Spill Kit', 'priority': 5, 'rationale': 'Management of cytotoxic spills'},
                {'name': 'Anti-Nausea Medication Delivery', 'priority': 4, 'rationale': 'Symptom management'}
            ],
            'radiation_therapy': [
                {'name': 'Positioning Aids', 'priority': 5, 'rationale': 'Reproducible patient positioning'},
                {'name': 'Radiation Shield', 'priority': 5, 'rationale': 'Protection of non-targeted areas'}
            ],
            'dialysis': [
                {'name': 'Dialysis Machine', 'priority': 5, 'rationale': 'Renal replacement therapy'},
                {'name': 'Dialysis Chair', 'priority': 4, 'rationale': 'Patient comfort during treatment'},
                {'name': 'Fluid Balance Equipment', 'priority': 5, 'rationale': 'Precise fluid removal monitoring'}
            ],
            'physical_therapy': [
                {'name': 'Therapeutic Exercise Equipment', 'priority': 4, 'rationale': 'Rehabilitation progress'},
                {'name': 'Parallel Bars', 'priority': 3, 'rationale': 'Gait training'},
                {'name': 'Therapy Mats', 'priority': 3, 'rationale': 'Safe exercise surface'}
            ]
        }
        
    def get_recommendations(self, patient_data):
        """
        Generate personalized equipment recommendations based on patient data.
        
        Args:
            patient_data (dict): Dictionary containing patient information:
                - conditions (list): List of medical conditions
                - demographics (dict): Age, weight, etc.
                - clinical_needs (list): Special clinical requirements
                - treatments (list): Current treatments
                - acuity (int): Patient acuity level (1-5)
                
        Returns:
            dict: Personalized equipment recommendations with rationales
        """
        recommendations = []
        equipment_scores = defaultdict(int)
        equipment_rationales = {}
        
        # Process medical conditions
        conditions = patient_data.get('conditions', [])
        for condition in conditions:
            if condition.lower() in self.condition_equipment_map:
                for equip in self.condition_equipment_map[condition.lower()]:
                    equipment_scores[equip['name']] += equip['priority']
                    if equip['name'] not in equipment_rationales:
                        equipment_rationales[equip['name']] = []
                    equipment_rationales[equip['name']].append(
                        f"[{condition}] {equip['rationale']}"
                    )
        
        # Process demographics
        demographics = patient_data.get('demographics', {})
        age = demographics.get('age', 0)
        weight = demographics.get('weight', 0)
        
        # Apply demographic rules
        if age < 18:
            demo_type = 'pediatric'
        elif age > 65:
            demo_type = 'geriatric'
        else:
            demo_type = 'adult'
            
        # Weight-based considerations (simplified BMI calculation)
        height = demographics.get('height', 170)  # cm
        if height > 0 and weight > 0:
            bmi = weight / ((height/100) ** 2)
            if bmi > 35:  # Simplified classification
                for equip in self.demographic_equipment_map['bariatric']:
                    equipment_scores[equip['name']] += equip['priority']
                    if equip['name'] not in equipment_rationales:
                        equipment_rationales[equip['name']] = []
                    equipment_rationales[equip['name']].append(
                        f"[Bariatric needs] {equip['rationale']}"
                    )
        
        # Apply demographic equipment
        if demo_type in self.demographic_equipment_map:
            for equip in self.demographic_equipment_map[demo_type]:
                equipment_scores[equip['name']] += equip['priority']
                if equip['name'] not in equipment_rationales:
                    equipment_rationales[equip['name']] = []
                equipment_rationales[equip['name']].append(
                    f"[{demo_type.title()} patient] {equip['rationale']}"
                )
        
        # Process special clinical needs
        clinical_needs = patient_data.get('clinical_needs', [])
        for need in clinical_needs:
            if need.lower() in self.clinical_needs_map:
                for equip in self.clinical_needs_map[need.lower()]:
                    equipment_scores[equip['name']] += equip['priority']
                    if equip['name'] not in equipment_rationales:
                        equipment_rationales[equip['name']] = []
                    equipment_rationales[equip['name']].append(
                        f"[{need}] {equip['rationale']}"
                    )
        
        # Process treatments
        treatments = patient_data.get('treatments', [])
        for treatment in treatments:
            if treatment.lower() in self.treatment_equipment_map:
                for equip in self.treatment_equipment_map[treatment.lower()]:
                    equipment_scores[equip['name']] += equip['priority']
                    if equip['name'] not in equipment_rationales:
                        equipment_rationales[equip['name']] = []
                    equipment_rationales[equip['name']].append(
                        f"[{treatment}] {equip['rationale']}"
                    )
        
        # Acuity adjustment - increase priority of monitoring equipment for high acuity
        acuity = patient_data.get('acuity', 3)
        if acuity >= 4:
            monitoring_equipment = [
                'Cardiac Monitor', 'Pulse Oximeter', 'Blood Pressure Monitor', 
                'Ventilator', 'IV Pump'
            ]
            for equip in monitoring_equipment:
                equipment_scores[equip] += acuity - 2  # Boost by acuity level
                if equip not in equipment_rationales:
                    equipment_rationales[equip] = []
                equipment_rationales[equip].append(
                    f"[High Acuity (Level {acuity})] Enhanced monitoring required"
                )
        
        # Sort equipment by score (priority)
        sorted_equipment = sorted(
            equipment_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Format final recommendations
        for equip_name, score in sorted_equipment:
            recommendations.append({
                'name': equip_name,
                'priority_score': score,
                'rationales': equipment_rationales[equip_name]
            })
        
        return {
            'patient_info': {
                'conditions': conditions,
                'demographics': demographics,
                'acuity': acuity
            },
            'recommendations': recommendations
        }
    
    def get_equipment_details(self, equipment_name):
        """
        Get detailed specifications for a specific piece of equipment.
        
        Args:
            equipment_name (str): Name of the equipment
            
        Returns:
            dict: Equipment specifications
        """
        equipment_specs = {
            'Cardiac Monitor': {
                'description': 'Continuous electrocardiographic monitoring device',
                'dimensions': '12" x 10" x 6"',
                'electrical': '120V AC',
                'connectivity': 'Wireless telemetry',
                'features': ['Arrhythmia detection', 'ST segment analysis', 'QT monitoring'],
                'placement': 'Wall mount or cart at head of bed, visible from door'
            },
            'Ventilator': {
                'description': 'Mechanical breathing support device',
                'dimensions': '15" x 15" x 48"',
                'electrical': '120V AC, battery backup',
                'connectivity': 'HL7 integration',
                'features': ['Volume/pressure modes', 'PEEP', 'Pressure support'],
                'placement': 'Right side of bed (for right-handed clinicians)'
            },
            'IV Pump': {
                'description': 'Precision intravenous fluid/medication delivery device',
                'dimensions': '6" x 8" x 10" per channel',
                'electrical': '120V AC, battery backup',
                'connectivity': 'Wireless medication library updates',
                'features': ['Drug library', 'Dose error reduction', 'Multiple infusion modes'],
                'placement': 'IV pole, left side of bed'
            },
            'Defibrillator': {
                'description': 'Cardiac resuscitation device',
                'dimensions': '12" x 14" x 8"',
                'electrical': '120V AC, battery powered',
                'connectivity': 'Code event documentation',
                'features': ['Biphasic waveform', 'AED mode', 'Transcutaneous pacing'],
                'placement': 'Crash cart, accessible from all sides of patient'
            },
            'Oxygen Delivery System': {
                'description': 'Wall-mounted or portable oxygen source',
                'dimensions': 'Wall outlet or E-cylinder (4" x 26")',
                'features': ['Flowmeter', 'Humidification capability'],
                'placement': 'Head wall, left side'
            }
        }
        
        # Add more equipment specs as needed
        
        # Return details if available, otherwise return basic info
        if equipment_name in equipment_specs:
            return {
                'name': equipment_name,
                'details': equipment_specs[equipment_name]
            }
        else:
            return {
                'name': equipment_name,
                'details': {
                    'description': 'Medical equipment',
                    'placement': 'As per clinical need'
                }
            }
