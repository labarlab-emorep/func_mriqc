"""Resources for scheduling work.

submit_sbatch : submit bash command to SLURM scheduler
schedule_subj : schedule subject workflow with SLURM

"""

import sys
import textwrap
import subprocess


def submit_sbatch(
    bash_cmd,
    job_name,
    log_dir,
    num_hours=1,
    num_cpus=1,
    mem_gig=1,
):
    """Schedule child SBATCH job.

    Parameters
    ----------
    bash_cmd : str
        Bash syntax, work to schedule
    job_name : str
        Name for scheduler
    log_dir : Path
        Location of output dir for writing logs
    num_hours : int
        Walltime to schedule
    num_cpus : int
        Number of CPUs required by job
    mem_gig : int
        Job RAM requirement for each CPU (GB)

    Returns
    -------
    tuple
        [0] = stdout of subprocess
        [1] = stderr of subprocess

    """
    sbatch_cmd = f"""
        sbatch \
        -J {job_name} \
        -t {num_hours}:00:00 \
        --cpus-per-task={num_cpus} \
        --mem={mem_gig}G \
        -o {log_dir}/out_{job_name}.log \
        -e {log_dir}/err_{job_name}.log \
        --wait \
        --wrap="{bash_cmd}"
    """
    print(f"Submitting SBATCH job:\n\t{sbatch_cmd}\n")
    h_sp = subprocess.Popen(sbatch_cmd, shell=True, stdout=subprocess.PIPE)
    h_out, h_err = h_sp.communicate()
    h_sp.wait()
    return (h_out, h_err)


def schedule_subj(
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
    """Schedule Parent SBATCH job.

    Write and schedule parent job which controls workflow.

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
    tuple
        [0] = stdout of sbatch submit
        [1] = stderr of sbatch submit

    Notes
    -----
    Writes parent python script to log_dir

    """
    # Write parent python script
    sbatch_cmd = f"""\
        #!/bin/env {sys.executable}

        #SBATCH --job-name=p{subj[4:]}s{sess[7:]}
        #SBATCH --output={log_dir}/par{subj[4:]}s{sess[7:]}.txt
        #SBATCH --time=10:00:00
        #SBATCH --mem=6G

        from func_mriqc import workflows


        workflows.wf_mriqc_subj(
            "{sing_mriqc}",
            "{work_deriv}",
            "{work_mriqc}",
            "{log_dir}",
            "{proj_research}",
            "{proj_raw}",
            "{proj_mriqc}",
            "{subj}",
            "{sess}",
            {fd_thresh},
        )

    """
    sbatch_cmd = textwrap.dedent(sbatch_cmd)
    py_script = f"{log_dir}/run_mriqc_{subj}_{sess}.py"
    with open(py_script, "w") as ps:
        ps.write(sbatch_cmd)

    # Execute script
    h_sp = subprocess.Popen(
        f"sbatch {py_script}",
        shell=True,
        stdout=subprocess.PIPE,
    )
    h_out, h_err = h_sp.communicate()
    print(f"{h_out.decode('utf-8')}\tfor {subj} {sess}")
    return (h_out, h_err)
