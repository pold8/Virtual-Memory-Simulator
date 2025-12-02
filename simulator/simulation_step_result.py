from dataclasses import dataclass
from typing import Optional, List

@dataclass
class SimulationStepResult:
    step_index: int
    virtual_address: int
    operation: str
    page: int
    offset: int
    hit: bool
    fault: bool
    frame_index: Optional[int]
    evicted_page: Optional[int]
    victim_frame_index: Optional[int]
    frames_snapshot: List[Optional[int]]
