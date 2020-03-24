"""A command-line tool to convert a print job to PDF using Ghostscript/GhostPCL"""
__version__ = "0.1.0"

import datetime
import os.path
import subprocess
import sys
from enum import Enum, auto, unique
from pathlib import Path
from typing import Optional, Type

import click

# noinspection SpellCheckingInspection
SAFE_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_,.-=+!@$()"


def make_safe_file_name_part(user_input: str, replacement: str = "_") -> str:
    """Replace any characters unsafe for a file name"""
    result = ""
    for char in user_input:
        if char in SAFE_CHARS:
            result += char
        else:
            result += replacement
    return result


@unique
class JobLanguage(Enum):
    """The supported print job languages."""

    PCL = auto()
    PS = auto()


class ClickChoiceEnum(click.Choice):
    """Improve on click.Choice so that choices is a class inheriting from Enum
    and the parameter value becomes the enumeration member."""

    def __init__(self, enum_class: Type[Enum], case_sensitive=True):
        super().__init__([member.name for member in enum_class], case_sensitive=case_sensitive)
        self.enum_class = enum_class

    def convert(self, value, param, ctx):
        str_value = super().convert(value, param, ctx)
        return self.enum_class[str_value]


def this_exe() -> Path:
    """The full absolute resolved path to this executable file."""
    return Path(sys.executable if getattr(sys, "frozen", False) else sys.argv[0]).resolve()


def dir_with_this_exe() -> Path:
    """The full absolute resolved path to the directory containing this executable file."""
    return this_exe().parent.resolve()


def get_gpcl_exe() -> str:
    """Return full path to GhostPCL exe file"""
    return str(dir_with_this_exe() / "gpcl" / "gpcl6win64.exe")


def get_gs_exe() -> str:
    """Return full path to Ghostscript exe file"""
    return str(dir_with_this_exe() / "gs" / "bin" / "gswin64c.exe")


# noinspection PyUnusedLocal
def do_self_test(ctx, param, value):  # pylint: disable=unused-argument
    """Verifies that the program is able to run."""
    if value is True:
        click.echo("self-test started")
        subprocess.check_call([get_gpcl_exe()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.check_call([get_gs_exe(), "-h"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        click.echo("self-test OK")
        sys.exit(0)


@click.command()
@click.version_option(version=__version__)
@click.option("--self-test", is_flag=True, is_eager=True, callback=do_self_test, help="Do nothing and exit with exit code 0.")
@click.option("--job-language", type=ClickChoiceEnum(JobLanguage, case_sensitive=False), required=True, help="Print job language.")
@click.option("--title", help="Optional text to append to the output file name.")
@click.option("--timeout", metavar="S", type=click.IntRange(min=1), help="Optional time limit (in seconds) for the conversion to run.")
@click.argument("input_fn", metavar="INPUT", type=click.Path(exists=True, dir_okay=False, resolve_path=True, allow_dash=True))
@click.argument("output_dir", metavar="OUTPUT_DIR", type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
def pdl2pdf(
    self_test: bool, job_language: JobLanguage, title: Optional[str], timeout: Optional[int], input_fn: str, output_dir: str
):  # pylint: disable=too-many-arguments
    """Make a PDF file in <OUTPUT_DIR> out of print job file <INPUT>."""
    assert not self_test
    # this gives YYYYmmdd_HHMMSS_xxx where xxx means milliseconds - reasonably sure to be unique but still readable
    timestamp = datetime.datetime.now().isoformat("_", timespec="milliseconds").replace(":", "").replace("-", "").replace(".", "_")
    if title:
        output_fn = f"{timestamp}-{make_safe_file_name_part(title)}.pdf"
    else:
        output_fn = f"{timestamp}.pdf"
    full_output_fn = os.path.join(output_dir, output_fn)
    click.echo(f"Converting from {job_language} file {input_fn} to {full_output_fn}")
    if job_language == JobLanguage.PCL:
        program = get_gpcl_exe()
    elif job_language == JobLanguage.PS:
        program = get_gs_exe()
    else:
        raise RuntimeError("unknown language")
    params = [program, "-sPAPERSIZE=a4", "-sDEVICE=pdfwrite", "-o", full_output_fn, input_fn]
    subprocess.check_call(params, timeout=timeout)
    if os.path.isfile(full_output_fn):
        click.echo(f"Successfully produced {full_output_fn}")
    else:
        click.echo(f"Something went wrong; after running the converter, there is no {full_output_fn}")


if __name__ == "__main__":
    pdl2pdf()  # parameters supplied by click -- pylint: disable=no-value-for-parameter
