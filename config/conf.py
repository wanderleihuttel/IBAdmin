# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from libs.conf import *
from libs.client import extractclientparams
from libs.plat import getOStype
from .conflib import *
from .confinfo import *
from ibadmin.settings import DATABASES
import os


def saveLicenseKey(key=None):
    if key is None:
        return
    dircompid = getDIRcompid()
    dirname = getDIRname()
    resid = getresourceid(dircompid, dirname, 'Director')
    license = getparameter(resid, '.IBADLicenseKey')
    if license is None:
        if key == '':
            return
        addparameter(resid, '.IBADLicenseKey', key)
    else:
        if key == '':
            deleteparameter(resid, '.IBADLicenseKey')
        updateparameterresid(resid, '.IBADLicenseKey', key)


def createBCDirector(compid, name, address, password):
    # create resource
    resid = createBCresDirector(compid, name)
    # add parameters
    addparameter(resid, 'DirPort', 9101)
    addparameter(resid, 'Address', address)
    # encrypt password
    encpass = getencpass(name, password)
    addparameterenc(resid, 'Password', encpass)


def createDIRDirector(dircompid=None, name='ibadmin', descr=''):
    # create resource
    resid = createDIRresDirector(dircompid, name, descr)
    # add parameters
    addparameter(resid, 'MaximumConcurrentJobs', 50)
    addparameterstr(resid, 'Messages', 'Daemon')
    addparameterstr(resid, 'PidDirectory', '/opt/bacula/working')
    addparameterstr(resid, 'QueryFile', '/opt/bacula/scripts/query.sql')
    addparameterstr(resid, 'WorkingDirectory', '/opt/bacula/working')
    # TODO: może wymagane będą poniższe parametry:
    # MaximumReloadRequests = <number>
    # Statistics Retention = <time>
    # VerId = <string>
    # generate password
    password = randomstr()
    encpass = getencpass(name, password)
    addparameterenc(resid, 'Password', encpass)
    # bconsole config here because we have a generated password
    bconsoleid = createBCcomponent(name)
    createBCDirector(bconsoleid, name, 'localhost', password)


def createFDDirector(fdcompid=None, dirname=None, name='ibadmin', password='ibadminpassword', descr=''):
    # create resource
    resid = createFDresDirector(fdcompid=fdcompid, dirname=dirname, descr=descr)
    # add parameters
    encpass = getencpass(name, password)
    addparameterenc(resid, 'Password', encpass)


def createSDDirector(sdcompid=None, dirname=None, name='ibadmin', password='ibadminpassword', descr=''):
    # create resource
    resid = createSDresDirector(sdcompid=sdcompid, dirname=dirname, descr=descr)
    # add parameters
    encpass = getencpass(name, password)
    addparameterenc(resid, 'Password', encpass)


def createDIRCatalog(dircompid=None, dirname=None, dbname='bacula', dbuser='bacula', dbpassword=''):
    # create resource
    resid = createDIRresCatalog(dircompid)
    # add parameters
    addparameterstr(resid, 'dbname', dbname)
    addparameterstr(resid, 'dbuser', dbuser)
    addparameterstr(resid, 'dbaddress', 'localhost')
    if dirname is None:
        dirname = getDIRname()
    encpass = getencpass(dirname, dbpassword)
    addparameterenc(resid, 'dbpassword', encpass)


def createDIRMessages(dircompid, name, email='root@localhost', log='bacula.log', descr='', fatal=True):
    # create resource
    resid = createDIRresMessages(dircompid, name, descr)
    # add parameters
    addparameterstr(resid, 'MailCommand',
                    '/opt/bacula/bin/bsmtp -h localhost -f \\"(Inteos Backup) <%r>\\" -s \\"ibad: %t %e of %n %l\\" %r')
    # addparameterstr(resid,'OperatorCommand','/opt/bacula/bin/bsmtp -h localhost -f \"(Bacula) <%r>\" -s \"IBackup:
    # Intervention needed for %j\" %r')
    if fatal:
        addparameter(resid, 'Mail', email + ' = All, !Debug, !Skipped, !Restored')
    else:
        addparameter(resid, 'Mail', email + ' = All, !Fatal, !Debug, !Skipped, !Restored')
    # addparameter(resid,'Operator','root@localhost=All,!Debug,!Skipped')
    addparameter(resid, 'Catalog', 'All')
    addparameter(resid, 'Append', "/opt/bacula/log/" + log + " = All, !Debug, !Skipped")


def createFDMessages(fdcompid=None, dirname=None):
    # create resource
    resid = createFDresMessages(fdcompid=fdcompid, name='Standard', descr='Default Messages to Director')
    # add parameters
    # wydaje się, że to może być ciekawy pomysł aby z klienta przesyłać także informacje o odtworzonych plikach
    # będzie to w logu w bazie danych oraz pliku logu, ale
    # TODO: można dodać do parametrów konfiguracyjnych opcję, czy admin chce otrzymywać tą informację mailem
    # addparameter(resid, 'Director', dirname + ' = All, !Debug, !Skipped, !Restored')
    addparameter(resid, 'Director', dirname + ' = All, !Debug, !Skipped')


def createSDMessages(sdcompid=None, dirname=None):
    # create resource
    resid = createSDresMessages(sdcompid=sdcompid, name='Standard', descr='Default Messages to Director')
    # add parameters
    addparameter(resid, 'Director', dirname + ' = All, !Debug, !Skipped, !Restored')


def createDIRClient(dircompid=None, dirname=None, name='ibadmin', password='ibadminpassword', address='localhost',
                    os='rhel', catalog='Catalog', descr='', internal=False, encpass=None, cluster=None, alias=None,
                    service=None):
    # create resource
    resid = createDIRresClient(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    addparameterstr(resid, 'Address', address)
    addparameterstr(resid, 'Catalog', catalog)
    if os == 'win32' or os == 'win64':
        maxjobs = 1
    else:
        maxjobs = 10
    addparameter(resid, 'MaximumConcurrentJobs', maxjobs)
    addparameterstr(resid, '.OS', os)
    addparameterstr(resid, 'AutoPrune', 'No')
    addparameterstr(resid, 'Enabled', 'Yes')
    if encpass is None:
        encpass = getencpass(dirname, password)
    addparameterenc(resid, 'Password', encpass)
    if internal:
        addparameterstr(resid, '.InternalClient', 'Yes')
    if cluster is not None:
        addparameterstr(resid, '.ClusterName', cluster)
    if alias is not None:
        addparameterstr(resid, '.Alias', alias)
    if service is not None:
        addparameterstr(resid, '.ClusterService', service)


def createDIRPool(dircompid=None, name='Default', disktype=False, retention=None, useduration=None, nextpool=None,
                  storage=None, descr=''):
    # create resource
    resid = createDIRresPool(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    addparameter(resid, 'PoolType', 'Backup')
    addparameter(resid, 'AutoPrune', 'No')
    addparameter(resid, 'Recycle', 'Yes')
    addparameter(resid, 'VolumeRetention', retention or '2 weeks')
    if useduration is not None:
        addparameter(resid, 'VolumeUseDuration', useduration)
    if disktype:
        addparameterstr(resid, 'LabelFormat', 'DiskVol')
        addparameter(resid, 'ActionOnPurge', 'Truncate')
    if nextpool is not None:
        addparameterstr(resid, 'NextPool', nextpool)
    if storage is not None:
        addparameterstr(resid, 'Storage', storage)


def check_or_createPool(dircompid=None, name='Default', disktype=False, retention=None, useduration=None):
    poolid = getDIRPoolid(dircompid=dircompid, name=name)
    if poolid is None:
        # Pool does not exist, create it
        createDIRPool(dircompid=dircompid, name=name, disktype=disktype, retention=retention, useduration=useduration,
                      descr='Pool for ' + retention + ' retention')


def createFSIncludeFile(resid, include):
    if include is not None:
        for f in include:
            addparameterstr(resid, 'File', f)


def createFSIncludePlugin(resid, include):
    if include is not None:
        for f in include:
            addparameterstr(resid, 'Plugin', f)


def createFSExclude(resid, exclude):
    if exclude is not None:
        for f in exclude:
            addparameterstr(resid, 'File', f)


def createDIRFileSetFile(dircompid=None, name='fs-default', vss=False, dedup=False, include=None, exclude=None, descr=''):
    # create resource
    resid = createDIRresFileSet(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    if vss:
        addparameterstr(resid, 'EnableVss', 'Yes')
    # Include {} subresource
    includeid = createDIRresFSInclude(dircompid, resid, dedup=dedup)
    createFSIncludeFile(resid=includeid, include=include)
    # Exclude {} subresource
    excludeid = createDIRresFSExclude(dircompid, resid)
    createFSExclude(excludeid, exclude)


def createDIRFileSetPlugin(dircompid=None, name='fs-default', include=None, dedup=False, descr=''):
    # create resource
    resid = createDIRresFileSet(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    # Include {} subresource
    includeid = createDIRresFSInclude(dircompid, resid, dedup=dedup)
    createFSIncludePlugin(includeid, include)


def createDIRJob(dircompid=None, name='SYS-Default', jd='jd-backup-files', descr='', client=None, pool=None,
                 storage=None, fileset=None, schedule=None, level=None, maxfullinterval=None, internal=False,
                 scheduleparam=None, scheduletime=None, scheduleweek=None, schedulemonth=None):
    # create resource
    resid = createDIRresJob(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    addparameterstr(resid, 'JobDefs', jd)
    if level is not None:
        addparameterstr(resid, 'Level', getlevelname(level))
    if client is not None:
        addparameterstr(resid, 'Client', client)
    if storage is not None:
        addparameterstr(resid, 'Storage', storage)
    if pool is not None:
        addparameterstr(resid, 'Pool', pool)
    if fileset is not None:
        addparameterstr(resid, 'FileSet', fileset)
    if schedule is not None:
        addparameterstr(resid, 'Schedule', schedule)
    if scheduleparam is not None:
        addparameter(resid, '.Scheduleparam', scheduleparam)
    if scheduletime is not None:
        addparameter(resid, '.Scheduletime', scheduletime)
    if scheduleweek is not None:
        addparameter(resid, '.Scheduleweek', scheduleweek)
    if schedulemonth is not None:
        addparameter(resid, '.Schedulemonth', schedulemonth)
    if maxfullinterval is not None:
        addparameter(resid, 'MaxFullInterval', maxfullinterval)
    if internal:
        addparameter(resid, '.InternalJob', 'Yes')
    addparameter(resid, 'Enabled', 'Yes')


def createDIRJobDefs(dircompid=None, name='jd-default', descr='', btype='Backup', fileset=None, level=None, pool=None,
                     schedule=None, storage=None, client=None, priority=10, dirjob=None, beforejob=None, afterjob=None,
                     allowduplicatejob='No', writebootstrap='/opt/bacula/bsr/%c-%n.bsr'):
    # create new JobDefs {} resource
    resid = createDIRresJobDefs(dircompid, name, descr)
    # add parameters
    addparameter(resid, 'Type', btype)
    if btype == 'Backup':
        addparameter(resid, 'Accurate', 'Yes')
    addparameter(resid, 'AllowDuplicateJobs', allowduplicatejob)
    addparameter(resid, 'CancelQueuedDuplicates', 'Yes')
    addparameter(resid, 'SpoolAttributes', 'Yes')     # TODO trzeba zastanowić się jak rozwiązać problem Tape=SpoolData
    addparameter(resid, 'Priority', priority)
    addparameterstr(resid, 'Messages', 'Standard')
    addparameterstr(resid, 'WriteBootstrap', writebootstrap)
    if level is not None:
        addparameter(resid, 'Level', level)
    if pool is not None:
        addparameterstr(resid, 'Pool', pool)
    if fileset is not None:
        addparameterstr(resid, 'Fileset', fileset)
    if schedule is not None:
        addparameterstr(resid, 'Schedule', schedule)
    if storage is not None:
        addparameterstr(resid, 'Storage',  storage)
    if client is not None:
        addparameterstr(resid, 'Client', client)
    if beforejob is not None:
        addparameterstr(resid, 'ClientRunBeforeJob', beforejob)
    if dirjob is not None:
        addparameterstr(resid, 'RunBeforeJob', dirjob)
    if afterjob is not None:
        addparameterstr(resid, 'ClientRunAfterJob', afterjob)


def createDIRJobDefsCatalog(dircompid=None, storage='ibadmin'):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-catalog', descr='Catalog Backup Defs', priority=20,
                     fileset='fs-catalog-backup', schedule='sch-backup-catalog', storage=storage,
                     beforejob='/opt/bacula/scripts/make_catalog_backup_ibadmin.pl Catalog',
                     afterjob='/opt/bacula/scripts/delete_catalog_backup_ibadmin',
                     writebootstrap='/opt/bacula/bsr/SYS-Backup-Catalog.bsr')


def createDIRJobDefsRestore(dircompid=None, client='ibadmin', storage='ibadmin'):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-restore', btype='Restore', descr='Required Restore Job',
                     fileset='fs-default', level='Full', pool='Default', storage=storage, client=client)


def createDIRJobDefsAdmin(dircompid=None, client='ibadmin', storage='ibadmin'):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-admin', btype='Admin', descr='AdminJob Defs',
                     fileset='fs-default', level='Full', pool='Default', storage=storage, client=client,
                     dirjob='/opt/bacula/scripts/SYS-Admin.sh', schedule='sch-admin')


def createDIRJobDefsFiles(dircompid=None):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-files', descr='Backup Files Defs', level='Incremental')


def createDIRSchDay(resid=None, params=None):
    if resid is None or params is None:
        return
    sch = params['level'] + ' at ' + number2time(params['time'], 0)
    addparameter(resid, 'Run', sch)


def createDIRSchHours(resid=None, params=None):
    if resid is None or params is None:
        return
    cycle = params['backuprepeat']
    if cycle == 'r24':
        # hack when createDIRSchDay was not fired directly
        return createDIRSchDay(resid, params)
    level = getlevelname(params['level'])
    times = params['time']
    if cycle == 'r1':
        # every hour
        addparameter(resid, 'Run', level + ' hourly at ' + times)
        return
    if cycle == 'r2':
        # every 2H, so 12 entries
        for h in range(0, 12):
            sch = level + ' at ' + number2time(times, h * 2)
            addparameter(resid, 'Run', sch)
        return
    if cycle == 'r3':
        # every 3H, so 8 entries
        for h in range(0, 8):
            sch = level + ' at ' + number2time(times, h * 3)
            addparameter(resid, 'Run', sch)
        return
    if cycle == 'r4':
        # every 4H, so 6 entries
        for h in range(0, 6):
            sch = level + ' at ' + number2time(times, h * 4)
            addparameter(resid, 'Run', sch)
        return
    if cycle == 'r6':
        # every 6H, so 4 entries
        for h in range(0, 4):
            sch = level + ' at ' + number2time(times, h * 6)
            addparameter(resid, 'Run', sch)
        return
    if cycle == 'r8':
        # every 8H, so 3 entries
        for h in range(0, 3):
            sch = level + ' at ' + number2time(times, h * 8)
            addparameter(resid, 'Run', sch)
        return
    if cycle == 'r12':
        # every 12H, so 2 entries
        for h in range(0, 2):
            sch = params['level'] + ' at ' + number2time(times, h * 12)
            addparameter(resid, 'Run', sch)
        return


def createDIRSchWeek(resid=None, params=None):
    """ 'scheduleweek': u'off:off:off:off:off:off:off:off', """
    # get required data
    SCHWEEKDAYS = (
        'mon',
        'tue',
        'wed',
        'thu',
        'fri',
        'sat',
        'sun',
    )
    dlist = params['scheduleweek'].split(':')
    time = params['time']
    # insert parameters
    if dlist[-1] != 'off':
        # everylevel
        level = getlevelname(dlist[-1])
        sch = level + " at " + params['time']
        addparameter(resid, 'Run', sch)
    else:
        for i, lvl in enumerate(dlist[:-1]):
            if lvl != 'off':
                level = getlevelname(lvl)
                sch = level + " " + SCHWEEKDAYS[i] + " at " + time
                addparameter(resid, 'Run', sch)


def createDIRSchMonth(resid=None, params=None):
    """ 'schedulemonth': u'off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off'
                          ':off:off:off:off:off:off:off:off:off' """
    # insert parameters
    dlist = params['schedulemonth'].split(':')
    time = params['time']
    if dlist[-1] != 'off':
        # everylevel
        level = getlevelname(dlist[-1])
        sch = level + " at " + time
        addparameter(resid, 'Run', sch)
    else:
        for i, lvl in enumerate(dlist[:-1]):
            if lvl != 'off':
                level = getlevelname(lvl)
                sch = level + " on " + str(i + 1) + " at " + time
                addparameter(resid, 'Run', sch)


def createDIRSchedule(dircompid=None, name='sch-default', cycle='Hours', params=None, descr=''):
    """
    Creates a full schedule based on supplied parameters. When cycle is unknown (or None) the a routine has no effect.
    This means it creates a schedule resource but with no Run schedule parameters.
    :param dircompid: director component id
    :param name: name of the schedule
    :param cycle: defined schedule cycle, allowed values: Hours, Day, Week, Month
    :param params: schedule parameters as dict, i.e. 'level', 'time', 'scheduleweek', 'schedulemonth', 'backuprepeat'
    :param descr: description of the resource
    :return: none
    """
    # create resource
    resid = createDIRresSchedule(dircompid=dircompid, name=name, descr=descr)
    # add parameters based on cycle
    if cycle == 'Hours':
        # c1 - cycle during Day, every xx hours
        createDIRSchHours(resid, params)
        return
    if cycle == 'Day':
        # used only for single day schedule
        createDIRSchDay(resid, params)
        return
    if cycle == 'Week':
        # c2 - cycle during Week
        createDIRSchWeek(resid, params)
        return
    if cycle == 'Month':
        # c3 - cycle during Month
        createDIRSchMonth(resid, params)
        return


schmaxfulldict = {
        'c1': '1 Week',     # sensowny kompromis
        'c2': '1 Week',
        'c3': '1 Month'
    }


def createJobForm(dircompid=None, data=None, jd='jd-backup-files'):
    """{
    'name': u'asd',
    'descr': u'',
    'storage': u'ibadmin-File1',
    'backuplevel': u'full',
    'starttime': datetime.time(18, 55),
    'backuprepeat': u'r1',
    'scheduleweek': u'off:off:off:off:off:off:off:off',
    'schedulemonth': u'off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:'
                      'off:off:off:off:off:off:off:off',
    'client': u'debian',
    'exclude': u'',
    'include': u'asd',
    'backupsch': u'c1',
    'retention': u'30 days'
    }"""
    if data is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    jobname = data['name'].encode('ascii', 'ignore')
    # create Pool
    disktype = True     # TODO zrobić weryfikację
    poolname = 'Pool-' + data['retention'].replace(' ', '-')
    check_or_createPool(dircompid=dircompid, name=poolname, disktype=disktype, retention=data['retention'],
                        useduration='1 Day')
    # create Schedule
    schcycledict = {
        'c1': 'Hours',
        'c2': 'Week',
        'c3': 'Month'
    }
    schname = 'sch-' + jobname
    schcycle = schcycledict[data['backupsch']]
    starttime = str(data['starttime'])[:-3]
    level = data['backuplevel']
    params = {
        'level': level,
        'time': starttime,
        'scheduleweek': data['scheduleweek'],
        'schedulemonth': data['schedulemonth'],
        'backuprepeat': data['backuprepeat'],
    }
    createDIRSchedule(dircompid=dircompid, name=schname, cycle=schcycle, params=params,
                      descr='Schedule for Job: ' + data['name'])
    # create FileSet
    include = data['include'].splitlines()
    exclude = data['exclude'].splitlines()
    clientos = getDIRClientOS(dircompid=dircompid, name=data['client'])
    vss = updateFSdefaultexclude(exclude=exclude, clientos=clientos)
    fsname = 'fs-' + jobname
    dedup = getStorageisDedup(data['storage'])
    createDIRFileSetFile(dircompid=dircompid, name=fsname, vss=vss, include=include, exclude=exclude,
                         descr='Fileset for Job: ' + data['name'], dedup=dedup)
    # create Job
    if schcycle is not 'Hours':
        level = 'Incremental'
    # schedule form parameters (backupsch, backuprepeat, starttime, scheduleweek, schedulemonth)
    schparam = data['backupsch'] + ':' + data['backuprepeat']
    createDIRJob(dircompid=dircompid, name=jobname, jd=jd, descr=data['descr'], client=data['client'],
                 pool=poolname, storage=data['storage'], fileset=fsname, schedule=schname, level=level,
                 maxfullinterval=schmaxfulldict[data['backupsch']],
                 scheduleparam=schparam, scheduletime=starttime, scheduleweek=data['scheduleweek'],
                 schedulemonth=data['schedulemonth'])


def createDefaultClientJob(dircompid=None, name=None, clientos=None, client=None):
    if name is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if clientos is None and client is not None:
        clientos = getDIRClientOS(name=client)
    include = ['/', '/boot']
    if clientos is not None and clientos.startswith('win'):
        include = ['C:/']
    exclude = []
    vss = updateFSdefaultexclude(exclude=exclude, clientos=clientos)
    jobname = name + '-DefaultJob'
    storage = getDefaultStorage(dircompid)
    # create Schedule
    schname = 'sch-' + jobname
    schcycle = 'Week'
    starttime = '20:00'
    level = 'incr'
    scheduleweek = 'incr:incr:incr:incr:incr:incr:incr:incr'
    schedulemonth = 'off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:' \
                    'off:off:off:off:off:off:off:off'
    params = {
        'level': level,
        'time': starttime,
        'scheduleweek': scheduleweek,
        'schedulemonth': schedulemonth,
        'backuprepeat': 'r1',
    }
    createDIRSchedule(dircompid=dircompid, name=schname, cycle=schcycle, params=params,
                      descr='Schedule for Job: ' + jobname)
    # create FileSet
    fsname = 'fs-' + jobname
    createDIRFileSetFile(dircompid=dircompid, name=fsname, vss=vss, include=include, exclude=exclude,
                         descr='Fileset for Job: ' + jobname)
    # create Job
    if schcycle is not 'Hours':
        level = 'Incremental'
    # schedule form parameters (backupsch, backuprepeat, starttime, scheduleweek, schedulemonth)
    schparam = 'c2:r1'
    createDIRJob(dircompid=dircompid, name=jobname, jd='jd-backup-files', descr='Default Client Backup Job',
                 client=name, pool='Default', storage=storage, fileset=fsname, schedule=schname, level=level,
                 maxfullinterval='1 Week', scheduleparam=schparam, scheduletime=starttime, scheduleweek=scheduleweek,
                 schedulemonth=schedulemonth)


def createFDFileDaemon(fdcompid=None, name='ibadmin', descr='', address='localhost', os='rhel'):
    # create resource
    resid = createFDresFileDaemon(fdcompid=fdcompid, name=name, descr=descr)
    # add parameters
    if os == 'win32' or os == 'win64':
        maxjobs = 2
        piddir = 'C:/Program Files/Bacula/working'
        plugdir = 'C:/Program Files/Bacula/plugins'
        workdir = 'C:/Program Files/Bacula/working'
    elif os == 'osx':
        maxjobs = 10
        piddir = '/var/run'
        plugdir = '/usr/local/bacula/plugins'
        workdir = '/private/var/bacula/working'
    else:
        maxjobs = 10
        piddir = '/opt/bacula/working'
        plugdir = '/opt/bacula/plugins'
        workdir = '/opt/bacula/working'
    addparameter(resid, 'MaximumConcurrentJobs', maxjobs)
    addparameterstr(resid, '.OS', os)
    addparameterstr(resid, 'PidDirectory', piddir)
    addparameterstr(resid, 'PluginDirectory', plugdir)
    addparameterstr(resid, 'WorkingDirectory', workdir)
    addparameter(resid, 'HeartbeatInterval', 60)
    addparameter(resid, 'FDAddress', address)
    addparameter(resid, 'FDPort', 9102)


def createClientNode(dircompid=None, dirname=None, name='ibadmin', address='localhost', os='rhel', descr='',
                     cluster=None, clusterlist=None, internal=False):
    if cluster is not None and len(cluster):
        # New cluster name
        cl = cluster
        encpass = None
    else:
        # existing cluster
        cl = clusterlist
        encpass = getDIRClientsClusterEncpass(cluster=cl)
    createClient(dircompid=dircompid, dirname=dirname, name=name, address=address, os=os, cluster=cl, descr=descr,
                 internal=internal, encpass=encpass)


def createClient(dircompid=None, dirname=None, name='ibadmin', address='localhost', os='rhel', descr='',
                 internal=False, cluster=None, encpass=None):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    # generate password
    if encpass is None:
        password = randomstr()
    else:
        password = getdecpass(dirname, encpass)
    # insert new Client {} resource into Dir conf
    createDIRClient(dircompid=dircompid, dirname=dirname, name=name, password=password, address=address, os=os,
                    descr=descr, internal=internal, cluster=cluster)
    # create a FD component
    fdcompid = createFDcomponent(name=name)
    # insert new FileDaemon {} resource into FD conf
    createFDDirector(fdcompid=fdcompid, dirname=dirname, name=name, password=password)
    createFDFileDaemon(fdcompid=fdcompid, name=name, descr=descr, address=address, os=os)
    createFDMessages(fdcompid=fdcompid, dirname=dirname)


def createClientAlias(dircompid=None, dirname=None, name='ibadmin', client=None, descr=''):
    if client is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    # TODO wykorzystać funkcje jak w updateClientAlias
    clientinfo = getDIRClientinfo(name=client)
    clientparams = extractclientparams(clientinfo)
    encpass = clientparams['Password']
    address = clientparams['Address']
    os = clientparams['OS']
    # insert new Client {} resource into Dir conf
    createDIRClient(dircompid=dircompid, dirname=dirname, name=name, encpass=encpass, address=address, os=os,
                    descr=descr, alias=client)


def updateClientAlias(dircompid=None, name='ibadmin', alias='ibadmin'):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    address = getDIRClientAddress(dircompid=dircompid, name=alias)
    updateparameter(dircompid, name, 'Client', 'Address', address)
    updateparameter(dircompid, name, 'Client', '.Alias', alias)
    encpass = getDIRClientEncpass(dircompid=dircompid, name=alias)
    updateparameter(dircompid, name, 'Client', 'Password', encpass)
    os = getDIRClientOS(dircompid=dircompid, name=alias)
    updateparameter(dircompid, name, 'Client', '.OS', os)


def createClientService(dircompid=None, dirname=None, name='ibadmin', address='127.0.0.1', cluster=None, descr=''):
    if cluster is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    client = getDIRClusterClientname(dircompid=dircompid, name=cluster)
    clientinfo = getDIRClientinfo(name=client)
    clientparams = extractclientparams(clientinfo)
    encpass = clientparams['Password']
    os = clientparams['OS']
    # insert new Client {} resource into Dir conf
    createDIRClient(dircompid=dircompid, dirname=dirname, name=name, encpass=encpass, address=address, os=os,
                    descr=descr, service=cluster)


def updateDIRClientDescr(dircompid=None, name='ibadmin', descr=''):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    updateresdescription(dircompid, name, 'Client', descr)


def updateDIRStorageDescr(dircompid=None, name=None, descr=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    updateresdescription(dircompid, name, 'Storage', descr)


def updateClientDescr(dircompid=None, name=None, descr=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    updateresdescription(dircompid, name, 'Client', descr)
    fdcompid = getFDcompid(name)
    updateresdescription(fdcompid, name, 'FileDaemon', descr)


def updateClientCluster(dircompid=None, name=None, cluster=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    updateparameter(dircompid, name, 'Client', '.ClusterService', cluster)
    # get cluster node info
    client = getDIRClusterClientname(dircompid=dircompid, name=cluster)
    clientinfo = getDIRClientinfo(name=client)
    clientparams = extractclientparams(clientinfo)
    encpass = clientparams['Password']
    updateparameter(dircompid, name, 'Client', 'Password', encpass)


def updateDIRClientAddress(dircompid=None, name=None, address='localhost'):
    if name is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    updateparameter(dircompid, name, 'Client', 'Address', address)


def updateClientAddress(dircompid=None, name=None, address='localhost'):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    clients = getDIRClientAliases(name=name)
    clients += (name,)
    for cl in clients:
        updateDIRClientAddress(dircompid=dircompid, name=cl, address=address)
    fdcompid = getFDcompid(name)
    updateparameter(fdcompid, name, 'FileDaemon', 'FDAddress', address)


def updateDIRJobDescr(dircompid=None, name=None, descr=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    updateresdescription(dircompid, name, 'Job', descr)


def updateDIRDescr(dircompid=None, dirname=None, descr=''):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    updateresdescription(dircompid, dirname, 'Director', descr)


def updateDIRadminemail(dircompid=None, dirname=None, email=''):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    emailstr = email + ' = All, !Debug, !Skipped, !Restored'
    updateparameter(dircompid, 'Standard', 'Messages', 'Mail', emailstr)
    emailstr = email + ' = All, !Fatal, !Debug, !Skipped, !Restored'
    updateparameter(dircompid, 'Daemon', 'Messages', 'Mail', emailstr)


def updateJobStorage(dircompid=None, name=None, storage='ibadmin'):
    # get required data
    if name is None:
        return
    if dircompid is None:
        dircompid = getDIRcompid()
    updateparameter(dircompid, name, 'Job', 'Storage', storage)
    dedup = getStorageisDedup(storage)
    fsname = 'fs-' + name
    updateFSOptionsDedup(dircompid=dircompid, fsname=fsname, dedup=dedup)


def updateJobClient(dircompid=None, name=None, client='ibadmin'):
    if name is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    updateparameter(dircompid, name, 'Job', 'Client', client)


def updateFSOptionsDedup(dircompid=None, fsname=None, includeid=None, dedup=False):
    if fsname is None:
        return
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if includeid is None:
        resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
        includeid = getsubresourceid(resid=resid, typename='Include')
    optionid = getsubresourceid(resid=includeid, typename='Options')
    dedupparam = ConfParameter.objects.filter(resid=optionid, name='Dedup').count() > 0
    if dedup is True and dedupparam is False:
        addparameter(optionid, 'Dedup', 'BothSides')
    elif dedup is False and dedupparam is True:
        deleteparameter(optionid, 'Dedup')


def updateFSIncludeFile(dircompid=None, fsname=None, include=''):
    if fsname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    includelist = include.splitlines()
    resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
    includeid = getsubresourceid(resid=resid, typename='Include')
    query = ConfParameter.objects.filter(resid=includeid)
    query.delete()
    createFSIncludeFile(resid=includeid, include=includelist)


def updateFSExclude(dircompid=None, fsname=None, exclude='', client=None):
    if fsname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    excludelist = exclude.splitlines()
    clientos = getDIRClientOS(dircompid=dircompid, name=client)
    updateFSdefaultexclude(exclude=excludelist, clientos=clientos)
    resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
    excludeid = getsubresourceid(resid=resid, typename='Exclude')
    query = ConfParameter.objects.filter(resid=excludeid)
    query.delete()
    createFSExclude(resid=excludeid, exclude=excludelist)


def updateFSIncludePlugin(dircompid=None, fsname=None, include=''):
    if fsname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
    includeid = getsubresourceid(resid=resid, typename='Include')
    query = ConfParameter.objects.filter(resid=includeid)
    query.delete()
    createFSIncludePlugin(resid=includeid, include=include)


def updateJobEnabled(dircompid=None, name=None, enabled=True):
    if name is None:
        return
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    ena = 'No'
    if enabled:
        ena = 'Yes'
    resid = getresourceid(compid=dircompid, name=name, typename='Job')
    updateparameterresid(resid=resid, name='Enabled', value=ena)


def updateJobRunBefore(dircompid=None, name=None, runbefore=''):
    if name is None:
        return
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    param = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__name=name, resid__type__name='Job',
                                         name='ClientRunBeforeJob').first()
    if runbefore is not None and len(runbefore):
        # add or change runbefore
        if param is None:
            # require param to add
            resid = getresourceid(compid=dircompid, name=name, typename='Job')
            param = ConfParameter(resid_id=resid, name='ClientRunBeforeJob', value=runbefore, str=True)
        else:
            param.value = runbefore
        param.save()
    else:
        # disable runbefore
        if param is None:
            # disabled already
            return
        param.delete()


def updateJobRunAfter(dircompid=None, name=None, runafter=''):
    if name is None:
        return
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    param = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__name=name, resid__type__name='Job',
                                         name='ClientRunAfterJob').first()
    if runafter is not None and len(runafter):
        # add or change runbefore
        if param is None:
            # require param to add
            resid = getresourceid(compid=dircompid, name=name, typename='Job')
            param = ConfParameter(resid_id=resid, name='ClientRunAfterJob', value=runafter, str=True)
        else:
            param.value = runafter
        param.save()
    else:
        # disable runbefore
        if param is None:
            # disabled already
            return
        param.delete()


def deleteDIRFileSet(dircompid=None, fsname=None):
    if fsname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
    # delete options subresource of include subresource
    includeid = getsubresourceid(resid=resid, typename='Include')
    deletesubresource(includeid, 'Options')
    deletesubresource(resid, 'Include')
    # delete exclude subresource
    deletesubresource(resid, 'Exclude')
    # delete fileset resource
    deleteresource(resid)


def updateRetention(dircompid=None, name=None, retention=None):
    # get required data
    if name is None or retention is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    # create Pool
    disktype = True  # TODO zrobić weryfikację
    poolname = 'Pool-' + retention.replace(' ', '-')
    check_or_createPool(dircompid=dircompid, name=poolname, disktype=disktype, retention=retention,
                        useduration='1 Day')
    updateparameter(compid=dircompid, resname=name, restype='Job', name='Pool', value=poolname)


def updateSchedule(dircompid=None, jobname=None, data=None, backupsch='', starttime='', scheduleweek='',
                   schedulemonth='', backuprepeat='', backuplevel=''):
    """

    :param dircompid:
    :param jobname: Job name for which
    :param data:
    :param backupsch:
    :param starttime:
    :param scheduleweek:
    :param schedulemonth:
    :param backuprepeat:
    :param backuplevel:
    :return:
    """
    if jobname is None and data is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if data is not None:
        if jobname is None:
            jobname = data['name']
        backupsch = data['backupsch']
        starttime = data['starttime']
        scheduleweek = data['scheduleweek']
        schedulemonth = data['schedulemonth']
        backuprepeat = data['backuprepeat']
        backuplevel = data['backuplevel']
    schname = 'sch-' + jobname
    resid = getresourceid(compid=dircompid, name=schname, typename='Schedule')
    query = ConfParameter.objects.filter(resid=resid)
    query.delete()
    schtime = str(starttime)[:-3]
    params = {
        'level': backuplevel,
        'time': schtime,
        'scheduleweek': scheduleweek,
        'schedulemonth': schedulemonth,
        'backuprepeat': backuprepeat,
    }
    if backupsch == 'c1':
        # c1 - cycle during Day, every xx hours
        createDIRSchHours(resid, params)
    if backupsch == 'c2':
        # c2 - cycle during Week
        createDIRSchWeek(resid, params)
        lvl = scheduleweek.split(':')[7]
        if lvl != 'off':
            backuplevel = lvl
        else:
            backuplevel = 'incr'
    if backupsch == 'c3':
        # c3 - cycle during Month
        createDIRSchMonth(resid, params)
        lvl = schedulemonth.split(':')[31]
        if lvl != 'off':
            backuplevel = lvl
        else:
            backuplevel = 'incr'
    jresid = getresourceid(compid=dircompid, name=jobname, typename='Job')
    updateparameterresid(resid=jresid, name='Level', value=getlevelname(backuplevel))
    schparam = data['backupsch'] + ':' + data['backuprepeat']
    updateparameterresid(resid=jresid, name='.Scheduleparam', value=schparam)
    updateparameterresid(resid=jresid, name='.Scheduletime', value=schtime)
    updateparameterresid(resid=jresid, name='.Scheduleweek', value=scheduleweek)
    updateparameterresid(resid=jresid, name='.Schedulemonth', value=schedulemonth)
    updateparameterresid(resid=jresid, name='MaxFullInterval', value=schmaxfulldict[backupsch])


def updateScheduletime(dircompid=None, name=None, jobname=None, level='', starttime='05:00:00'):
    if name is None or jobname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    schtime = str(starttime)[:-3]
    schparam = level + ' at ' + schtime
    resid = getresourceid(compid=dircompid, name=name, typename='Schedule')
    updateparameterresid(resid=resid, name='Run', value=schparam)
    jresid = getresourceid(compid=dircompid, name=jobname, typename='Job')
    updateparameterresid(resid=jresid, name='.Scheduletime', value=schtime)


def deleteDIRSchedule(dircompid=None, schname=None):
    if schname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    resid = getresourceid(compid=dircompid, name=schname, typename='Schedule')
    deleteresource(resid)


def createDIRStorage(dircompid=None, dirname=None, name='ibadmin', password='ibadminpassword', address='localhost',
                     device='ibadmin-File1', mediatype='File', descr='', internal=False, sdcomponent='ibadmin',
                     encpass=None, sddirdevice=None, sddirdedupidx=None):
    # create resource
    resid = createDIRresStorage(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    addparameterstr(resid, 'Address', address)
    addparameter(resid, 'SDPort', 9103)
    addparameterstr(resid, 'Device', device)
    addparameterstr(resid, 'MediaType', mediatype)
    # it is BEE only directive, I think?
    addparameter(resid, 'Autochanger', 'Yes')
    addparameter(resid, 'MaximumConcurrentJobs', 10)
    if encpass is None:
        encpass = getencpass(dirname, password)
    addparameterenc(resid, 'Password', encpass)
    if internal:
        addparameter(resid, '.InternalStorage', 'Yes')
    addparameter(resid, '.StorageComponent', sdcomponent)
    if sddirdevice is not None:
        addparameter(resid, '.StorageDirDevice', sddirdevice)
    if sddirdedupidx is not None:
        addparameter(resid, '.StorageDirDedupidx', sddirdedupidx)


def createSDStorage(sdcompid=None, name='ibadmin', address='localhost', dedupdir=None, dedupindx=None, descr=''):
    # create resource
    resid = createSDresStorage(sdcompid=sdcompid, name=name, descr=descr)
    # add parameters
    addparameter(resid, 'SDPort', 9103)
    addparameter(resid, 'SDAddress', address)
    # static BEE parameters
    addparameterstr(resid, 'WorkingDirectory', '/opt/bacula/working')
    addparameterstr(resid, 'PidDirectory', '/opt/bacula/working')
    addparameterstr(resid, 'PluginDirectory', '/opt/bacula/plugins')
    addparameter(resid, 'MaximumConcurrentJobs', 11)
    # optional parameters for dedup
    if dedupdir is not None and dedupindx is not None:
        addparameterstr(resid, 'DedupDirectory', dedupdir)
        addparameterstr(resid, 'DedupIndexDirectory', dedupindx)


def createSDAutochanger(sdcompid=None, name='File1', changerdev='/dev/null', changercmd='', devices=None, descr=''):
    # check required data
    if sdcompid is None or devices is None:
        return
    # create resource
    resid = createSDresAutochanger(sdcompid=sdcompid, name=name, descr=descr)
    # add parameters
    addparameterstr(resid, 'ChangerCommand', changercmd)
    addparameterstr(resid, 'ChangerDevice', changerdev)
    for dev in devices:
        addparameterstr(resid, 'Device', dev['name'])


def createSDDevice(sdcompid=None, dtype='File', device=None):
    if sdcompid is None or device is None:
        return
    # create resource
    resid = createSDresDevice(sdcompid=sdcompid, name=device['name'])
    # add parameters
    addparameter(resid, 'AlwaysOpen', 'Yes')
    addparameterstr(resid, 'ArchiveDevice', device['archdir'])
    addparameter(resid, 'Autochanger', 'Yes')
    addparameter(resid, 'AutomaticMount', 'Yes')
    addparameter(resid, 'DeviceType', dtype)
    addparameter(resid, 'DriveIndex', device['devindex'])
    addparameterstr(resid, 'MediaType', device['mediatype'])
    if dtype == 'Tape':
        addparameter(resid, 'RandomAccess', 'No')
        addparameter(resid, 'RemovableMedia', 'Yes')
    else:
        addparameter(resid, 'RandomAccess', 'Yes')
        addparameter(resid, 'RemovableMedia', 'No')
        addparameter(resid, 'LabelMedia', 'Yes')
    addparameterstr(resid, 'SpoolDirectory', '/opt/bacula/working')
    addparameter(resid, 'MaximumConcurrentJobs', 1)


def createStorage(dircompid=None, dirname=None, storname='ibadmin', address='localhost', descr='', stortype='file',
                  archdir='/tmp', dedupdir=None, dedupidxdir=None, internal=False):
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    if stortype == 'file':
        archdirn = os.path.abspath(archdir)
        return createStoragefile(dircompid=dircompid, dirname=dirname, storname=storname, address=address, descr=descr,
                                 archdir=archdirn, internal=internal)
    if stortype == 'dedup':
        dedupdirn = os.path.abspath(dedupdir)
        dedupidxdirn = os.path.abspath(dedupidxdir)
        return createStoragededup(dircompid=dircompid, dirname=dirname, storname=storname, address=address, descr=descr,
                                  dedupdir=dedupdirn, dedupidxdir=dedupidxdirn, internal=internal)
    return None


def createStoragefile(dircompid=None, dirname=None, storname='ibadmin', address='localhost', descr='', archdir='/tmp',
                      internal=False):
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    devtype = 'File'
    mediatype = devtype + getnextStorageid()
    dirstorname = storname + '-' + mediatype
    # generate password
    password = randomstr()
    # insert new Storage {} resource into Dir conf
    createDIRStorage(dircompid=dircompid, dirname=dirname, name=dirstorname, password=password, address=address,
                     descr=descr, device=mediatype, mediatype=mediatype, internal=internal, sdcomponent=storname,
                     sddirdevice=archdir)
    # create SD component
    sdcompid = createSDcomponent(name=storname)
    # insert new Director {} resource into SD conf
    createSDDirector(sdcompid=sdcompid, dirname=dirname, name=storname, password=password, descr=descr)
    # insert new Storage {} resource into SD conf
    createSDStorage(sdcompid=sdcompid, name=storname, descr=descr, address=address)
    # insert new Messages {} resource into SD conf
    createSDMessages(sdcompid=sdcompid, dirname=dirname)
    # create a list of archive devices
    devices = []
    for nr in range(0, 9):
        devices.append({
            'name': mediatype + 'Dev' + str(nr),
            'archdir': archdir,
            'devindex': nr,
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev='/dev/null', changercmd='', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype=devtype, device=dev)
    return dirstorname


def createStoragededup(dircompid=None, dirname=None, storname='ibadmin', address='localhost', descr='', dedupdir='/tmp',
                       dedupidxdir='/tmp', internal=False):
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    devtype = 'Dedup'
    mediatype = devtype + getnextStorageid()
    dirstorname = storname + '-' + mediatype
    # TODO: removed until we will know how to handle this
    # archdir = dedupdir + '/volumes'
    archdir = dedupdir
    # generate password
    password = randomstr()
    # insert new Storage {} resource into Dir conf
    createDIRStorage(dircompid=dircompid, dirname=dirname, name=dirstorname, password=password, address=address,
                     descr=descr, device=mediatype, mediatype=mediatype, internal=internal, sdcomponent=storname,
                     sddirdevice=archdir, sddirdedupidx=dedupidxdir)
    # create SD component
    sdcompid = createSDcomponent(name=storname)
    # insert new Director {} resource into SD conf
    createSDDirector(sdcompid=sdcompid, dirname=dirname, name=storname, password=password, descr=descr)
    # insert new Storage {} resource into SD conf
    createSDStorage(sdcompid=sdcompid, name=storname, descr=descr, address=address, dedupdir=dedupdir, dedupindx=dedupidxdir)
    # insert new Messages {} resource into SD conf
    createSDMessages(sdcompid=sdcompid, dirname=dirname)
    # create a list of archive devices
    devices = []
    for nr in range(0, 9):
        devices.append({
            'name': mediatype + 'Dev' + str(nr),
            'archdir': archdir,
            'devindex': nr,
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev='/dev/null', changercmd='', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype=devtype, device=dev)
    return dirstorname


def extendStoragefile(dircompid=None, dirname=None, sdcompid=None, storname=None, descr='', sdcomponent=None, archdir='/tmp'):
    if storname is None or (sdcomponent is None and sdcompid is None):
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    mediatype = 'File' + getnextStorageid()
    archdirn = os.path.abspath(archdir)
    encpass = getSDStorageEncpass(sdcompid=sdcompid, name=sdcomponent)
    password = getdecpass(comp=sdcomponent, encpass=encpass)
    address = getSDStorageAddress(sdcompid=sdcompid, sdname=sdcomponent)
    # insert new Storage {} resource into Dir conf
    createDIRStorage(dircompid=dircompid, dirname=dirname, name=storname, password=password, address=address,
                     descr=descr, device=mediatype, mediatype=mediatype, sdcomponent=sdcomponent, sddirdevice=archdirn)
    # TODO: extend maximumconcurrentjobs for SD
    # create a list of archive devices
    devices = []
    for nr in range(0, 9):
        devices.append({
            'name': mediatype + 'Dev' + str(nr),
            'archdir': archdirn,
            'devindex': nr,
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev='/dev/null', changercmd='', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype='File', device=dev)


def extendStoragededup(dircompid=None, dirname=None, sdcompid=None, storname=None, descr='', sdcomponent=None,
                       dedupdir='/tmp', dedupidxdir='/tmp'):
    if storname is None or (sdcomponent is None and sdcompid is None):
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    mediatype = 'Dedup' + getnextStorageid()
    dedupdirn = os.path.abspath(dedupdir)
    dedupidxdirn = os.path.abspath(dedupidxdir)
    encpass = getSDStorageEncpass(sdcompid=sdcompid, name=sdcomponent)
    password = getdecpass(comp=sdcomponent, encpass=encpass)
    address = getSDStorageAddress(sdcompid=sdcompid, sdname=sdcomponent)
    # insert new Storage {} resource into Dir conf
    createDIRStorage(dircompid=dircompid, dirname=dirname, name=storname, password=password, address=address,
                     descr=descr, device=mediatype, mediatype=mediatype, sdcomponent=sdcomponent, sddirdevice=dedupdirn,
                     sddirdedupidx=dedupidxdirn)
    # TODO: extend maximumconcurrentjobs for SD
    # create a list of archive devices
    devices = []
    for nr in range(0, 9):
        devices.append({
            'name': mediatype + 'Dev' + str(nr),
            'archdir': dedupdirn,
            'devindex': nr,
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev='/dev/null', changercmd='', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype='Dedup', device=dev)
    resid = getresourceid(sdcompid, sdcomponent, 'Storage')
    addparameterstr(resid, 'DedupDirectory', dedupdirn)
    addparameterstr(resid, 'DedupIndexDirectory', dedupidxdirn)


def updateStorageArchdir(dircompid=None, sdcompid=None, sdcomponent=None, storname=None, archdir='/tmp'):
    if storname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if sdcomponent is None:
        data = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type__name='Storage', resid__name=storname,
                                         name='.StorageComponent')
        sdcomponent = data.value
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    archdirn = os.path.abspath(archdir)
    mediatype = getDIRStorageMediatype(name=storname)
    res = ConfResource.objects.filter(compid_id=sdcompid, type__name='Device', confparameter__name='MediaType',
                                      confparameter__value=mediatype)
    params = ConfParameter.objects.filter(resid__in=res, name='ArchiveDevice')
    params.update(value=archdirn)
    updateparameter(dircompid, storname, 'Storage', '.StorageDirDevice', archdirn)


def updateStorageDedupdir(dircompid=None, sdcompid=None, sdcomponent=None, storname=None, dedupdir='/tmp'):
    if storname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if sdcomponent is None:
        data = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type__name='Storage', resid__name=storname,
                                         name='.StorageComponent')
        sdcomponent = data.value
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    dedupdirn = os.path.abspath(dedupdir)
    mediatype = getDIRStorageMediatype(name=storname)
    res = ConfResource.objects.filter(compid_id=sdcompid, type__name='Device', confparameter__name='MediaType',
                                      confparameter__value=mediatype)
    params = ConfParameter.objects.filter(resid__in=res, name='ArchiveDevice')
    params.update(value=dedupdirn)
    updateparameter(sdcompid, sdcomponent, 'Storage', 'DedupDirectory', dedupdirn)
    updateparameter(dircompid, storname, 'Storage', '.StorageDirDevice', dedupdirn)


def updateStorageDedupidxdir(dircompid=None, sdcompid=None, sdcomponent=None, storname=None, dedupidxdir='/tmp'):
    if storname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if sdcomponent is None:
        data = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type__name='Storage', resid__name=storname,
                                         name='.StorageComponent')
        sdcomponent = data.value
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    dedupidxdirn = os.path.abspath(dedupidxdir)
    updateparameter(sdcompid, sdcomponent, 'Storage', 'DedupIndexDirectory', dedupidxdirn)
    updateparameter(dircompid, storname, 'Storage', '.StorageDirDedupidx', dedupidxdirn)


def updateStorageAddress(dircompid=None, sdcompid=None, sdcomponent=None, address='localhost'):
    if dircompid is None:
        dircompid = getDIRcompid()
    params = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__type__name='Storage', name='Address')
    params.update(value=address)
    if sdcomponent is None:
        res = ConfResource.objects.get(compid_id=dircompid, type__name='Storage', confparameter__name='.InternalStorage')
        data = ConfParameter.objects.get(resid=res, name='.StorageComponent')
        sdcomponent = data.value
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    # Yes, SDComponent:name and SDComponent:Storage:name are always the same
    updateparameter(sdcompid, sdcomponent, 'Storage', 'SDAddress', address)


def updateDIRdefaultStorage(dircompid=None, storname=None):
    if storname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    # delete current InternalStorage parameter
    query = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type__name='Storage', name='.InternalStorage')
    query.delete()
    res = ConfResource.objects.get(compid_id=dircompid, type__name='Storage', name=storname)
    addparameter(res.resid, '.InternalStorage', 'Yes')
    updateparameter(dircompid, 'SYS-Backup-Catalog', 'Job', 'Storage', storname)


def deleteDIRJob(dircompid=None, name=None, job=None):
    if name is None and job is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if job is not None:
        name = job.name
        resid = job.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, typename='Job')
    # delete FileSet
    fsname = 'fs-' + name
    deleteDIRFileSet(dircompid=dircompid, fsname=fsname)
    # delete Schedule
    schname = 'sch-' + name
    deleteDIRSchedule(dircompid=dircompid, schname=schname)
    # delete Job resource and parameters
    deleteresource(resid)


def disableDIRJob(dircompid=None, name=None, job=None):
    if name is None and job is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if job is not None:
        resid = job.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, typename='Job')
    # change Enabed parameter to No
    updateparameterresid(resid=resid, name='Enabled', value='No')
    addparameter(resid=resid, name='.Disabledfordelete', value='Yes')


def disableDIRClient(dircompid=None, name=None, client=None):
    if name is None and client is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if client is not None:
        resid = client.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, typename='Client')
    addparameter(resid=resid, name='.Disabledfordelete', value='Yes')
    addparameter(resid=resid, name='Enabled', value='No')


def deleteDIRClient(dircompid=None, name=None, client=None):
    if name is None and client is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if client is not None:
        name = client.name
        resid = client.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, typename='Client')
    # delete Client resource and parameters
    deleteresource(resid)


def deleteFDClient(name=None):
    if name is None:
        return None
    # get and prepare required data
    fdcompid = getFDcompid(name=name)
    if fdcompid is None:
        return None
    fdparams = ConfParameter.objects.filter(resid__compid_id=fdcompid)
    fdparams.delete()
    fdres = ConfResource.objects.filter(compid_id=fdcompid)
    fdres.delete()
    fdcomp = ConfComponent.objects.filter(compid=fdcompid)
    fdcomp.delete()


def initialize(name='ibadmin', descr='', email='root@localhost', password=None, stortype='File',
               address='localhost', archdir='/tmp', dedupdir=None, dedupidxdir=None):
    # prepare variables
    clientip = address
    storip = address
    # create DIR component
    dircompid = createDIRcomponent(name=name)
    # create DIR Director Resource
    createDIRDirector(dircompid=dircompid, name=name, descr=descr)
    # create DIR Catalog Resource
    dbname = DATABASES['default']['NAME']
    dbuser = DATABASES['default']['USER']
    dbpass = DATABASES['default']['PASSWORD']
    createDIRCatalog(dircompid=dircompid, dbname=dbname, dbuser=dbuser, dbpassword=dbpass)
    # create DIR Messages Standard Resource
    createDIRMessages(dircompid=dircompid, name='Standard', email=email, log='bacula.log',
                      descr='Standard Job Messages')
    # create DIR Messages Daemon Resource
    createDIRMessages(dircompid=dircompid, name='Daemon', email=email, log='daemon.log', descr='Daemon Messages',
                      fatal=False)
    # create Admin Schedule
    scheduletimeadmin = '05:00'
    createDIRSchedule(dircompid=dircompid, name='sch-admin', cycle='Day', params={'level': '', 'time': scheduletimeadmin})
    # create Catalog backup Schedule
    scheduletime = '05:05'
    createDIRSchedule(dircompid=dircompid, name='sch-backup-catalog', cycle='Day',
                      params={'level': 'Full', 'time': scheduletime})
    # create default FileSet
    createDIRFileSetFile(dircompid=dircompid, name='fs-default', include=['/'],
                         exclude=['/opt/bacula/working', '/proc', '/tmp'],
                         descr='Default FileSet')
    # create Catalog backup FileSet
    createDIRFileSetFile(dircompid=dircompid, name='fs-catalog-backup',
                         include=['/opt/bacula/working/bacula.sql', '/opt/bacula/scripts', '/opt/bacula/bsr'],
                         exclude=['/opt/bacula/working'],
                         descr='Catalog backup FileSet')
    # create Client
    createClient(dircompid=dircompid, dirname=name, name=name, address=clientip, descr='Default local client',
                 internal=True, os=getOStype())
    # create Storage
    storname = createStorage(dircompid=dircompid, dirname=name, storname=name, address=storip,
                             descr='Default local storage', stortype=stortype, archdir=archdir, dedupdir=dedupdir,
                             dedupidxdir=dedupidxdir, internal=True)
    # create default Pool
    createDIRPool(dircompid=dircompid, name='Default', disktype=stortype is not 'Tape', retention='2 weeks',
                  useduration='1 day', descr='Default System Pool with 2W retention')
    # create Scratch Pool
    createDIRPool(dircompid=dircompid, name='Scratch', retention='2 weeks', descr='Management Scratch Pool')
    # create Admin JobDefs
    createDIRJobDefsAdmin(dircompid=dircompid, client=name, storage=storname)
    # create Restore JobDefs
    createDIRJobDefsRestore(dircompid=dircompid, client=name, storage=storname)
    # create Catalog backup JobDefs
    createDIRJobDefsCatalog(dircompid=dircompid, storage=storname)
    # create Catalog backup JobDefs
    createDIRJobDefsFiles(dircompid=dircompid)
    # create Admin Job
    onceaday = 'c1:r24'     # this is en equivalent to once a day :)
    createDIRJob(dircompid=dircompid, name='SYS-Admin', jd='jd-admin', internal=True,
                 descr='Internal administration job for system maintanance',
                 scheduleparam=onceaday, scheduletime=scheduletimeadmin)
    # create Restore Job
    createDIRJob(dircompid=dircompid, name='Restore', jd='jd-restore', descr='Internal Restore Job', internal=True)
    # create Catalog backup Job
    createDIRJob(dircompid=dircompid, name='SYS-Backup-Catalog', jd='jd-backup-catalog', client=name, internal=True,
                 pool='Default', storage=storname, level='Full', descr='Internal job for backup Catalog database',
                 scheduleparam=onceaday, scheduletime=scheduletime)
