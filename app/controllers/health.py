import time
from datetime import datetime

from scraper import check_bna_status
from models.health import Dependency, Health


def get_health() -> Health:
    start = time.time()
    bna_status = check_bna_status()
    elapsed = time.time() - start
    return Health(
        datetime=datetime.now().isoformat(),
        response_time=f"{elapsed:.3f}s",
        dependencies=[Dependency(name="BNA", status=bna_status)],
    )
