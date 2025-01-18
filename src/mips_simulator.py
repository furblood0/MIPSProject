from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QSplitter, QHeaderView, QFrame, QGroupBox, QSizePolicy
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
import sys


class MIPSSimulator(QMainWindow):
#Başlangıç ve UI    
    def __init__(self):
        super().__init__()
        # Memory configuration
        self.MEMORY_SIZE = 512  # 512 bytes
        self.WORD_SIZE = 4      # 32-bit = 4 bytes
        self.instruction_memory = [0] * (self.MEMORY_SIZE // self.WORD_SIZE)  # 512 bytes / 4 = 128 words
        self.data_memory = [0] * (self.MEMORY_SIZE // self.WORD_SIZE)        # 512 bytes / 4 = 128 words
        
        # Register configuration
        self.NUM_REGISTERS = 32
        self.registers = [0] * self.NUM_REGISTERS
        self.register_names = {
            "$zero": 0,  # Constant 0
            "$at": 1,    # Assembler temporary
            "$v0": 2, "$v1": 3,  # Values for results and expression evaluation
            "$a0": 4, "$a1": 5, "$a2": 6, "$a3": 7,  # Arguments
            "$t0": 8, "$t1": 9, "$t2": 10, "$t3": 11,  # Temporaries
            "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15,
            "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19,  # Saved temporaries
            "$s4": 20, "$s5": 21, "$s6": 22, "$s7": 23,
            "$t8": 24, "$t9": 25,  # More temporaries
            "$k0": 26, "$k1": 27,  # Reserved for OS kernel
            "$gp": 28,  # Global pointer
            "$sp": 29,  # Stack pointer
            "$fp": 30,  # Frame pointer
            "$ra": 31   # Return address
        }
        # Add numeric register names
        self.register_map = {f"$r{i}": i for i in range(32)}
        self.register_map.update(self.register_names)  # Add named registers
        
        # Initialize other components
        self.current_instruction = 0
        self.labels = {}
        self.machine_code = []
        self.execution_trace = []
        self.pc = 0
        
        # Initialize UI
        self.initUI()
        
        # Connect buttons to functions
        self.run_button.clicked.connect(self.run_program)
        self.step_button.clicked.connect(self.step_program)
        self.reset_button.clicked.connect(self.reset_program)

        # Initialize tables
        self.populate_memory()
        self.populate_registers()

    def initUI(self):
        self.setWindowTitle("MIPS Simulator")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("font-family: Arial; font-size: 14px;")

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Top layout: Splitter for Assembly Code and Memory/Register Views
        top_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(top_splitter)

        # Modify the left panel to include both assembly and machine code
        left_panel = QSplitter(Qt.Vertical)
        top_splitter.addWidget(left_panel)

        # Assembly Code Editor (now in left panel)
        code_editor_group = QGroupBox("Assembly Code")
        code_editor_group.setStyleSheet("font-weight: bold;")
        code_layout = QVBoxLayout()
        code_editor_group.setLayout(code_layout)

        self.assembly_editor = QTextEdit()
        self.assembly_editor.setPlaceholderText("Enter your MIPS assembly code here...")
        self.assembly_editor.setFont(QFont("Courier", 12))
        code_layout.addWidget(self.assembly_editor)
        left_panel.addWidget(code_editor_group)

        # Machine Code Display (new addition)
        machine_code_group = QGroupBox("Machine Code")
        machine_code_group.setStyleSheet("font-weight: bold;")
        machine_code_layout = QVBoxLayout()
        machine_code_group.setLayout(machine_code_layout)

        self.machine_code_table = QTableWidget()
        self.machine_code_table.setColumnCount(3)
        self.machine_code_table.setHorizontalHeaderLabels(["Address", "Instruction", "Machine Code"])
        self.machine_code_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.machine_code_table.setFont(QFont("Courier", 12))
        machine_code_layout.addWidget(self.machine_code_table)
        left_panel.addWidget(machine_code_group)

        # Right Panel: Memory and Registers
        right_splitter = QSplitter(Qt.Vertical)
        top_splitter.addWidget(right_splitter)

        # Data Memory Group
        memory_group = QGroupBox("Data Memory")
        memory_layout = QVBoxLayout()
        memory_group.setLayout(memory_layout)

        self.data_memory_table = QTableWidget(16, 2)
        self.data_memory_table.setHorizontalHeaderLabels(["Address", "Value"])
        self.data_memory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        memory_layout.addWidget(self.data_memory_table)
        right_splitter.addWidget(memory_group)

        # Register File Group
        register_group = QGroupBox("Register File")
        register_layout = QVBoxLayout()
        register_group.setLayout(register_layout)

        self.register_file_table = QTableWidget(32, 3)
        self.register_file_table.setHorizontalHeaderLabels(["Numeric", "Symbolic", "Value"])
        self.register_file_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        register_layout.addWidget(self.register_file_table)
        right_splitter.addWidget(register_group)

        # Bottom Layout: Controls and Output/Trace
        bottom_layout = QVBoxLayout()
        main_layout.addLayout(bottom_layout)

        # Controls Section
        controls_group = QGroupBox("Controls")
        controls_layout = QHBoxLayout()
        controls_group.setLayout(controls_layout)

        self.run_button = QPushButton("Run")
        self.step_button = QPushButton("Step")
        self.reset_button = QPushButton("Reset")
        
        # Buton stilleri
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.step_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        controls_layout.addWidget(self.run_button)
        controls_layout.addWidget(self.step_button)
        controls_layout.addWidget(self.reset_button)
        bottom_layout.addWidget(controls_group)

        # Create horizontal layout for Output and Trace
        output_trace_layout = QHBoxLayout()
        bottom_layout.addLayout(output_trace_layout)

        # Output Section
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        output_group.setLayout(output_layout)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        self.output_log.setFont(QFont("Courier", 12))
        output_layout.addWidget(self.output_log)
        output_trace_layout.addWidget(output_group)

        # Execution Trace Section
        trace_group = QGroupBox("Execution Trace")
        trace_layout = QVBoxLayout()
        trace_group.setLayout(trace_layout)

        self.trace_display = QTextEdit()
        self.trace_display.setReadOnly(True)
        self.trace_display.setFont(QFont("Courier", 10))
        trace_layout.addWidget(self.trace_display)
        
        # Add trace_group to output_trace_layout
        output_trace_layout.addWidget(trace_group)

        # Set size policy for both groups to be equal
        output_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        trace_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

#Program kontrol butonları
    def reset_program(self):
        # Registers'ları sıfırla
        self.registers = [0] * 32
        
        # Memory'i sıfırla
        self.data_memory = [0] * self.MEMORY_SIZE
        
        # Program counter'ı sıfırla
        self.pc = 0
        
        # Current instruction'ı sıfırla
        self.current_instruction = 0
        
        # Machine code'u sıfırla
        self.machine_code = []
        
        # Machine code tablosunu temizle
        self.machine_code_table.setRowCount(0)
        
        # Execution trace'i temizle
        self.execution_trace = []
        self.update_trace_display()
        
        # Instruction count'u sıfırla
        self.instruction_count = 0
        
        # Register ve memory tablolarını güncelle
        self.populate_registers()
        self.populate_memory()
        
        # Output log'u temizle
        self.output_log.clear()
        self.output_log.append("System reset completed")

    def run_program(self):
        try:
            # Program durumunu sıfırla
            self.reset_program()
            self.labels = {}
            
            # Assembly kodunu al ve temizle
            assembly_code = self.assembly_editor.toPlainText()
            instructions = [line.strip() for line in assembly_code.splitlines() 
                           if line.strip() and not line.strip().startswith('#')]
            
            # Etiketleri topla
            cleaned_instructions = []
            instruction_index = 0
            for line in instructions:
                if ':' in line:
                    parts = line.split(':')
                    label = parts[0].strip()
                    self.labels[label] = instruction_index
                    if len(parts) > 1 and parts[1].strip():
                        cleaned_instructions.append(parts[1].strip())
                        instruction_index += 1
                else:
                    cleaned_instructions.append(line)
                    instruction_index += 1
            
            # Machine code table'ı hazırla
            self.machine_code_table.setRowCount(len(cleaned_instructions))
            
            # Her komut için machine code oluştur ve tabloya ekle
            for i, instruction in enumerate(cleaned_instructions):
                # Adres sütunu
                addr_item = QTableWidgetItem(f"0x{i*4:08x}")
                self.machine_code_table.setItem(i, 0, addr_item)
                
                # Komut sütunu
                inst_item = QTableWidgetItem(instruction)
                self.machine_code_table.setItem(i, 1, inst_item)
                
                # Machine code sütunu
                code = self.generate_machine_code(instruction)
                code_item = QTableWidgetItem(code)
                self.machine_code_table.setItem(i, 2, code_item)
            
            # Komutları çalıştır
            self.current_instruction = 0
            while self.current_instruction < len(cleaned_instructions):
                instruction = cleaned_instructions[self.current_instruction]
                try:
                    self.execute_instruction(instruction)
                    # Branch/jump değilse sonraki komuta geç
                    parts = instruction.split()
                    op = parts[0].lower()
                    if op not in ['beq', 'bne', 'j', 'jal', 'jr']:
                        self.current_instruction += 1
                except Exception as e:
                    self.output_log.append(f"Error executing: {instruction}")
                    self.output_log.append(f"Error: {str(e)}")
                    break
            
            # Program tamamlandı
            self.output_log.append("\nProgram execution completed!")
            self.output_log.append("-" * 40)
            
            # Bellek ve register tablolarını güncelle
            self.populate_memory()
            self.populate_registers()
            
        except Exception as e:
            self.output_log.append(f"Program execution failed: {str(e)}")

    def step_program(self):
        try:
            # Assembly kodunu al ve temizle
            assembly_code = self.assembly_editor.toPlainText()
            instructions = [line.strip() for line in assembly_code.splitlines() 
                           if line.strip() and not line.strip().startswith('#')]
            
            # Etiketleri topla (eğer henüz toplanmamışsa)
            if not hasattr(self, 'labels') or not self.labels:
                self.labels = {}
                instruction_index = 0
                for line in instructions:
                    if ':' in line:
                        parts = line.split(':')
                        label = parts[0].strip()
                        self.labels[label] = instruction_index
                        if len(parts) > 1 and parts[1].strip():
                            instruction_index += 1
                    else:
                        instruction_index += 1
            
            # Temiz komutları oluştur
            cleaned_instructions = []
            for line in instructions:
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) > 1 and parts[1].strip():
                        cleaned_instructions.append(parts[1].strip())
                else:
                    cleaned_instructions.append(line)
            
            # Program tamamlandı mı kontrol et
            if self.current_instruction >= len(cleaned_instructions):
                self.output_log.clear()
                self.output_log.append("Program execution completed!")
                self.output_log.append("-" * 40)
                return
            
            # Machine code table'ı hazırla (eğer henüz hazır değilse)
            if self.machine_code_table.rowCount() != len(cleaned_instructions):
                self.machine_code_table.setRowCount(len(cleaned_instructions))
                # Tüm komutlar için machine code'ları oluştur
                for i, inst in enumerate(cleaned_instructions):
                    addr_item = QTableWidgetItem(f"0x{i*4:08x}")
                    inst_item = QTableWidgetItem(inst)
                    code = self.generate_machine_code(inst)
                    code_item = QTableWidgetItem(code)
                    
                    self.machine_code_table.setItem(i, 0, addr_item)
                    self.machine_code_table.setItem(i, 1, inst_item)
                    self.machine_code_table.setItem(i, 2, code_item)
            
            # Mevcut komutu highlight et
            for i in range(len(cleaned_instructions)):
                for j in range(3):
                    item = self.machine_code_table.item(i, j)
                    if item:
                        item.setBackground(Qt.yellow if i == self.current_instruction else Qt.white)
            
            instruction = cleaned_instructions[self.current_instruction]
            machine_code = self.generate_machine_code(instruction)
            
            # Output log'u güncelle
            self.output_log.clear()
            self.output_log.append(f"Step {self.current_instruction + 1}")
            self.output_log.append("-" * 40)
            self.output_log.append(f"Instruction: {instruction}")
            self.output_log.append(f"Machine Code: {machine_code}")
            self.output_log.append("")
            self.output_log.append("Explanation:")
            
            # Execute instruction and track changes
            old_reg_values = self.registers.copy()
            old_mem_values = self.data_memory.copy()
            
            try:
                old_instruction = self.current_instruction
                self.execute_instruction(instruction)
                
                # Show changes
                reg_changes = self.get_register_changes(old_reg_values)
                mem_changes = self.get_memory_changes(old_mem_values)
                
                self.output_log.append("")
                self.output_log.append("Result:")
                if reg_changes != "No changes":
                    self.output_log.append(f"• Register: {reg_changes}")
                if mem_changes != "No changes":
                    self.output_log.append(f"• Memory: {mem_changes}")
                
                # Register ve memory tablolarını güncelle ve değişiklikleri vurgula
                self.populate_registers(old_reg_values)
                self.populate_memory(old_mem_values)
                
            except Exception as e:
                self.output_log.append(f"Error executing: {instruction}")
                self.output_log.append(f"Error: {str(e)}")
            
            self.output_log.append("-" * 40)
            
            # Move to next instruction if not a branch/jump
            parts = instruction.split()
            op = parts[0].lower()
            if op not in ['beq', 'bne', 'j', 'jal', 'jr']:
                self.current_instruction += 1
                
        except Exception as e:
            self.output_log.append(f"Error: {str(e)}")

#Komut işleme
    def fetch_instruction(self):
        if self.pc // 4 < len(self.instruction_memory):
            instruction = self.instruction_memory[self.pc // 4]
            self.output_log.append(f"Fetch: PC = 0x{self.pc:08x}, Instruction = {instruction}")
            return instruction
        return None

    def decode_instruction(self, instruction):
        parts = instruction.split()
        op = parts[0].lower()
        self.output_log.append(f"Decode: Operation = {op}")
        return parts

    def execute_instruction(self, instruction):
        """Komutları yürütür"""
        # Yorumları kaldır
        instruction = instruction.split('#')[0].strip()
        
        # Mevcut durumu kaydet
        old_reg_values = self.registers.copy()
        old_mem_values = self.data_memory.copy()
        
        # Parametreleri temizle
        clean_params, op = self.clean_instruction_params(instruction)
        
        try:
            if op == "addi":
                rt, rs, imm = clean_params
                rt_idx = self.register_map[rt]
                rs_idx = self.register_map[rs]
                self.registers[rt_idx] = self.registers[rs_idx] + int(imm)
                self.output_log.append(f"{rt} = {self.registers[rt_idx]}")
            
            elif op == "add":
                rd, rs, rt = clean_params
                rd_idx = self.register_map[rd]
                rs_idx = self.register_map[rs]
                rt_idx = self.register_map[rt]
                rs_val = self.registers[rs_idx]
                rt_val = self.registers[rt_idx]
                result = rs_val + rt_val
                # 32-bit integer taşma kontrolü
                if result > 0x7FFFFFFF:  # Pozitif taşma
                    result = (result & 0xFFFFFFFF) - (1 << 32)
                elif result < -0x80000000:  # Negatif taşma
                    result = (result & 0xFFFFFFFF)
                self.registers[rd_idx] = result
                self.output_log.append(f"{rd} = {self.registers[rd_idx]}")
            
            elif op == "sub":
                rd, rs, rt = clean_params
                rd_idx = self.register_map[rd]
                rs_idx = self.register_map[rs]
                rt_idx = self.register_map[rt]
                self.registers[rd_idx] = self.registers[rs_idx] - self.registers[rt_idx]
                self.output_log.append(f"{rd} = {self.registers[rd_idx]}")
            
            elif op == "and":
                rd, rs, rt = clean_params
                rd_idx = self.register_map[rd]
                rs_idx = self.register_map[rs]
                rt_idx = self.register_map[rt]
                self.registers[rd_idx] = self.registers[rs_idx] & self.registers[rt_idx]
                self.output_log.append(f"{rd} = {self.registers[rd_idx]}")
            
            elif op == "or":
                rd, rs, rt = clean_params
                rd_idx = self.register_map[rd]
                rs_idx = self.register_map[rs]
                rt_idx = self.register_map[rt]
                self.registers[rd_idx] = self.registers[rs_idx] | self.registers[rt_idx]
                self.output_log.append(f"{rd} = {self.registers[rd_idx]}")
            
            elif op == "slt":
                rd, rs, rt = clean_params
                rd_idx = self.register_map[rd]
                rs_idx = self.register_map[rs]
                rt_idx = self.register_map[rt]
                self.registers[rd_idx] = int(self.registers[rs_idx] < self.registers[rt_idx])
                self.output_log.append(f"{rd} = {self.registers[rd_idx]}")
            
            elif op == "sll":
                rd, rt, shamt_or_reg = clean_params
                rd_idx = self.register_map[rd]
                rt_idx = self.register_map[rt]
                try:
                    # Eğer üçüncü parametre bir sayı (immediate) ise doğrudan kullanılır
                    shamt = int(shamt_or_reg)
                except ValueError:
                    # Eğer üçüncü parametre bir register ise onun değerini kullan
                    shamt = self.registers[self.register_map[shamt_or_reg]]
                self.registers[rd_idx] = self.registers[rt_idx] << shamt
                self.output_log.append(f"{rd} = {self.registers[rd_idx]}")
                        
            elif op == "srl":
                rd, rt, shamt_or_reg = clean_params
                rd_idx = self.register_map[rd]
                rt_idx = self.register_map[rt]
                try:
                    # Eğer üçüncü parametre bir sayı (immediate) ise doğrudan kullanılır
                    shamt = int(shamt_or_reg)
                except ValueError:
                    # Eğer üçüncü parametre bir register ise onun değerini kullan
                    shamt = self.registers[self.register_map[shamt_or_reg]]
                self.registers[rd_idx] = self.registers[rt_idx] >> shamt
                self.output_log.append(f"{rd} = {self.registers[rd_idx]}")
            
            elif op == "beq":
                rs, rt, label = clean_params
                rs_idx = self.register_map[rs]
                rt_idx = self.register_map[rt]
                if self.registers[rs_idx] == self.registers[rt_idx]:
                    if label in self.labels:
                        self.current_instruction = self.labels[label]
                    else:
                        raise Exception(f"Label not found: {label}")
                else:
                    # Eğer branch alınmazsa, bir sonraki komuta geç
                    self.current_instruction += 1
                self.output_log.append(f"beq evaluated to {'taken' if self.registers[rs_idx] == self.registers[rt_idx] else 'not taken'}")
            
            elif op == "bne":
                rs, rt, label = clean_params
                rs_idx = self.register_map[rs]
                rt_idx = self.register_map[rt]
                if self.registers[rs_idx] != self.registers[rt_idx]:
                    if label in self.labels:
                        self.current_instruction = self.labels[label]
                    else:
                        raise Exception(f"Label not found: {label}")
                else:
                    # Eğer branch alınmazsa, bir sonraki komuta geç
                    self.current_instruction += 1
                self.output_log.append(f"bne evaluated to {'taken' if self.registers[rs_idx] != self.registers[rt_idx] else 'not taken'}")
            
            elif op == "j":
                target = clean_params[0]
                self.current_instruction = self.labels[target]
                self.output_log.append(f"Jump to {target}")
            
            elif op == "jal":
                target = clean_params[0]
                self.registers[self.register_map['$ra']] = self.current_instruction + 1
                self.current_instruction = self.labels[target]
                self.output_log.append(f"Jump and link to {target}")
            
            elif op == "jr":
                rs = clean_params[0]
                rs_idx = self.register_map[rs]
                self.current_instruction = self.registers[rs_idx]
                self.output_log.append(f"Jump to register {rs}")
            
            elif op == "lw":
                rt = clean_params[0]
                offset_base = clean_params[1]
                offset, base = offset_base.split('(')
                base = base.strip(')')
                rt_idx = self.register_map[rt]
                base_idx = self.register_map[base]
                address = (self.registers[base_idx] + int(offset)) // self.WORD_SIZE
                if 0 <= address < (self.MEMORY_SIZE // self.WORD_SIZE):
                    self.registers[rt_idx] = self.data_memory[address]
                    self.output_log.append(f"{rt} = {self.registers[rt_idx]}")
            
            elif op == "sw":
                rt = clean_params[0]
                offset_base = clean_params[1]
                offset, base = offset_base.split('(')
                base = base.strip(')')
                rt_idx = self.register_map[rt]
                base_idx = self.register_map[base]
                address = (self.registers[base_idx] + int(offset)) // self.WORD_SIZE
                if 0 <= address < (self.MEMORY_SIZE // self.WORD_SIZE):
                    self.data_memory[address] = self.registers[rt_idx]
                    self.output_log.append(f"Memory[{address*4}] = {self.registers[rt_idx]}")

            # Trace'e ekle
            machine_code = self.generate_machine_code(instruction)
            self.add_to_trace(instruction, machine_code, old_reg_values, old_mem_values)

        except Exception as e:
            self.output_log.append(f"Error executing: {instruction}")
            self.output_log.append(f"Error: {str(e)}")
            raise

    def clean_instruction_params(self, instruction):
        """Temiz parametre listesi döndürür"""
        # Önce yorumları kaldır
        instruction = instruction.split('#')[0].strip()
        
        parts = instruction.split(None, 1)  # İlk boşluktan böl (opcode ve parametreleri ayır)
        if len(parts) < 2:
            return [], ""
        
        op = parts[0].lower()
        params_str = parts[1]
        
        # Tüm boşlukları kaldır ve virgülle ayrılmış parametreleri al
        clean_params = [p.strip() for p in params_str.replace(" ", "").split(",")]
        return clean_params, op

    def clean_params(self, params):
        # Önce tüm virgülleri boşluğa çevir
        params = params.replace(',', ' ')
        # Birden fazla boşluğu tek boşluğa çevir
        params = ' '.join(params.split())
        # Boşluklarla ayır ve temizle
        return [p.strip() for p in params.split()]

#Makine kodu üretimi
    def generate_machine_code(self, instruction):
        """MIPS komutları için binary machine code üretimi"""
        try:
            # Yorum satırını kaldır
            instruction = instruction.split('#')[0].strip()
            if not instruction:
                return "00000000000000000000000000000000"

            # Komut ve parametreleri ayır
            parts = instruction.split()
            op = parts[0].lower()
            params = [p.strip().rstrip(',') for p in parts[1:]]

            # R-Format Instructions
            if op == "add":  # 000000 rs rt rd 00000 100000
                rd = self.register_map[params[0]] & 0x1F
                rs = self.register_map[params[1]] & 0x1F
                rt = self.register_map[params[2]] & 0x1F
                return f"{0:06b}{rs:05b}{rt:05b}{rd:05b}{0:05b}100000"

            elif op == "sub":  # 000000 rs rt rd 00000 100010
                rd = self.register_map[params[0]] & 0x1F
                rs = self.register_map[params[1]] & 0x1F
                rt = self.register_map[params[2]] & 0x1F
                return f"{0:06b}{rs:05b}{rt:05b}{rd:05b}{0:05b}100010"

            elif op == "and":  # 000000 rs rt rd 00000 100100
                rd = self.register_map[params[0]] & 0x1F
                rs = self.register_map[params[1]] & 0x1F
                rt = self.register_map[params[2]] & 0x1F
                return f"{0:06b}{rs:05b}{rt:05b}{rd:05b}{0:05b}100100"

            elif op == "or":   # 000000 rs rt rd 00000 100101
                rd = self.register_map[params[0]] & 0x1F
                rs = self.register_map[params[1]] & 0x1F
                rt = self.register_map[params[2]] & 0x1F
                return f"{0:06b}{rs:05b}{rt:05b}{rd:05b}{0:05b}100101"

            elif op == "slt":  # 000000 rs rt rd 00000 101010
                rd = self.register_map[params[0]] & 0x1F
                rs = self.register_map[params[1]] & 0x1F
                rt = self.register_map[params[2]] & 0x1F
                return f"{0:06b}{rs:05b}{rt:05b}{rd:05b}{0:05b}101010"

            elif op == "sll":  # 000000 00000 rt rd shamt 000000
                rd = self.register_map[params[0]] & 0x1F
                rt = self.register_map[params[1]] & 0x1F
                try:
                    shamt = int(params[2]) & 0x1F
                except ValueError:
                    shamt = self.registers[self.register_map[params[2]]] & 0x1F
                return f"{0:06b}{0:05b}{rt:05b}{rd:05b}{shamt:05b}000000"


            elif op == "srl":  # 000000 00000 rt rd shamt 000010
                rd = self.register_map[params[0]] & 0x1F
                rt = self.register_map[params[1]] & 0x1F
                try:
                    shamt = int(params[2]) & 0x1F
                except ValueError:
                    shamt = self.registers[self.register_map[params[2]]] & 0x1F
                return f"{0:06b}{0:05b}{rt:05b}{rd:05b}{shamt:05b}000010"

            # I-Format Instructions
            elif op == "addi":  # 001000 rs rt immediate
                rt = self.register_map[params[0]] & 0x1F
                rs = self.register_map[params[1]] & 0x1F
                imm = int(params[2]) & 0xFFFF
                return f"001000{rs:05b}{rt:05b}{imm:016b}"

            elif op == "lw":    # 100011 rs rt offset
                rt = self.register_map[params[0]] & 0x1F
                offset_base = params[1]
                offset, base = offset_base.split('(')
                base = base.rstrip(')')
                rs = self.register_map[base] & 0x1F
                offset = int(offset) & 0xFFFF
                return f"100011{rs:05b}{rt:05b}{offset:016b}"

            elif op == "sw":    # 101011 rs rt offset
                rt = self.register_map[params[0]] & 0x1F
                offset_base = params[1]
                offset, base = offset_base.split('(')
                base = base.rstrip(')')
                rs = self.register_map[base] & 0x1F
                offset = int(offset) & 0xFFFF
                return f"101011{rs:05b}{rt:05b}{offset:016b}"

            elif op == "beq":   # 000100 rs rt offset
                rs = self.register_map[params[0]] & 0x1F
                rt = self.register_map[params[1]] & 0x1F
                offset = (self.labels.get(params[2], 0) - self.current_instruction - 1) & 0xFFFF
                return f"000100{rs:05b}{rt:05b}{offset:016b}"

            elif op == "bne":   # 000101 rs rt offset
                rs = self.register_map[params[0]] & 0x1F
                rt = self.register_map[params[1]] & 0x1F
                offset = (self.labels.get(params[2], 0) - self.current_instruction - 1) & 0xFFFF
                return f"000101{rs:05b}{rt:05b}{offset:016b}"

            # J-Format Instructions
            elif op == "j":     # 000010 target
                target = params[0]
                if target in self.labels:
                    target_address = self.labels[target] & 0x3FFFFFF
                    return f"000010{target_address:026b}"
                else:
                    self.output_log.append(f"Warning: Label '{target}' not found")
                    return "00001000000000000000000000000000"

            elif op == "jal":   # 000011 target
                target = params[0]
                if target in self.labels:
                    target_address = self.labels[target] & 0x3FFFFFF
                    return f"000011{target_address:026b}"
                else:
                    self.output_log.append(f"Warning: Label '{target}' not found")
                    return "00001100000000000000000000000000"

            elif op == "jr":    # 000000 rs 00000 00000 00000 001000
                rs = self.register_map[params[0]] & 0x1F
                return f"000000{rs:05b}000000000000000001000"

            return "00000000000000000000000000000000"

        except Exception as e:
            print(f"Error in machine code generation: {str(e)}")
            return "00000000000000000000000000000000"

    def update_machine_code_display(self, instructions):
        self.machine_code_table.setRowCount(len(instructions))
        for i, (inst, code) in enumerate(zip(instructions, self.machine_code)):
            self.machine_code_table.setItem(i, 0, QTableWidgetItem(f"0x{i*4:08x}"))
            self.machine_code_table.setItem(i, 1, QTableWidgetItem(inst))
            self.machine_code_table.setItem(i, 2, QTableWidgetItem(code))

#Durum takip ve görüntüleme
    def populate_memory(self, old_values=None):
        """Data memory tablosunu doldurur"""
        for i in range(self.MEMORY_SIZE // self.WORD_SIZE):
            # Adres sütunu
            addr_item = QTableWidgetItem(f"0x{i*4:08x}")
            self.data_memory_table.setItem(i, 0, addr_item)
            
            # Değer sütunu
            value_item = QTableWidgetItem(str(self.data_memory[i]))
            
            # Eğer eski değerler varsa ve değişiklik olduysa arka planı renklendir
            if old_values is not None and self.data_memory[i] != old_values[i]:
                value_item.setBackground(QColor(255, 255, 0))  # Sarı renk
            else:
                value_item.setBackground(Qt.white)
            
            self.data_memory_table.setItem(i, 1, value_item)

    def populate_registers(self, old_values=None):
        """Registers tablosunu hem numerik hem sembolik isimlerle doldurur"""
        # Register açıklamaları ve grupları
        register_info = [
            ("$zero", 0, "Constant 0"),
            ("$at", 1, "Assembler temporary"),
            ("$v0", 2, "Values for results"),
            ("$v1", 3, "Values for results"),
            ("$a0", 4, "Arguments"),
            ("$a1", 5, "Arguments"),
            ("$a2", 6, "Arguments"),
            ("$a3", 7, "Arguments"),
            ("$t0", 8, "Temporaries"),
            ("$t1", 9, "Temporaries"),
            ("$t2", 10, "Temporaries"),
            ("$t3", 11, "Temporaries"),
            ("$t4", 12, "Temporaries"),
            ("$t5", 13, "Temporaries"),
            ("$t6", 14, "Temporaries"),
            ("$t7", 15, "Temporaries"),
            ("$s0", 16, "Saved temporaries"),
            ("$s1", 17, "Saved temporaries"),
            ("$s2", 18, "Saved temporaries"),
            ("$s3", 19, "Saved temporaries"),
            ("$s4", 20, "Saved temporaries"),
            ("$s5", 21, "Saved temporaries"),
            ("$s6", 22, "Saved temporaries"),
            ("$s7", 23, "Saved temporaries"),
            ("$t8", 24, "More temporaries"),
            ("$t9", 25, "More temporaries"),
            ("$k0", 26, "Reserved for OS"),
            ("$k1", 27, "Reserved for OS"),
            ("$gp", 28, "Global pointer"),
            ("$sp", 29, "Stack pointer"),
            ("$fp", 30, "Frame pointer"),
            ("$ra", 31, "Return address")
        ]
        
        # Tabloyu doldur
        for i, (name, number, desc) in enumerate(register_info):
            # Numeric isim
            numeric_item = QTableWidgetItem(f"$r{number}")
            
            # Sembolik isim
            symbolic_item = QTableWidgetItem(name)
            
            # Değer
            value_item = QTableWidgetItem(str(self.registers[i]))
            
            # Eğer eski değerler varsa ve değişiklik olduysa arka planı renklendir
            if old_values is not None and self.registers[i] != old_values[i]:
                value_item.setBackground(QColor(255, 255, 0))  # Sarı renk
            else:
                value_item.setBackground(Qt.white)
            
            # Tabloya ekle
            self.register_file_table.setItem(i, 0, numeric_item)
            self.register_file_table.setItem(i, 1, symbolic_item)
            self.register_file_table.setItem(i, 2, value_item)
        
        # Sütun genişliklerini ayarla
        header = self.register_file_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Numeric sütunu içeriğe göre
        header.setSectionResizeMode(1, QHeaderView.Fixed)            # Symbolic sütunu sabit genişlik
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Value sütunu kalan alanı doldursun
        
        # Symbolic sütununun genişliğini manuel ayarla
        self.register_file_table.setColumnWidth(1, 80)  # Piksel cinsinden genişlik

    def get_register_changes(self, old_values):
        changes = []
        for i in range(len(self.registers)):
            if self.registers[i] != old_values[i]:
                reg_name = f"${next((k[1:] for k, v in self.register_names.items() if v == i), f'r{i}')}"
                changes.append(f"{reg_name}: {old_values[i]} -> {self.registers[i]}")
        return ", ".join(changes) if changes else "No changes"

    def get_memory_changes(self, old_values):
        changes = []
        for i in range(len(self.data_memory)):
            if self.data_memory[i] != old_values[i]:
                changes.append(f"M[0x{i*4:03x}]: {old_values[i]} -> {self.data_memory[i]}")
        return ", ".join(changes) if changes else "No changes"

    def show_changes(self, old_reg_values, old_mem_values):
        """Register ve bellek değişikliklerini gösterir"""
        # Register değişikliklerini kontrol et
        reg_changes = []
        for i in range(len(self.registers)):
            if self.registers[i] != old_reg_values[i]:
                reg_name = next((k for k, v in self.register_map.items() if v == i), f'$r{i}')
                reg_changes.append(f"{reg_name}: {old_reg_values[i]} → {self.registers[i]}")
        
        # Bellek değişikliklerini kontrol et
        mem_changes = []
        for i in range(len(self.data_memory)):
            if self.data_memory[i] != old_mem_values[i]:
                mem_changes.append(f"Memory[{i*4}]: {old_mem_values[i]} → {self.data_memory[i]}")
        
        # Değişiklikleri output_log'a ekle
        if reg_changes:
            self.output_log.append("\nRegister Changes:")
            for change in reg_changes:
                self.output_log.append(f"  {change}")
            
        if mem_changes:
            self.output_log.append("\nMemory Changes:")
            for change in mem_changes:
                self.output_log.append(f"  {change}")
            
        if not reg_changes and not mem_changes:
            self.output_log.append("\nNo changes in registers or memory")

#Trace ekleme
    def add_to_trace(self, instruction, machine_code, old_reg_values, old_mem_values):
        # Instruction count'u tutmak için yeni bir sınıf değişkeni
        if not hasattr(self, 'instruction_count'):
            self.instruction_count = 0
        self.instruction_count += 1
        
        trace_entry = (
            f"Step {self.instruction_count}\n"
            f"PC: 0x{self.pc:08x}\n"
            f"Instruction: {instruction}\n"
            f"Machine Code: {machine_code}\n"
            f"Register Changes: {self.get_register_changes(old_reg_values)}\n"
            f"Memory Changes: {self.get_memory_changes(old_mem_values)}\n"
            f"{'-'*50}\n"
        )
        self.execution_trace.append(trace_entry)
        self.update_trace_display()

        # Program sonunda toplam adım sayısını göster
        if instruction.strip().lower() == 'beq $s1, $s0, end_sort' and self.registers[self.register_map['$s1']] == self.registers[self.register_map['$s0']]:
            summary = f"\nProgram completed in {self.instruction_count} steps\n{'-'*50}\n"
            self.execution_trace.append(summary)
            self.update_trace_display()

    def update_trace_display(self):
        self.trace_display.setText("".join(self.execution_trace))
        # Otomatik olarak en alta kaydır
        self.trace_display.verticalScrollBar().setValue(
            self.trace_display.verticalScrollBar().maximum()
        )


def main():
    app = QApplication(sys.argv)
    window = MIPSSimulator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
