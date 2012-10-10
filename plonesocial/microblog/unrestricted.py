from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser

#
#
# http://collective-docs.readthedocs.org/en/latest/security/permissions.html
#
#


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


def execute_under_special_role(portal, role, function, *args, **kwargs):
    """ Execute code under special role priviledges.

    Example how to call::

        execute_under_special_role(portal, "Manager",
            doSomeNormallyNotAllowedStuff,
            source_folder, target_folder)


    @param portal: Reference to ISiteRoot object whose access controls
    we are using

    @param function: Method to be called with special priviledges

    @param role: User role we are using for the security context when
    calling the priviledged code. For example, use "Manager".

    @param args: Passed to the function

    @param kwargs: Passed to the function
    """

    sm = getSecurityManager()

    try:
        try:
            # Clone the current access control user and assign a new role
            # Note that the username (getId()) is left in exception tracebacks
            # in error_log so it is important thing to store
            tmp_user = UnrestrictedUser(
              sm.getUser().getId(),
               '', [role],
               ''
           )

            # Act as user of the portal
            tmp_user = tmp_user.__of__(portal.acl_users)
            newSecurityManager(None, tmp_user)

            # Call the function
            return function(*args, **kwargs)

        except:
            # If special exception handlers are needed, run them here
            raise
    finally:
        # Restore the old security manager
        setSecurityManager(sm)
