class StatisticsTracker:

    def __init__(self) -> None:
        self.hits = 0
        self.faults = 0
        self.steps = []

    def record_step(self, step_result):
        self.steps.append(step_result)

        if step_result.hit:
            self.hits += 1
        else:
            self.faults += 1

    @property
    def total_accesses(self) -> int:
        return self.hits + self.faults

    @property
    def hit_ratio(self) -> float:
        if self.total_accesses == 0:
            return 0.0
        return self.hits / self.total_accesses

    @property
    def fault_ratio(self) -> float:
        if self.total_accesses == 0:
            return 0.0
        return self.faults / self.total_accesses

    def reset(self):
        self.hits = 0
        self.faults = 0
        self.steps.clear()
