"""
Interactive 3D Model Viewer for Medical Equipment
"""
import plotly.graph_objects as go
import numpy as np
import streamlit as st

def create_equipment_model(equipment_type):
    """Create a 3D model of medical equipment based on type."""
    
    # Default parameters
    length, width, height = 1.0, 0.5, 0.4  # Basic dimensions
    color = 'lightblue'
    
    # Equipment-specific parameters
    if equipment_type.lower() == 'patient bed':
        length, width, height = 2.0, 0.9, 0.7
        color = '#3498db'
        return create_bed_model(length, width, height, color)
    
    elif equipment_type.lower() == 'ventilator':
        length, width, height = 0.5, 0.5, 1.2
        color = '#2ecc71'
        return create_ventilator_model(length, width, height, color)
    
    elif equipment_type.lower() == 'monitor':
        length, width, height = 0.4, 0.1, 0.3
        color = '#e74c3c'
        return create_monitor_model(length, width, height, color)
    
    elif equipment_type.lower() == 'operating table':
        length, width, height = 2.0, 0.7, 0.9
        color = '#3498db'
        return create_operating_table_model(length, width, height, color)
        
    elif equipment_type.lower() == 'crash cart':
        length, width, height = 0.9, 0.6, 1.0
        color = '#e67e22'
        return create_cart_model(length, width, height, color)
    
    else:
        # Generic equipment model
        return create_generic_model(length, width, height, color, equipment_type)

def create_bed_model(length, width, height, color):
    """Create a 3D model of a hospital bed."""
    # Base frame
    base_x, base_y, base_z = create_box_vertices(length, width, height*0.3)
    
    # Mattress
    mattress_x, mattress_y, mattress_z = create_box_vertices(length*0.9, width*0.9, height*0.2)
    mattress_z = [z + height*0.3 for z in mattress_z]  # Place on top of base
    
    # Head/foot boards
    head_x, head_y, head_z = create_box_vertices(width*0.1, width, height*0.7)
    head_x = [x + length*0.45 for x in head_x]  # Place at head of bed
    head_z = [z + height*0.3 for z in head_z]  # Place on top of base
    
    foot_x, foot_y, foot_z = create_box_vertices(width*0.1, width, height*0.5)
    foot_x = [x - length*0.45 for x in foot_x]  # Place at foot of bed
    foot_z = [z + height*0.3 for z in foot_z]  # Place on top of base
    
    # Side rails
    rail1_x, rail1_y, rail1_z = create_box_vertices(length*0.7, width*0.05, height*0.3)
    rail1_y = [y + width*0.45 for y in rail1_y]  # Place on side
    rail1_z = [z + height*0.5 for z in rail1_z]  # Raise to proper height
    
    rail2_x, rail2_y, rail2_z = create_box_vertices(length*0.7, width*0.05, height*0.3)
    rail2_y = [y - width*0.45 for y in rail2_y]  # Place on other side
    rail2_z = [z + height*0.5 for z in rail2_z]  # Raise to proper height
    
    # Create a figure
    fig = go.Figure()
    
    # Add base
    fig.add_trace(go.Mesh3d(
        x=base_x, y=base_y, z=base_z,
        color=color, opacity=0.7, name='Bed Frame'
    ))
    
    # Add mattress
    fig.add_trace(go.Mesh3d(
        x=mattress_x, y=mattress_y, z=mattress_z,
        color='white', opacity=0.9, name='Mattress'
    ))
    
    # Add head/foot boards
    fig.add_trace(go.Mesh3d(
        x=head_x, y=head_y, z=head_z,
        color=color, opacity=0.8, name='Headboard'
    ))
    
    fig.add_trace(go.Mesh3d(
        x=foot_x, y=foot_y, z=foot_z,
        color=color, opacity=0.8, name='Footboard'
    ))
    
    # Add side rails
    fig.add_trace(go.Mesh3d(
        x=rail1_x, y=rail1_y, z=rail1_z,
        color='lightgrey', opacity=0.8, name='Side Rail'
    ))
    
    fig.add_trace(go.Mesh3d(
        x=rail2_x, y=rail2_y, z=rail2_z,
        color='lightgrey', opacity=0.8, name='Side Rail'
    ))
    
    return fig

def create_ventilator_model(length, width, height, color):
    """Create a 3D model of a ventilator."""
    # Main body
    body_x, body_y, body_z = create_box_vertices(length, width, height*0.8)
    
    # Screen
    screen_x, screen_y, screen_z = create_box_vertices(length*0.8, width*0.1, height*0.4)
    screen_y = [y - width*0.45 for y in screen_y]  # Place on front
    screen_z = [z + height*0.3 for z in screen_z]  # Raise to proper height
    
    # Tubes
    tube_radius = 0.05
    tube_theta = np.linspace(0, 2*np.pi, 20)
    tube_x = []
    tube_y = []
    tube_z = []
    
    for t in np.linspace(0, 1, 20):
        tube_x.append(length*0.4)
        tube_y.append(width*0.3)
        tube_z.append(height*(0.8 + 0.2*t))
    
    # Create a figure
    fig = go.Figure()
    
    # Add body
    fig.add_trace(go.Mesh3d(
        x=body_x, y=body_y, z=body_z,
        color=color, opacity=0.8, name='Ventilator Body'
    ))
    
    # Add screen
    fig.add_trace(go.Mesh3d(
        x=screen_x, y=screen_y, z=screen_z,
        color='black', opacity=0.9, name='Display Screen'
    ))
    
    # Add tube
    fig.add_trace(go.Scatter3d(
        x=tube_x, y=tube_y, z=tube_z,
        mode='lines', line=dict(color='lightgrey', width=10),
        name='Ventilator Tube'
    ))
    
    return fig

def create_monitor_model(length, width, height, color):
    """Create a 3D model of a patient monitor."""
    # Screen
    screen_x, screen_y, screen_z = create_box_vertices(length, width, height)
    
    # Stand
    stand_x, stand_y, stand_z = create_box_vertices(length*0.2, width, height*0.2)
    stand_z = [z - height*0.1 for z in stand_z]  # Place at bottom of screen
    
    # Create a figure
    fig = go.Figure()
    
    # Add screen
    fig.add_trace(go.Mesh3d(
        x=screen_x, y=screen_y, z=screen_z,
        color=color, opacity=0.8, name='Monitor Screen'
    ))
    
    # Add stand
    fig.add_trace(go.Mesh3d(
        x=stand_x, y=stand_y, z=stand_z,
        color='darkgrey', opacity=0.9, name='Monitor Stand'
    ))
    
    return fig

def create_operating_table_model(length, width, height, color):
    """Create a 3D model of an operating table."""
    # Table top
    top_x, top_y, top_z = create_box_vertices(length, width, height*0.1)
    top_z = [z + height*0.7 for z in top_z]  # Raise to proper height
    
    # Base
    base_x, base_y, base_z = create_box_vertices(length*0.5, width*0.8, height*0.2)
    
    # Column
    column_x, column_y, column_z = create_box_vertices(length*0.2, width*0.2, height*0.7)
    column_z = [z + height*0.2 for z in column_z]  # Place on top of base
    
    # Create a figure
    fig = go.Figure()
    
    # Add table top
    fig.add_trace(go.Mesh3d(
        x=top_x, y=top_y, z=top_z,
        color=color, opacity=0.9, name='Table Surface'
    ))
    
    # Add base
    fig.add_trace(go.Mesh3d(
        x=base_x, y=base_y, z=base_z,
        color='darkgrey', opacity=0.8, name='Table Base'
    ))
    
    # Add column
    fig.add_trace(go.Mesh3d(
        x=column_x, y=column_y, z=column_z,
        color='darkgrey', opacity=0.8, name='Table Column'
    ))
    
    return fig

def create_cart_model(length, width, height, color):
    """Create a 3D model of a medical cart."""
    # Main body
    body_x, body_y, body_z = create_box_vertices(length, width, height*0.9)
    
    # Wheels
    wheel_radius = min(length, width) * 0.1
    wheel_positions = [
        [length/2-wheel_radius, width/2-wheel_radius, -wheel_radius],
        [length/2-wheel_radius, -width/2+wheel_radius, -wheel_radius],
        [-length/2+wheel_radius, width/2-wheel_radius, -wheel_radius],
        [-length/2+wheel_radius, -width/2+wheel_radius, -wheel_radius]
    ]
    
    # Drawers
    drawer_count = 3
    drawer_height = height * 0.8 / drawer_count
    drawers_x = []
    drawers_y = []
    drawers_z = []
    
    for i in range(drawer_count):
        # Each drawer is slightly smaller than the cart body
        d_x, d_y, d_z = create_box_vertices(length*0.95, width*0.9, drawer_height*0.9)
        # Position the drawer
        d_y = [y - width*0.05 for y in d_y]  # Indent from front
        d_z = [z + i*drawer_height + drawer_height*0.05 for z in d_z]
        drawers_x.extend(d_x)
        drawers_y.extend(d_y)
        drawers_z.extend(d_z)
    
    # Create a figure
    fig = go.Figure()
    
    # Add body
    fig.add_trace(go.Mesh3d(
        x=body_x, y=body_y, z=body_z,
        color=color, opacity=0.8, name='Cart Body'
    ))
    
    # Add wheels
    for pos in wheel_positions:
        # Create coordinates for wheel
        wheel_x, wheel_y, wheel_z = [], [], []
        for theta in np.linspace(0, 2*np.pi, 20):
            for phi in np.linspace(0, np.pi, 10):
                wheel_x.append(pos[0] + wheel_radius * np.sin(phi) * np.cos(theta))
                wheel_y.append(pos[1] + wheel_radius * np.sin(phi) * np.sin(theta))
                wheel_z.append(pos[2] + wheel_radius * np.cos(phi))
        
        fig.add_trace(go.Mesh3d(
            x=wheel_x, y=wheel_y, z=wheel_z,
            color='black', opacity=0.8, name='Wheel'
        ))
    
    # Add drawer outlines
    fig.add_trace(go.Scatter3d(
        x=drawers_x, y=drawers_y, z=drawers_z,
        mode='lines', line=dict(color='white', width=2),
        name='Drawers'
    ))
    
    return fig

def create_generic_model(length, width, height, color, equipment_type):
    """Create a generic 3D model for equipment."""
    # Main body
    body_x, body_y, body_z = create_box_vertices(length, width, height)
    
    # Create a figure
    fig = go.Figure()
    
    # Add body
    fig.add_trace(go.Mesh3d(
        x=body_x, y=body_y, z=body_z,
        color=color, opacity=0.8, name=equipment_type
    ))
    
    # Add text label
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[height/2],
        mode='text',
        text=[equipment_type],
        textposition='middle center',
        textfont=dict(size=12, color='black'),
        name='Label'
    ))
    
    return fig

def create_box_vertices(length, width, height):
    """Create vertices for a box."""
    x = []
    y = []
    z = []
    
    # Bottom face
    x.extend([length/2, length/2, -length/2, -length/2, length/2])
    y.extend([width/2, -width/2, -width/2, width/2, width/2])
    z.extend([0, 0, 0, 0, 0])
    
    # Top face
    x.extend([length/2, length/2, -length/2, -length/2, length/2])
    y.extend([width/2, -width/2, -width/2, width/2, width/2])
    z.extend([height, height, height, height, height])
    
    # Connect bottom to top
    x.extend([length/2, length/2, -length/2, -length/2])
    y.extend([width/2, -width/2, -width/2, width/2])
    z.extend([0, 0, 0, 0])
    
    x.extend([length/2, length/2, -length/2, -length/2])
    y.extend([width/2, -width/2, -width/2, width/2])
    z.extend([height, height, height, height])
    
    return x, y, z

def update_figure_layout(fig, equipment_type):
    """Update layout properties of the figure."""
    fig.update_layout(
        title=f"3D Model: {equipment_type}",
        scene=dict(
            xaxis_title="Length",
            yaxis_title="Width",
            zaxis_title="Height",
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0,
            xanchor="right",
            x=1
        )
    )
    
    # Add camera position for better initial view
    fig.update_layout(
        scene_camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    )
    
    return fig

def display_3d_model(equipment_type):
    """Main function to display a 3D model in Streamlit."""
    
    # Create the equipment model
    fig = create_equipment_model(equipment_type)
    
    # Update layout
    fig = update_figure_layout(fig, equipment_type)
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    # Add instructions
    st.caption("**Interactive Controls:** Click and drag to rotate. Scroll to zoom. Right-click and drag to pan.")
    
    return fig
