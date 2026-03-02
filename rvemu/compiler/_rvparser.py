from . import _rvparser_handler as rvp


def parse(input_file: str, output_file: str) -> None:
    rvp.parse(input_file, output_file)
