import pytest
from unittest.mock import ANY

from medperf.entities.cube import Cube
from medperf.entities.result import Result
from medperf.entities.benchmark import Benchmark
from medperf.commands.mlcube.associate import AssociateCube

PATCH_ASSOC = "medperf.commands.mlcube.associate.{}"


@pytest.fixture
def cube(mocker):
    cube = mocker.create_autospec(spec=Cube)
    mocker.patch.object(Cube, "get", return_value=cube)
    cube.name = "name"
    return cube


@pytest.fixture
def benchmark(mocker):
    benchmark = mocker.create_autospec(spec=Benchmark)
    mocker.patch.object(Benchmark, "get", return_value=benchmark)
    benchmark.name = "name"
    return benchmark


@pytest.fixture
def result(mocker):
    result = mocker.create_autospec(spec=Result)
    mocker.patch.object(Result, "todict", return_value={})
    return result


@pytest.mark.parametrize("cube_uid", [2405, 4186])
@pytest.mark.parametrize("benchmark_uid", [4416, 1522])
def test_run_associates_cube_with_comms(
    mocker, cube, benchmark, result, cube_uid, benchmark_uid, comms, ui
):
    # Arrange
    spy = mocker.patch.object(comms, "associate_cube")
    comp_ret = ("", "", "", result)
    mocker.patch.object(ui, "prompt", return_value="y")
    mocker.patch(
        PATCH_ASSOC.format("CompatibilityTestExecution.run"), return_value=comp_ret
    )

    # Act
    AssociateCube.run(cube_uid, benchmark_uid, comms, ui)

    # Assert
    spy.assert_called_once_with(cube_uid, benchmark_uid, ANY)


@pytest.mark.parametrize("cube_uid", [3081, 1554])
@pytest.mark.parametrize("benchmark_uid", [3739, 4419])
def test_run_calls_compatibility_test(
    mocker, cube, benchmark, cube_uid, benchmark_uid, result, comms, ui
):
    # Arrange
    comp_ret = ("", "", "", result)
    mocker.patch.object(ui, "prompt", return_value="y")
    spy = mocker.patch(
        PATCH_ASSOC.format("CompatibilityTestExecution.run"), return_value=comp_ret
    )

    # Act
    AssociateCube.run(cube_uid, benchmark_uid, comms, ui)

    # Assert
    spy.assert_called_once_with(benchmark_uid, comms, ui, model=cube_uid)
