
# Pylok
Manipulates lock files with the option to add data to the lock file.


### Possible uses:
* Load balancer control
* Deployment control
* File Editing Control

When deploying, performing maintenance, patching, or troubleshooting sometimes we need to lock certain aspects of a environment such as load balancers, network switches, or configuration files from outside management sources.

With pylok this is made simple and extensible into your current workflow. Create lock files, that have intelligent data you define for later use in your workflow.

Lock files will have yaml as a default markup language for storing lock information.

#### Ex:
```
lock_file_status: unlocked
lock_action: status
lock_file_location: /lock/location/obj.lock
```

### Scenarios

#### Load Balancer

When deploying an application, a load balancer must be set in the correct state to minimize downtime for the end user. Some load balancers load balance not only many servers but many applications on the same server.

The ability to create structured data about information needed is as easy as passing the structured data to the lock function.

```
from pylok import lock, is_locked
from pprint import pprint

# Example data to be injected into the lock_file

# Execute locking of data 
lock_data = lock(
            '/tmp/locks/',
            'server-cluster3w1-2',
            lock_data={},
            lock_action='lock',
            ensure_unlock_state=True)

pprint(lock_data)

#{'lock_file_location': '/tmp/locks/server-cluster3w1-2.lock',
#'lock_file_status': 'locked'
#'lock_action': 'lock'}

lock_data.update({'msg': 'Locking App1 on server-cluster3w1-2 for canary deployment',
                'data': {'backend': 'App1', 'server': 'server-cluster3w1-2', 'status': 'MAINT'},
                'contact_email': 'billyjenkins@example.com',
                'datetime': '2019-12-19 09:26:03.478039',
                'lock_action': 'status'})

lock_data = lock('/tmp/locks/',
            lock_data['data']['server'],
            lock_data=lock_data,
            lock_action=lock_data['lock_action'])
           
 pprint(lock_data)

#{'contact_email': 'billyjenkins@example.com',
# 'data': {'backend': 'App1',
#          'server': 'server-cluster3w1-2',
#          'status': 'MAINT'},
# 'datetime': '2019-12-19 09:26:03.478039',
# 'lock_action': 'status',
# 'lock_file_location': '/tmp/locks/server-cluster3w1-2.lock',
# 'lock_file_status': 'locked',
# 'msg': 'Locking App1 on server-cluster3w1-2 for canary deployment'}

# lock() will update the lock_data dictionary with the information with the
# new lock info.


obj_status = lock_data['data']['status']
obj_name = lock_data['data']['server']

# Validate
if is_locked('/tmp/locks/server-cluster3w1-2.lock'): # or lock_data['lock_file_location']
    # custom validation of lock information to proceed
    if obj_status == 'MAINT':
        deploy_to.Server(obj_name)
        setserverto.ready(obj_name)

# Update lock action to reuse data
lock_data.update({'lock_action': 'unlock'})
lock_data['data'].update({'status': 'READY'})
lock_data.update({'msg': 'Unlocked App1 on server-cluster3w1-2, canary deployment complete'})

lock_data = lock('/tmp/locks/',
            lock_data['data']['server'],
            lock_data=lock_data,
            lock_action=lock_data['lock_action'])

pprint(lock_data)

#{'contact_email': 'billyjenkins@example.com',
# 'data': {'backend': 'App1',
#          'server': 'server-cluster3w1-2',
#          'status': 'READY'},
# 'datetime': '2019-12-19 09:26:03.478039',
# 'lock_action': 'unlock',
# 'lock_file_location': None,
# 'lock_file_status': 'unlocked',
# 'msg': 'Locking App1 on server-cluster3w1-2 for canary deployment'}

```

## Parameters:

* lock_file_directory (str): directory to store lock in. # sanatize later
* lock_object (str) : name of object to lock, will need to be consistent for each check. Creates lock file of 'lock_obj.lock'
* lock_data (dict): Data to be written to lock_file in yaml, when lock_action == lock, also return data
* lock_action (enum) (default:'status'):  ['status', 'lock', 'unlock'] action to perform 
* ensure_unlock (bool): default: False | Checks for lock file, raises exception if file lock present
* ensure_lock (bool): default: False | Checks for lock file, raises exception if file lock not present

## Notes

* Flags *--ensure-lock* and *--ensure-unlock* have conflicting logic and will rase the *LockFilePresentError* and *LockFileNotPresentError*'s respectivly, if their validation fails
* lock_data does not need to be provided, for the return result to contain a dictionary of lock info.

## Returns/Output:
        
Dictionary with data written to lock file as well as the initial lock_data.
    
### Ex:
    {       
        'lock_file_location': '/tmp/locks/server-cluster3w1-2.lock',
        'lock_file_status': 'locked'
        'lock_action': 'lock'
    }


## Examples:

### Our Data Lock Info
```
from pylok import *

# This information will be returned to us in addition to lock data.
data_to_lock = {'msg': 'Locking for maintenance in reference to ticket 65807417',
                'contact': 'Billy Jenkins',
                'contact_email': 'billyjenkins@example.com',
                'datetime': '2019-12-19 09:26:03.478039',
                'expire': '2019-12-20 00:00:00',
                'lock_action': 'lock'}

# ensure unlocked BEFORE creation of lock, lock server-cluster3w1-2, export data into lock file.
lock_data = lock('/tmp/locks/',
                'server-cluster3w1-2',
                lock_data=data_to_lock,
                lock_action=data_to_lock['lock_action'],
                ensure_unlock_state=True)
                ```
### Output:

pprint(lock_data)

{
    'msg': 'Locking for maintenance in reference to ticket 65807417'
    'contact': 'Billy Jenkins',
    'contact_email': 'billyjenkins@example.com',
    'datetime': '2019-12-19 09:26:03.478039',
    'expire': '2019-12-20 00:00:00',
    'lock_file_location': '/tmp/locks/server-cluster3w1-2.lock',
    'lock_file_status': 'locked'
    'lock_action': 'lock'
}


# Expire could be controlled by a external audit/state scraper that deletes the lock at expire time.

# Update lock action
data_to_lock.update({'lock_action': 'status'})

# Status Check
lock_data = lock(
            '/tmp/locks/',
            'server-cluster3w1-2',
            lock_data=data_to_lock,
            lock_action=data_to_lock['lock_action'])

pprint(lock_data)

# Output    
{
    'msg': 'Locking for maintenance in reference to ticket 65807417'
    'contact': 'Billy Jenkins',
    'contact_email': 'billyjenkins@example.com',
    'datetime': '2019-12-19 09:26:03.478039',
    'expire': '2019-12-20 00:00:00',
    'lock_file_location': '/tmp/locks/server-cluster3w1-2.lock',
    'lock_file_status': 'locked'
    'lock_action': 'status'
}
```

