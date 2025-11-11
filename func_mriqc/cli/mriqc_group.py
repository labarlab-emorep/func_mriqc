r"""Conduct group MRIQC.

Use the output of mriqc_subj (subject-level MRIQC) to get
group-level stats.

Notes
-----
- Written to be executed on the local lab VM
- Requires the docker container nipreps/mriqc

Example
-------
mriqc_group \
    -d f"{os.environ["SERVER_BIDS_DIR"]}/derivatives/mriqc"

"""

# %%
import sys, os
import textwrap
import platform
from argparse import ArgumentParser, RawTextHelpFormatter
from func_mriqc import workflows


def _get_args():
    """Get and parse arguments."""
    parser = ArgumentParser(
        description=__doc__, formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        "--proj-raw",
        type=str,
        default=f"{os.environ["SERVER_BIDS_DIR"]}/rawdata",  # noqa: E501
        help=textwrap.dedent(
            """\
            Path to BIDS-formatted project rawdata directory
            (default : %(default)s)
            """
        ),
    )

    required_args = parser.add_argument_group("Required Arguments")
    required_args.add_argument(
        "-d",
        "--deriv-dir",
        type=str,
        help="Path to MRIQC derivatives directory",
        required=True,
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    return parser


# %%
def main():
    """Setup, run group MRIQC."""
    # Check env
    if os.environ["SERVER_NAME"] not in platform.uname().node:
        print("mriqc_group is required to run on the lab server.")
        sys.exit(1)

    # Capture CLI arguments
    args = _get_args().parse_args()
    proj_raw = args.proj_raw
    proj_mriqc = args.deriv_dir

    # Run
    workflows.wf_mriqc_group(proj_raw, proj_mriqc)


if __name__ == "__main__":
    # Require proj env
    env_found = [x for x in sys.path if "emorep" in x]
    if not env_found:
        print("\nERROR: missing required project environment 'emorep'.")
        print("\tHint: $labar_env emorep\n")
        sys.exit(1)
    main()
