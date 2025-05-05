import unittest
import os
import sys

# Configuração crucial do path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def load_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        start_dir=os.path.join(project_root, 'tests'),
        pattern='test_*.py',
        top_level_dir=project_root
    )
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(load_tests())
    
    # DEBUG: Mostra os testes encontrados
    print("\n=== DEBUG INFORMATION ===")
    print(f"Python Path: {sys.path}")
    print(f"Project Root: {project_root}")
    print(f"Test Directory: {os.path.join(project_root, 'tests')}")
    
    if result.testsRun == 0:
        print("\n⚠️ Nenhum teste foi executado. Possíveis causas:")
        print("- O nome do arquivo de teste não segue o padrão 'test_*.py'")
        print("- A classe de teste não herda de unittest.TestCase")
        print("- Os métodos de teste não começam com 'test_'")
        print("- O arquivo candidate_data_service.py não está no local correto")
    
    if not result.wasSuccessful():
        sys.exit(1)