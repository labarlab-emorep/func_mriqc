"""MRIQC workflows.

wf_mriqc_subj : conduct MRIQC for single subject and session
wf_mriqc_group : conduct MRIQC for group

"""

import os
from func_mriqc import process


def wf_mriqc_subj(
    sing_mriqc,
    work_deriv,
    work_mriqc,
    log_dir,
    proj_research,
    proj_raw,
    proj_mriqc,
    subj,
    sess,
    fd_thresh,
):
    """Run MRIQC workflow for single subejct and session.

    Pull required data from Keoki, executed MRIQC, and then
    push output back to Keoki.

    Parameters
    ----------
    sing_mriqc : str, os.PathLike
        Location of MRIQC singularity image
    work_deriv : str, os.PathLike
        Location of work derivatives (required for binding)
    work_mriqc : str, os.PathLike
        Location of work derivatives/mriqc
    log_dir : str, os.PathLike
        Location of work log directory
    proj_research : str, os.PathLike
        Location of group research bin, contains simg file
        e.g. /hpc/group/labarlab/research_bin
    proj_raw : str, os.PathLike
        Location of project rawdir
    proj_mriqc : str, os.PathLike
        Location of project derivatives/mriqc
    subj : str
        BIDS subject identifier
    sess : str
        BIDS session identifier
    fd_thresh : float
        Framewise displacement value

    """
    # Get data
    push_pull = process.PushPull(subj, sess)
    push_pull.pull_data()

    # Run MRIQC
    mriqc_done = process.mriqc_subj(
        sing_mriqc,
        work_deriv,
        work_mriqc,
        log_dir,
        proj_research,
        proj_raw,
        proj_mriqc,
        subj,
        sess,
        fd_thresh,
    )

    # Send data and clean up
    clean_data = process.CleanDcc(subj, proj_mriqc)
    if mriqc_done:
        clean_data.clean_work(work_mriqc)
    push_pull.push_data(os.path.join(proj_mriqc, f"{subj}*"))
    clean_data.clean_group(proj_raw)


def wf_mriqc_group(proj_raw, proj_mriqc):
    """Trigger group-level MRIQC.

    Parameters
    ----------
    proj_raw : str, os.PathLike
        Location of project rawdir
    proj_mriqc : str, os.PathLike
        Location of project derivatives/mriqc

    """
    process.mriqc_group(proj_raw, proj_mriqc)
