# Virtual Memory Simulator

A Python-based simulator for virtual memory management concepts. This project provides both a command-line interface (CLI) and a graphical user interface (GUI) to visualize how virtual memory, physical memory (frames), page tables, and TLBs interact.

## Features

- **Virtual to Physical Address Translation**: Simulates the mapping process using page tables.
- **Translation Lookaside Buffer (TLB)**: Simulates TLB hits and misses to speed up translation.
- **Page Replacement Algorithms**:
  - **FIFO** (First-In, First-Out)
  - **LRU** (Least Recently Used)
  - **Optimal** (Belady's Algorithm)
- **Visual Interface**: A Pygame-based GUI to watch the memory simulation in real-time.
- **Statistics**: detailed hits, faults, and ratio statistics.

## Requirements

- Python 3.x
- Pygame (for the GUI)

## Installation

1.  Clone the repository or download the source code.
2.  Install the required dependencies:

    ```bash
    pip install pygame
    ```

## Usage

### Graphical User Interface (GUI)
To run the visual simulator:

```bash
python run_ui.py
```

This will open a window where you can:
- Configure memory settings.
- Select a page replacement policy.
- Step through memory references visually.

### Command Line Interface (CLI)
To run the text-based simulation:

```bash
python main.py
```

You can modify `main.py` to change the reference string, memory configuration, or selected algorithm.

## Project Structure

- `main.py`: Entry point for the CLI simulation.
- `run_ui.py`: Entry point for the GUI application.
- `simulator/`: Core logic for memory management, page tables, and algorithms.
  - `replacement_policies/`: Implementation of FIFO, LRU, and Optimal algorithms.
- `ui/`: Code related to the Pygame visualization.
- `tests/`: Unit tests for the simulator components.
