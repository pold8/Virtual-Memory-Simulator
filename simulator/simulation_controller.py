from simulator.simulation_engine import SimulationEngine
from simulator.statistics_tracker import StatisticsTracker
from simulator.vm_config import VMConfig
from simulator.base_policy import ReplacementPolicy

class SimulationController:

    def __init__(
        self,
        vm_config: VMConfig,
        reference_string: list[tuple[int, str]],
        policy: ReplacementPolicy
    ):
        self.vm_config = vm_config
        self.reference_string = reference_string
        self.policy = policy

        self.engine = SimulationEngine(vm_config, reference_string, policy)
        self.stats = StatisticsTracker()

    def step(self):
        if self.engine.has_finished():
            return None
        step = self.engine.step()
        self.stats.record_step(step)
        return step

    def run_all(self):
        results = []
        while not self.engine.has_finished():
            results.append(self.step())
        return results

    def reset(self):
        self.engine = SimulationEngine(self.vm_config, self.reference_string, self.policy)
        self.stats.reset()

    def is_finished(self):
        return self.engine.has_finished()
