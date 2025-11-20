"""
FIDD-Bench Main Entry Point

Command-line interface for generating synthetic datasets and running benchmarks.
"""

import click
import json
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from llm.client import LLMClient
from llm.parser import ConfigParser
from generator.core import DataGenerator
from benchmark.spmf_runner import SPMFRunner
from benchmark.metrics import MetricsCalculator
from utils.file_io import FileIO, load_config
from utils.logger import setup_logger


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to config file')
@click.pass_context
def cli(ctx, verbose, config):
    """
    FIDD-Bench: Flexible & Intelligent Data Generator for Data Mining Benchmarking
    
    Generate synthetic datasets using natural language descriptions and
    benchmark pattern mining algorithms.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Load configuration
    try:
        ctx.obj['config'] = load_config(config) if config else load_config()
    except Exception as e:
        click.echo(f"Warning: Could not load config: {e}", err=True)
        ctx.obj['config'] = {}
    
    # Setup logger
    log_level = "DEBUG" if verbose else ctx.obj['config'].get('logging', {}).get('level', 'INFO')
    ctx.obj['logger'] = setup_logger(level=log_level)


@cli.command()
@click.option('--prompt', '-p', help='Natural language description of dataset')
@click.option('--output', '-o', required=True, type=click.Path(), help='Output file path (.spmf)')
@click.option('--config-json', type=click.Path(exists=True), help='Use JSON config instead of LLM')
@click.option('--save-config', type=click.Path(), help='Save generated config to file')
@click.option('--seed', type=int, help='Random seed for reproducibility')
@click.option('--stats', is_flag=True, help='Print dataset statistics')
@click.pass_context
def generate(ctx, prompt, output, config_json, save_config, seed, stats):
    """
    Generate a synthetic dataset from natural language description or JSON config.
    
    Examples:
        # Using JSON config file (no API needed)
        fidd-bench generate --config-json config.json -o data.spmf
        
        # Using natural language prompt (requires LLM API)
        fidd-bench generate -p "1000 transactions, 100 items, sparse retail data" -o data.spmf
    """
    logger = ctx.obj['logger']
    logger.info("Starting data generation...")
    
    # Validate: need either prompt or config_json
    if not prompt and not config_json:
        click.echo("Error: Must provide either --prompt or --config-json", err=True)
        sys.exit(1)
    
    try:
        # Step 1: Get configuration
        if config_json:
            logger.info(f"Loading configuration from {config_json}")
            config = ConfigParser.from_file(config_json)
        else:
            logger.info("Parsing natural language prompt with LLM...")
            llm_config = ctx.obj['config'].get('llm', {})
            client = LLMClient(
                provider=llm_config.get('provider', 'openai'),
                model=llm_config.get('model'),
                temperature=llm_config.get('temperature', 0.3)
            )
            
            raw_config = client.generate_config(prompt)
            logger.debug(f"Raw LLM output: {json.dumps(raw_config, indent=2)}")
            
            # Validate and parse
            parser = ConfigParser(strict_mode=False)
            config = parser.parse(raw_config)
        
        # Save config if requested
        if save_config:
            FileIO.write_json(config, save_config)
            logger.info(f"Configuration saved to {save_config}")
        
        # Step 2: Generate data
        logger.info("Generating dataset...")
        generator = DataGenerator(config)
        data = generator.generate(seed=seed)
        
        # Step 3: Save to file
        logger.info(f"Saving dataset to {output}...")
        generator.to_spmf(output)
        
        # Step 4: Print statistics
        if stats or logger.level <= 20:  # INFO level or below
            dataset_stats = generator.get_statistics()
            click.echo("\n" + "="*60)
            click.echo("Dataset Statistics:")
            click.echo("="*60)
            click.echo(f"Transactions: {dataset_stats['num_transactions']}")
            click.echo(f"Items: {dataset_stats['num_items']}")
            click.echo(f"Density: {dataset_stats['actual_density']:.2%}")
            click.echo(f"Avg Transaction Length: {dataset_stats['avg_transaction_length']:.2f}")
            click.echo(f"Patterns Injected: {dataset_stats['num_patterns_injected']}")
            
            if dataset_stats.get('injected_patterns'):
                click.echo("\nInjected Patterns:")
                for pattern in dataset_stats['injected_patterns']:
                    click.echo(f"  {pattern['id']}: {pattern['items']}")
                    click.echo(f"    Target Support: {pattern['target_support']:.2%}")
                    click.echo(f"    Actual Support: {pattern['actual_support']:.2%}")
            click.echo("="*60 + "\n")
        
        click.echo(f"✓ Dataset generated successfully: {output}", err=False)
        
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True), help='Input dataset (.spmf)')
@click.option('--algorithm', '-a', required=True, help='Algorithm name (Apriori, FPGrowth, etc.)')
@click.option('--min-support', '-s', required=True, type=float, help='Minimum support threshold')
@click.option('--output', '-o', type=click.Path(), help='Output file for patterns')
@click.option('--ground-truth', type=click.Path(exists=True), help='Ground truth JSON for accuracy calculation')
@click.pass_context
def benchmark(ctx, input, algorithm, min_support, output, ground_truth):
    """
    Run a pattern mining algorithm on a dataset.
    
    Example:
        fidd-bench benchmark -i data.spmf -a Apriori -s 0.05 -o results.txt
    """
    logger = ctx.obj['logger']
    logger.info(f"Running benchmark: {algorithm}")
    
    try:
        # Setup output path
        if not output:
            output = f"output_{algorithm}_{min_support}.txt"
        
        # Initialize SPMF runner
        spmf_config = ctx.obj['config'].get('benchmark', {})
        jar_path = spmf_config.get('spmf_jar_path', './lib/spmf.jar')
        java_memory = spmf_config.get('java_memory', '4g')
        
        runner = SPMFRunner(jar_path, java_memory)
        
        # Run algorithm
        logger.info(f"Executing {algorithm} with min_support={min_support}...")
        result = runner.run_algorithm(
            algorithm=algorithm,
            input_file=input,
            output_file=output,
            min_support=min_support,
            timeout=spmf_config.get('timeout', 300)
        )
        
        # Display results
        click.echo("\n" + "="*60)
        click.echo(f"Benchmark Results: {algorithm}")
        click.echo("="*60)
        click.echo(f"Execution Time: {result['execution_time']:.4f}s")
        click.echo(f"Patterns Found: {result.get('num_patterns_found', 'N/A')}")
        
        # Calculate accuracy if ground truth provided
        if ground_truth:
            gt_data = FileIO.read_json(ground_truth)
            gt_patterns = gt_data.get('pattern_injection', [])
            
            found_patterns = runner.parse_output(output)
            
            calculator = MetricsCalculator(ground_truth=gt_patterns)
            accuracy = calculator.calculate_accuracy(found_patterns, min_support)
            
            if accuracy.get('precision') is not None:
                click.echo(f"\nAccuracy Metrics:")
                click.echo(f"  Precision: {accuracy['precision']:.2%}")
                click.echo(f"  Recall: {accuracy['recall']:.2%}")
                click.echo(f"  F1 Score: {accuracy['f1_score']:.4f}")
        
        click.echo("="*60 + "\n")
        click.echo(f"✓ Benchmark completed: {output}", err=False)
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--prompt', '-p', required=True, help='Natural language description')
@click.option('--dataset', '-d', type=click.Path(), help='Dataset output path')
@click.option('--algorithms', '-a', multiple=True, help='Algorithms to test (can specify multiple)')
@click.option('--min-support', '-s', type=float, default=0.05, help='Minimum support threshold')
@click.option('--report', '-r', type=click.Path(), help='Report output path')
@click.option('--seed', type=int, help='Random seed')
@click.pass_context
def full_pipeline(ctx, prompt, dataset, algorithms, min_support, report, seed):
    """
    Run the full pipeline: generate dataset + run multiple benchmarks.
    
    Example:
        fidd-bench full-pipeline -p "sparse retail data" -a Apriori -a FPGrowth -s 0.05
    """
    logger = ctx.obj['logger']
    logger.info("Starting full pipeline...")
    
    # Default dataset path
    if not dataset:
        dataset = "data/processed/pipeline_dataset.spmf"
    
    # Default algorithms
    if not algorithms:
        algorithms = ['Apriori', 'FPGrowth']
    
    # Generate dataset
    ctx.invoke(generate, prompt=prompt, output=dataset, seed=seed, stats=True)
    
    # Run benchmarks
    results = []
    for algo in algorithms:
        try:
            output_file = f"data/benchmarks/{algo}_output.txt"
            ctx.invoke(
                benchmark,
                input=dataset,
                algorithm=algo,
                min_support=min_support,
                output=output_file
            )
            # results.append(result)  # Would collect for comparison
        except Exception as e:
            logger.error(f"Algorithm {algo} failed: {e}")
    
    click.echo("\n✓ Full pipeline completed!", err=False)


if __name__ == '__main__':
    cli(obj={})
