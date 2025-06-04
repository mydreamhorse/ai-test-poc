from unittest.mock import patch
import pytest

import src.dspy_optimizer as dspy_optimizer


class TestConceptualTestGenerationModule:
    def test_load_rag_data_for_poc(self):
        module = dspy_optimizer.ConceptualTestGenerationModule()
        dummy_data = [{'filename': 'case.txt', 'natural_language_case': 'A', 'ideal_script': 'B'}]
        with patch('src.dspy_optimizer.rag_system.load_rag_data', return_value=dummy_data) as mock_load, \
             patch('builtins.print') as mock_print:
            module.load_rag_data_for_poc('dummy_dir')
            mock_load.assert_called_once_with('dummy_dir')
            mock_print.assert_any_call("  ConceptualTestGenerationModule: Loading RAG data from dummy_dir for PoC simulation.")
            mock_print.assert_any_call(f"  ConceptualTestGenerationModule: Loaded {len(dummy_data)} RAG examples.")
            assert module.rag_data_store == dummy_data

    def test_forward_invokes_components(self):
        module = dspy_optimizer.ConceptualTestGenerationModule()
        module.rag_data_store = ['existing']
        retrieved = [{'natural_language_case': 'Example', 'ideal_script': 'def test(): pass'}]
        with patch('src.dspy_optimizer.rag_system.retrieve_relevant_examples', return_value=retrieved) as mock_retrieve, \
             patch('src.dspy_optimizer.llm_interface.generate_test_script', return_value='generated') as mock_generate, \
             patch('builtins.print') as mock_print:
            result = module.forward('desc')
            mock_retrieve.assert_called_once_with('desc', module.rag_data_store, num_examples=1)
            mock_generate.assert_called_once()
            assert result == 'generated'


def test_conceptual_dspy_optimization_loop_prints():
    with patch('builtins.print') as mock_print:
        dspy_optimizer.conceptual_dspy_optimization_loop()
        mock_print.assert_any_call("\n--- Conceptual DSPy Optimization Loop ---")
        assert mock_print.call_count > 5
