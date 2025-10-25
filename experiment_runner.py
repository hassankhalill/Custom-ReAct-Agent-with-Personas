"""
Experiment Runner for testing different agent configurations
Tests various personas, prompts, and LLM configurations
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

from react_agent import ReActAgent
from personas import get_persona, list_personas


class ExperimentRunner:
    """
    Manages and runs experiments with different agent configurations
    """

    def __init__(self, output_dir: str = "experiment_results"):
        """
        Initialize experiment runner

        Args:
            output_dir: Directory to save experiment results
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.experiments = []
        self.results = []

    def add_experiment(
        self,
        persona_key: str,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        max_iterations: int = 5,
        test_queries: List[str] = None
    ):
        """
        Add an experiment configuration

        Args:
            persona_key: Key for the persona to test
            model_name: OpenAI model name
            temperature: Temperature parameter
            max_tokens: Max tokens in response
            top_p: Top-p sampling parameter
            max_iterations: Max ReAct iterations
            test_queries: List of test queries to run
        """
        if test_queries is None:
            test_queries = self._get_default_test_queries()

        experiment = {
            "id": len(self.experiments) + 1,
            "persona_key": persona_key,
            "model_name": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "max_iterations": max_iterations,
            "test_queries": test_queries
        }

        self.experiments.append(experiment)
        print(f"Added experiment #{experiment['id']}: {persona_key} with {model_name} (temp={temperature})")

    def _get_default_test_queries(self) -> List[str]:
        """Get default test queries covering various scenarios"""
        return [
            "What services do you offer?",
            "I have severe allergies. Can you help me?",
            "What cleaning products do you use?",
            "Do you service the Downtown area?",
            "I'd like to schedule a deep cleaning for my home"
        ]

    def run_experiments(self, verbose: bool = True):
        """
        Run all configured experiments

        Args:
            verbose: Print detailed output during experiments
        """
        print(f"\n{'='*80}")
        print(f"STARTING EXPERIMENT SUITE")
        print(f"Total experiments: {len(self.experiments)}")
        print(f"{'='*80}\n")

        for exp in self.experiments:
            print(f"\n{'='*80}")
            print(f"EXPERIMENT #{exp['id']}")
            print(f"Persona: {exp['persona_key']}")
            print(f"Model: {exp['model_name']} (temp={exp['temperature']}, top_p={exp['top_p']})")
            print(f"{'='*80}\n")

            # Get persona config
            persona_config = get_persona(exp["persona_key"])

            # Create agent
            agent = ReActAgent(
                persona_name=persona_config["name"],
                system_prompt=persona_config["system_prompt"],
                model_name=exp["model_name"],
                temperature=exp["temperature"],
                max_tokens=exp["max_tokens"],
                top_p=exp["top_p"],
                max_iterations=exp["max_iterations"]
            )

            # Run test queries
            query_results = []
            for i, query in enumerate(exp["test_queries"], 1):
                print(f"\n--- Test Query {i}/{len(exp['test_queries'])} ---")
                print(f"Query: {query}\n")

                try:
                    response = agent.run(query)

                    query_result = {
                        "query_number": i,
                        "query": query,
                        "response": response,
                        "success": True
                    }

                    if verbose:
                        print(f"\nResponse: {response}\n")

                except Exception as e:
                    print(f"ERROR: {str(e)}")
                    query_result = {
                        "query_number": i,
                        "query": query,
                        "response": None,
                        "success": False,
                        "error": str(e)
                    }

                query_results.append(query_result)

            # Get agent logs and convert datetime objects to strings
            agent_logs = agent.get_logs()
            logs_serializable = []
            for log in agent_logs:
                log_copy = log.copy()
                # Convert datetime objects to ISO format strings
                if 'start_time' in log_copy and hasattr(log_copy['start_time'], 'isoformat'):
                    log_copy['start_time'] = log_copy['start_time'].isoformat()
                if 'end_time' in log_copy and hasattr(log_copy['end_time'], 'isoformat'):
                    log_copy['end_time'] = log_copy['end_time'].isoformat()
                logs_serializable.append(log_copy)

            # Save experiment result
            result = {
                "experiment_id": exp["id"],
                "persona_key": exp["persona_key"],
                "persona_name": persona_config["name"],
                "model_name": exp["model_name"],
                "temperature": exp["temperature"],
                "max_tokens": exp["max_tokens"],
                "top_p": exp["top_p"],
                "max_iterations": exp["max_iterations"],
                "timestamp": datetime.now().isoformat(),
                "query_results": query_results,
                "agent_logs": logs_serializable
            }

            self.results.append(result)

            # Save individual experiment result
            result_file = os.path.join(
                self.output_dir,
                f"experiment_{exp['id']}_{exp['persona_key']}.json"
            )
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)

            print(f"\n✓ Experiment #{exp['id']} completed. Results saved to {result_file}")

        print(f"\n{'='*80}")
        print(f"ALL EXPERIMENTS COMPLETED")
        print(f"{'='*80}\n")

        # Save summary
        self._save_summary()

    def _save_summary(self):
        """Save experiment summary"""
        summary_file = os.path.join(self.output_dir, "experiment_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Summary saved to {summary_file}")

        # Create comparison table
        self._create_comparison_table()

    def _create_comparison_table(self):
        """Create a comparison table of results"""
        comparison_data = []

        for result in self.results:
            row = {
                "Experiment ID": result["experiment_id"],
                "Persona": result["persona_key"],
                "Model": result["model_name"],
                "Temperature": result["temperature"],
                "Top-P": result["top_p"],
                "Total Queries": len(result["query_results"]),
                "Successful": sum(1 for qr in result["query_results"] if qr["success"]),
                "Avg Iterations": sum(log["iterations"] for log in result["agent_logs"]) / len(result["agent_logs"]) if result["agent_logs"] else 0,
                "Avg Duration (s)": sum(log["duration"] for log in result["agent_logs"]) / len(result["agent_logs"]) if result["agent_logs"] else 0
            }
            comparison_data.append(row)

        df = pd.DataFrame(comparison_data)

        # Save to CSV
        csv_file = os.path.join(self.output_dir, "comparison_table.csv")
        df.to_csv(csv_file, index=False)

        print(f"Comparison table saved to {csv_file}")
        print("\nComparison Summary:")
        print(df.to_string(index=False))

    def get_results(self) -> List[Dict]:
        """Get all experiment results"""
        return self.results


def create_comprehensive_experiment_suite():
    """
    Create a comprehensive suite of experiments testing:
    - Different personas (Friendly, Expert, Cautious)
    - Different prompt types (Zero-shot, Few-shot, CoT)
    - Different temperatures (0.3, 0.7, 1.0)
    - Different models (gpt-4o-mini, gpt-4o)
    """
    runner = ExperimentRunner()

    # Test queries covering different scenarios
    test_queries = [
        "What services do you offer?",
        "I have severe allergies to dust and pet dander. Can you help?",
        "What cleaning products do you use? I'm concerned about chemicals.",
        "Do you service the Downtown area?",
        "I'd like to book a deep cleaning. My name is John Smith, email john@example.com"
    ]

    # ========================================================================
    # Experiment Set 1: Persona Comparison (same config, different personas)
    # ========================================================================
    print("\n=== EXPERIMENT SET 1: Persona Comparison ===")

    personas_to_test = [
        "friendly_zero_shot",
        "expert_zero_shot",
        "cautious_zero_shot"
    ]

    for persona in personas_to_test:
        runner.add_experiment(
            persona_key=persona,
            model_name="gpt-4o-mini",
            temperature=0.7,
            test_queries=test_queries
        )

    # ========================================================================
    # Experiment Set 2: Prompt Engineering (Zero-shot vs Few-shot vs CoT)
    # ========================================================================
    print("\n=== EXPERIMENT SET 2: Prompt Engineering ===")

    # Test with Friendly persona
    for prompt_type in ["zero_shot", "few_shot", "cot"]:
        runner.add_experiment(
            persona_key=f"friendly_{prompt_type}",
            model_name="gpt-4o-mini",
            temperature=0.7,
            test_queries=test_queries
        )

    # ========================================================================
    # Experiment Set 3: Temperature Variations
    # ========================================================================
    print("\n=== EXPERIMENT SET 3: Temperature Variations ===")

    for temp in [0.3, 0.7, 1.0]:
        runner.add_experiment(
            persona_key="friendly_zero_shot",
            model_name="gpt-4o-mini",
            temperature=temp,
            test_queries=test_queries
        )

    # ========================================================================
    # Experiment Set 4: Model Comparison
    # ========================================================================
    print("\n=== EXPERIMENT SET 4: Model Comparison ===")

    for model in ["gpt-4o-mini", "gpt-4o"]:
        runner.add_experiment(
            persona_key="friendly_cot",
            model_name=model,
            temperature=0.7,
            test_queries=test_queries
        )

    # ========================================================================
    # Experiment Set 5: Top-P Variations
    # ========================================================================
    print("\n=== EXPERIMENT SET 5: Top-P Variations ===")

    for top_p in [0.5, 0.9, 1.0]:
        runner.add_experiment(
            persona_key="expert_zero_shot",
            model_name="gpt-4o-mini",
            temperature=0.7,
            top_p=top_p,
            test_queries=test_queries
        )

    return runner


if __name__ == "__main__":
    # Create and run comprehensive experiment suite
    runner = create_comprehensive_experiment_suite()

    print(f"\nTotal experiments configured: {len(runner.experiments)}")
    print("\nStarting experiments...\n")

    runner.run_experiments(verbose=False)

    print("\n✓ All experiments completed!")
    print(f"Results saved in '{runner.output_dir}' directory")
