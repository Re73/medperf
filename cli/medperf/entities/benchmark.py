import os
import yaml
import logging
from typing import List
from collections import defaultdict

import medperf.config as config
from medperf.entities.interface import Entity
from medperf.comms.interface import Comms
from medperf.utils import storage_path, pretty_error


class Benchmark(Entity):
    """
    Class representing a Benchmark

    a benchmark is a bundle of assets that enables quantitative
    measurement of the performance of AI models for a specific
    clinical problem. A Benchmark instance contains information
    regarding how to prepare datasets for execution, as well as
    what models to run and how to evaluate them.
    """

    def __init__(self, benchmark_dict: dict):
        """Creates a new benchmark instance

        Args:
            uid (str): The benchmark UID
            benchmark_dict (dict): key-value representation of the benchmark.
        """
        bmk_dict = defaultdict(lambda: None, benchmark_dict)
        # Getting None by default allows creating empty benchmarks for tests
        self.uid = bmk_dict["uid"]
        self.name = bmk_dict["name"]
        self.description = bmk_dict["description"]
        self.docs_url = bmk_dict["docs_url"]
        self.created_at = bmk_dict["created_at"]
        self.modified_at = bmk_dict["modified_at"]
        self.owner = bmk_dict["owner"]
        self.demo_dataset_url = bmk_dict["demo_dataset_tarball_url"]
        self.demo_dataset_hash = bmk_dict["demo_dataset_tarball_hash"]
        self.demo_dataset_generated_uid = bmk_dict["demo_dataset_generated_uid"]
        self.data_preparation = bmk_dict["data_preparation_mlcube"]
        self.reference_model = bmk_dict["reference_model_mlcube"]
        self.evaluator = bmk_dict["data_evaluator_mlcube"]
        # Default value for fields that should not be None in any particular scenario
        self.models = bmk_dict["models"] or []
        self.state = bmk_dict["state"] or "DEVELOPMENT"
        self.is_valid = bmk_dict["is_valid"] or True
        self.approval_status = bmk_dict["approval_status"] or "PENDING"
        self.metadata = bmk_dict["metadata"] or {}

    @classmethod
    def all(cls) -> List["Benchmark"]:
        """Gets and creates instances of all locally present benchmarks

        Returns:
            List[Benchmark]: a list of Benchmark instances.
        """
        logging.info("Retrieving all benchmarks")
        bmks_storage = storage_path(config.benchmarks_storage)
        try:
            uids = next(os.walk(bmks_storage))[1]
        except StopIteration:
            msg = "Couldn't iterate over benchmarks directory"
            logging.warning(msg)
            pretty_error(msg, config.ui)

        benchmarks = [cls.get(uid) for uid in uids]

        return benchmarks

    @classmethod
    def get(cls, benchmark_uid: str, force_update: bool = False) -> "Benchmark":
        """Retrieves and creates a Benchmark instance from the server.
        If benchmark already exists in the platform then retrieve that
        version.

        Args:
            benchmark_uid (str): UID of the benchmark.
            comms (Comms): Instance of a communication interface.
            force_update (bool): Wether to download the benchmark regardless of cache. Defaults to False

        Returns:
            Benchmark: a Benchmark instance with the retrieved data.
        """
        comms = config.comms
        # Get local benchmarks
        bmk_storage = storage_path(config.benchmarks_storage)
        local_bmks = os.listdir(bmk_storage)
        if str(benchmark_uid) in local_bmks and not force_update:
            benchmark_dict = cls.__get_local_dict(benchmark_uid)
        else:
            # Download benchmark
            benchmark_dict = comms.get_benchmark(benchmark_uid)
            ref_model = benchmark_dict["reference_model_mlcube"]
            add_models = cls.get_models_uids(benchmark_uid, comms)
            benchmark_dict["models"] = [ref_model] + add_models
        benchmark_dict["uid"] = benchmark_uid
        benchmark = cls(benchmark_dict)
        benchmark.write()
        return benchmark

    @classmethod
    def __get_local_dict(cls, benchmark_uid: str) -> dict:
        """Retrieves a local benchmark information

        Args:
            benchmark_uid (str): uid of the local benchmark

        Returns:
            dict: information of the benchmark
        """
        logging.info(f"Retrieving benchmark {benchmark_uid} from local storage")
        storage = storage_path(config.benchmarks_storage)
        bmk_storage = os.path.join(storage, str(benchmark_uid))
        bmk_file = os.path.join(bmk_storage, config.benchmarks_filename)
        with open(bmk_file, "r") as f:
            data = yaml.safe_load(f)

        return data

    @classmethod
    def tmp(
        cls,
        data_preparator: str,
        model: str,
        evaluator: str,
        demo_url: str = None,
        demo_hash: str = None,
    ) -> "Benchmark":
        """Creates a temporary instance of the benchmark

        Args:
            data_preparator (str): UID of the data preparator cube to use.
            model (str): UID of the model cube to use.
            evaluator (str): UID of the evaluator cube to use.
            demo_url (str, optional): URL to obtain the demo dataset. Defaults to None.
            demo_hash (str, optional): Hash of the demo dataset tarball file. Defaults to None.

        Returns:
            Benchmark: a benchmark instance
        """
        benchmark_uid = f"{config.tmp_prefix}{data_preparator}_{model}_{evaluator}"
        benchmark_dict = {
            "uid": benchmark_uid,
            "name": benchmark_uid,
            "data_preparation_mlcube": data_preparator,
            "reference_model_mlcube": model,
            "data_evaluator_mlcube": evaluator,
            "demo_dataset_tarball_url": demo_url,
            "demo_dataset_tarball_hash": demo_hash,
            "models": [model],
        }
        benchmark = cls(benchmark_dict)
        benchmark.write()
        return benchmark

    @classmethod
    def get_models_uids(cls, benchmark_uid: str, comms: Comms) -> List[str]:
        """Retrieves the list of models associated to the benchmark

        Args:
            benchmark_uid (str): UID of the benchmark.
            comms (Comms): Instance of the communications interface.

        Returns:
            List[str]: List of mlcube uids
        """
        return comms.get_benchmark_models(benchmark_uid)

    def todict(self) -> dict:
        """Dictionary representation of the benchmark instance

        Returns:
        dict: Dictionary containing benchmark information
        """
        return {
            "uid": self.uid,
            "name": self.name,
            "description": self.description,
            "docs_url": self.docs_url,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "owner": self.owner,
            "demo_dataset_tarball_url": self.demo_dataset_url,
            "demo_dataset_tarball_hash": self.demo_dataset_hash,
            "demo_dataset_generated_uid": self.demo_dataset_generated_uid,
            "data_preparation_mlcube": int(self.data_preparation),
            "reference_model_mlcube": int(self.reference_model),
            "models": self.models,
            "data_evaluator_mlcube": int(self.evaluator),
            "state": self.state,
            "is_valid": self.is_valid,
            "approval_status": self.approval_status,
            "metadata": self.metadata,
        }

    def write(self, filename: str = config.benchmarks_filename) -> str:
        """Writes the benchmark into disk

        Args:
            filename (str, optional): name of the file. Defaults to config.benchmarks_filename.

        Returns:
            str: path to the created benchmark file
        """
        data = self.todict()
        storage = storage_path(config.benchmarks_storage)
        bmk_path = os.path.join(storage, str(self.uid))
        if not os.path.exists(bmk_path):
            os.makedirs(bmk_path, exist_ok=True)
        filepath = os.path.join(bmk_path, filename)
        with open(filepath, "w") as f:
            yaml.dump(data, f)
        return filepath

    def upload(self, comms: Comms):
        """Uploads a benchmark to the server

        Args:
            comms (Comms): communications entity to submit through
        """
        body = self.todict()
        comms.upload_benchmark(body)
