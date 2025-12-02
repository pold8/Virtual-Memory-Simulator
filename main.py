from simulator.vm_config import VMConfig
from simulator.simulation_controller import SimulationController
from simulator.replacement_policies.lru import LRUAlgorithm
from simulator.replacement_policies.fifo import FIFOAlgorithm
from simulator.replacement_policies.optimal import OptimalAlgorithm

def main():

    vm = VMConfig(
        virtual_memory_size=65536,
        physical_memory_size=4096,
        page_size=256
    )

    reference = [
        (120, "R"),
        (240, "R"),
        (4095, "W"),
        (8192, "R"),
        (9000, "W"),
        (256, "R")
    ]

    policy = LRUAlgorithm()

    controller = SimulationController(vm, reference, policy)

    while not controller.is_finished():
        step = controller.step()
        print(
            f"Step {step.step_index:02d} | VA {step.virtual_address} | "
            f"page {step.page} | offset {step.offset} | {step.operation} | "
            f"{'HIT' if step.hit else 'FAULT'} | frames={step.frames_snapshot} | "
            f"{'evicted ' + str(step.evicted_page) if step.evicted_page else ''}"
        )

    print("\n--- Statistics ---")
    print("Hits:", controller.stats.hits)
    print("Faults:", controller.stats.faults)
    print("Hit ratio:", controller.stats.hit_ratio)

if __name__ == "__main__":
    main()
