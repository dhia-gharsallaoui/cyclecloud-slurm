from slurmcc import azslurmd
from slurmcc import util as slutil
from slurmcc.allocation import EXTERNAL_NODE_FEATURE
from slurmcc_test import testutil
from slurmcc_test.azslurmd_test import MockNodeSource


def _setup() -> testutil.MockClusterBinding:
    testutil.make_native_cli(False)
    slutil.SLURM_CLI.create_nodes(["onprem-1"], features=[EXTERNAL_NODE_FEATURE])
    slutil.SLURM_CLI.create_nodes(["onprem-2"], features=[])
    slutil.SLURM_CLI.slurm_nodes["onprem-1"]["NodeAddr"] = "10.102.64.10"
    slutil.SLURM_CLI.slurm_nodes["onprem-2"]["NodeAddr"] = "10.102.64.11"
    return testutil.make_test_node_manager().cluster_bindings


def test_external_node_is_left_alone() -> None:
    bindings = _setup()
    azslurmd.AzslurmDaemon(MockNodeSource(bindings)).run_once()

    node = slutil.SLURM_CLI.slurm_nodes["onprem-1"]
    assert node["State"] == "idle"
    assert node["Reason"] == ""
    assert node["NodeAddr"] == "10.102.64.10"


def test_node_without_the_feature_is_still_marked_missing() -> None:
    bindings = _setup()
    azslurmd.AzslurmDaemon(MockNodeSource(bindings)).run_once()

    node = slutil.SLURM_CLI.slurm_nodes["onprem-2"]
    assert node["State"] == "down"
    assert node["Reason"] == "cyclecloud_no_node"
    assert node["NodeAddr"] == "onprem-2"
