"""Resources for conducting MRIQC.

PushPull : sync relevant files with Keoki.
mriqc_subj : trigger MRIQC for single subject
mriqc_group : trigger MRIQC group-level
CleanDcc : remove files from work, group locations

"""

import os
import glob
import subprocess
from typing import Tuple, Union
from func_mriqc import submit


def _bash_subprocess(bash_cmd: str) -> Tuple:
    """Submit BASH CMD as subprocess, retour stdout/err."""
    h_sp = subprocess.Popen(bash_cmd, shell=True, stdout=subprocess.PIPE)
    h_out, h_err = h_sp.communicate()
    h_sp.wait()
    return (h_out, h_err)


class PushPull:
    """Get and send relevant files to Keoki.

    Methods
    -------
    pull_data()
        Download rawdata to DCC
    push_data(subj_final)
        Upload final subject directory to Keoki

    """

    def __init__(self, subj: str, sess: str):
        """Initialize."""
        try:
            self._rsa_key = os.environ["RSA_LS2"]
        except KeyError as e:
            raise Exception(
                "No global variable 'RSA_LS2' defined in user env"
            ) from e
        self._subj = subj
        self._sess = sess
        self._dcc_path = (
            "/hpc/group/labarlab/EmoRep/Exp2_Compute_Emotion/"
            + "data_scanner_BIDS"
        )

        # Setup remote paths, addresses
        self._keoki_path = (
            "/mnt/keoki/experiments2/EmoRep/"
            + "Exp2_Compute_Emotion/data_scanner_BIDS"
        )
        self._keoki_addr = f"{os.environ['USER']}@ccn-labarserv2.vm.duke.edu"
        self._keoki_full = f"{self._keoki_addr}:{self._keoki_path}"

    def pull_data(self):
        """Download session rawdata from keoki."""
        src = os.path.join(
            f"{self._keoki_full}",
            "rawdata",
            self._subj,
            self._sess,
        )
        dst = os.path.join(self._dcc_path, "rawdata", self._subj)
        if not os.path.exists(dst):
            os.makedirs(dst)
        _, _ = self._submit_rsync(src, dst)

    def push_data(self, subj_final: Union[str, os.PathLike]):
        """Push data to remote destination."""
        dst = f"{self._keoki_addr}:{self._keoki_path}/derivatives/mriqc"
        self._mk_dst()
        _, _ = self._submit_rsync(subj_final, dst)

    def _mk_dst(self):
        """Make remote destination."""
        keoki_dst = os.path.join(
            self._keoki_path, "derivatives/mriqc", self._subj, self._sess
        )
        make_dst = f"""\
            ssh \
                -i {self._rsa_key} \
                {self._keoki_addr} \
                " command ; bash -c 'mkdir -p {keoki_dst}'"
            """
        _, _ = _bash_subprocess(make_dst)

    def _submit_rsync(self, src: str, dst: str) -> Tuple:
        """Execute rsync between DCC and labarserv2."""
        bash_cmd = f"""\
            rsync \
            -e "ssh -i {self._rsa_key}" \
            -rauv {src} {dst}
        """
        h_out, h_err = _bash_subprocess(bash_cmd)
        return (h_out, h_err)


def mriqc_subj(
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
    """Generate and run mriqc command.

    Conduct MRIQC for a single subject via singularity. Write the bash
    command and then submit work as a subprocess.

    Parameters
    ----------
    sing_mriqc : path
        Location of MRIQC singularity image
    work_deriv : path
        Location of work derivatives (required for binding)
    work_mriqc : path
        Location of work derivatives/mriqc
    log_dir : path
        Location of work log directory
    proj_research : path
        Location of group research bin, contains simg file
        e.g. /hpc/group/labarlab/research_bin
    proj_raw : path
        Location of project rawdir
    proj_mriqc : path
        Location of project derivatives/mriqc
    subj : str
        BIDS subject identifier
    sess : str
        BIDS session identifier
    fd_thresh : float
        Framewise displacement value

    Returns
    -------
    False, str, os.PathLike
        If mriqc output already exists in proj_mriqc
        Location of subject mriqc output in work

    """
    # Setup tmp dir
    work_mriqc_tmp = os.path.join(work_mriqc, "tmp_work", subj, sess)
    if not os.path.exists(work_mriqc_tmp):
        os.makedirs(work_mriqc_tmp)

    # Avoid repeating work
    proj_mriqc_file = os.path.join(proj_mriqc, f"{subj}_{sess}_T1w.html")
    if os.path.exists(proj_mriqc_file):
        print(f"\tOutput file already exists: {proj_mriqc_file}.")
        return False

    # Construct, schedule work
    bash_cmd = f"""
        singularity run \\
        --cleanenv \\
        --bind {work_deriv}:{work_deriv} \\
        --bind {proj_raw}:{proj_raw} \\
        --bind {proj_research}:{proj_research} \\
        --bind {proj_raw}:/data:ro \\
        --bind {work_mriqc}:/out \\
        {sing_mriqc} \\
        /data \\
        /out \\
        participant \\
        --participant_label {subj[4:]} \\
        --session-id {sess[4:]} \\
        --work {work_mriqc_tmp} \\
        --no-sub \\
        --fd_thres {fd_thresh} \\
        --nprocs 8
    """
    _, _ = submit.submit_sbatch(
        bash_cmd,
        f"{subj[7:]}s{sess[7:]}_mriqc",
        log_dir,
        num_hours=16,
        num_cpus=10,
        mem_gig=24,
    )

    # Check for output
    check_file = os.path.join(work_mriqc, f"{subj}_{sess}_T1w.html")
    if not os.path.exists(check_file):
        raise FileNotFoundError(f"Failed to find {check_file}.")
    return check_file


def mriqc_group(proj_raw, proj_mriqc):
    """Conduct group-level MRIQC via docker.

    Parameters
    ----------
    proj_raw : path
        Location of project rawdata
    proj_mriqc : path
        Location of project derivatives/mriqc

    """
    # Write docker command
    bash_cmd = f"""
        docker run --rm \\
        -v {proj_raw}:/data:ro \\
        -v {proj_mriqc}:/out \\
        nipreps/mriqc:latest \\
            /data \\
            /out \\
            group
    """

    # Run docker command as subprocess
    print(f"Running:\n{bash_cmd}")
    _, _ = _bash_subprocess(bash_cmd)

    # Check for output
    group_out = glob.glob(f"{proj_mriqc}/group*.html")
    if not group_out:
        raise FileNotFoundError(
            f"Failed to find group*.html files in {proj_mriqc}"
        )


class CleanDcc:
    """Remove files from group and work locations.

    Parameters
    ----------
    subj : str
        BIDS subject identifier
    proj_mriqc : str, os.PathLike
        Location of project derivatives/mriqc

    Methods
    -------
    clean_work(work_mriqc)
        Remove files from work location
    clean_group(proj_raw)
        Remove files from group rawdata

    """

    def __init__(self, subj, proj_mriqc):
        """Initialize."""
        self._subj = subj
        self._proj_mriqc = proj_mriqc

    def clean_work(self, work_mriqc):
        """Remove files from work location.

        Parameters
        ----------
        work_mriqc : str, os.PathLike
            Location of work derivatives/mriqc

        """
        bash_cmd = f"""
            cp -r {work_mriqc}/{self._subj}* {self._proj_mriqc}/ &&
                rm -r {work_mriqc}/{self._subj}* &&
                rm -r {work_mriqc}/tmp_work/{self._subj}
        """
        _, _ = _bash_subprocess(bash_cmd)

    def clean_group(self, proj_raw):
        """Remove files from group location.

        Paramters
        ---------
        proj_raw : str, os.PathLike
            Location of project rawdir

        """
        cl_raw = f"rm -r {proj_raw}/{self._subj}"
        cl_der = f"rm -r {self._proj_mriqc}/{self._subj}*"
        for bash_cmd in [cl_raw, cl_der]:
            _, _ = _bash_subprocess(bash_cmd)
