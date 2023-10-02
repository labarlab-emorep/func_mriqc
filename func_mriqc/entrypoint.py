"""Print entrypoint help."""
import func_mriqc._version as ver


def main():
    print(
        f"""

    Version : {ver.__version__}

    This package conducts MRIQC for subject- and group-level MRI
    datasets. Trigger helps and usages with the following entrypoints:

        mriqc_subj    : conduct subject-level MRIQC
        mriqc_group   : conduct group-level MRIQC

    """
    )
    pass


if __name__ == "__main__":
    main()
