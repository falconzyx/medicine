# Medical Equipment Placement & Training System

## Overview
This application is a comprehensive platform for medical equipment planning, placement, and training. It helps healthcare professionals optimize equipment selection and placement in medical rooms while providing interactive learning tools to enhance equipment proficiency.

## Features

### Equipment Chatbot
An intelligent assistant that answers questions about medical equipment and provides detailed recommendations for room planning.

### Room Planning Visualization
- Interactive 2D room layouts for different medical room types (ICU, Operating Room, Emergency Room, etc.)
- Detailed equipment placement recommendations with proper spacing and workflow considerations
- Visual representation of optimal equipment arrangements

### Interactive 3D Equipment Models
- Detailed 3D models of medical equipment with interactive controls
- Full rotation and zoom capabilities for equipment inspection
- Educational visualizations of equipment components

### Patient-Specific Equipment Recommendation Engine
- Personalized equipment suggestions based on patient conditions and needs
- Clinical rationale for each equipment recommendation
- Acuity-based room and equipment optimization

### Gamified Learning System (Design Documentation)
- Comprehensive design for an interactive learning platform
- Game mechanics for equipment training and competency development
- Detailed implementation roadmap

## Getting Started

### Requirements
- Python 3.8+
- Streamlit
- Pandas
- NumPy
- Matplotlib
- Plotly
- Scikit-learn

### Installation

```bash
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run equipment_chatbot.py
```

## Demo

Access the live demo on Streamlit Community Cloud: [Medical Equipment Placement System](https://medical-equipment-chatbot.streamlit.app/)

## Project Structure

- `equipment_chatbot.py`: Main application interface
- `room_planner.py`: Room planning and equipment recommendation logic
- `model_viewer_3d.py`: Interactive 3D model visualization
- `patient_recommender.py`: Patient-specific equipment recommendation engine
- `design_documents/`: Design specifications and documentation
  - `Gamified_Learning_System_Design.md`: Detailed design for the gamified learning system

## Future Enhancements

- Implementation of the gamified learning system
- Integration with hospital inventory systems
- Advanced room planning with VR visualization
- Machine learning-based equipment optimization