from no_sql_client import NoSQLClient
from administrativelevels import models as administrativelevels_models

def get_cvds(facilitator):
    administrative_levels = facilitator['administrative_levels']

    CVDs = []
    villages = []
    for _index in range(len(administrative_levels)):
        adl = administrative_levels[_index]
        if elt.get('villages') and adl['id'] in elt['villages']:

            _in_list = False
            for v in villages:
                if adl['id'] == v['id']:
                    _in_list = True
            if not _in_list:
                villages.append(adl)

                if adl.get('is_headquarters_village'):
                    elt['village'] = adl
                    elt['village_id'] = adl['id']

    # elt['village'] = villages[0] if len(villages) != 0 else None
    # elt['village_id'] = villages[0]['id'] if len(villages) != 0 else None
    if elt.get('village_id'):
        elt['villages'] = villages
        elt['unit'] = ''
        CVDs.append(elt)

    return CVDs


def single_task_by_cvd(tasks, cvds):
    _tasks = []
    a = -1
    for _ in tasks:
        a += 1
        if not is_village_principal(cvds, _['administrative_level_id']):
            continue
        _['administrative_level_name'] = get_cvd_name_by_village_id(cvds, _['administrative_level_id'])
        _tasks.append(_)

    return _tasks
