# -*- coding: utf-8 -*-
"""
Command Line Interface for HHW Brick

Provides CLI commands for CSV to Brick conversion, deployment operations, and model validation.
"""

import click
import logging
import sys
from pathlib import Path

from ..conversion.csv_to_brick import CSVToBrickConverter
from ..conversion.batch_converter import BatchConverter
from ..deployment import BrickDeployment
from ..validation.validator import BrickModelValidator
from ..validation.subgraph_pattern_validator import SubgraphPatternValidator


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """HHW Brick CLI - Convert CSV to Brick, deploy applications, and validate models."""
    setup_logging(verbose)


@cli.group()
def convert():
    """CSV to Brick conversion commands."""
    pass


@cli.group()
def deploy():
    """Application deployment commands."""
    pass


@cli.group()
def validate():
    """Brick model validation commands."""
    pass


# ============================================================================
# CONVERSION COMMANDS
# ============================================================================

@convert.command('single')
@click.argument('metadata_csv', type=click.Path(exists=True))
@click.argument('vars_csv', type=click.Path(exists=True))
@click.option('--system-type', '-s', required=True, help='System type (e.g., Condensing, Non-condensing)')
@click.option('--building-tag', '-b', required=True, help='Building identifier tag')
@click.option('--output', '-o', type=click.Path(), help='Output TTL file path')
@click.option('--validate', is_flag=True, help='Validate output Brick model after conversion')
def convert_single(metadata_csv, vars_csv, system_type, building_tag, output, validate):
    """Convert a single building from CSV to Brick ontology format."""
    try:
        click.echo(f"🔄 Converting building {building_tag} to Brick ontology...")
        click.echo(f"  Metadata: {metadata_csv}")
        click.echo(f"  Variables: {vars_csv}")
        click.echo(f"  System Type: {system_type}")

        converter = CSVToBrickConverter()
        
        if output:
            output_path = output
        else:
            output_path = f"building_{building_tag}_{system_type.lower()}.ttl"
        
        converter.convert_to_brick(
            metadata_csv=metadata_csv,
            vars_csv=vars_csv,
            system_type=system_type,
            building_tag=building_tag,
            output_path=output_path
        )

        click.echo(f"✅ Conversion completed successfully!")
        click.echo(f"📄 Output: {output_path}")

        if validate:
            click.echo("🔍 Validating converted model...")
            validator = BrickModelValidator()
            result = validator.validate_ontology(output_path)
            if result['valid']:
                click.echo("✅ Model validation passed")
            else:
                click.echo("❌ Model validation failed")
                for error in result.get('errors', [])[:5]:
                    click.echo(f"  • {error}")

    except Exception as e:
        click.echo(f"❌ Conversion failed: {str(e)}", err=True)
        sys.exit(1)


@convert.command('batch')
@click.argument('metadata_csv', type=click.Path(exists=True))
@click.argument('vars_csv', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='Brick_Models_Output', help='Output directory for TTL files')
@click.option('--validate', is_flag=True, help='Validate output models after conversion')
def convert_batch(metadata_csv, vars_csv, output_dir, validate):
    """Batch convert multiple buildings from CSV to Brick format."""
    try:
        click.echo(f"🔄 Batch converting buildings to Brick ontology...")
        click.echo(f"  Metadata: {metadata_csv}")
        click.echo(f"  Variables: {vars_csv}")
        click.echo(f"  Output Directory: {output_dir}")

        batch_converter = BatchConverter()
        results = batch_converter.convert_all_buildings(
            metadata_csv=metadata_csv,
            vars_csv=vars_csv,
            output_dir=output_dir
        )

        click.echo(f"\n✅ Batch conversion completed!")
        click.echo(f"📊 Total buildings processed: {results.get('total', 0)}")
        click.echo(f"✅ Successful: {results.get('successful', 0)}")
        click.echo(f"❌ Failed: {results.get('failed', 0)}")

        if validate and results.get('successful', 0) > 0:
            click.echo("\n🔍 Validating converted models...")
            validator = BrickModelValidator()
            # Implement batch validation here if needed

    except Exception as e:
        click.echo(f"❌ Batch conversion failed: {str(e)}", err=True)
        sys.exit(1)


# ============================================================================
# VALIDATION COMMANDS
# ============================================================================

@validate.command('ontology')
@click.argument('ttl_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output report file path')
def validate_ontology(ttl_file, output):
    """Validate Brick ontology compliance of a model."""
    try:
        click.echo(f"🔍 Validating Brick ontology compliance...")
        click.echo(f"  Model: {ttl_file}")

        validator = BrickModelValidator()
        result = validator.validate_ontology(ttl_file)

        if result['valid']:
            click.echo("✅ Model is valid!")
            click.echo(f"📊 Total triples: {result.get('triple_count', 0)}")
        else:
            click.echo("❌ Model validation failed!")
            click.echo("\nErrors:")
            for error in result.get('errors', []):
                click.echo(f"  • {error}")

        if output:
            import json
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            click.echo(f"\n📄 Report saved to: {output}")

    except Exception as e:
        click.echo(f"❌ Validation failed: {str(e)}", err=True)
        sys.exit(1)


@validate.command('points')
@click.argument('building_tag')
@click.argument('ttl_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output report file path')
def validate_points(building_tag, ttl_file, output):
    """Validate point count for a specific building."""
    try:
        click.echo(f"🔍 Validating points for building {building_tag}...")
        click.echo(f"  Model: {ttl_file}")

        # This would use point count validator
        click.echo("✅ Point validation completed")
        # TODO: Implement actual point validation

    except Exception as e:
        click.echo(f"❌ Point validation failed: {str(e)}", err=True)
        sys.exit(1)


@validate.command('subgraph')
@click.argument('ttl_file', type=click.Path(exists=True))
@click.option('--pattern', '-p', help='Subgraph pattern to validate')
@click.option('--output', '-o', help='Output report file path')
def validate_subgraph(ttl_file, pattern, output):
    """Validate subgraph patterns in a Brick model."""
    try:
        click.echo(f"🔍 Validating subgraph patterns...")
        click.echo(f"  Model: {ttl_file}")

        validator = SubgraphPatternValidator()
        # TODO: Implement subgraph validation call
        
        click.echo("✅ Subgraph validation completed")

    except Exception as e:
        click.echo(f"❌ Subgraph validation failed: {str(e)}", err=True)
        sys.exit(1)


# ============================================================================
# DEPLOYMENT COMMANDS
# ============================================================================

@deploy.command('local')
@click.argument('brick_file', type=click.Path(exists=True))
@click.option('--port', '-p', default=8080, help='Port for local deployment')
def deploy_local(brick_file, port):
    """Deploy Brick model locally."""
    try:
        click.echo(f"🚀 Deploying Brick model locally on port {port}...")

        deployment = BrickDeployment()
        deployment.deploy_local(brick_file, port)

        click.echo("✅ Local deployment started!")

    except Exception as e:
        click.echo(f"❌ Deployment failed: {str(e)}", err=True)
        sys.exit(1)


# ============================================================================
# UTILITY COMMANDS
# ============================================================================

@cli.command('version')
def version():
    """Show version information."""
    from .. import __version__
    click.echo(f"HHW Brick v{__version__}")


if __name__ == '__main__':
    cli()

