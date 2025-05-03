from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


def process_agent_data(
        agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    # Constants for road condition classification
    POTHOLE_THRESHOLD = 1.8  # Threshold for y-axis acceleration to detect potholes
    BUMP_THRESHOLD = 1.5  # Threshold for z-axis acceleration to detect bumps

    # Extract accelerometer data
    accel_x = agent_data.accelerometer_x
    accel_y = agent_data.accelerometer_y
    accel_z = agent_data.accelerometer_z

    # Determine road condition based on accelerometer data
    road_condition = "normal"
    confidence = 0.8  # Default confidence for normal roads

    # Check for pothole (significant negative y-axis acceleration)
    if abs(accel_y) > POTHOLE_THRESHOLD:
        road_condition = "pothole"
        # Higher confidence for values significantly above threshold
        confidence = min(0.95, 0.7 + 0.1 * (abs(accel_y) / POTHOLE_THRESHOLD))

    # Check for bump (significant positive z-axis acceleration)
    elif abs(accel_z) > BUMP_THRESHOLD:
        road_condition = "bump"
        # Confidence based on how much the value exceeds the threshold
        confidence = min(0.9, 0.65 + 0.1 * (abs(accel_z) / BUMP_THRESHOLD))
    else:
        # Normal road - confidence inversely proportional to acceleration values
        max_accel = max(abs(accel_x), abs(accel_y), abs(accel_z))
        confidence = 0.9 - 0.1 * (max_accel / min(POTHOLE_THRESHOLD, BUMP_THRESHOLD))

    # Create processed data with classification results
    return ProcessedAgentData(
        road_condition=road_condition,
        confidence=confidence,
        location_lat=agent_data.gps_latitude,
        location_lon=agent_data.gps_longitude,
        timestamp=agent_data.timestamp,
        raw_data={
            "acceleration_x": accel_x,
            "acceleration_y": accel_y,
            "acceleration_z": accel_z
        }
    )
