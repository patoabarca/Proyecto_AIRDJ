#!/usr/bin/env python
"""
Script para ejecutar todos los tests de Módulos 8 y 9.
"""

import sys
import unittest

sys.path.insert(0, '.')

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Cargar tests del Módulo 8
    suite1 = loader.discover('tests', pattern='test_media_controller.py')
    suite.addTests(suite1)
    
    # Cargar tests del Módulo 9
    suite2 = loader.discover('tests', pattern='test_interface.py')
    suite.addTests(suite2)
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESULTADO FINAL DE PRUEBAS")
    print("=" * 60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Estado: {'ÉXITO ✓' if result.wasSuccessful() else 'FALLO ✗'}")
    print("=" * 60)
    
    sys.exit(0 if result.wasSuccessful() else 1)
