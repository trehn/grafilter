def build_cache(backend, config_dir):
    return {
        'metrics': backend.metrics(),
    }
