from .utils import quote


def build_cache(backend, config_dir):
    return {
        'metrics': [(metric, quote(metric)) for metric in backend.metrics()],
    }
