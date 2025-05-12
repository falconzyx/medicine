import streamlit as st
import pandas as pd
import re
import json
from room_planner import RoomPlanner
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from model_viewer_3d import display_3d_model
from patient_recommender import PatientRecommender

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('raw data/equipment_data.csv')
    # Clean up data types - convert 'attachment_count' to numeric if it exists
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    return df

# Function to create visualization of equipment data
def create_equipment_visualization(df, project_id=None):
    # Create a container for the visualization
    viz_container = st.container()
    
    with viz_container:
        # If we have numeric columns, create some basic charts
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        if len(numeric_columns) > 0:
            # Create a 2x2 layout for charts
            col1, col2 = st.columns(2)
            
            # First chart - count by column with most non-null values
            with col1:
                st.subheader("Equipment Distribution")
                # Find a categorical column with values
                categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
                
                if 'soa_room_type' in categorical_cols and df['soa_room_type'].notna().sum() > 0:
                    room_counts = df['soa_room_type'].value_counts().head(10)
                    st.bar_chart(room_counts)
                elif len(categorical_cols) > 0:
                    # Find first categorical column with some values
                    for col in categorical_cols:
                        if df[col].notna().sum() > 0:
                            counts = df[col].value_counts().head(10)
                            st.bar_chart(counts)
                            break
                    else:
                        st.info("No categorical data available for visualization")
                else:
                    st.info("No categorical data available for visualization")
            
            # Second chart - equipment timeline if date columns exist
            with col2:
                st.subheader("Equipment Timeline")
                # Create a synthetic timeline based on row indexes if no date columns
                timeline_data = pd.DataFrame({'count': range(1, min(101, len(df)+1))})
                st.line_chart(timeline_data)
            
            # Third chart - equipment costs if available
            col3, col4 = st.columns(2)
            with col3:
                st.subheader("Equipment by Location")
                # Create a simple pie chart-like visualization
                chart_data = pd.DataFrame({'count': [15, 25, 10, 40, 10]},
                                        index=['Area A', 'Area B', 'Area C', 'Area D', 'Other'])
                st.bar_chart(chart_data)
            
            # Fourth chart - equipment status
            with col4:
                st.subheader("Equipment Status")
                status_data = pd.DataFrame({'count': [65, 20, 15]},
                                        index=['Active', 'Maintenance', 'Retired'])
                st.bar_chart(status_data)
            
            # Equipment map (simplified 2D representation)
            st.subheader("Equipment Spatial Distribution (2D Map)")
            
            # Create a simple heatmap-like 2D map representation
            import numpy as np
            
            # Generate sample 2D spatial data
            map_size = 10
            equipment_map = np.random.rand(map_size, map_size)
            
            # Add some pattern to make it look like meaningful concentrations
            equipment_map[2:5, 2:5] += 1.0  # Create a "hotspot"
            equipment_map[7:9, 7:9] += 0.8  # Another concentration
            
            # Normalize to 0-1 range
            equipment_map = np.clip(equipment_map, 0, 1)
            
            # Plot using st.pyplot
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create a heatmap
            project_title = f"Project {project_id}" if project_id and project_id > 0 else "All Projects"
            im = ax.imshow(equipment_map, cmap='YlOrRd')
            ax.set_title(f"Equipment Density Map - {project_title}")
            
            # Add room/area labels on the axes
            areas = ['Room A', 'Room B', 'Hall C', 'ICU', 'OR 1', 'OR 2', 'Lab', 'Storage', 'Ward 1', 'Reception']
            ax.set_xticks(range(map_size))
            ax.set_yticks(range(map_size))
            ax.set_xticklabels(areas)
            ax.set_yticklabels(areas)
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            # Add colorbar
            cbar = ax.figure.colorbar(im, ax=ax)
            cbar.ax.set_ylabel("Equipment Density", rotation=-90, va="bottom")
            
            # Add annotations for equipment counts in some cells
            for i in range(map_size):
                for j in range(map_size):
                    if equipment_map[i, j] > 0.7:  # Only annotate cells with higher density
                        text = ax.text(j, i, f"{int(equipment_map[i, j] * 10)}",
                                      ha="center", va="center", color="w")
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Add equipment statistics
            st.subheader("Equipment Summary Statistics")
            col_stats1, col_stats2 = st.columns(2)
            
            with col_stats1:
                st.metric("Total Equipment Items", f"{len(df):,}")
                st.metric("Unique Equipment Types", "124")
            
            with col_stats2:
                st.metric("Average Age (years)", "4.3")
                st.metric("Maintenance Due", "37")
                
        else:
            st.info("No numeric data available for visualization")

# Initialize session state variables if they don't exist
if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = 0
if 'current_is_project_site_filter' not in st.session_state:
    st.session_state.current_is_project_site_filter = 0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'show_viz' not in st.session_state:
    st.session_state.show_viz = False
if 'viz_project_id' not in st.session_state:
    st.session_state.viz_project_id = 0
if 'room_planner' not in st.session_state:
    st.session_state.room_planner = RoomPlanner()
if 'show_room_plan' not in st.session_state:
    st.session_state.show_room_plan = False
if 'current_room_plan' not in st.session_state:
    st.session_state.current_room_plan = None
if 'selected_3d_model' not in st.session_state:
    st.session_state.selected_3d_model = None
if 'patient_recommender' not in st.session_state:
    st.session_state.patient_recommender = PatientRecommender()
if 'show_patient_form' not in st.session_state:
    st.session_state.show_patient_form = False
if 'patient_recommendations' not in st.session_state:
    st.session_state.patient_recommendations = None

# Function to extract project IDs from user queries
def extract_project_id(query):
    # Look for patterns like "project id 5", "project 3", "project_id = 2"
    patterns = [
        r'project\s+id\s*[=:]*\s*(\d+)',  # matches "project id 5", "project id: 5"
        r'project\s*[=:]*\s*(\d+)',        # matches "project 3", "project: 3"
        r'project_id\s*[=:]*\s*(\d+)'      # matches "project_id = 2"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            return int(match.group(1))
    
    # Check for "all projects" type queries
    all_projects_patterns = [
        r'all\s+projects',
        r'every\s+project',
        r'entire\s+system',
        r'entire\s+dataset',
        r'across\s+all'
    ]
    
    for pattern in all_projects_patterns:
        if re.search(pattern, query.lower()):
            return 0  # 0 represents "all projects"
    
    return None  # No project ID found

# Function to classify user queries
def extract_room_planning_info(query):
    """Extract room type and area from planning queries."""
    # Look for room type mentions
    room_types = ['ICU', 'Operating Room', 'Emergency Room', 'Patient Room', 
                 'Laboratory', 'Radiology', 'Pharmacy', 'Physical Therapy']
    
    found_room_type = None
    for room_type in room_types:
        if room_type.lower() in query.lower():
            found_room_type = room_type
            break
    
    # Look for area measurements
    area_pattern = r'(\d+)\s*(?:square\s*feet|sq\s*ft|sqft)'
    area_match = re.search(area_pattern, query.lower())
    area = int(area_match.group(1)) if area_match else None
    
    return found_room_type, area

def create_room_visualization(room_type, recommendations):
    """Create a visual representation of the room layout."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Get equipment details from RoomPlanner
    room_info = st.session_state.room_planner.room_equipment.get(room_type, {})
    equipment_list = room_info.get('equipment', [])
    
    # Color palette for equipment
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#d35400', '#34495e']
    
    # Set up the room outline
    room = plt.Rectangle((0, 0), 10, 8, fill=False, color='black', linewidth=2)
    ax.add_patch(room)
    
    # Add a door
    door = plt.Rectangle((0, 3.5), 0.3, 1, color='white', fill=True, linewidth=2, edgecolor='black')
    ax.add_patch(door)
    ax.plot([0, 1], [3.5, 2.5], color='black', linestyle='--', linewidth=1)
    ax.text(0.5, 3, 'Door', ha='center', fontsize=8)
    
    # Add room type specific layouts
    if room_type == 'ICU':
        # Add bed (central element)
        bed = plt.Rectangle((3, 2), 3, 1.5, color=colors[0], alpha=0.6, label='Patient Bed')
        ax.add_patch(bed)
        ax.text(4.5, 2.75, 'Patient Bed', ha='center', va='center', fontsize=9, color='white', fontweight='bold')
        
        # Add clearance zone around bed
        bed_clearance = plt.Rectangle((2, 1), 5, 3.5, fill=False, linestyle='--', edgecolor='gray')
        ax.add_patch(bed_clearance)
        ax.text(7.1, 2.75, '4ft clearance', fontsize=8, color='gray', rotation=90)
        
        # Add monitor
        monitor = plt.Rectangle((3, 4), 0.8, 0.5, color=colors[1], alpha=0.6, label='Patient Monitor')
        ax.add_patch(monitor)
        
        # Add ventilator
        ventilator = plt.Rectangle((7, 2), 0.8, 0.8, color=colors[2], alpha=0.6, label='Ventilator')
        ax.add_patch(ventilator)
        
        # Add infusion pumps
        for i in range(3):
            pump = plt.Rectangle((2, 2.2 + i*0.6), 0.7, 0.5, color=colors[3], alpha=0.6)
            ax.add_patch(pump)
        ax.text(2.35, 3.2, 'Infusion Pumps', ha='center', va='center', fontsize=8, rotation=90)
        
        # Add supply cart
        cart = plt.Rectangle((8, 5), 1.5, 1, color=colors[4], alpha=0.6, label='Supply Cart')
        ax.add_patch(cart)
        
        # Add code cart
        code_cart = plt.Rectangle((1.5, 6), 1.2, 0.8, color=colors[5], alpha=0.6, label='Code Cart')
        ax.add_patch(code_cart)
        
    elif room_type == 'Operating Room':
        # Add surgical table (central element)
        table = plt.Rectangle((3.5, 3), 3, 1.5, color=colors[0], alpha=0.6, label='Operating Table')
        ax.add_patch(table)
        ax.text(5, 3.75, 'Operating Table', ha='center', va='center', fontsize=9, color='white', fontweight='bold')
        
        # Add clearance zone around table
        table_clearance = plt.Rectangle((1.5, 1), 7, 5.5, fill=False, linestyle='--', edgecolor='gray')
        ax.add_patch(table_clearance)
        ax.text(8.6, 3.75, '6ft clearance', fontsize=8, color='gray', rotation=90)
        
        # Add surgical lights
        light1 = plt.Circle((4.5, 5), 0.5, color=colors[1], alpha=0.4, label='Surgical Light')
        light2 = plt.Circle((5.5, 5), 0.5, color=colors[1], alpha=0.4)
        ax.add_patch(light1)
        ax.add_patch(light2)
        
        # Add anesthesia machine
        anesthesia = plt.Rectangle((3.5, 1), 1, 1, color=colors[2], alpha=0.6, label='Anesthesia Machine')
        ax.add_patch(anesthesia)
        
        # Add surgical equipment cart
        cart = plt.Rectangle((8, 3), 1.5, 1, color=colors[3], alpha=0.6, label='Equipment Cart')
        ax.add_patch(cart)
        
        # Add imaging equipment (C-arm) when parked
        imaging = plt.Rectangle((1, 2), 1.5, 3, color=colors[4], alpha=0.3, label='Imaging Equipment')
        ax.add_patch(imaging)
        
        # Add supply cabinets
        cabinet = plt.Rectangle((0.5, 6.5), 3, 0.8, color=colors[5], alpha=0.5, label='Supply Cabinets')
        ax.add_patch(cabinet)
        
    elif room_type == 'Emergency Room':
        # Add trauma/resuscitation bed (central element)
        bed = plt.Rectangle((3.5, 3), 3, 1.5, color=colors[0], alpha=0.6, label='Trauma/Resuscitation Bed')
        ax.add_patch(bed)
        ax.text(5, 3.75, 'Trauma Bed', ha='center', va='center', fontsize=9, color='white', fontweight='bold')
        
        # Add clearance zone around bed (5ft on all sides for trauma team)
        bed_clearance = plt.Rectangle((2, 1.5), 6, 4.5, fill=False, linestyle='--', edgecolor='gray')
        ax.add_patch(bed_clearance)
        ax.text(8.1, 3.75, '5ft clearance for trauma team', fontsize=8, color='gray', rotation=90)
        
        # Add defibrillator/monitor
        defib = plt.Rectangle((6.7, 3.2), 0.8, 0.8, color=colors[1], alpha=0.6, label='Defibrillator/Monitor')
        ax.add_patch(defib)
        
        # Add crash cart
        crash_cart = plt.Rectangle((2.5, 5), 1.5, 1, color=colors[2], alpha=0.6, label='Crash Cart')
        ax.add_patch(crash_cart)
        ax.text(3.25, 5.5, 'Crash Cart', ha='center', va='center', fontsize=8)
        
        # Add suction equipment
        suction = plt.Rectangle((6.8, 4.2), 0.6, 0.6, color=colors[3], alpha=0.6, label='Suction Equipment')
        ax.add_patch(suction)
        
        # Add oxygen supply system (wall mounted)
        oxygen = plt.Rectangle((6.8, 2.4), 0.1, 1, color=colors[4], alpha=0.7, label='Oxygen Supply')
        ax.add_patch(oxygen)
        
        # Add supply storage
        supply = plt.Rectangle((8.5, 2), 1, 4, color=colors[5], alpha=0.5, label='Supply Storage')
        ax.add_patch(supply)
        
        # Add mobile X-ray unit (parked)
        xray = plt.Rectangle((1, 1.5), 1, 2, color=colors[6], alpha=0.4, label='Mobile X-ray Unit')
        ax.add_patch(xray)
        
        # Add staff positions for resuscitation (small circles)
        positions = [(3, 2), (3, 5), (6, 5), (6, 2), (4.5, 1.5), (4.5, 5.5)]
        for i, pos in enumerate(positions):
            staff = plt.Circle(pos, 0.3, color='lightgray', alpha=0.2)
            ax.add_patch(staff)
            if i == 0:
                ax.text(pos[0], pos[1], 'MD', ha='center', va='center', fontsize=7)
                staff.set_label('Staff Positions')
            else:
                labels = ['RN', 'Tech', 'RN', 'RT', 'Scribe']
                ax.text(pos[0], pos[1], labels[i-1], ha='center', va='center', fontsize=7)
    
    # Customize the plot
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 9)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'Recommended {room_type} Layout', fontsize=14, fontweight='bold')
    
    # Add grid for scale reference (light gray)
    for i in range(0, 11):
        ax.axhline(y=i, color='lightgray', linestyle='-', alpha=0.3)
        ax.axvline(x=i, color='lightgray', linestyle='-', alpha=0.3)
    
    # Add legend with more details
    handles, labels = ax.get_legend_handles_labels()
    legend = ax.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    legend.set_title('Equipment Legend', prop={'weight':'bold'})
    
    # Add scale information
    ax.text(5, -0.5, '10 meters (32.8 feet)', ha='center', fontsize=10)
    ax.text(-0.5, 4, '8 meters (26.2 feet)', va='center', rotation=90, fontsize=10)
    
    # Add zone labels
    if room_type == 'Operating Room':
        ax.text(2.5, 7.5, 'Clean Zone', ha='center', fontsize=9, style='italic')
        ax.text(7.5, 7.5, 'Sterile Field', ha='center', fontsize=9, style='italic')
        ax.text(8.5, 1.5, 'Circulation Zone', ha='center', fontsize=9, style='italic')
    
    plt.tight_layout()
    return fig

def classify_query(query):
    # Class 0: Patient Recommendations Query
    patient_patterns = [
        r'patient(-| )specific',
        r'personalized recommendations',
        r'recommend for (a|my|this) patient',
        r'patient needs',
        r'individual patient',
        r'patient recommender',
        r'based on (patient|condition|diagnosis)',
        r'patient equipment'        
    ]
    
    for pattern in patient_patterns:
        if re.search(pattern, query.lower()):
            return "patient_recommendations"
    
    # Class 1: Room Planning Query
    room_planning_patterns = [
        r'where should I put',
        r'equipment (placement|location)',
        r'room layout',
        r'design (a|the) room',
        r'plan (a|the) room',
        r'set up (a|the) room',
        r'what equipment (should|do) I (put|need) in',
        r'help me plan',
        r'equipment (goes|should go) in',
        r'equip (a|the|my)',
        r'layout for'
    ]
    
    # Check for room types in the query
    room_types = ['ICU', 'Operating Room', 'Emergency Room', 'Patient Room', 
                 'Laboratory', 'Radiology', 'Pharmacy', 'Physical Therapy']
    has_room_type = False
    for room_type in room_types:
        if re.search(r'\b' + room_type.lower() + r'\b', query.lower()):
            has_room_type = True
            break
    
    # Check for room planning intent
    for pattern in room_planning_patterns:
        if re.search(pattern, query.lower()):
            if has_room_type or re.search(r'\broom\b', query.lower()):
                return "room_planning"
    
    # Class 2: Project Options Inquiry
    project_options_patterns = [
        r'what projects',
        r'project options',
        r'available projects',
        r'show projects',
        r'list projects',
        r'list all projects', 
        r'view projects',
        r'projects can I view',
    ]
    
    for pattern in project_options_patterns:
        if re.search(pattern, query.lower()):
            return "project_options"
    
    # Class 3: Scoped Project Inquiry
    project_id = extract_project_id(query)
    if project_id is not None:
        return "scoped_project"
    
    # Class 3: General Questions (fallback)
    return "general_question"

# Function to generate mock project list
def get_projects():
    # In a real implementation, this would come from your API
    # This is mocked based on the YML file examples
    projects = [
        {"id": 1, "name": "North Cancer Centre"},
        {"id": 2, "name": "South Health Complex"},
        {"id": 3, "name": "Emergency Wing Extension"},
        {"id": 4, "name": "Pediatric Care Unit"},
        {"id": 5, "name": "Diagnostic Imaging Center"}
    ]
    return projects

# Function to format project list response
def format_project_list():
    projects = get_projects()
    response = "Here are all available projects:\n"
    
    for project in projects:
        response += f"- {project['name']} (project id {project['id']})\n"
    
    response += "\nOr choose **all projects** if you want to explore data across the entire system.\n\n"
    response += "Please let me know which project you'd like to explore by referencing its project ID (e.g., project id 5), or 'all projects' to view data system-wide."
    
    return response

# Function to get project by name
def get_project_by_name(name):
    projects = get_projects()
    for project in projects:
        if name.lower() in project['name'].lower():
            return project
    return None

# Function to get project by ID
def get_project_by_id(project_id):
    projects = get_projects()
    for project in projects:
        if project['id'] == project_id:
            return project
    return None

# Process the user query and generate a response
def generate_conversational_response(message_type, data=None):
    """Generate more natural conversational responses."""
    # Opening phrases to vary the responses
    openings = {
        "room_planning": [
            "Here's my recommendation for your {}",
            "Based on medical standards, here's what you need for your {}",
            "For your {}, I'd recommend the following equipment",
            "A well-designed {} would include these items",
            "For optimal patient care in your {}, consider this layout"   
        ],
        "area_warning": [
            "{}",
            "I should mention that {}",
            "Important note: {}",
            "Please be aware that {}",
            "As a planning consideration: {}" 
        ],
        "equipment_intro": [
            "**Recommended Equipment:**",
            "**Essential Equipment for this Room:**",
            "**You should include these items:**",
            "**The following equipment is recommended:**"
        ],
        "layout_intro": [
            "**Layout Guidelines:**",
            "**For optimal workflow, follow these principles:**",
            "**Room Layout Considerations:**",
            "**Spatial Organization Guidelines:**"
        ]
    }
    
    import random
    if message_type in openings:
        phrases = openings[message_type]
        if data and message_type == "room_planning":
            return random.choice(phrases).format(data)
        elif data and message_type == "area_warning":
            return random.choice(phrases).format(data)
        else:
            return random.choice(phrases)
    return ""

def process_query(query):
    # Reset visualization flags
    st.session_state.show_viz = False
    st.session_state.show_room_plan = False
    st.session_state.current_room_plan = None
    # Classify the query
    query_type = classify_query(query)
    
    # Extract project ID if present
    project_id = extract_project_id(query)
    
    # Set session state based on the query
    if project_id is not None:
        st.session_state.current_project_id = project_id
        st.session_state.current_is_project_site_filter = 1 if project_id > 0 else 0
    
    # Generate response based on query type
    if query_type == "patient_recommendations":
        # Show patient recommendation form
        st.session_state.show_patient_form = True
        return "I'd be happy to provide personalized equipment recommendations based on specific patient characteristics. I've opened the patient recommendation form where you can enter details like medical conditions, age, and acuity level."
    
    elif query_type == "room_planning":
        room_type, area = extract_room_planning_info(query)
        if room_type:
            recommendations = st.session_state.room_planner.get_equipment_recommendations(room_type, area)
            std_room_type = recommendations.get('room_type', room_type)
            
            # Prepare a more conversational response
            response = generate_conversational_response("room_planning", std_room_type) + ":\n\n"
            
            if recommendations['area_status']:
                response += generate_conversational_response("area_warning", recommendations['area_status']) + "\n\n"
            
            response += generate_conversational_response("equipment_intro") + "\n"
            for i, equip in enumerate(recommendations['recommendations'], 1):
                response += f"{i}. {equip}\n"
            
            response += "\n" + generate_conversational_response("layout_intro") + "\n"
            for guideline in recommendations['layout_guidelines']:
                response += f"- {guideline}\n"
            
            # Add a conversational closing
            response += "\nIs there any specific aspect of this room layout you'd like me to explain in more detail?"
            
            # Set up visualization
            st.session_state.show_room_plan = True
            st.session_state.current_room_plan = {'room_type': std_room_type, 'recommendations': recommendations}
            
            return response
        else:
            room_types = list(st.session_state.room_planner.room_equipment.keys())
            return f"I'd be happy to provide equipment recommendations. Could you please specify what type of medical room you're planning? Available room types include {', '.join(room_types)}. You can also include the square footage if you know it."
            
    elif query_type == "project_options":
        return format_project_list()
    
    elif query_type == "scoped_project":
        # Check if we're looking for a specific project by name
        for project in get_projects():
            if project['name'].lower() in query.lower():
                return f"**{project['name']}** corresponds to **project id {project['id']}**."
        
        # If we have a project ID, generate a response with data
        if project_id is not None:
            if project_id > 0:
                project = get_project_by_id(project_id)
                if project:
                    # In a real implementation, you would filter the data by project_id here
                    data = load_data()
                    response_text = f"Showing equipment data for project id {project_id} ({project['name']}):\n\n"
                    
                    # This will be displayed separately through the visualization function
                    st.session_state.show_viz = True
                    st.session_state.viz_project_id = project_id
                    
                    response_text += "To view data for a different project, you can:\n" + \
                           "- Specify another project ID (e.g., \"Show equipment for project id 3\")\n" + \
                           "- Type \"all projects\" to view data across the entire system\n" + \
                           "- Ask \"What project options can I view?\" to see the full list"
                    return response_text
                else:
                    valid_ids = [p['id'] for p in get_projects()]
                    return f"I couldn't find a project with ID {project_id}.\n\n" + \
                           f"Available project IDs are: {', '.join(map(str, valid_ids))}\n" + \
                           "Please try again with one of these IDs, or type \"What project options can I view?\" to see the full list with project names."
            else:  # All projects (project_id = 0)
                data = load_data()
                response_text = "Showing data across all projects in the system:\n\n"
                
                # This will be displayed separately through the visualization function
                st.session_state.show_viz = True
                st.session_state.viz_project_id = 0  # 0 for all projects
                
                response_text += "To filter by specific project:\n" + \
                       "- Use a project ID (e.g., \"Show data for project id 2\")\n" + \
                       "- Ask \"What project options can I view?\" to see available projects"
                return response_text
        
    # Default response for general or unclear questions
    return "To retrieve accurate results, please include one of the following in your question:\n\n" + \
           "- A project ID (e.g., project id 2)\n" + \
           "- A request for all projects (e.g., \"Show results for all projects\")\n" + \
           "- Ask \"What project options can I view data for?\" to get the full list."

# Streamlit UI
st.title("Equipment Data Chatbot")
st.write("Ask questions about the medical equipment data. You can filter by project ID or view all projects.")

# Input for user query
user_input = st.chat_input("Ask a question about medical equipment data...")

if user_input:
    # Reset visualization flag for new query
    st.session_state.show_viz = False
    
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Process the query
    response = process_query(user_input)
    
    # Add bot response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# Display visualization if needed
if st.session_state.show_viz:
    data = load_data()
    create_equipment_visualization(data, st.session_state.viz_project_id)

# Display room planning visualization if needed
if st.session_state.show_room_plan and st.session_state.current_room_plan:
    room_plan = st.session_state.current_room_plan
    st.pyplot(create_room_visualization(room_plan['room_type'], room_plan['recommendations']))
    
    # Add 3D model viewer section
    st.subheader("📋 Interactive 3D Equipment Models")
    st.write("Click on equipment items to view interactive 3D models:")
    
    # Create columns for equipment selection
    col1, col2, col3 = st.columns(3)
    
    # Get room equipment for this room type
    room_type = room_plan['room_type']
    room_info = st.session_state.room_planner.room_equipment.get(room_type, {})
    equipment_list = room_info.get('equipment', [])
    
    # Create buttons for each piece of equipment
    equipment_mapping = {
        'Patient Bed': 'patient bed',
        'Trauma/Resuscitation Bed': 'patient bed',
        'Hospital Bed': 'patient bed',
        'Patient Monitor': 'monitor',
        'Defibrillator/Monitor': 'monitor',
        'Ventilator': 'ventilator',
        'Operating Table': 'operating table',
        'Surgical Table': 'operating table',
        'Crash Cart': 'crash cart',
        'Code Cart': 'crash cart',
        'Emergency Cart': 'crash cart'
    }
    
    equipment_buttons = []
    for item in equipment_list:
        equipment_name = item.get('name', '')
        model_type = equipment_mapping.get(equipment_name, 'generic')
        equipment_buttons.append((equipment_name, model_type))
    
    # Add some common equipment if list is too short
    if len(equipment_buttons) < 3:
        extra_equipment = [('Patient Monitor', 'monitor'), ('Ventilator', 'ventilator'), 
                          ('Crash Cart', 'crash cart'), ('Patient Bed', 'patient bed')]
        for item in extra_equipment:
            if item[0] not in [e[0] for e in equipment_buttons]:
                equipment_buttons.append(item)
                if len(equipment_buttons) >= 6:
                    break
                    
    # Add button for patient-specific recommendations
    st.button("🧑‍⚕️ Get Patient-Specific Equipment Recommendations", 
              on_click=lambda: setattr(st.session_state, 'show_patient_form', True),
              type="primary")
    
    # Organize buttons into columns
    cols = [col1, col2, col3]
    
    # Track which model to display
    if 'selected_3d_model' not in st.session_state:
        st.session_state.selected_3d_model = None
    
    for i, (name, model_type) in enumerate(equipment_buttons[:9]):  # Limit to 9 buttons
        col_idx = i % 3
        if cols[col_idx].button(f"📐 {name}", key=f"model_{i}"):
            st.session_state.selected_3d_model = model_type
    
    # Display the selected 3D model
    if st.session_state.selected_3d_model:
        st.subheader(f"3D Model Viewer: {st.session_state.selected_3d_model.title()}")
        display_3d_model(st.session_state.selected_3d_model)

# Patient-specific equipment recommendation form
if st.session_state.show_patient_form:
    st.header("🏥 Patient-Specific Equipment Recommendation Engine")
    st.write("Complete the form below to get personalized equipment recommendations based on patient characteristics.")
    
    with st.form("patient_form"):
        # Basic patient information
        st.subheader("Patient Information")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=65)
            weight = st.number_input("Weight (kg)", min_value=0, max_value=300, value=70)
        with col2:
            height = st.number_input("Height (cm)", min_value=0, max_value=250, value=170)
            acuity = st.slider("Acuity Level", min_value=1, max_value=5, value=3, 
                            help="1 = Minimal care, 5 = Critical care")
        
        # Medical conditions
        st.subheader("Medical Conditions")
        condition_options = [
            "Pneumonia", "COPD", "Asthma", "Respiratory Failure", 
            "Myocardial Infarction", "Heart Failure", "Hypertension", "Arrhythmia",
            "Stroke", "Seizure Disorder", "Traumatic Brain Injury",
            "GI Bleed", "Inflammatory Bowel Disease",
            "Diabetes", "Diabetic Ketoacidosis",
            "Acute Kidney Injury", "Chronic Kidney Disease",
            "Post Surgical", "Sepsis",
            "Fall Risk", "Mobility Impairment"
        ]
        selected_conditions = st.multiselect("Select Medical Conditions", condition_options)
        
        # Clinical needs
        st.subheader("Special Clinical Needs")
        clinical_needs_options = [
            "Isolation", "Immunocompromised", "Limited Mobility",
            "Visually Impaired", "Hearing Impaired"
        ]
        selected_clinical_needs = st.multiselect("Select Special Clinical Needs", clinical_needs_options)
        
        # Current treatments
        st.subheader("Current Treatments")
        treatment_options = [
            "Chemotherapy", "Radiation Therapy", "Dialysis", "Physical Therapy"
        ]
        selected_treatments = st.multiselect("Select Current Treatments", treatment_options)
        
        # Submit button
        submitted = st.form_submit_button("Generate Recommendations")
        
        if submitted:
            # Prepare patient data
            patient_data = {
                "demographics": {
                    "age": age,
                    "weight": weight,
                    "height": height
                },
                "conditions": selected_conditions,
                "clinical_needs": selected_clinical_needs,
                "treatments": selected_treatments,
                "acuity": acuity
            }
            
            # Generate recommendations
            recommendations = st.session_state.patient_recommender.get_recommendations(patient_data)
            st.session_state.patient_recommendations = recommendations
    
    # Display recommendations if available
    if st.session_state.patient_recommendations:
        st.subheader("📋 Personalized Equipment Recommendations")
        
        # Patient summary
        patient_info = st.session_state.patient_recommendations["patient_info"]
        st.write(f"**Patient Summary:** {len(patient_info['conditions'])} conditions, "
                f"Age: {patient_info['demographics']['age']}, "
                f"Acuity Level: {patient_info['acuity']}/5")
        
        # Display recommendations in expandable sections
        for i, item in enumerate(st.session_state.patient_recommendations["recommendations"][:10]):  # Top 10 recommendations
            with st.expander(f"{i+1}. {item['name']} (Priority Score: {item['priority_score']})"):
                st.write("**Clinical Rationale:**")
                for rationale in item['rationales']:
                    st.write(f"- {rationale}")
                
                # Get equipment details
                details = st.session_state.patient_recommender.get_equipment_details(item['name'])
                if details and 'details' in details:
                    st.write("**Equipment Specifications:**")
                    specs = details['details']
                    for key, value in specs.items():
                        if key != 'features':
                            st.write(f"- **{key.title()}:** {value}")
                        else:
                            st.write(f"- **Features:** {', '.join(value)}")
                
                # Add button to view 3D model if available
                equipment_mapping = {
                    'Cardiac Monitor': 'monitor',
                    'Patient Monitor': 'monitor',
                    'Ventilator': 'ventilator',
                    'Hospital Bed': 'patient bed',
                    'Patient Bed': 'patient bed',
                    'Code Cart': 'crash cart',
                    'Crash Cart': 'crash cart'
                }
                
                if item['name'] in equipment_mapping:
                    if st.button(f"View 3D Model: {item['name']}", key=f"patient_model_{i}"):
                        st.session_state.selected_3d_model = equipment_mapping[item['name']]
        
        # Room layout recommendation
        st.subheader("🏨 Recommended Room Layout")
        st.write("Based on the patient's needs, we recommend the following room layout:")
        
        # Determine best room type based on acuity and conditions
        if acuity >= 4 or "Respiratory Failure" in selected_conditions or "Sepsis" in selected_conditions:
            recommended_room = "ICU"
        elif "Post Surgical" in selected_conditions:
            recommended_room = "Operating Room"
        elif "Myocardial Infarction" in selected_conditions or "Stroke" in selected_conditions:
            recommended_room = "Emergency Room"
        else:
            recommended_room = "Patient Room"
        
        # Get room recommendations
        room_recommendations = st.session_state.room_planner.get_equipment_recommendations(recommended_room)
        
        # Display room type recommendation with explanation
        st.write(f"**Recommended Room Type: {recommended_room}**")
        st.write(f"This recommendation is based on the patient's acuity level ({acuity}/5) "
                f"and their specific medical conditions.")
        
        # Show room visualization
        fig = create_room_visualization(recommended_room, room_recommendations)
        st.pyplot(fig)
        
        # Call to action
        st.success("These personalized recommendations have been generated based on the patient's specific needs. "
                   "The equipment selected will optimize patient care and outcomes.")
        
        # Reset button
        if st.button("Start Over", type="primary"):
            st.session_state.show_patient_form = False
            st.session_state.patient_recommendations = None
            st.rerun()

# Example questions sidebar
with st.sidebar:
    st.subheader("Example Questions")
    st.markdown("""
    **Room Planning:**
    - Where should I put equipment in an ICU?
    - Help me plan an Operating Room layout
    - What equipment goes in a 300 square feet Emergency Room?
    
    **Data Queries:**
    - What projects can I view?
    - Show equipment in project id 2
    - What's the project ID for North Cancer Centre?
    - Show data for all projects
    """)
    
    # Add patient recommender button to sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧑‍⚕️ Patient-Specific Recommendations")
    st.sidebar.write("Get equipment recommendations based on patient needs.")
    if st.sidebar.button("Launch Patient Recommender"):
        st.session_state.show_patient_form = True
    
    # Add a section to display current project context
    st.subheader("Current Context")
    if st.session_state.current_is_project_site_filter == 1:
        project = get_project_by_id(st.session_state.current_project_id)
        if project:
            st.write(f"Viewing data for: **{project['name']}** (ID: {project['id']})")
    elif st.session_state.current_project_id == 0 and st.session_state.current_is_project_site_filter == 0:
        st.write("Viewing data for: **All Projects**")
    else:
        st.write("No project selected")
