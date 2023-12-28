import sys
import os

# Get the current directory of this __init__.py file
package_directory = os.path.dirname(__file__)

# Add the current package directory to sys.path
sys.path.append(package_directory)

from helper import product_common_url
from product_details import get_product_details

__all__ = (
    get_product_details, product_common_url
)
