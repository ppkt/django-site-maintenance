from maintenance import api


def maintenance():
    return {
        'maintenance_status': api.status()
    }
