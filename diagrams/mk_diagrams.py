# %%
from diagrams import Cluster, Diagram, Edge

# %%
from diagrams.aws.compute import Compute, Batch
from diagrams.aws.database import Database
from diagrams.aws.devtools import CommandLineInterface
from diagrams.aws.general import General
from diagrams.digitalocean.compute import Docker


# %%
with Diagram("imports", direction="TB", show=False):
    with Cluster("cli"):
        mrig = General("mriqc_group")
        mris = General("mriqc_subj")

    wf = General("workflows")
    pro = General("process")
    sub = General("submit")

    mrig << wf
    mris << sub
    wf << pro
    pro << sub


# %%
graph_attr = {
    "layout": "dot",
    "compound": "true",
}

with Diagram("process", graph_attr=graph_attr, show=True):
    with Cluster("cli"):
        mrig = CommandLineInterface("mriqc_group")
        mris = CommandLineInterface("mriqc_subj")

    with Cluster("workflows"):
        wf_group = Compute("wf_mriqc_group")

    with Cluster("process"):
        proc_mrig = Compute("mriqc_group")
        sing_mriqc = Docker("MRIQC")

    with Cluster("resources.submit"):
        sched_subj = Batch("schedule_subj")

    with Cluster("sbatch"):
        with Cluster("workflows"):
            run_mriqc = Compute("wf_mriqc_subj")
        with Cluster("process"):
            with Cluster("PushPull"):
                pull = Database("pull_data")
                push = Database("push_data")
            proc_mris = Compute("mriqc_subj")

    with Cluster("sbatch_child"):
        dock_mriqc = Docker("MRIQC")

    mrig >> wf_group >> proc_mrig >> sing_mriqc
    mris >> sched_subj >> Edge(lhead="cluster_sbatch") >> run_mriqc
    run_mriqc >> pull >> proc_mris >> push
    proc_mris >> Edge(lhead="cluster_sbatch_child") >> dock_mriqc


# %%
