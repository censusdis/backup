# censusdis/backup

This project is a command-line utility for bulk downloads of 
U.S. Census data.

## Installation

```shell
pip install census_backup
```

## Usage Examples

### Download from a group across all available bulk geographies

This is the simplest way to use this tool. It will look for all
available geographies for the given dataset and vintage, then
download all variables in the specified group for every geography
it can.

```shell
census-backup -d acs/acs5 -v 2020 -g B02001 -o ~/tmp/backup
```

The required arguments are:

- `-d`: the data set
- `-v`: the vintage
- `-g`: the variable group

The `-o` is an optional output directory. The default is the current working
directory.

### Download geometries that have `state` as a component

Sometimes we really only care about a specific set of geography
levels. This example will download at the [state], [state, county],
[state, county, tract] etc... levels.

```shell
census-backup -d acs/acs5 -v 2020 -g B02001 -G state -o ~/tmp/backup-states-and-below
```

### Download state aggregated data only

This will not get geographies within the state. It will only get data
aggregate at the state level.

```shell
census-backup -d acs/acs5 -v 2020 -g B02001 -G +state -o ~/tmp/backup-states
```

## More Help

```shell
census-backup --help
```