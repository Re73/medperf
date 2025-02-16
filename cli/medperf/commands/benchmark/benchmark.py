import typer

import medperf.config as config
from medperf.utils import cleanup
from medperf.decorators import clean_except
from medperf.commands.benchmark.list import BenchmarksList
from medperf.commands.benchmark.submit import SubmitBenchmark
from medperf.commands.benchmark.associate import AssociateBenchmark

app = typer.Typer()


@app.command("ls")
@clean_except
def list(
    all: bool = typer.Option(False, help="Display all benchmarks in the platform")
):
    """Lists all benchmarks created by the user
    If --all is used, displays all benchmarks in the platform
    """
    ui = config.ui
    comms = config.comms
    BenchmarksList.run(comms, ui, all)


@app.command("submit")
@clean_except
def submit(
    name: str = typer.Option(..., "--name", "-n", help="Name of the benchmark"),
    description: str = typer.Option(
        ..., "--description", "-d", help="Description of the benchmark"
    ),
    docs_url: str = typer.Option("", "--docs-url", "-u", help="URL to documentation"),
    demo_url: str = typer.Option(
        "", "--demo-url", help="URL to demonstration dataset tarball file"
    ),
    demo_hash: str = typer.Option(
        "", "--demo-hash", help="SHA1 of demonstration dataset tarball file"
    ),
    data_preparation_mlcube: str = typer.Option(
        ..., "--data-preparation-mlcube", "-p", help="Data Preparation MLCube UID"
    ),
    reference_model_mlcube: str = typer.Option(
        ..., "--reference-model-mlcube", "-m", help="Reference Model MLCube UID"
    ),
    evaluator_mlcube: str = typer.Option(
        ..., "--evaluator-mlcube", "-e", help="Evaluator MLCube UID"
    ),
):
    """Submits a new benchmark to the platform"""
    comms = config.comms
    ui = config.ui
    benchmark_info = {
        "name": name,
        "description": description,
        "docs_url": docs_url,
        "demo_url": demo_url,
        "demo_hash": demo_hash,
        "data_preparation_mlcube": data_preparation_mlcube,
        "reference_model_mlcube": reference_model_mlcube,
        "evaluator_mlcube": evaluator_mlcube,
    }
    SubmitBenchmark.run(benchmark_info, comms, ui)
    cleanup()
    ui.print("✅ Done!")


@app.command("associate")
@clean_except
def associate(
    benchmark_uid: str = typer.Option(
        ..., "--benchmark_uid", "-b", help="UID of benchmark to associate with"
    ),
    model_uid: str = typer.Option(
        None, "--model_uid", "-m", help="UID of model MLCube to associate"
    ),
    dataset_uid: str = typer.Option(
        None, "--data_uid", "-d", help="Server UID of registered dataset to associate"
    ),
    approval: bool = typer.Option(False, "-y", help="Skip approval step"),
):
    """Associates a benchmark with a given mlcube or dataset. Only one option at a time.
    """
    comms = config.comms
    ui = config.ui
    AssociateBenchmark.run(
        benchmark_uid, model_uid, dataset_uid, comms, ui, approved=approval
    )
    ui.print("✅ Done!")
