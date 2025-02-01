"""Main entry point for backup."""

from logging import getLogger

from pathlib import Path

from logargparser import LoggingArgumentParser

import pandas as pd

import censusdis.data as ced
from censusdis.states import ALL_STATES_DC_AND_PR


logger = getLogger(__name__)


dry_run = False


def _write(df: pd.DataFrame, path: Path, file_name: str):
    if not dry_run:
        path.mkdir(exist_ok=True, parents=True)

    file = path / file_name

    if dry_run:
        logger.info(f"Dry run: not writing ouput: {file}")
    else:
        logger.info(f"Writing ouput: {file}")
        df.to_csv(file)


def _download(dataset: str, vintage: int, group: str, **kwargs) -> pd.DataFrame:
    if dry_run:
        return pd.DataFrame()

    df = ced.download(dataset, vintage, group=group, **kwargs)

    return df


def do_backup(
    dataset: str, vintage: int, group: str, output_dir: Path, api_key: str | None
):
    """Do the backup."""
    for geo in ced.geographies(dataset, vintage):
        logger.info(f"Geography: {geo}")
        geo_kwargs = {level: "*" for level in geo}

        if "state" in geo and len(geo) > 1:
            for state in ALL_STATES_DC_AND_PR:
                geo_kwargs["state"] = state

                if "county" in geo and len(geo) > 2:
                    df_counties = ced.download(
                        dataset, vintage, ["NAME"], state=state, county="*"
                    )
                    for county in df_counties["COUNTY"]:
                        geo_kwargs["county"] = county

                        df = _download(dataset, vintage, group=group, **geo_kwargs)

                        path = output_dir / f"state={state}" / f"county={county}"
                        for level in geo[:-1]:
                            if level not in ["state", "county"]:
                                path = path / level
                        _write(df, path, f"{geo[-1]}.csv")
                else:
                    df = _download(dataset, vintage, group=group, **geo_kwargs)

                    path = output_dir / f"state={state}"
                    for level in geo[:-1]:
                        if level != "state":
                            path = path / level
                    _write(df, path, f"{geo[-1]}.csv")
        else:
            path = output_dir
            for level in geo[:-1]:
                path = path / level
            df = _download(dataset, vintage, group=group, **geo_kwargs)

            _write(df, path, f"{geo[-1]}.csv")


def main():
    """Entry point for backup."""
    parser = LoggingArgumentParser(logger, prog="backup")

    parser.add_argument(
        "-d", "--dataset", type=str, required=True, help="The data set."
    )

    parser.add_argument("-v", "--vintage", type=int, required=True, help="The vintage.")

    parser.add_argument(
        "-g", "--group", type=str, required=True, help="The group of variables."
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output directory under which to store the backups.",
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="Optional API key. Alternatively, store your key in "
        "~/.censusdis/api_key.txt. It you don't have a key, you "
        "may get throttled or blocked. Get one from "
        "https://api.census.gov/data/key_signup.html",
    )

    parser.add_argument("--dry-run", action="store_true", help="Dry run only.")

    args = parser.parse_args()

    global dry_run
    dry_run = args.dry_run

    if args.output is not None:
        output_dir = Path(args.output)

        if not output_dir.exists():
            if not dry_run:
                output_dir.mkdir(parents=True)
        elif not output_dir.is_dir():
            logger.error(
                f"Ouput directory {args.output} exists but is not a directory."
            )
    else:
        output_dir = Path.cwd()

    dataset = args.dataset
    vintage = args.vintage
    group = args.group

    logger.info(f"Backing up {group} {dataset} {vintage} into {output_dir}.")

    api_key = args.api_key

    do_backup(dataset, vintage, group, output_dir, api_key)


if __name__ == "__main__":
    main()
