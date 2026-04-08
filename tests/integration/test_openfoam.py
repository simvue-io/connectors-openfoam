from simvue_openfoam.connector import OpenfoamRun
import pytest
import pathlib
import tempfile
import simvue
from simvue.sender import Sender
import subprocess
import uuid
import time
import shutil
import tempfile


def run_openfoam(case_name, upload_as_zip, offline, load):
    # Copy case to temp dir
    with tempfile.TemporaryDirectory() as tempd:
        shutil.copytree(
            pathlib.Path(__file__).parent.joinpath(
                "example_data", "load" if load else "launch", case_name
            ),
            tempd,
            dirs_exist_ok=True,
        )

        # Initialise the OpenFOAM class as a context manager
        with OpenfoamRun(mode="offline" if offline else "online") as run:
            # Initialise the run, providing a name for the run, and optionally extra information such as a folder, description, tags etc
            run.init(
                name=f"openfoam-integration-{case_name}-{'offline' if offline else 'online'}-{'load' if load else 'launch'}-{str(uuid.uuid4())}",
                description="An example of using the OpenfoamRun Connector to track an OpenFOAM simulation.",
                folder="/openfoam_connector_integration_tests",
                tags=["openfoam", "integration", "test"],
                retention_period="30 mins",
            )

            # You can use any of the Simvue Run() methods to upload extra information before/after the simulation
            run.create_metric_threshold_alert(
                name="ux_residuals_too_high",
                metric="residuals.initial.Ux",
                rule="is above",
                threshold=0.1,
                frequency=1,
                window=1,
            )
            if load:
                run.load(openfoam_case_dir=tempd, upload_as_zip=upload_as_zip)
            else:
                run.launch(openfoam_case_dir=tempd, upload_as_zip=upload_as_zip)

            # Once the simulation is complete, you can upload any final items to the Simvue run before it closes
            run.log_event("Test...")

            run_id = run.id

            time.sleep(2)

            if offline:
                sender = Sender(throw_exceptions=True)
                sender.upload()
                run_id = sender._id_mapping.get(run_id)

        return run_id


@pytest.mark.parametrize("load", (True, False), ids=("load", "launch"))
@pytest.mark.parametrize("offline", (True, False), ids=("offline", "online"))
def test_openfoam_airfoil(offline_cache_setup, offline, load):

    run_id = run_openfoam(
        case_name="airFoil2D",
        upload_as_zip=True,
        offline=offline,
        load=load,
    )

    client = simvue.Client()
    run_data = client.get_run(run_id)
    events = [event["message"] for event in client.get_events(run_id)]

    # Check run description and tags from init have been added
    assert (
        run_data.description
        == "An example of using the OpenfoamRun Connector to track an OpenFOAM simulation."
    )
    assert sorted(run_data.tags) == ["integration", "openfoam", "test"]

    # Check alert has been added
    assert "ux_residuals_too_high" in [
        alert["name"] for alert in run_data.get_alert_details()
    ]

    # Check metadata from Openfoam log header has been uploaded
    assert run_data.metadata["openfoam"]["nprocs"] == "1"

    assert (
        "[simpleFoam]: Create mesh for time = 0" in events
        or "[foamRun -solver incompressibleFluid]: Create mesh for time = 0" in events
    )

    # Check metrics uploaded for residuals
    metrics = dict(run_data.metrics)
    assert metrics["residuals.initial.Ux"]["count"] > 0
    assert metrics["residuals.final.Ux"]["count"] > 0

    with tempfile.TemporaryDirectory() as temp_dir:
        # Check input files uploaded as zip
        client.get_artifacts_as_files(run_id, "input", temp_dir)
        assert pathlib.Path(temp_dir).joinpath("inputs.zip").exists()

        # Check results uploaded as zip
        client.get_artifacts_as_files(run_id, "output", temp_dir)
        assert pathlib.Path(temp_dir).joinpath("results.zip").exists()


@pytest.mark.parametrize("load", (True, False), ids=("load", "launch"))
@pytest.mark.parametrize("offline", (True, False), ids=("offline", "online"))
def test_openfoam_movingcone(offline_cache_setup, offline, load):

    run_id = run_openfoam(
        case_name="movingCone",
        upload_as_zip=False,
        offline=offline,
        load=load,
    )

    client = simvue.Client()
    run_data = client.get_run(run_id)
    events = [event["message"] for event in client.get_events(run_id)]

    # Check run description and tags from init have been added
    assert (
        run_data.description
        == "An example of using the OpenfoamRun Connector to track an OpenFOAM simulation."
    )
    assert sorted(run_data.tags) == ["integration", "openfoam", "test"]

    # Check alert has been added
    assert "ux_residuals_too_high" in [
        alert["name"] for alert in run_data.get_alert_details()
    ]

    # Check metadata from Openfoam log header has been uploaded
    assert run_data.metadata["openfoam"]["nprocs"] == "1"

    # Check events uploaded from each log
    assert (
        "[pimpleFoam]: Create mesh for time = 0" in events
        or "[foamRun]: Create mesh for time = 0" in events
    )

    # Different blockMesh solvers also run
    assert "[blockMesh -mesh 0.003]: Creating block mesh topology" in events
    assert "[blockMesh]: Creating block mesh topology" in events

    # Check metrics uploaded for residuals
    metrics = dict(run_data.metrics)
    assert metrics["residuals.initial.Ux"]["count"] > 0
    assert metrics["residuals.final.Ux"]["count"] > 0

    with tempfile.TemporaryDirectory() as temp_dir:
        # Check input files uploaded - NOT as zip
        client.get_artifacts_as_files(run_id, "input", temp_dir)

        assert pathlib.Path(temp_dir).joinpath("0", "p").exists()
        assert (
            pathlib.Path(temp_dir).joinpath("constant", "physicalProperties").exists()
        )
        assert pathlib.Path(temp_dir).joinpath("system", "controlDict").exists()

        # Check results uploaded - NOT as zip
        client.get_artifacts_as_files(run_id, "output", temp_dir)
        assert pathlib.Path(temp_dir).joinpath("0.0001", "p").exists()
        assert pathlib.Path(temp_dir).joinpath("0.0009", "p").exists()
