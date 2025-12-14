import pygame
import sys
import os
from typing import Dict, Optional

# Add parent directory to path to import simulator modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from simulator.vm_config import VMConfig
from simulator.simulation_controller import SimulationController
from simulator.replacement_policies.lru import LRUAlgorithm
from simulator.simulation_step_result import SimulationStepResult

# --- Constants & Configuration ---
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Colors
COLOR_BG = (30, 30, 30)         # Dark Grey
COLOR_PANEL = (45, 45, 45)      # Lighter Grey
COLOR_ACCENT = (230, 60, 60)      # Brighter Red
COLOR_HIGHLIGHT = (255, 100, 100) # Lighter Red for highlights
COLOR_TEXT_MAIN = (240, 240, 240)
COLOR_TEXT_DIM = (180, 180, 180)
COLOR_GREEN = (50, 200, 100)
COLOR_BLUE = (50, 100, 200)
COLOR_BORDER = (60, 60, 60)

# Layout
CONFIG_PANEL_X = 20
CONFIG_PANEL_Y = 60
CONFIG_PANEL_W = WINDOW_WIDTH - 40
CONFIG_PANEL_H = 180
CONTENT_TOP = CONFIG_PANEL_Y + CONFIG_PANEL_H + 20
BUTTON_AREA_Y = WINDOW_HEIGHT - 70

# Fonts
FONT_MAIN = None
FONT_HEADER = None
FONT_SMALL = None
FONT_LARGE = None

def init_fonts():
    global FONT_MAIN, FONT_HEADER, FONT_SMALL, FONT_LARGE
    pygame.font.init()
    # Try to use a nice modern font if available, fallback to default
    available_fonts = pygame.font.get_fonts()
    font_name = "segoeui" if "segoeui" in available_fonts else None
    
    FONT_HEADER = pygame.font.SysFont(font_name, 32, bold=True)
    FONT_LARGE = pygame.font.SysFont(font_name, 26, bold=True)
    FONT_MAIN = pygame.font.SysFont(font_name, 20)
    FONT_SMALL = pygame.font.SysFont(font_name, 15)

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, surface):
        color = COLOR_HIGHLIGHT if self.hovered else COLOR_ACCENT
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 1, border_radius=8)
        
        text_surf = FONT_MAIN.render(self.text, True, COLOR_TEXT_MAIN)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.action()

class TextInput:
    def __init__(self, x, y, width, height, label, text="", numeric=False, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.text = str(text)
        self.placeholder = str(placeholder if placeholder else text)
        self.active = False
        self.numeric = numeric

    def draw(self, surface):
        label_surf = FONT_SMALL.render(self.label, True, COLOR_TEXT_DIM)
        # Increased vertical space from -18 to -24
        surface.blit(label_surf, (self.rect.x, self.rect.y - 24))

        pygame.draw.rect(surface, COLOR_BORDER, self.rect, 2 if self.active else 1, border_radius=6)
        bg_color = (55, 55, 55) if self.active else (50, 50, 50)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=6)

        # Clip text to input box
        old_clip = surface.get_clip()
        surface.set_clip(self.rect.inflate(-8, -4))

        txt = self.text if self.text else self.placeholder
        color = COLOR_TEXT_MAIN if self.text else COLOR_TEXT_DIM
        text_surf = FONT_MAIN.render(txt, True, color)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 8, self.rect.centery))
        surface.blit(text_surf, text_rect)

        surface.set_clip(old_clip)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                if self.numeric and not event.unicode.isdigit():
                    return
                self.text += event.unicode

class MemoryVisualizer:
    def __init__(self):
        pygame.init()
        init_fonts()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Virtual Memory Simulator")
        self.clock = pygame.time.Clock()
        
        # Preset configuration & inputs
        self.default_reference_text = (
            "120 R, 240 R, 4095 W, 8192 R, 9000 W, 256 R, 9000 R, 40000 R, "
            "120 W, 8192 W, 40000 W, 256 W, 500 R, 600 R, 700 R, 800 R, "
            "500 W, 4095 R, 120 R, 24000 W"
        )
        self.reference_string = self.parse_reference_string(self.default_reference_text)
        self.vm_config = VMConfig(
            virtual_memory_size=65536,     # 64 KB
            physical_memory_size=4096,     # 4 KB (16 frames)
            offset_bits=8                  # 256 bytes per page
        )
        # Store defaults for reset
        self.default_config = {
            "virtual": 65536,
            "physical": 4096,
            "offset": 8,
            "reference": self.default_reference_text
        }

        self.policy = LRUAlgorithm()
        self.controller = SimulationController(
            self.vm_config, self.reference_string, self.policy, tlb_entries=4
        )
        self.last_step_result: Optional[SimulationStepResult] = None
        self.auto_run = False
        self.auto_run_delay = 500  # ms
        self.last_step_time = 0
        self.simulation_finished = False
        self.info_message = ""
        self.page_writes: Dict[int, Dict[str, int]] = {}

        # GUI Elements
        self.input_fields = self.build_input_fields()
        # Buttons are initialized inside build_input_fields to maintain layout consistency
        


    # --- Input helpers ---
    def build_input_fields(self):
        # Zone 2 Left: Config Panel (Top)
        # Increased start_y to clear the "Configuration" title text completely
        start_y = 125 
        x = 30
        width = 220
        height = 30
        spacing = 45 # Increased spacing for breathing room

        fields = {
            "virtual": TextInput(x, start_y, width, height, "Virtual Memory (bytes)", self.vm_config.virtual_memory_size, numeric=True),
            "physical": TextInput(x, start_y + spacing, width, height, "Physical Memory (bytes)", self.vm_config.physical_memory_size, numeric=True),
            "offset": TextInput(x, start_y + spacing * 2, width, height, "Offset Bits", self.vm_config.offset_bits, numeric=True),
            "reference": TextInput(x, start_y + spacing * 3, width, height, "Reference String", self.default_reference_text, placeholder="120 R, ..."),
        }
        
        # Config Actions (Submit/Reset Defaults) just below inputs
        btn_y = start_y + spacing * 4 + 10
        self.submit_button = Button(x, btn_y, 105, 30, "Submit", self.apply_inputs)
        self.default_button = Button(x + 115, btn_y, 105, 30, "Defaults", self.reset_defaults)
        
        # Random Reference Button
        self.random_button = Button(x, btn_y + 40, width, 30, "Random Ref String", self.generate_random_reference)
        
        # Zone 2 Left: Simulation Controls (Bottom)
        # Push controls down to separate panel
        ctrl_y = btn_y + 90 
        self.buttons = [
            Button(x, ctrl_y, 105, 35, "Next Step", self.next_step),
            Button(x + 115, ctrl_y, 105, 35, "Auto Run", self.toggle_auto),
            Button(x, ctrl_y + 45, width, 30, "Reset Sim", self.reset_sim),
        ]
        
        return fields

    def parse_reference_string(self, text: str):
        if not text.strip():
            raise ValueError("Reference string is empty.")

        cleaned = text.replace(";", ",")
        pairs = []
        for raw in cleaned.split(","):
            token = raw.strip()
            if not token:
                continue
            if " " in token:
                parts = token.split()
                if len(parts) != 2:
                    raise ValueError(f"Invalid token '{token}'. Use 'addr op'.")
                addr_str, op = parts
            elif ":" in token:
                addr_str, op = token.split(":")
            else:
                addr_str, op = token[:-1], token[-1]

            if not addr_str.isdigit():
                raise ValueError(f"Address '{addr_str}' is not a number.")
            addr = int(addr_str)
            op = op.upper()
            if op not in ("R", "W"):
                raise ValueError(f"Operation must be R or W, got '{op}'.")
            pairs.append((addr, op))

        if not pairs:
            raise ValueError("Reference string is empty after parsing.")
        return pairs

    def apply_inputs(self):
        try:
            virtual_size = int(self.input_fields["virtual"].text or 0)
            physical_size = int(self.input_fields["physical"].text or 0)
            offset_bits = int(self.input_fields["offset"].text or 0)
            reference_string = self.parse_reference_string(self.input_fields["reference"].text)

            if offset_bits <= 0:
                raise ValueError("Offset bits must be positive.")

            page_size = 1 << offset_bits
            if physical_size % page_size != 0:
                raise ValueError("Physical memory size must be a multiple of page size.")
            if virtual_size % page_size != 0:
                raise ValueError("Virtual memory size must be a multiple of page size.")
            if physical_size <= 0 or virtual_size <= 0:
                raise ValueError("Memory sizes must be positive.")
            if physical_size > virtual_size:
                raise ValueError("Physical memory cannot exceed virtual memory.")

            self.vm_config = VMConfig(
                virtual_memory_size=virtual_size,
                physical_memory_size=physical_size,
                offset_bits=offset_bits
            )
            self.reference_string = reference_string
            self.build_controller()
            self.info_message = "Applied inputs and reset simulation."
        except ValueError as e:
            self.info_message = f"Input error: {e}"

    def build_controller(self):
        self.policy = LRUAlgorithm()
        self.controller = SimulationController(
            self.vm_config, self.reference_string, self.policy, tlb_entries=4
        )
        self.last_step_result = None
        self.simulation_finished = False
        self.auto_run = False
        self.last_step_time = 0
        self.page_writes = {}

    def reset_defaults(self):
        self.input_fields["virtual"].text = str(self.default_config["virtual"])
        self.input_fields["physical"].text = str(self.default_config["physical"])
        self.input_fields["offset"].text = str(self.default_config["offset"])
        self.input_fields["reference"].text = self.default_config["reference"]
        self.apply_inputs()
        self.info_message = "Reset to default values."

    def reset_sim(self):
        self.build_controller()
        self.info_message = "Simulation reset."

    def next_step(self):
        if not self.controller.is_finished():
            self.last_step_result = self.controller.step()
            self.record_write(self.last_step_result)
        else:
            self.simulation_finished = True
            self.auto_run = False

    def record_write(self, result: Optional[SimulationStepResult]):
        if result and result.operation == "W" and result.frame_index is not None:
            physical_address = result.frame_index * self.vm_config.page_size + result.offset
            self.page_writes[result.page] = {
                "virtual_address": result.virtual_address,
                "physical_address": physical_address,
                "step": result.step_index
            }

    def generate_random_reference(self):
        import random
        # Generate 20-30 ops with locality of reference to ensure hits
        count = random.randint(20, 30)
        ops = []
        
        # Define a "working set" of a few pages to generate hits
        # e.g. select 3 random pages that will be accessed frequently
        total_pages = self.vm_config.virtual_memory_size // self.vm_config.page_size
        working_set = [random.randint(0, total_pages - 1) for _ in range(3)]
        
        for _ in range(count):
            # 80% chance to pick from working set (Locality), 20% random
            if random.random() < 0.8:
                page = random.choice(working_set)
            else:
                page = random.randint(0, total_pages - 1)
                
            # Random offset within the page
            offset = random.randint(0, self.vm_config.page_size - 1)
            addr = page * self.vm_config.page_size + offset
            
            # 25% Write, 75% Read
            op = 'W' if random.random() < 0.25 else 'R'
            ops.append(f"{addr} {op}")
        
        self.input_fields["reference"].text = ", ".join(ops)
        self.info_message = "Generated local-reference string."

    def toggle_auto(self):
        self.auto_run = not self.auto_run

    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                for btn in self.buttons + [self.submit_button, self.default_button, self.random_button]:
                    btn.handle_event(event)
                for field in self.input_fields.values():
                    field.handle_event(event)

            # Auto Run Logic
            if self.auto_run and not self.simulation_finished:
                if current_time - self.last_step_time > self.auto_run_delay:
                    self.next_step()
                    self.last_step_time = current_time

            # Drawing
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def compute_layout(self):
        header_h = 60
        gap = 12

        # Tweak heights to ensure fit
        row2_h = 510  # Reduced slightly from 520
        config_h = 360  # Reduced height
        
        row2_y = header_h + gap

        col1_x = 20
        col1_w = 280

        col2_x = col1_x + col1_w + gap
        col2_w = 340

        col3_x = col2_x + col2_w + gap
        col3_w = WINDOW_WIDTH - col3_x - 20

        row3_y = row2_y + row2_h + gap
        # Force bottom panels to fit strictly within window minus margin
        row3_h = WINDOW_HEIGHT - row3_y - 15
        if row3_h < 150: # safety floor
             row3_h = 150 

        bottom_split_w = (WINDOW_WIDTH - 40 - gap) // 2

        controls_h = max(130, row2_h - config_h - gap)
        controls_y = row2_y + config_h + gap

        return {
            "header_h": header_h,
            "gap": gap,
            "row2_y": row2_y,
            "row2_h": row2_h,
            "row3_y": row3_y,
            "row3_h": row3_h,
            "col1_x": col1_x,
            "col1_w": col1_w,
            "col2_x": col2_x,
            "col2_w": col2_w,
            "col3_x": col3_x,
            "col3_w": col3_w,
            "bottom_split_w": bottom_split_w,
            "config_h": config_h,
            "controls_h": controls_h,
            "controls_y": controls_y,
        }

    def apply_layout(self, layout):
        base_x = layout["col1_x"] + 14
        base_y = layout["row2_y"] + 70
        field_w = layout["col1_w"] - 28
        field_h = 30
        spacing = 52 # Increased spacing
        gap_small = 12

        # Stack inputs evenly
        for idx, key in enumerate(["virtual", "physical", "offset", "reference"]):
            field = self.input_fields[key]
            field.rect.x = base_x
            field.rect.y = base_y + idx * spacing
            field.rect.w = field_w
            field.rect.h = field_h

        # Config buttons (Submit/Defaults)
        # Position them relative to base_y (inputs start)
        # 4 inputs * spacing(42) = 168 offset.
        # Button Y should be approx base_y + 168 + padding
        btn_y = base_y + spacing * 4 - 6
        
        half_w = (field_w - gap_small) // 2
        self.submit_button.rect.update(base_x, btn_y, half_w, 34)
        self.default_button.rect.update(base_x + half_w + gap_small, btn_y, half_w, 34)
        
        # Random button below them
        rand_y = btn_y + 34 + 10
        self.random_button.rect.update(base_x, rand_y, field_w, 34)

        # Sim Control buttons
        # Start top of the panel since there is no title now
        ctrl_y = layout["controls_y"] + 15
        btn_h = 34
        gap_btn = 10
        self.buttons[0].rect.update(base_x, ctrl_y, field_w, btn_h)                    # Next
        self.buttons[1].rect.update(base_x, ctrl_y + btn_h + gap_btn, field_w, btn_h)  # Auto
        # Reset button often needs less vertical space or same
        self.buttons[2].rect.update(base_x, ctrl_y + (btn_h + gap_btn) * 2, field_w, btn_h) # Reset

    def draw(self):
        self.screen.fill(COLOR_BG)
        self.draw_header()

        layout = self.compute_layout()
        self.apply_layout(layout)
        # Provide inst section height for downstream drawing
        self.inst_section_height = 200

        row2_y = layout["row2_y"]
        row2_h = layout["row2_h"]
        gap = layout["gap"]
        col1_x = layout["col1_x"]
        col1_w = layout["col1_w"]
        col2_x = layout["col2_x"]
        col2_w = layout["col2_w"]
        col3_x = layout["col3_x"]
        col3_w = layout["col3_w"]
        row3_y = layout["row3_y"]
        row3_h = layout["row3_h"]
        bottom_split_w = layout["bottom_split_w"]
        config_h = layout["config_h"]
        controls_h = layout["controls_h"]
        controls_y = layout["controls_y"]

        # --- Drawing Zone 2 ---
        self.draw_panel_rect(col1_x, row2_y, col1_w, config_h, "Configuration")
        # Draw second panel without title ("")
        self.draw_panel_rect(col1_x, controls_y, col1_w, controls_h, "")
        
        for field in self.input_fields.values():
            field.draw(self.screen)
        self.submit_button.draw(self.screen)
        self.default_button.draw(self.screen)
        self.random_button.draw(self.screen)
        for btn in self.buttons:
            if btn.action == self.toggle_auto:
                btn.text = "Stop Auto" if self.auto_run else "Auto Run"
            btn.draw(self.screen)

        # 2. TLB (Center) - Occupies full height now
        # Removed Address Breakdown as requested to maximize TLB space
        self.draw_tlb_view(col2_x, row2_y, col2_w, row2_h)
        
        # 3. Page Table (Right)
        self.draw_virtual_memory_view(col3_x, row2_y, col3_w, row2_h)
        
        # --- Drawing Zone 3 ---
        
        # 4. Stats & Reference (Bottom Left)
        self.draw_stats_panel(20, row3_y, bottom_split_w, row3_h)
        
        # 5. Physical Memory (Bottom Right)
        pm_x = 20 + bottom_split_w + gap
        self.draw_memory_view(pm_x, row3_y, bottom_split_w, row3_h)

    def draw_instruction_breakdown(self, x, y, w, h):
        self.draw_panel_rect(x, y, w, h, "Address Breakdown")
        
        if not self.last_step_result:
             msg = FONT_MAIN.render("Waiting for step...", True, COLOR_TEXT_DIM)
             self.screen.blit(msg, (x + 20, y + 60))
             return

        res = self.last_step_result
        
        # Box for Virtual Address
        va_val = res.virtual_address
        page = res.page
        offset = res.offset
        
        # Binary/Hex strings if needed, but decimal is clearer for general users
        # Layout: [ Virtual Address ] -> [ Page # ] [ Offset ]
        cx = x + w // 2
        cy = y + 55  # Keep everything higher in the panel
        
        # VA Box
        va_rect = pygame.Rect(0, 0, 140, 32)
        va_rect.center = (cx, cy)
        pygame.draw.rect(self.screen, COLOR_PANEL, va_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, va_rect, 1, border_radius=6)
        
        va_txt = FONT_MAIN.render(f"VA: {va_val}", True, COLOR_TEXT_MAIN)
        self.screen.blit(va_txt, va_txt.get_rect(center=va_rect.center))
        
        # Arrows
        pygame.draw.line(self.screen, COLOR_TEXT_DIM, (cx, cy + 16), (cx - 50, cy + 52), 2)
        pygame.draw.line(self.screen, COLOR_TEXT_DIM, (cx, cy + 16), (cx + 50, cy + 52), 2)
        
        # Page / Offset Boxes
        p_rect = pygame.Rect(0, 0, 90, 32)
        p_rect.center = (cx - 70, cy + 70)
        
        o_rect = pygame.Rect(0, 0, 90, 32)
        o_rect.center = (cx + 70, cy + 70)
        
        pygame.draw.rect(self.screen, (60, 60, 80), p_rect, border_radius=6)
        pygame.draw.rect(self.screen, (60, 80, 60), o_rect, border_radius=6)
        
        p_txt = FONT_SMALL.render(f"Page {page}", True, COLOR_TEXT_MAIN)
        o_txt = FONT_SMALL.render(f"Off {offset}", True, COLOR_TEXT_MAIN)
        
        self.screen.blit(p_txt, p_txt.get_rect(center=p_rect.center))
        self.screen.blit(o_txt, o_txt.get_rect(center=o_rect.center))
        
        # Operation
        op_text = "READ" if res.operation == "R" else "WRITE"
        op_col = COLOR_GREEN if res.operation == "R" else COLOR_HIGHLIGHT
        
        # Position OP text safely within the panel
        op_rect = pygame.Rect(0, 0, 140, 34)
        # Anchor the op text just above the bottom padding of this panel to avoid overlap
        target_bottom = y + h - 30
        op_rect.center = (cx, target_bottom)
        pygame.draw.rect(self.screen, COLOR_BG, op_rect, border_radius=6)
        
        op_surf = FONT_LARGE.render(op_text, True, op_col)
        self.screen.blit(op_surf, op_surf.get_rect(center=op_rect.center))

    def draw_panel_rect(self, x, y, w, h, title):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, COLOR_PANEL, rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_BORDER, rect, 2, border_radius=12)
        
        title_surf = FONT_HEADER.render(title, True, COLOR_ACCENT)
        self.screen.blit(title_surf, (x + 15, y + 10))
        return rect

    def draw_header(self):
        # Header background
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 60)
        pygame.draw.rect(self.screen, (25, 25, 25), header_rect)
        pygame.draw.line(self.screen, COLOR_BORDER, (0, 60), (WINDOW_WIDTH, 60), 2)
        
        title = FONT_HEADER.render("Virtual Memory Simulator", True, COLOR_TEXT_MAIN)
        self.screen.blit(title, (20, 10))
        
        # Critical State Indicators
        # 1. Step Counter
        step_txt = FONT_MAIN.render(f"Step: {self.controller.engine.current_step}", True, COLOR_TEXT_DIM)
        self.screen.blit(step_txt, (500, 20))
        
        # 2. Hit/Miss/Fault Indicator (Big & Colorful)
        status_rect = pygame.Rect(650, 10, 200, 40)
        status_msg = "READY"
        status_col = COLOR_TEXT_DIM
        
        if self.last_step_result:
            res = self.last_step_result
            if not res.hit:
                status_msg = "PAGE FAULT"
                status_col = COLOR_ACCENT # Red
            elif res.tlb_hit:
                status_msg = "TLB HIT"
                status_col = COLOR_GREEN
            else:
                status_msg = "RAM HIT"
                status_col = COLOR_BLUE
                
        # Draw status pill
        if status_msg != "READY":
             pygame.draw.rect(self.screen, status_col, status_rect, border_radius=20)
             stat_txt = FONT_LARGE.render(status_msg, True, (255, 255, 255))
             rect = stat_txt.get_rect(center=status_rect.center)
             self.screen.blit(stat_txt, rect)
             
        # Global Status (Running/Finished)
        r_status = "IDLE"
        if self.auto_run: r_status = "RUNNING >>"
        elif self.simulation_finished: r_status = "FINISHED"
        
        s_surf = FONT_MAIN.render(r_status, True, COLOR_HIGHLIGHT if self.auto_run else COLOR_TEXT_DIM)
        self.screen.blit(s_surf, (WINDOW_WIDTH - 150, 20))

    # Removed draw_config_panel and draw_reference_string from generic usage or kept if needed.
    # We replaced config panel drawing in draw().
    # Ref string is no longer a primary panel, or we can stash it in Stats? 
    # Current stats panel is large, we can put Ref string in there?
    # Let's Modify draw_stats_panel to include Reference String list at bottom.

    def draw_memory_view(self, x, y, w, h):
        self.draw_panel_rect(x, y, w, h, "Phys. Mem") # Shorter title
        
        # Clip content
        old_clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(x + 5, y + 50, w - 10, h - 55))
        
        frames = self.controller.engine.frames
        
        cols = 4 # Wide view again
        rows = max(1, len(frames) // cols + (1 if len(frames) % cols else 0))
        cell_w = (w - 40) // cols
        
        # Calculate cell_h dynamically to fit available height if possible, else fixed
        available_h = h - 80
        cell_h = min(60, available_h // rows) if rows > 0 else 60
        # Ensure minimum size
        cell_h = max(40, cell_h)

        for i, frame in enumerate(frames):
            col = i % cols
            row = i // cols
            
            cx = x + 20 + col * cell_w
            cy = y + 70 + row * cell_h
            
            # Skip drawing if outside bounds (optimization)
            if cy + cell_h > y + h: break
            
            frame_rect = pygame.Rect(cx + 5, cy + 5, cell_w - 10, cell_h - 10)
            
            is_active = False
            is_victim = False
            if self.last_step_result:
                if self.last_step_result.frame_index == i:
                    is_active = True
                if self.last_step_result.victim_frame_index == i:
                    is_victim = True
            
            color = (60, 60, 60)
            if not frame.is_free:
                color = (80, 80, 80)
            
            if is_active:
                color = COLOR_GREEN
            if is_victim:
                color = COLOR_HIGHLIGHT
                
            pygame.draw.rect(self.screen, color, frame_rect, border_radius=6)
            pygame.draw.rect(self.screen, COLOR_BORDER, frame_rect, 1, border_radius=6)
            
            # Frame ID in top-left, small
            id_text = FONT_SMALL.render(f"F{i}", True, COLOR_TEXT_DIM)
            self.screen.blit(id_text, (cx + 8, cy + 6))
            
            # Page ID in center, larger
            if not frame.is_free:
                content_text = FONT_MAIN.render(f"Pg {frame.page}", True, COLOR_TEXT_MAIN)
                rect = content_text.get_rect(center=frame_rect.center)
                self.screen.blit(content_text, rect)
            else:
                 # Optional: Draw 'Empty' or nothing
                 pass
        
        self.screen.set_clip(old_clip)

    def draw_virtual_memory_view(self, x, y, w, h):
        self.draw_panel_rect(x, y, w, h, "Page Table")
        entries = list(self.controller.engine.page_table.all_entries().values())
        if not entries:
            empty = FONT_MAIN.render("No pages touched yet.", True, COLOR_TEXT_DIM)
            self.screen.blit(empty, (x + 20, y + 60))
            return

        # Clip content
        old_clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(x + 5, y + 50, w - 10, h - 55))

        entries.sort(key=lambda e: e.page)
        highlight_page = self.last_step_result.page if self.last_step_result else None

        line_height = 26
        start_y = y + 70
        visible = max(1, (h - 70) // line_height)

        # Keep the highlighted page in view if possible
        start_index = 0
        if highlight_page is not None:
            for idx, entry in enumerate(entries):
                if entry.page == highlight_page:
                    start_index = max(0, idx - visible // 2)
                    break
        entries = entries[start_index:start_index + visible]

        for i, entry in enumerate(entries):
            line_y = start_y + i * line_height
            row_rect = pygame.Rect(x + 10, line_y - 3, w - 20, line_height)
            base_color = (70, 70, 70)
            if entry.page == highlight_page:
                base_color = COLOR_BLUE
            elif entry.dirty:
                base_color = (90, 70, 70)
            pygame.draw.rect(self.screen, base_color, row_rect, border_radius=4)

            phys_range = "-"
            if entry.present and entry.frame_index is not None:
                start_addr = entry.frame_index * self.vm_config.page_size
                end_addr = start_addr + self.vm_config.page_size - 1
                phys_range = f"Frame {entry.frame_index} [{start_addr}-{end_addr}]"

            last_write = self.page_writes.get(entry.page)
            if last_write:
                write_info = f"last W: VA {last_write['virtual_address']} -> PA {last_write['physical_address']}"
            else:
                write_info = "last W: none"

            flags = []
            if entry.present: flags.append("Present")
            if entry.dirty: flags.append("Dirty")
            if entry.referenced: flags.append("Ref")
            flags_text = ", ".join(flags) if flags else "Not in RAM"

            line = f"P{entry.page:03d} | {phys_range} | {flags_text} | {write_info}"
            color = (0, 0, 0) if entry.page == highlight_page else COLOR_TEXT_MAIN
            text_surf = FONT_SMALL.render(line, True, color)
            self.screen.blit(text_surf, (x + 15, line_y))
            
        self.screen.set_clip(old_clip)

    def draw_tlb_view(self, x, y, w, h):
        self.draw_panel_rect(x, y, w, h, "TLB")
        
        # Clip content
        old_clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(x + 5, y + 50, w - 10, h - 55))
        
        tlb = self.controller.engine.tlb
        entries = tlb.entries
        
        item_w = (w - 30) // 2 # 2 cols for TLB
        item_h = 72 # Taller rows to avoid text crowding
        
        sorted_entries = sorted(entries.values(), key=lambda e: e.last_access)
        
        # Grid layout for TLB
        for i, entry in enumerate(sorted_entries):
            col = i % 2
            row = i // 2
            
            ex = x + 15 + col * item_w
            ey = y + 50 + row * (item_h + 8)
            
            # Avoid drawing outside
            if ex + item_w > x + w: break

            rect = pygame.Rect(ex + 5, ey, item_w - 10, item_h)
            
            is_hit = False
            if self.last_step_result and self.last_step_result.tlb_hit:
                if self.last_step_result.page == entry.page:
                    is_hit = True
            
            color = COLOR_GREEN if is_hit else (70, 70, 70)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            
            txt_page = FONT_MAIN.render(f"Page: {entry.page}", True, COLOR_TEXT_MAIN)
            txt_frame = FONT_MAIN.render(f"Frame: {entry.frame}", True, COLOR_TEXT_MAIN)
            
            self.screen.blit(txt_page, (ex + 15, ey + 10))
            self.screen.blit(txt_frame, (ex + 15, ey + 42))
            
        self.screen.set_clip(old_clip)

    def draw_stats_panel(self, x, y, w, h):
        self.draw_panel_rect(x, y, w, h, "Statistics & Reference Stream")
        
        # Clip content
        old_clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(x + 5, y + 40, w - 10, h - 45))
        
        # Split into Stats (Left) and Ref Stream (Right)
        split_x = x + 240 # Width for stats
        
        stats = self.controller.stats
        lines = [
            f"Total Steps: {self.controller.engine.current_step}",
            f"TLB Hits: {stats.tlb_hits} ({stats.tlb_hit_ratio:.1%})",
            f"Pg Faults: {stats.page_faults} ({stats.page_fault_ratio:.1%})",
            f"Pg Hits: {stats.page_hits}",
            f"Disk Writes: {stats.disk_writes}",
        ]
        
        line_height = 30
        start_y = y + 60
        for i, line in enumerate(lines):
            surf = FONT_MAIN.render(line, True, COLOR_TEXT_MAIN)
            self.screen.blit(surf, (x + 20, start_y + i * 30))
            
        # Divider Line
        pygame.draw.line(self.screen, COLOR_BORDER, (split_x, y + 50), (split_x, y + h - 10), 2)
        
        # Reference Stream (Right side)
        ref_x = split_x + 10
        ref_w = w - (split_x - x) - 20
        
        self.screen.blit(FONT_MAIN.render("Upcoming Operations:", True, COLOR_ACCENT), (ref_x, y + 50))
        
        current_step = self.controller.engine.current_step
        visible_items = max(1, (h - 90) // 25)
        
        for i in range(visible_items):
            idx = current_step + i
            if idx >= len(self.reference_string): break
            
            addr, op = self.reference_string[idx]
            
            # Highlight next immediate op
            col = COLOR_HIGHLIGHT if i == 0 else COLOR_TEXT_DIM
            bg_col = (50, 50, 50) if i == 0 else None
            
            line_y = y + 80 + i * 25
            
            if bg_col:
                bg_rect = pygame.Rect(ref_x, line_y - 2, ref_w, 24)
                pygame.draw.rect(self.screen, bg_col, bg_rect, border_radius=4)
                
            txt = f"{i+1}. {op} @ {addr} (Pg {addr >> self.vm_config.offset_bits})"
            surf = FONT_SMALL.render(txt, True, col)
            self.screen.blit(surf, (ref_x + 5, line_y))

        self.screen.set_clip(old_clip)

if __name__ == "__main__":
    viz = MemoryVisualizer()
    viz.run()
