r"""Conduct participant MRIQC.

Run subjects through "participant" mode of MRIQC. A single process of
MRIQC is conducted for each subject, whick coordinates data download
from Keoki, MRIQC execution, output upload to Keoki, and clean up.

Notes
-----
- Only supports single session at one time
- Written to be executed on the Duke Compute Cluster
- Requires global variables:
    - SING_MRIQC - path to singularity image of MRIQC
    - RSA_LS2 - path to RSA key for labarserv2

Example
-------
mriqc_subj \
    -s sub-ER0009 sub-ER0010 \
    -e ses-day2

"""

# %%
import os
import sys
import time
import textwrap
import platform
from datetime import datetime
from argparse import ArgumentParser, RawTextHelpFormatter
from func_mriqc import submit


def _get_args():
    """Get and parse arguments."""
    parser = ArgumentParser(
        description=__doc__, formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        "--fd-thresh",
        type=float,
        default=0.3,
        help=textwrap.dedent(
            """\
            Framewise displacement threshold
            (default : %(default)s)
            """
        ),
    )
    parser.add_argument(
        "--proj-dir",
        type=str,
        default="/hpc/group/labarlab/EmoRep/Exp2_Compute_Emotion/data_scanner_BIDS",  # noqa: E501
        help=textwrap.dedent(
            """\
            Path to BIDS-formatted project directory
            (default : %(default)s)
            """
        ),
    )
    parser.add_argument(
        "--proj-research",
        type=str,
        default="/hpc/group/labarlab/research_bin",
        help=textwrap.dedent(
            """\
            Path to parent directory of mriqc.simg location
            (default : %(default)s)
            """
        ),
    )

    required_args = parser.add_argument_group("Required Arguments")
    required_args.add_argument(
        "-s",
        "--sub-list",
        nargs="+",
        help="List of subject IDs to submit for MRIQC",
        type=str,
        required=True,
    )
    required_args.add_argument(
        "-e",
        "--sess",
        choices=["ses-day2", "ses-day3"],
        help="BIDS session ID",
        type=str,
        required=True,
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    return parser


# %%
def main():
    """Setup and coordinate resources."""
    # Check env
    if "dcc" not in platform.uname().node:
        print("mriqc_subj workflow is required to run on DCC.")
        sys.exit(1)

    # Capture CLI arguments
    args = _get_args().parse_args()
    subj_list = args.sub_list
    sess = args.sess
    proj_dir = args.proj_dir
    proj_research = args.proj_research
    fd_thresh = args.fd_thresh

    # Setup group project directory, paths
    proj_raw = os.path.join(proj_dir, "rawdata")
    proj_mriqc = os.path.join(proj_dir, "derivatives/mriqc")
    if not os.path.exists(proj_mriqc):
        os.makedirs(proj_mriqc)

    # Get environmental vars
    sing_mriqc = os.environ["SING_MRIQC"]
    user_name = os.environ["USER"]

    # Setup work directory, for intermediates
    work_deriv = os.path.join("/work", user_name, "EmoRep")
    now_time = datetime.now()
    log_dir = os.path.join(
        work_deriv, f"logs/mriqc_{now_time.strftime('%y-%m-%d_%H:%M')}"
    )
    work_mriqc = os.path.join(work_deriv, "mriqc")
    for h_dir in [log_dir, work_mriqc]:
        if not os.path.exists(h_dir):
            os.makedirs(h_dir)

    # Setup and submit jobs for subjects
    for subj in subj_list:
        subj_deriv = os.path.join(proj_mriqc, subj, sess)
        if not os.path.exists(subj_deriv):
            os.makedirs(subj_deriv)

        _, _ = submit.schedule_subj(
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
        time.sleep(3)


if __name__ == "__main__":
    # Require proj env
    env_found = [x for x in sys.path if "emorep" in x]
    if not env_found:
        print("\nERROR: missing required project environment 'emorep'.")
        print("\tHint: $labar_env emorep\n")
        sys.exit(1)
    main()
