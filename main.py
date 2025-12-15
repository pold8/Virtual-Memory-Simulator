from simulator.replacement_policies.fifo import FIFOAlgorithm
from simulator.vm_config import VMConfig
from simulator.simulation_controller import SimulationController
from simulator.replacement_policies.lru import LRUAlgorithm
from simulator.replacement_policies.optimal import OptimalAlgorithm

def main():

    vm = VMConfig(
        virtual_memory_size=2048,     # 2 KB
        physical_memory_size=16,      # 16 bytes = 4 frames
        offset_bits=2                 # 4 byte pages (2^2)
    )

    reference = [
        (0, "R"),
        (4, "R"),
        (8, "R"),
        (12, "R"),
        (16, "R"),
        (0, "R"),
        (4, "R"),
        (20, "R"),
        (24, "R"),
        (28, "R"),
        (32, "R"),
        (0, "W"),
        (4, "W"),
        (36, "R"),
        (40, "R")
    ]

    controller = SimulationController(
        vm,
        reference,
        policy=OptimalAlgorithm(),
        tlb_entries=10
    )

    while not controller.is_finished():
        s = controller.step()
        print(
            f"Step {s.step_index:02d} | VA {s.virtual_address} | "
            f"page={s.page} offset={s.offset} | "
            f"TLB={'HIT' if s.tlb_hit else 'MISS'} | "
            f"{'HIT' if s.hit else 'FAULT'} | "
            f"frames={s.frames_snapshot} "
            f"{'(evicted ' + str(s.evicted_page) + ')' if s.evicted_page else ''}"
        )

    print("\n=== Statistics ===")
    print("TLB hits:", controller.stats.tlb_hits)
    print("TLB misses:", controller.stats.tlb_misses)
    print("TLB hit ratio:", round(controller.stats.tlb_hit_ratio, 3))
    print("Page hits:", controller.stats.page_hits)
    print("Page faults:", controller.stats.page_faults)
    print("Page fault ratio:", round(controller.stats.page_fault_ratio, 3))

if __name__ == "__main__":
    main()
