from simulator.vm_config import VMConfig
from simulator.simulation_controller import SimulationController
from simulator.replacement_policies.lru import LRUAlgorithm

def main():

    vm = VMConfig(
        virtual_memory_size=65536,     # 64 KB
        physical_memory_size=4096,      # 4 KB
        offset_bits=8                   # 256 byte pages (2^8)
    )

    reference = [
        (120, "R"),
        (240, "R"),
        (4095, "W"),
        (8192, "R"),
        (9000, "W"),
        (256, "R"),
        (9000, "R"),
        (40000, "R")
    ]

    controller = SimulationController(
        vm,
        reference,
        policy=LRUAlgorithm(),
        tlb_entries=4
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
