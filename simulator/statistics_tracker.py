class StatisticsTracker:

    def __init__(self):
        self.page_hits = 0
        self.page_faults = 0
        self.tlb_hits = 0
        self.tlb_misses = 0
        self.disk_writes = 0  # NEW

    def record_step(self, step):
        if step.tlb_hit:
            self.tlb_hits += 1
        else:
            self.tlb_misses += 1
        
        if step.write_back:
            self.disk_writes += 1

        if step.hit:
            self.page_hits += 1
        else:
            self.page_faults += 1

    @property
    def total_accesses(self):
        return self.page_hits + self.page_faults

    @property
    def tlb_total(self):
        return self.tlb_hits + self.tlb_misses

    @property
    def tlb_hit_ratio(self):
        return self.tlb_hits / max(1, self.tlb_total)

    @property
    def page_fault_ratio(self):
        return self.page_faults / max(1, self.total_accesses)

    def reset(self):
        self.__init__()
