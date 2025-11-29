# AirCursor Evaluation Study

This application implements an evaluation study for the AirCursor system using Qt with PySide6.

## Original Study Design Overview

This is a **within-subject** study with 2 conditions x 3 tasks.
- Before starting the main tasks, users will complete a tutorial task to familiarize themselves with the system.
- Each task has 5 trails, each trail has randomized target settings.
- The order of conditions and tasks are counterbalanced using a Latin Square design.

**Conditions:**
- Aircursor (our system)
- Mouse

**Tasks:**
1. **Tutorial**: user practice using the system to complete simple pointing and clicking tasks.
   - moving the cursor into the target area
   - clicking the cursor inside the target area
2. **Menu Selection**: user open a menu and select a specified target item (T).
3. **Drag Drop**: user drag a square object and drop it into a target area (T).
4. **Keyboard Input**: user use the virtual keyboard to type a target word (T).

## Current Implementation

The current implementation focuses on the task execution framework using Qt with PySide6.

## Architecture

The application follows the **view-controller pattern**:

- **app.py**: Main application entry point
- **evaluation_controller.py**: Controller handling study logic and data recording
- **evaluation_view.py**: View managing the Qt user interface
- **recorder.py**: Data recording functionality
- **task_generator.py**: Task configuration generation and reading

## Features

- **Task Management**: Supports multiple task types (MenuSelect, DragDrop, KeyboardInput)
- **Progress Tracking**: Shows current task and trial progress
- **Data Recording**: Records performance metrics for each trial
- **Participant Management**: Supports multiple participants with unique IDs

## Tasks Implemented

### 1. Menu Selection Task
- Right-click to open context menu
- Select highlighted menu item
- Records: completion time, accuracy, precision, error distance

### 2. Drag & Drop Task
- Drag object to highlighted target area
- Records: completion time, accuracy, precision, drag distance

### 3. Keyboard Input Task
- Currently skipped as requested
- Framework ready for future implementation

## Usage

### Prerequisites
Make sure you have the required dependencies installed:
```bash
pip install -r requirements.txt
```

### Generate Task Configurations
```bash
python evaluation_study/task_generator.py
```

### Run the Study
```bash
# Run with default participant ID (0)
python evaluation_study/app.py

# Run with specific participant ID
python evaluation_study/app.py --pid 5
```

### Command Line Arguments
- `--pid`: Participant ID (integer, default: 0)

## Data Output

Results are saved to: `evaluation_study/datasets/p{pid}/task_result.csv`

### Data Fields
- **Global fields**: pid, task_type, trial_index, complete_time, is_correct, precision
- **Task-specific fields**: Each task type has specific payload fields

### MenuSelect Fields
- menu_length, target_index, selected_index
- error_distance, target_distance, moving_distance

### DragDrop Fields
- target_area, dropped_area
- error_distance, target_distance, drag_distance, moving_distance

## Study Flow

1. **Welcome Screen**: Study introduction and participant information
2. **Task Instructions**: Detailed instructions for each task type
3. **Trial Execution**: Individual trial execution with progress tracking
4. **Completion Screen**: Study completion confirmation

## Configuration

Task configurations are generated using a Latin square design for counterbalancing. Each participant receives:
- 5 Menu Selection trials
- 5 Drag & Drop trials 
- 5 Keyboard Input trials (currently skipped)

The order of task types is counterbalanced across participants using modulo operation.

