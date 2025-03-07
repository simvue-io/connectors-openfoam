# Simvue Connectors - OpenFoam

<br/>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/simvue-io/.github/blob/5eb8cfd2edd3269259eccd508029f269d993282f/simvue-white.png" />
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/simvue-io/.github/blob/5eb8cfd2edd3269259eccd508029f269d993282f/simvue-black.png" />
    <img alt="Simvue" src="https://github.com/simvue-io/.github/blob/5eb8cfd2edd3269259eccd508029f269d993282f/simvue-black.png" width="500">
  </picture>
</p>

<p align="center">
Allow easy connection between Simvue and OpenFOAM, allowing for easy tracking and monitoring of CFD simulations in real time.
</p>

<div align="center">
<a href="https://github.com/simvue-io/client/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/github/license/simvue-io/client"/></a>
<img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue">
</div>

<h3 align="center">
 <a href="https://simvue.io"><b>Website</b></a>
  •
  <a href="https://docs.simvue.io"><b>Documentation</b></a>
</h3>

## Implementation
A customised `OpenfoamRun` class has been created which automatically does the following:

* Uploads the input files stored in the Constant and System directories, as well as the initial conditions in the 0 directory, as input artifacts
* Uploads the Allrun script as a code artifact
* Uploads information from the top of the log files, such as the OpenFOAM build used, as metadata
* Uploads information from the log files before the solve begins to the events log
* Tracks the residuals being calculated for each parameter as metrics
* Once complete, uploads all of the outputs for each time step as output artifacts

The `OpenfoamRun` class also inherits from the `Run()` class of the Simvue Python API, allowing for further detailed control over how your simulation is tracked.

## Installation
To install and use this connector, first create a virtual environment:
```
python -m venv venv
```
Then activate it:
```
source venv/bin/activate
```
And then use pip to install this module:
```
pip install simvue-openfoam
```

## Configuration
The service URL and token can be defined as environment variables:
```sh
export SIMVUE_URL=...
export SIMVUE_TOKEN=...
```
or a file `simvue.toml` can be created containing:
```toml
[server]
url = "..."
token = "..."
```
The exact contents of both of the above options can be obtained directly by clicking the **Create new run** button on the web UI. Note that the environment variables have preference over the config file.

## Usage example
{Replace the example below with a similar example exhibiting how to use your Connector. The example for the FDS (Fire Dynamics Simulator) connector is given below:}

```python
from simvue_fds.connector import FDSRun

...

if __name__ == "__main__":

    ...

    # Using a context manager means that the status will be set to completed automatically,
    # and also means that if the code exits with an exception this will be reported to Simvue
    with FDSRun() as run:

        # Specify a run name, along with any other optional parameters:
        run.init(
          name = 'my-fds-simulation',                                   # Run name
          metadata = {'number_fires': 3},                               # Metadata
          tags = ['fds', 'multiple-fires'],                             # Tags
          description = 'FDS simulation of fires in a parking garage.', # Description
          folder = '/fds/parking-garage/trial_1'                        # Folder path
        )

        # Set folder details if necessary
        run.set_folder_details(
          metadata = {'simulation_type': 'parking_garage'},             # Metadata
          tags = ['fds'],                                               # Tags
          description = 'FDS simulations with fires in different areas' # Description
        )

        # Can use the base Simvue Run() methods to upload extra information, eg:
        run.save_file(os.path.abspath(__file__), "code")

        # Can add alerts specific to your simulation, eg:
        run.create_metric_threshold_alert(
          name="visibility_below_five_metres",    # Name of Alert
          metric="eye_level_visibility",          # Metric to monitor
          frequency=1,                            # Frequency to evaluate rule at (mins)
          rule="is below",                        # Rule to alert on
          threshold=5,                            # Threshold to alert on
          notification='email',                   # Notification type
          trigger_abort=True                      # Abort simulation if triggered
        )

        # Launch the FDS simulation
        run.launch(
            fds_input_path='path/to/my/input_file.i',   # Path to your FDS input file
            workdir_path='path/to/my/results_dir',      # Path where results should be created
            run_in_parallel=True,                       # Whether to run in parallel using MPI
            num_processors=2                            # Number of cores to use if in parallel

            )

```

## License

Released under the terms of the [Apache 2](https://github.com/simvue-io/client/blob/main/LICENSE) license.
