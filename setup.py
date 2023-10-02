from setuptools import setup, find_packages

exec(open("func_mriqc/_version.py").read())

setup(
    name="func_mriqc",
    version=__version__,  # noqa: F821
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "func_mriqc=func_mriqc.entrypoint:main",
            "mriqc_subj=func_mriqc.cli.mriqc_subj:main",
            "mriqc_group=func_mriqc.cli.mriqc_group:main",
        ]
    },
    install_requires=[
        "setuptools>=65.5.0",
    ],
)
