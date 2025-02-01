"""Main entry point for backup."""

import sys
from typing import Iterable
from logging import getLogger

from pathlib import Path

from datetime import datetime

import json

from logargparser import LoggingArgumentParser
from argparse import BooleanOptionalAction

import pandas as pd

import censusdis.data as ced
from censusdis.states import ALL_STATES_DC_AND_PR
from censusdis import CensusApiException

import census_backup


logger = getLogger(__name__)


dry_run = False


def _write(df: pd.DataFrame | None, path: Path, file_name: str):
    if df is None:
        logger.info("Not writing df because it was not loaded.")
    else:
        if not dry_run:
            path.mkdir(exist_ok=True, parents=True)

        file = path / file_name

        if dry_run:
            logger.info(f"Dry run: not writing ouput: {file}")
        else:
            logger.info(f"Writing ouput: {file}")
            df.to_csv(file)


def _download(
    dataset: str, vintage: int, group: str, ignore_errors: bool = True, **kwargs
) -> pd.DataFrame:
    if dry_run:
        return pd.DataFrame()

    if ignore_errors:
        try:
            df = ced.download(dataset, vintage, ["NAME"], group=group, **kwargs)
        except CensusApiException as e:
            logger.warning(f"Ignoring error {e}")
            return None
    else:
        df = ced.download(dataset, vintage, ["NAME"], group=group, **kwargs)

    return df


def do_backup(
    dataset: str,
    vintage: int,
    group: str,
    geographies: Iterable[str] | None,
    exclude_geographies: Iterable[str] | None,
    output_dir: Path,
    api_key: str | None,
):
    """Do the backup."""
    if geographies is None:
        geographies = []

    if exclude_geographies is None:
        exclude_geographies = []

    end_geos = [geo for geo in geographies if geo.startswith("+")]
    if end_geos:
        end_geo = end_geos[0][1:]
        if len(end_geos) > 1:
            logger.warning(f"Multiple end geographies {end_geos}. Choosing {end_geo}")
        logger.info(f"Geography must end in {end_geo}")
    else:
        end_geo = None

    geos = [geo for geo in geographies if geo not in end_geos]

    if geos:
        logger.info(f"Geography must contain: {geos}")

    for geo in ced.geographies(dataset, vintage):
        skip = not all(g in geo for g in geos)
        if skip:
            logger.info(f"Skipping {geo} due to mismatch with {geos}.")
            continue
        skip = geo[-1] != end_geo
        if skip:
            logger.info(f"Skipping {geo} due to mismatch with {end_geo}.")
            continue
        excluded = [g for g in exclude_geographies if g in geo]
        if excluded:
            logger.info(f"Skipping {geo} due to excluded components {excluded}")
            continue

        logger.info(f"Geography: {geo}")
        geo_kwargs = {level: "*" for level in geo}

        if "state" in geo and len(geo) > 1:
            for state in ALL_STATES_DC_AND_PR:
                geo_kwargs["state"] = state

                if "county" in geo and len(geo) > 2:
                    df_counties = ced.download(
                        dataset, vintage, ["NAME"], state=state, county="*"
                    )
                    counties = [county for county in df_counties["COUNTY"]]

                    geo_kwargs["county"] = counties

                    df = _download(dataset, vintage, group=group, **geo_kwargs)

                    path = output_dir / f"state={state}" / "county"
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
    prog = "census-backup"

    meta_data = {
        "census-backup-version": census_backup.version,
        "start-time": datetime.now().isoformat(),
        "args": [prog] + [arg for arg in sys.argv[1:]],
    }

    parser = LoggingArgumentParser(logger, prog=prog)

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
        "-G",
        "--geography",
        type=str,
        nargs="*",
        help="""Geography filters. Only download geographies containing these keys.
For example, `-G county` will only download geographies that have county among their
components, like [state, county, tract] and [state, county]. If a + is prepended
then the geography must end in the components, so `-G +county` will only match
[state, county], not [state, county, tract]. Multiple values can be passed, like
`-G state county` or `-G state +county`. See also -X.
""",
    )

    parser.add_argument(
        "-X",
        "--exclude-geography",
        type=str,
        nargs="*",
        help="Skip any geography containing this component or components.",
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

    parser.add_argument(
        "--ignore-errors",
        action=BooleanOptionalAction,
        default=True,
        help="Ignore download errors and just continue on.",
    )

    parser.add_argument(
        "--overwrite-ok",
        action="store_true",
        help="OK to overwrite non-empty directory.",
    )

    args = parser.parse_args()

    global dry_run
    dry_run = args.dry_run

    if args.output is not None:
        output_dir = Path(args.output)

        if not dry_run:
            if not output_dir.exists():
                if not dry_run:
                    output_dir.mkdir(parents=True)
            elif not output_dir.is_dir():
                logger.error(
                    f"Ouput directory {args.output} exists but is not a directory."
                )
                sys.exit(1)
            if not args.overwrite_ok and any(output_dir.iterdir()):
                logger.error(f"Ouput directory {args.output} is not empty.")
                sys.exit(2)
    else:
        output_dir = Path.cwd()

    dataset = args.dataset
    vintage = args.vintage
    group = args.group
    geographies = args.geography
    exclude_geographies = args.exclude_geography

    logger.info(f"Backing up {group} {dataset} {vintage} into {output_dir}.")

    api_key = args.api_key

    do_backup(
        dataset, vintage, group, geographies, exclude_geographies, output_dir, api_key
    )

    meta_data["end-time"] = datetime.now().isoformat()

    if not dry_run:
        with open(output_dir / "metadata.json", "w") as meta_data_file:
            json.dump(meta_data, meta_data_file, indent=2)


if __name__ == "__main__":
    main()
