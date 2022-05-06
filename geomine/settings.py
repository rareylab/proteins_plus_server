"""Specific settings of the GeoMine app"""
import os


class GeoMineSettings:  # pylint: disable=too-few-public-methods
    """Holds all app specific settings

    TODO: If there are multiple tools accessing different databases
    merge geomine credentials with proteinsplus user credentials to
    only have one set of credentals for the postgres db cluster.

    Hostname is a text variable so read the value from the environment.
    Password and username are given to the geomine executable as
    environment variables and are parsed in the binary as a security
    feature."""
    GEOMINE_HOSTNAME = os.environ['GEOMINE_HOSTNAME'] if 'GEOMINE_HOSTNAME' in os.environ \
                                                      else ''
    GEOMINE_PGUSER_ENV_VAR = 'GEOMINE_PGUSER'
    GEOMINE_PGPASSWORD_ENV_VAR = 'GEOMINE_PGPASSWORD'

    # Database name is usually 'geominedb', if you want to change that set the environment
    # variable GEOMINE_DB_NAME
    GEOMINE_DB_NAME = os.environ['GEOMINE_DB_NAME'] if 'GEOMINE_DB_NAME' in os.environ \
                                                    else 'geominedb'
