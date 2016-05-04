# -*- coding: utf-8 -*-
import sys
from utils import lain_yaml_data
from lain_sdk.util import error, info, warn
from lain_sdk.yaml.validator import validate as sdk_validate


def _validate():
    yaml_source_data = lain_yaml_data()
    return sdk_validate(yaml_source_data)


def validate_only_warning():
    valid, _ = _validate()
    if not valid:
        error('##############################')
        error('#  maybe invalid lain.yaml   #')
        error('#  check the schema with     #')
        error('#    lain validate           #')
        error('##############################')
        exit(1)


def validate():
    """
    Validate lain.yaml
    """

    valid, msg = _validate()
    if valid:
        info('valid lain.yaml.')
    else:
        error('invalid lain.yaml.')
        warn('error message:')
        info(msg)
        # TODO : show related doc url
        warn('for details of lain.yaml schema please check related docs.')
        sys.exit(1)
