"""A command-line tool to convert a print job to PDF using Ghostscript/GhostPCL"""
__version__ = "0.1.0"

import sys
from enum import Enum, unique, auto
from typing import Type, BinaryIO

import click


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


# noinspection PyUnusedLocal
def do_self_test(ctx, param, value):  # pylint: disable=unused-argument
    """Verifies that the program is able to run."""
    if value is True:
        click.echo("ran OK")
        sys.exit(0)


@click.command()
@click.version_option(version=__version__)
@click.option('--self-test', is_flag=True, is_eager=True, callback=do_self_test, help="Do nothing and exit with exit code 0.")
@click.option('--job-language', type=ClickChoiceEnum(JobLanguage, case_sensitive=False), required=True, help="Print job language.")
@click.argument('input_fn', metavar="INPUT", type=click.Path(exists=True, dir_okay=False, resolve_path=True, allow_dash=True))
@click.argument('output_f', metavar="OUTPUT", type=click.File('wb'))
def pdl2pdf(self_test: bool, job_language: JobLanguage, input_fn: str, output_f: BinaryIO):
    """Make a PDF file called <OUTPUT> out of print job file <INPUT>."""
    assert not self_test
    click.echo(f"Using job language {job_language}, convert from {input_fn} to {output_f.name}")


if __name__ == "__main__":
    pdl2pdf()  # parameters supplied by click -- pylint: disable=no-value-for-parameter
