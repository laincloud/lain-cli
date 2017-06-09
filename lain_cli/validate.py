# -*- coding: utf-8 -*-
import sys
from argh.decorators import arg

from utils import lain_yaml_data, lain_yaml, LAIN_YAML_PATH
from lain_sdk.util import error, info, warn
from lain_sdk.yaml.validator import validate as sdk_validate


def _validate(config):
    if _exist_same_procname_for_depends(config):
        return False, 'procname of the depended services and resources should be different'

    yaml_source_data = lain_yaml_data(config)
    return sdk_validate(yaml_source_data)


def _exist_same_procname_for_depends(config):
    yml = lain_yaml(config, ignore_prepare=True)

    service_procs, resource_procs = [], []
    if hasattr(yml, 'use_services'):
        use_services = yml.use_services
        for _, service_list in use_services.iteritems():
            for service in service_list:
                service_procs.append(service)

    if hasattr(yml, 'use_resources'):
        use_resources = yml.use_resources
        for _, resource_props in use_resources.iteritems():
            for resouce_service_proc_name in resource_props['services']:
                resource_procs.append(resouce_service_proc_name)

    commons = set(service_procs) | set(resource_procs)
    return len(commons) < len(service_procs) + len(resource_procs)


def validate_only_warning(config):
    valid, _ = _validate(config)
    if not valid:
        error('##############################')
        error('#  maybe invalid %s          #' % config)
        error('#  check the schema with     #')
        error('#    lain validate           #')
        error('##############################')


@arg('--config',  help="the configuration file path")
def validate(config=LAIN_YAML_PATH):
    """
    Validate config
    """

    valid, msg = _validate(config)
    if valid:
        info('valid %s.' % config)
    else:
        error('invalid %s.' % config)
        warn('error message:')
        info(msg)
        # TODO : show related doc url
        warn('for details of lain.yaml schema please check related docs.')
        sys.exit(1)
