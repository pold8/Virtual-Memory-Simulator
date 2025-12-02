from dataclasses import dataclass

@dataclass
class VMConfig:
    virtual_memory_size: int      # bytes
    physical_memory_size: int     # bytes
    offset_bits: int              # NEW: number of offset bits

    @property
    def page_size(self) -> int:
        return 1 << self.offset_bits    # 2^offset_bits

    @property
    def num_frames(self) -> int:
        return self.physical_memory_size // self.page_size

    @property
    def num_virtual_pages(self) -> int:
        return self.virtual_memory_size // self.page_size
