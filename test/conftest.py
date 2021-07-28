import os
import pytest

from c3python import get_c3

@pytest.fixture(scope="session")
def c3():
    """Loads c3 type system from a tag.
    
    Requires the following environment variables:
        URL:
        TAG:
        TENANT:

    Returns:
        c3 object: c3 type system
    """
    return get_c3(url=os.environ.get("URL"), tenant=os.environ.get("TENANT"), tag=os.environ.get("TAG"))