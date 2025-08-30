
def get_user_from_session(session):
    """
    Returns the user from the session.
    """
    return session.get('usuario')
