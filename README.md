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
After downloading STR-SUMO, place these 2 files in the `core` directory (if you are using Windows).

### `AstarController.py`
After downloading STR-SUMO, place this file in the `controller` directory.

### `experiment.py`
After downloading STR-SUMO, place this file in the root of the repository.

You can execute it by double-clicking the script (on Windows) or by running it from a terminal of your choice. If you run it from a terminal, you can additionally type `nogui` after the filename to run it without the GUI; do keep in mind it currently has less functionality without the GUI. Once the script is running, the rest should be self-explanitory.

## Adding more routing policies
`experiment.py` can access and run any routing policy placed in the `controller` directory of the repository, so new policies can be added by simply placing them in this directory and restarting the script.

To create a new routing policy, make a new file named `<name>Controller.py` (replacing `<name>` with something else), and in this file define one or more classed called `<name>Policy` (replacing each `<name>` with the name of the policy/algorithm) that inherit the `RouteController` class defined in STR-SUMO's `RouteController.py`. Further details can be found in comments inside of `RouteController.py`.

Please keep the following in mind:
   - If you want to use an already-existing policy with `experiment.py`, make sure the controller/policies follow the previously described naming conventions
   - When `experiment.py` asks for the name of a policy or controller, it only expects the `<name>` part of the policy/controller to be entered (without 'Controller.py' or 'Policy')
   - `<name>` is case sensitive

## Additional notes
`experiment.py` and `Astar.py` were developed and tested primarily in a Windows-based operating system. Although they *should* function in Unix-like OS's, they have not been tested in any and as such they may not work in those environments without minor tweaks/troubleshooting.
