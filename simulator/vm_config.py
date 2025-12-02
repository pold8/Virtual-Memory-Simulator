from dataclasses import dataclass

@dataclass
class VMConfig:
    virtual_memory_size: int
    physical_memory_size: int
    page_size: int

    @property
    def num_frames(self) -> int:
        return self.physical_memory_size // self.page_size

    @property
    def num_virtual_pages(self) -> int:
        return self.virtual_memory_size // self.page_size
