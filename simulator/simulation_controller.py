from simulator.simulation_engine import SimulationEngine
from simulator.statistics_tracker import StatisticsTracker

class SimulationController:

    def __init__(self, num_frames: int, reference_string: list[int], policy):
        self.num_frames = num_frames
        self.reference_string = reference_string
        self.policy = policy

        self.engine = SimulationEngine(num_frames, reference_string, policy)
        self.stats = StatisticsTracker()

    def step(self):
        if self.engine.has_finished():
            return None

        step_result = self.engine.step()
        self.stats.record_step(step_result)
        return step_result

    def run_all(self):
        results = []
        while not self.engine.has_finished():
            step = self.step()
            results.append(step)
        return results

    def reset(self):
        self.engine = SimulationEngine(self.num_frames, self.reference_string, self.policy)
        self.stats.reset()

    def is_finished(self) -> bool:
        return self.engine.has_finished()
