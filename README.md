# censusdis/backup

This project is a command-line utility for bulk downloads of 
U.S. Census data.

## Installation

```shell
pip install census-backup
```

## Usage Examples

Download from a group across all available bulk geographies:

```shell
census-backup -d acs/acs5 -v 2020 -g B02001 -o ~/tmp/backup-tracts
```

The required arguments are:

- `-d`: the data set
- `-v`: the vintage
- `-g`: the variable group

The `-o` is an optional output directory. The default is the current working
directory.

## More Help

```shell
census-backup --help
```