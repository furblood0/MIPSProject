# MIPS Simulator

## Overview
This project is a MIPS 32-bit architecture simulator designed to execute a subset of MIPS assembly instructions. It provides a user-friendly PyQt5-based graphical user interface (GUI) for loading, editing, and executing MIPS programs. This simulator implements a fetch-decode-execute cycle and supports viewing the state of registers, memory, and program execution trace.

## Features
- **Instruction Set Support**:
  - **R-Format**: `add`, `sub`, `and`, `or`, `slt`, `sll`, `srl`
  - **I-Format**: `addi`, `lw`, `sw`, `beq`, `bne`
  - **J-Format**: `j`, `jal`, `jr`
- **Memory Management**:
  - 512 bytes of instruction memory
  - 512 bytes of data memory
- **Registers**:
  - 32 general-purpose registers with symbolic names (e.g., `$t0`, `$s0`) and numeric indices.
- **Execution Modes**:
  - Step-by-step execution
  - Full program execution
  - Reset functionality
- **Trace and Debugging**:
  - Program execution trace
  - Real-time register and memory state updates
- **Error Handling**:
  - Validation for unsupported or incorrectly formatted instructions.

## System Requirements
- Python 3.8 or later
- PyQt5 library

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mips-simulator
   ```

2. Install required dependencies:
   ```bash
   pip install pyqt5
   ```

3. Run the simulator:
   ```bash
   python mips_simulator.py
   ```

## Usage
1. Open the application by running the `mips_simulator.py` file.
2. Enter MIPS assembly code in the "Assembly Code" editor.
3. Click:
   - **Run** to execute the entire program.
   - **Step** to execute instructions step-by-step.
   - **Reset** to clear the program state.
4. View the machine code, register values, data memory, and execution trace in their respective panels.

### Example Programs
#### R-Format Test:
```assembly
addi $t0, $zero, 10
addi $t1, $zero, 5
add $t2, $t0, $t1
sub $t3, $t0, $t1
and $t4, $t0, $t1
or $t5, $t0, $t1
slt $t6, $t1, $t0
```

#### I-Format Test:
```assembly
addi $t0, $zero, 100
sw $t0, 0($zero)
lw $t1, 0($zero)
beq $t0, $t1, equal
addi $t2, $zero, 1
equal:
bne $t0, $zero, next
next:
```

#### J-Format Test:
```assembly
j main
addi $t0, $zero, 1
main:
jal proc
j end
proc:
addi $t1, $zero, 2
jr $ra
end:
```

## File Structure
- `mips_simulator.py`: Main source code containing the simulator implementation.
- `README.md`: Documentation for the project.

## Known Issues
- Limited error handling for certain edge cases in assembly code input.
- Performance may degrade for very large instruction sets.

## Future Enhancements
- Support additional MIPS instructions.
- Add a feature to save and load programs from files.
- Implement a more comprehensive debugging tool.

## Acknowledgments
This project was developed as part of a course assignment to enhance understanding of computer architecture concepts through simulation.

---

For any issues or questions, please contact [Your Email/Name].

