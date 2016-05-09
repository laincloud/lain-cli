# -*- coding: utf-8 -*-
import sys
from utils import lain_yaml_data, lain_yaml
from lain_sdk.util import error, info, warn
from lain_sdk.yaml.validator import validate as sdk_validate


def _validate():
    if _exist_same_procname_for_depends():
        return False, 'procname of the depended services and resources should be different'

    yaml_source_data = lain_yaml_data()
    return sdk_validate(yaml_source_data)


def _exist_same_procname_for_depends():
    yml = lain_yaml(ignore_prepare=True)

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


def validate_only_warning():
    valid, _ = _validate()
    if not valid:
        error('##############################')
        error('#  maybe invalid lain.yaml   #')
        error('#  check the schema with     #')
        error('#    lain validate           #')
        error('##############################')


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
