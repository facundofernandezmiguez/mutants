import unittest
from lambda_function import is_mutant

class TestIsMutant(unittest.TestCase):

    def test_mutant_dna(self):
        """
        Test para ADN mutante, debe tener más de una secuencia de 4 caracteres iguales.
        """
        # Secuencia mutante (dos secuencias de 4 iguales: cuarta fila y diagonal principal)
        dna = [
            "ATGCGA",
            "CAGHCC",
            "TTATGT",
            "AAAAGG",  
            "CTCCTA",
            "TCACTG"
        ]
        result = is_mutant(dna)
        self.assertTrue(result)  # Debe ser mutante

    def test_non_mutant_dna(self):
        """
        Test para ADN no mutante, ninguna secuencia de 4 caracteres iguales.
        """
        # Secuencia no mutante (ninguna secuencia de 4 iguales)
        dna = [
            "ATGCGA",
            "CCGHCC",
            "TTATGT",
            "AAFAGG",  
            "CTCCTA",
            "TCACTG"
        ]
        result = is_mutant(dna)
        self.assertFalse(result)  # No es mutante

    def test_single_sequence_dna(self):
        """
        Test para ADN con solo una secuencia de 4 caracteres iguales.
        """
        # Secuencia con solo una secuencia de 4 caracteres iguales (4ta fila)
        dna = [
            "ATGCGA",
            "CTGHCC",
            "TTATGT",
            "AAAAGG", 
            "CTCCTA",
            "TCACTG"
        ]
        result = is_mutant(dna)
        self.assertFalse(result)  # No debe ser mutante

if __name__ == '__main__':
    unittest.main()
