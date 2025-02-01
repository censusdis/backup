# censusdis/backup

This project is a command-line utility for bulk downloads of 
U.S. Census data.

## Installation

```shell
pip install census_backup
```

## Usage Examples

### General help and overview

```shell
census-backup --help
```

### Download from a group across all available bulk geographies

This is the simplest way to use this tool. It will look for all
available geographies for the given dataset and vintage, then
download all variables in the specified group for every geography
it can.

```shell
census-backup -d acs/acs5 -v 2020 -g B02001 -o ~/tmp/backup  --log INFO
```

The required arguments are:

- `-d`: the data set
- `-v`: the vintage
- `-g`: the variable group

The option arguments are:

- `-o`: output directory. The default is the current working directory.
- `--log`: logging level. `INFO` is useful to see what is happening.

Logging will also help you see what geographies the script was not able
to download in bulk. The census API syntax does not allow all the bulk
downloads one might like to do.

Running this command takes about 20 minutes. It will vary depending on
the speed of your internet connection and the load on the census servers.

#### Data Files

When the command completes, you will find a whole tree full of files under the
output root `~/tmp/backup` that you chose. It will look something like
this:

```
├── american_indian_area_alaska_native_area_hawaiian_home_land.csv
├── american_indian_area_alaska_native_area_reservation_or_statistical_entity_only.csv
├── american_indian_area_off_reservation_trust_land_only_hawaiian_home_land.csv
├── combined_new_england_city_and_town_area
│   └── state_or_part.csv
├── combined_new_england_city_and_town_area.csv
├── combined_statistical_area.csv
├── division.csv
├── metadata.json
├── metropolitan_statistical_area_micropolitan_statistical_area.csv
├── new_england_city_and_town_area.csv
├── region.csv
├── state.csv
├── state=01
│   ├── american_indian_area_alaska_native_area_hawaiian_home_land_or_part.csv
│   ├── american_indian_area_alaska_native_area_reservation_or_statistical_entity_only_or_part.csv
│   ├── american_indian_area_off_reservation_trust_land_only_hawaiian_home_land_or_part.csv
│   ├── combined_statistical_area_or_part.csv
│   ├── congressional_district.csv
│   ├── county
│   │   ├── county_subdivision.csv
│   │   ├── tract
│   │   │   └── block_group.csv
│   │   └── tract.csv
│   ├── county.csv
│   ├── metropolitan_statistical_area_micropolitan_statistical_area_or_part.csv
│   ├── place.csv
│   ├── public_use_microdata_area.csv
│   ├── school_district_unified.csv
│   ├── state_legislative_district_lower_chamber.csv
│   └── state_legislative_district_upper_chamber.csv
├── state=02
│   ├── alaska_native_regional_corporation.csv
│   ├── american_indian_area_alaska_native_area_hawaiian_home_land_or_part.csv
│   ├── american_indian_area_alaska_native_area_reservation_or_statistical_entity_only_or_part.csv
│   ├── congressional_district.csv
│   ├── county
│   │   ├── county_subdivision.csv
```

At the top level files like `division.csv` and `region.csv` aggregate data
at those levels. If we look inside we will see that the first few columns look
something like this:

![Division-level data in spreadsheet form.](./images/division.png)

This is the data we downloaded at the divsion level. There is one row per
division and one column per variable. The variables include annotations and
margins of error. These are not always populated and not everyone looks at them,
but we include them because this is a backup file.

Notice also that there are some nested files below each state, which
aggregate the data at different geographic levels. For example, the file
`~/tmp/backup/state=01/county/tract.csv` has data at the census tract level
for the state of Alabama (FIPS code 01). If we look in that file, we see

![Alabama track data in spreadsheet form.](./images/alabama-tracts.png)

It has the same columns and the other file we looked at, but the rows are
aggregated at a much finer level of geography.

#### Metadata

In order to learn more about what the columns represent, we can look in the
file `~/tmp/backup/metadata.json`. This has a lot of metadata about the run,
how it was invoked, what the variables are, and how long it took. It is good
for future reference so we have a record of exactly when and how the data
was backed up from the census servers.

The relevant part of the metadata file for the variables looks like:

```json
  "dataset": "acs/acs5",
  "group": "B02001",
  "vintage": 2020,
  "vatiables": [
    {
      "YEAR": 2020,
      "DATASET": "acs/acs5",
      "GROUP": "B02001",
      "VARIABLE": "B02001_001E",
      "LABEL": "Estimate!!Total:",
      "SUGGESTED_WEIGHT": NaN,
      "VALUES": null
    },
    {
      "YEAR": 2020,
      "DATASET": "acs/acs5",
      "GROUP": "B02001",
      "VARIABLE": "B02001_001EA",
      "LABEL": "Annotation of Estimate!!Total:",
      "SUGGESTED_WEIGHT": NaN,
      "VALUES": null
    },
    {
      "YEAR": 2020,
      "DATASET": "acs/acs5",
      "GROUP": "B02001",
      "VARIABLE": "B02001_001M",
      "LABEL": "Margin of Error!!Total:",
      "SUGGESTED_WEIGHT": NaN,
      "VALUES": null
    },
    {
      "YEAR": 2020,
      "DATASET": "acs/acs5",
      "GROUP": "B02001",
      "VARIABLE": "B02001_001MA",
      "LABEL": "Annotation of Margin of Error!!Total:",
      "SUGGESTED_WEIGHT": NaN,
      "VALUES": null
    },
    {
      "YEAR": 2020,
      "DATASET": "acs/acs5",
      "GROUP": "B02001",
      "VARIABLE": "B02001_002E",
      "LABEL": "Estimate!!Total:!!White alone",
      "SUGGESTED_WEIGHT": NaN,
      "VALUES": null
    },
    ...
```

For each variable, we have its name, label, and other attributes.

The metadata file has other relevant information like the version of
`census-backup` that created it, the time it started and ended—that's
how we knew it took about 20 minutes—and the command-line arguments
that were used.

### Download multiple groups

Sometimes we want to download several groups of variables at once. To
do so, all we have to do is give multiple values to the `-g` argument.
For example,

```shell
census-backup -d dec/pl -v 2020 -g H1 P1 P2 P3 P4 P5 -G +block -o ~/tmp/decpl2020 --log INFO
```

This downloads six different groups from the decennial public law data set that
is used to apportion congressional districts among the states. This ends up being a lot of
columns. This command also used `-G +block` to download data at the block level,
which is the smallest level any census data sets are aggregated over. `dec/pl` is one
of the few data sets available at this fine a geography.

### Download geometries that have `state` as a component

For backup purposes, a command like the one we just saw is the
most complete way of getting as much data as possible from a given
dataset and group of variables.

But sometimes we really only care about a specific set of geography
levels. This example will download at the [state], [state, county],
[state, county, tract] etc... levels.

```shell
census-backup -d acs/acs5 -v 2020 -g B02001 -G state -o ~/tmp/backup-states-and-below  --log INFO
```

There will be fewer output data files than before, but the command will run
more quickly.

### Download state aggregated data only

This will not get geographies within the state. It will only get data
aggregate at the state level. The `+` prefix says that `state` must be
the last component of the geography, so it will not match [state, county]
like it would without the `+`.

```shell
census-backup -d acs/acs5 -v 2020 -g B02001 -G +state -o ~/tmp/backup-states  --log INFO
```

### Download county aggregated data within states only

This will not get geographies within the state. It will only get data
aggregate at the state level.

```shell
census-backup -d acs/acs5 -v 2020 -g B02001 -G state +county -o ~/tmp/backup-state-counties --log INFO
```

## Data sets and groups

Everything above assumed you were already familiar with the U.S. Census
data model and new what data set, group, and vintage you wanted. If you
are looking for what data sets are available, you can find an up-to-date
list of them in the `censusdis` repository in
[`datasets.py`](https://github.com/censusdis/censusdis/blob/main/censusdis/datasets.py).
For example, the American Community Survey (ACS) 5-year data set we used
in the examples above, is listed in that file as

```python
ACS5 = "acs/acs5"
```

Alternatively, you can consult the demo notebook
[Querying Available Data Sets.ipynb](https://github.com/censusdis/censusdis/blob/main/notebooks/Querying%20Available%20Data%20Sets.ipynb)
in the `censusdis` repo for more information about how to find
data sets and groups of variables that may be of interest to
you.

## More Help

There are additional arguments not discussed above. For a summary, please
run

```shell
census-backup --help
```

If you have additional questions, feel free to open a
[discussion](https://github.com/censusdis/backup/discussions)
in this repository. If you find a bug or have a feature
request, please open an
[issue](https://github.com/censusdis/backup/issues).
