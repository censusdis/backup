# censusdis/backup

This project is a command-line utility for bulk downloads of 
U.S. Census data.

## Installation

```shell
pip install census_backup
```

## Usage Examples

### Download from a group across all available bulk geographies

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

```shell
census-backup -d acs/acs5 -v 2020 -g B02001 -G state -o ~/tmp/backup-states-and-below
```

### Download state aggregated data only

This will not get geographies within the state.

```shell
census-backup -d acs/acs5 -v 2020 -g B02001 -G +state -o ~/tmp/backup-states
```

## More Help

```shell
census-backup --help
```