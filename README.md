# COSC4331-Project-Final
This is part of a project me and a partner did for our Real Time Systems course. These files are meant to be used with STR-SUMO (https://github.com/DDeChoU/Selfless-Traffic-Routing-Testbed).

## Explanation of the files
- `experiment.py` - Script that lets users easily simulate and benchmark arbitrary traffic routing algorithms
- `AstarController.py` - An implementation of the A\* routing/search algorithm
- `STR_SUMO_win.py` - Windows compatible version of original STR-SUMO file
- `target_vehicles_generation_protocols_win.py` - Windows compatible version of original STR-SUMO file


## Prerequisites
1. Download/install Python (Python 3 is recommended)
2. Download and install [SUMO](https://sumo.dlr.de/docs/Installing/index.html)
   - Make sure you properly configure the `SUMO_HOME` environment variable
3. Download [STR-SUMO](https://github.com/DDeChoU/Selfless-Traffic-Routing-Testbed)
   - Make sure to install everything listed in `requirements.txt` (using pip/pip3 is recommended)

## How to use the files
### `STR_SUMO_win.py` & `target_vehicles_generation_protocols_win.py`
After downloading STR-SUMO, place these 2 files in the `core` directory

### `AstarController.py`
After downloading STR-SUMO, place this file in the `controller` directory

### `experiment.py`
After downloading STR-SUMO, place this file in the root of the repository.

You can execute it by double-clicking the script (on Windows) or by running it from a terminal of your choice. If you run it from a terminal, you can additionally type `nogui` after the filename to run it without the GUI; do keep in mind it currently has less functionality without it.

## Adding more routing policies
[INSERT EXPLANATION]

## Additional notes
[INSERT ADDITIONAL NOTES]
