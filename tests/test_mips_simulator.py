import sys
import unittest
from PyQt5.QtWidgets import QApplication
from src.mips_simulator import MIPSSimulator

class TestMIPSSimulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Test sınıfı başlatılırken bir kez çalışır"""
        cls.app = QApplication(sys.argv)
        cls.simulator = MIPSSimulator()

    def setUp(self):
        """Her test öncesinde çalışır"""
        self.simulator.reset_program()

    def test_arithmetic_operations(self):
        """Aritmetik işlemlerin testleri"""
        # Addition test
        test_code = """
            addi $t0, $zero, 5    # t0 = 5
            addi $t1, $zero, 3    # t1 = 3
            add $t2, $t0, $t1     # t2 should be 8
        """
        self.simulator.assembly_editor.setText(test_code)
        self.simulator.run_program()
        
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t0']], 5)
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t1']], 3)
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t2']], 8)

    def test_logical_operations(self):
        """Mantıksal işlemlerin testleri"""
        test_code = """
            addi $t0, $zero, 12   # t0 = 12 (1100 in binary)
            addi $t1, $zero, 10   # t1 = 10 (1010 in binary)
            and $t2, $t0, $t1     # t2 should be 8 (1000 in binary)
            or $t3, $t0, $t1      # t3 should be 14 (1110 in binary)
        """
        self.simulator.assembly_editor.setText(test_code)
        self.simulator.run_program()
        
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t2']], 8)
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t3']], 14)

    def test_memory_operations(self):
        """Bellek işlemlerinin testleri"""
        test_code = """
            addi $t0, $zero, 42   # t0 = 42
            sw $t0, 0($zero)      # Store 42 at address 0
            lw $t1, 0($zero)      # Load from address 0 to t1
        """
        self.simulator.assembly_editor.setText(test_code)
        self.simulator.run_program()
        
        self.assertEqual(self.simulator.data_memory[0], 42)
        self.assertEqual(
            self.simulator.registers[self.simulator.register_map['$t1']], 
            self.simulator.registers[self.simulator.register_map['$t0']]
        )

    def test_branch_operations(self):
        """Dal işlemlerinin testleri"""
        test_code = """
            addi $t0, $zero, 5
            addi $t1, $zero, 5
            beq $t0, $t1, equal
            addi $t2, $zero, 1    # Should skip
            equal:
            addi $t3, $zero, 2    # Should execute
        """
        self.simulator.assembly_editor.setText(test_code)
        self.simulator.run_program()
        
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t3']], 2)
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t2']], 0)

    def test_jump_operations(self):
        """Atlama işlemlerinin testleri"""
        test_code = """
            j main
            addi $t0, $zero, 1    # Should skip
            main:
            addi $t1, $zero, 2    # Should execute
        """
        self.simulator.assembly_editor.setText(test_code)
        self.simulator.run_program()
        
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t0']], 0)
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t1']], 2)

    def test_edge_cases(self):
        """Sınır durumlarının testleri"""
        # Test maximum positive number
        test_code = """
            addi $t0, $zero, 2147483647  # Max positive 32-bit integer
            addi $t1, $zero, 1
            add $t2, $t0, $t1            # Should handle overflow
        """
        self.simulator.assembly_editor.setText(test_code)
        self.simulator.run_program()
        
        # Overflow durumunu kontrol et
        self.assertEqual(
            self.simulator.registers[self.simulator.register_map['$t2']], 
            -2147483648  # Expected result after overflow
        )

    def test_shift_operations(self):
        """Kaydırma işlemlerinin testleri"""
        test_code = """
            addi $t0, $zero, 8    # t0 = 8
            sll $t1, $t0, 2       # t1 should be 32 (8 << 2)
            srl $t2, $t1, 3       # t2 should be 4 (32 >> 3)
        """
        self.simulator.assembly_editor.setText(test_code)
        self.simulator.run_program()
        
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t1']], 32)
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t2']], 4)

    def test_reset_functionality(self):
        """Reset fonksiyonunun testi"""
        test_code = """
            addi $t0, $zero, 5    # t0 = 5
            addi $t1, $zero, 3    # t1 = 3
        """
        self.simulator.assembly_editor.setText(test_code)
        self.simulator.run_program()
        
        # Reset öncesi değerleri kontrol et
        self.assertNotEqual(self.simulator.registers[self.simulator.register_map['$t0']], 0)
        self.assertNotEqual(self.simulator.registers[self.simulator.register_map['$t1']], 0)
        self.assertNotEqual(len(self.simulator.machine_code), 0)
        self.assertNotEqual(self.simulator.machine_code_table.rowCount(), 0)
        
        # Reset yap
        self.simulator.reset_program()
        
        # Reset sonrası değerleri kontrol et
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t0']], 0)
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t1']], 0)
        self.assertEqual(len(self.simulator.machine_code), 0)
        self.assertEqual(self.simulator.machine_code_table.rowCount(), 0)
        self.assertEqual(self.simulator.instruction_count, 0)

    def test_step_execution(self):
        """Step-by-step çalıştırmanın testi"""
        test_code = """
            addi $t0, $zero, 5    # t0 = 5
            addi $t1, $zero, 3    # t1 = 3
            add $t2, $t0, $t1     # t2 = t0 + t1
        """
        self.simulator.assembly_editor.setText(test_code)
        
        # İlk adım
        self.simulator.step_program()
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t0']], 5)
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t1']], 0)
        self.assertEqual(self.simulator.instruction_count, 1)
        
        # İkinci adım
        self.simulator.step_program()
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t1']], 3)
        self.assertEqual(self.simulator.instruction_count, 2)
        
        # Üçüncü adım
        self.simulator.step_program()
        self.assertEqual(self.simulator.registers[self.simulator.register_map['$t2']], 8)
        self.assertEqual(self.simulator.instruction_count, 3)

    def test_bubble_sort(self):
        """Bubble sort algoritmasının testi"""
        # 6 elemanlı bir dizi için bubble sort kodu
        test_code = """
            # Array'i belleğe yükle
            addi $t0, $zero, 5
            sw $t0, 0($zero)
            addi $t0, $zero, 2
            sw $t0, 4($zero)
            addi $t0, $zero, 8
            sw $t0, 8($zero)
            addi $t0, $zero, 1
            sw $t0, 12($zero)
            addi $t0, $zero, 9
            sw $t0, 16($zero)
            addi $t0, $zero, 3
            sw $t0, 20($zero)
            
            # Bubble sort
            addi $s0, $zero, 6    # Array size
            addi $s1, $zero, 0    # Outer loop counter
            
        outer_loop:
            beq $s1, $s0, end_sort
            addi $s2, $zero, 0    # Inner loop counter
            
        inner_loop:
            sub $t0, $s0, $s1
            addi $t0, $t0, -1
            beq $s2, $t0, end_inner
            
            sll $t1, $s2, 2       # t1 = s2 * 4 (array index)
            addi $t2, $t1, 4      # t2 = next element index
            
            lw $t3, 0($t1)        # Load current element
            lw $t4, 0($t2)        # Load next element
            
            slt $t5, $t4, $t3     # if (next < current)
            beq $t5, $zero, no_swap
            
            # Swap elements
            sw $t4, 0($t1)
            sw $t3, 0($t2)
            
        no_swap:
            addi $s2, $s2, 1      # Increment inner loop counter
            j inner_loop
            
        end_inner:
            addi $s1, $s1, 1      # Increment outer loop counter
            j outer_loop
            
        end_sort:
        """
        
        self.simulator.assembly_editor.setText(test_code)
        self.simulator.run_program()
        
        # Sıralanmış array'i kontrol et
        expected = [1, 2, 3, 5, 8, 9]
        for i in range(6):
            self.assertEqual(self.simulator.data_memory[i*4], expected[i])

if __name__ == '__main__':
    unittest.main() 