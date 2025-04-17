"""Implementation for terraform_aws_provider_resources_listing resource."""

import sys
from loguru import logger
from pathlib import Path


# Configure logger for enhanced diagnostics with stacktraces
logger.configure(
    handlers=[
        {
            'sink': sys.stderr,
            'backtrace': True,
            'diagnose': True,
            'format': '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
        }
    ]
)

# Path to the static markdown file
STATIC_RESOURCES_PATH = (
    Path(__file__).parent.parent.parent / 'static' / 'AWS_PROVIDER_RESOURCES.md'
)


async def terraform_aws_provider_assets_listing_impl() -> str:
    """Generate a comprehensive listing of AWS provider resources and data sources.

    This implementation reads from a pre-generated static markdown file instead of
    scraping the web in real-time. The static file should be generated using the
    generate_aws_provider_resources.py script.

    Returns:
        A markdown formatted string with categorized resources and data sources
    """
    logger.info('Loading AWS provider resources listing from static file')

    try:
        # Check if the static file exists
        if STATIC_RESOURCES_PATH.exists():
            # Read the static file content
            with open(STATIC_RESOURCES_PATH, 'r') as f:
                content = f.read()
            logger.info('Successfully loaded AWS Provider asset list')
            return content
        else:
            # Send error if static file does not exist
            logger.debug(f"Static assets list file not found at '{STATIC_RESOURCES_PATH}'")
            raise Exception('Static assets list file not found')
    except Exception as e:
        logger.error(f'Error generating AWS provider assets listing: {e}')
        return f'# AWS Provider Assets Listing\n\nError generating listing: {str(e)}'
