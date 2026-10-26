# SMFR Core — Draft 0.1

Initial Python reference implementation of the [SMFR specification](https://github.com/mrkoszos/smfr).

## Local tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## CLI without installation

```bash
PYTHONPATH=src python -m smfr validate S2G.12A
PYTHONPATH=src python -m smfr parse S2G.12A
PYTHONPATH=src python -m smfr compare S2.12A S2.12B
```

Optionally, install locally with `python -m pip install -e .` and use `smfr` directly.

Note: This is experimental, not yet published to PyPI; it follows specification Draft 0.1.
