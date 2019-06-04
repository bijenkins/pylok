import errno
import os
import yaml
from enum import Enum

class LockAction(Enum):
    UNLOCK = 'unlock'
    LOCK = 'lock'
    STATUS= 'status'


class LockFileNotPresentError(Exception):
    def __init__(self, *args, **kwargs):
        default_message = 'Lock file expected BUT NOT present. Please verify status of Lock file'

        if not (args or kwargs): args = (default_message,)

        # Call super constructor
        super(LockFileNotPresentError, self).__init__(*args, **kwargs)

class LockFilePresentError(Exception):
    def __init__(self, *args, **kwargs):
        default_message = 'Lock file already present. Please verify status of Lock file'

        if not (args or kwargs): args = (default_message,)

        # Call super constructor
        super(LockFilePresentError, self).__init__(*args, **kwargs)


class LockFileNotPresentForRemoval(Exception):
    def __init__(self, *args, **kwargs):
        default_message = 'Attempted to remove lock file, but lock file not found.'

        if not (args or kwargs): args = (default_message,)

        super(LockFileNotPresentForRemoval, self).__init__(*args, **kwargs)

class LockActionError(Exception):
    def __init__(self, *args, **kwargs):
        default_message = 'Lock Action not actionable.'

        if not (args or kwargs): args = (default_message,)

        # Call super constructor
        super(LockActionError, self).__init__(*args, **kwargs)

def ensure_lock(lock_file):
    # ensure a lock file exists or don't proceed
    file_is_locked = is_locked(lock_file)
    if not file_is_locked:
        raise LockFileNotPresentError()
    return True

def ensure_unlock(lock_file):
    # ensure a lock file does not exist, or don't proceedz 
    file_is_locked = is_locked(lock_file)
    if file_is_locked:
        raise LockFilePresentError()
    return True

def create_lock_dir(lock_file_directory):
    # Make the directory
    try:
        os.makedirs(lock_file_directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def lock(lock_file_directory, lock_object, lock_data={}, lock_action='status', ensure_unlock_state=False, ensure_lock_state=False, ):
    """
    Manipulates lock files with the option to add data to the lock file.

    Possible uses:
        Load balancer control
        Deployment control
        File Editing Control


    Parameters:
        lock_file_directory (str): directory to store lock in. # sanatize later
        lock_object (str) : name of object to lock, will need to be consistent for each check. Creates lock file of 'lock_obj.lock'
        lock_data (dict): Data to be written to lock_file in yaml, when lock_action == lock, also return data
        lock_action (enum) (default:'status'):  ['status', 'lock', 'unlock'] action to perform 
        ensure_unlock (bool): default: False | Checks for lock file, raises exception if file lock present
        ensure_lock (bool): default: False | Checks for lock file, raises exception if file lock not present

    Returns:
        Dictionary with data written to lock file as well as the initial lock_data.
    
    Note:
        


    Examples:

        # ### Simple lock with simple info

        # Our Data Lock Info
        data_to_lock = {
            'msg': 'Locking for maintenance in reference to ticket 65807417',
            'contact': 'Billy Jenkins',
            'contact_email': 'billyjenkins@example.com',
            'datetime': '2019-12-19 09:26:03.478039',
            'expire': '2019-12-20 00:00:00',
            'lock_action': 'lock'
        }

        # ensure unlocked BEFORE creation of lock, lock server-cluster3w1-2, export data into lock file.
        lock_data = lock('/tmp/locks/', 'server-cluster3w1-2', lock_data=data_to_lock, lock_action=data_to_lock['lock_action'], ensure_unlock_state=True)

        # Output

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

        # ### Status Check
        lock_data = lock('/tmp/locks/', 'server-cluster3w1-2', lock_data=data_to_lock, lock_action=data_to_lock['lock_action'])

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




    """

    # if --ensure-lock-first is enabled, we will not run command unless lock file found.
    # if --ensure-unlock-first is enabled we will not run command unless lock file is nonexistant
    
    # Lock info
    lock_file_name = "{}.lock".format(lock_object)
    lock_file = "{}{}".format(lock_file_directory, lock_file_name)

    create_lock_dir(lock_file_directory)

        # Ignore lock functions on ignore
    if lock_action == LockAction.STATUS.value:

        file_is_locked = is_locked(lock_file)

        if file_is_locked is False:
            lock_file = None
            current_lock_status = 'unlocked'
        else:
            current_lock_status = 'locked'

        return_info = {
            'lock_file_location': lock_file,
            'lock_file_status': current_lock_status,
        }

        lock_data.update(return_info)

    elif lock_action == LockAction.UNLOCK.value:
        if ensure_lock_state:
            ensure_lock(lock_file)

        try:
            remove_lock_file(lock_file)
        except:
            raise LockFileNotPresentError()

        # Verify
        file_is_locked = is_locked(lock_file)

        if file_is_locked is False:
            current_lock_status = 'unlocked'
            lock_file = None

        else:
            raise LockFileNotPresentForRemoval()

        return_info = {
            'lock_file_location': lock_file,
            'lock_file_status': current_lock_status,
        }

        lock_data.update(return_info)

    elif lock_action == LockAction.LOCK.value:
        if ensure_unlock_state:
            ensure_unlock(lock_file)
            current_lock_status = 'unlocked'

        create_lock_file(lock_file)
        current_lock_status = 'locked'

        return_info = {
            'lock_file_location': lock_file,
            'lock_file_status': current_lock_status,
        }

        lock_data.update(return_info)

        write_to_lock_file(location=lock_file_directory, lock_object=lock_object, lock_data=lock_data)
        
        # Verify
        file_is_locked = is_locked(lock_file)

        if file_is_locked is True:
            current_lock_status = 'locked' 
            locked_file = lock_file
        else:
            raise LockFileNotPresentError()

    else:
        raise LockActionError()

    #print(lock_action)

    lock_data.update({'lock_action': lock_action})
    return lock_data


def create_lock_file(lock_file):
    open(lock_file, 'a').close()

def write_to_lock_file(location=None, lock_object=None, lock_data={}):
    lock_file = "{}{}.lock".format(location, lock_object)
    with open(lock_file, 'w') as locker:
        yaml.dump(lock_data, locker)

def is_locked(lock_file):

    try:
        file = open(lock_file, 'r')
        return True
    except:
        return False  

def remove_lock_file(lock_file):

    os.remove(lock_file)
