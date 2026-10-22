# Pantry

Pantry keeps track of the food in one household: what there is, how much, and what runs out soon. It runs on the household's own machine and serves a small JSON API to the household's devices.

    python3 -m pantry.api          # serve on http://127.0.0.1:8077
    python3 -m unittest discover -s tests -t .

This repo is the fixture for the xv-agents evals. It is small on purpose.
