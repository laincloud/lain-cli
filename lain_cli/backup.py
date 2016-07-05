# -*- coding: utf-8 -*-

import argparse
import requests, json
from argh.decorators import arg, aliases

from lain_sdk.util import warn
from lain_cli.utils import lain_yaml_data, check_phase
from lain_cli.utils import TwoLevelCommandBase, get_domain


class BackupCommands(TwoLevelCommandBase):

    @classmethod
    def subcommands(self):
        return [self.jobs, self.list, self.get, self.recover, self.migrate, self.records, self.run, self.delete]

    @classmethod
    def namespace(self):
        return "backup"

    @classmethod
    def help_message(self):
        return "operations for backup"

    @classmethod
    @arg('phase', help="lain cluster phase id, can be added by lain config save")
    def jobs(cls, phase):
        """
        list backup jobs for this lain app
        """
        check_phase(phase)
        appname = lain_yaml_data()['appname']
        route = "api/v2/app/%s/cron/jobs" % appname
        data = cls._request('GET', phase, route, None)
        if data:
            print json.dumps(data, indent=2)

    @classmethod
    @arg('phase', nargs=1, help="lain cluster phase id, can be added by lain config save")
    @arg('proc', nargs=1, help="proc name")
    @arg('path', nargs=1, help="the path of incremental backup, if full-backup given, will show backup's file info")
    @aliases('ls')
    def list(cls, phase, proc, path):
        """
        list files in the incremental backup direcotry
        """
        check_phase(phase[0])
        appname = lain_yaml_data()['appname']
        route = "api/v2/app/%s/proc/%s/backups/%s?open=true" % (appname, proc[0], path[0])
        data = cls._request('GET', phase[0], route, None)
        if data:
            print "%-10sFILENAME" % "SIZE"
            for item in data:
                print "%-10s%s%s" % (item['size'], item['name'], '/' if item['dir'] else '')

    @classmethod
    @arg('phase', nargs=1, help="lain cluster phase id, can be added by lain config save")
    @arg('proc', nargs=1, help="proc name")
    @arg('volume', nargs=1, help="volume defined in lain.yaml")
    def get(cls, phase, proc, volume):
        """
        get all the backups of the given proc's volume
        """
        check_phase(phase[0])
        appname = lain_yaml_data()['appname']
        route = "api/v2/app/%s/proc/%s/backups?volume=%s" % (appname, proc[0], volume[0])
        data = cls._request('GET', phase[0], route, None)
        if data:
            print json.dumps(data, indent=2)

    @classmethod
    @arg('phase', nargs=1, help="lain cluster phase id, can be added by lain config save")
    @arg('proc', nargs=1, help="proc name")
    @arg('files', nargs='+', help="backup files")
    def delete(cls, phase, proc, files):
        """
        delete a backup of a proc
        """
        check_phase(phase[0])
        appname = lain_yaml_data()['appname']
        route = "api/v2/app/%s/proc/%s/backups/actions/delete" % (appname, proc[0])
        data = cls._request('POST', phase[0], route, {'files': files})
        if data:
            print data

    @classmethod
    @arg('phase', nargs=1, help="lain cluster phase id, can be added by lain config save")
    @arg('proc', nargs=1, help="proc name")
    @arg('backup', nargs=1, help="backup file")
    @arg('files', nargs=argparse.REMAINDER, help="files in incremental backup directory, if this is given, backup must be a incremental backup")
    def recover(cls, phase, proc, backup, files):
        """
        recover the volume from given backup
        """
        check_phase(phase[0])
        appname = lain_yaml_data()['appname']
        if not files:
            route = "api/v2/app/%s/proc/%s/backups/%s/actions/recover" % (appname, proc[0], backup[0])
            data = cls._request('POST', phase[0], route, None)
        else:
            route = "api/v2/app/%s/proc/%s/backups/%s/actions/recover" % (appname, proc[0], backup[0])
            data = cls._request('POST', phase[0], route, {"files": files})
        if data:
            data

    @classmethod
    @arg('phase', nargs=1, help="lain cluster phase id, can be added by lain config save")
    @arg('proc', nargs=1, help="proc name")
    @arg('backup', nargs=1, help="backup file")
    @arg('files', nargs=argparse.REMAINDER, help="files in incremental backup directory, if this is given, backup must be a incremental backup")
    @arg('-v', '--volume', required=True, help="the volume which backup will move to", default="")
    @arg('-t', '--to', required=True, help="the instance number wish backup move to", default=0)
    def migrate(cls, phase, proc, backup, files, volume="", to=0):
        """
        recover a instance's volume from other instance's backup
        """
        check_phase(phase[0])
        appname = lain_yaml_data()['appname']
        if not files:
            route = "api/v2/app/%s/proc/%s/backups/%s/actions/migrate" % (appname, proc[0], backup[0])
            data = cls._request('POST', phase[0], route, {"volume": volume, "to": to})
        else:
            route = "api/v2/app/%s/proc/%s/backups/%s/actions/migrate" % (appname, proc[0], backup[0])
            data = cls._request('POST', phase[0], route, {"volume": volume, "to": to, "files": files})
        if data:
            data

    @classmethod
    @arg('phase', nargs=1, help="lain cluster phase id, can be added by lain config save")
    @arg('rid', nargs='?', default="", help="record id")
    @arg('-n', '--num', default=10, help="total records count, only used when rid is not given")
    def records(cls, phase, rid, num=10):
        """
        list job records of this lain app
        """
        check_phase(phase[0])
        appname = lain_yaml_data()['appname']
        route = "api/v2/app/%s/cron/records" % appname
        if rid:
            route = "%s/%s" % (route, rid)
        else:
            route += "?total=%d" % num
        data = cls._request('GET', phase[0], route, None)
        if data:
            print json.dumps(data, indent=2)

    @classmethod
    @arg('phase', nargs=1, help="lain cluster phase id, can be added by lain config save")
    @arg('id', nargs=1, help="backup job id")
    def run(cls, phase, id):
        """
        run a job right now
        """
        check_phase(phase[0])
        appname = lain_yaml_data()['appname']
        route = "api/v2/app/%s/cron/jobs/%s/actions/run" % (appname, id[0])
        data = cls._request('POST', phase[0], route, None)
        if data:
            print data

    @classmethod
    def _request(cls, method, phase, url, data):
        uri = "http://backupctl.%s/%s" % (get_domain(phase), url)

        if method.lower() == 'get':
            resp = requests.get(uri)
        elif method.lower() == 'post':
            resp = requests.post(uri, data)

        if resp.status_code >= 300:
            warn('backupctl return error: %s' % resp.text)
            return None
        if not resp.text:
            return None
        try:
            return json.loads(resp.text)
        except:
            warn("not valid json text: %s" % resp.text)
            return ""
