"""
OpenFOAM Connector Example
========================
This is an example of using OpenfoamRun to load historic simulation results

The OpenFOAM simulation used here simulates water flows after a dam breaks.

To run this example with Docker:
    - Pull the OpenFOAM image: docker run -it ghcr.io/simvue-io/openfoam_example
    - Create a simvue.toml file, copying in your information from the Simvue server: nano simvue.toml
    - Run the example script: python examples/load_dambreak_example.py

To run this example on your own system with Openfoam installed:
    - Ensure that you have OpenFOAM installed on your system
    - Clone this repository: git clone https://github.com/simvue-io/connectors-openfoam.git
    - Move into OpenFOAM connector directory: cd connectors-openfoam
    - Create a simvue.toml file, copying in your information from the Simvue server: nano simvue.toml
    - Install Poetry: pip install poetry
    - Install required modules: poetry install
    - Run the example script: poetry run python load_dambreak_example.py

For a more in depth example, see: https://docs.simvue.io/examples/openfoam/

"""

import pathlib
import subprocess
import uuid
from simvue_openfoam.connector import OpenfoamRun


def openfoam_example(run_folder, offline=False):

    # Initialise the OpenFOAM class as a context manager
    with OpenfoamRun(mode="offline" if offline else "online") as run:
        # Initialise the run, providing a name for the run, and optionally extra information such as a folder, description, tags etc
        run.init(
            name="openfoam_simulation_dambreak-%s" % str(uuid.uuid4()),
            description="An example of using the OpenfoamRun Connector to load OpenFOAM results.",
            folder=run_folder,
            tags=["openfoam", "dambreak"],
        )

        # Then call the .load() method to load your OpenFOAM results, providing the path to the case directory
        run.load(
            openfoam_case_dir=pathlib.Path(__file__).parent.joinpath("damBreak"),
        )

        # Once the simulation is complete, you can upload any final items to the Simvue run before it closes
        run.save_file(pathlib.Path(__file__), "code")

        return run.id


if __name__ == "__main__":
    openfoam_example("/openfoam_example")
