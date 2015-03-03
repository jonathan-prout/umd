#!/usr/bin/env python
""" SEE https://hg.python.org/cpython/rev/e67620048d2f#l1.2"""
from subprocess import *

class PopenFix(Popen):
    def __init__(self, args, bufsize=0, executable=None,
                 stdin=None, stdout=None, stderr=None,
                 preexec_fn=None, close_fds=False, shell=False,
                 cwd=None, env=None, universal_newlines=False,
                 startupinfo=None, creationflags=0):
        """Create new Popen instance."""
        _cleanup()

        self._child_created = False
        if not isinstance(bufsize, (int, long)):
            raise TypeError("bufsize must be an integer")

        if mswindows:
            if preexec_fn is not None:
                raise ValueError("preexec_fn is not supported on Windows "
                                 "platforms")
            if close_fds and (stdin is not None or stdout is not None or
                              stderr is not None):
                raise ValueError("close_fds is not supported on Windows "
                                 "platforms if you redirect stdin/stdout/stderr")
        else:
            # POSIX
            if startupinfo is not None:
                raise ValueError("startupinfo is only supported on Windows "
                                 "platforms")
            if creationflags != 0:
                raise ValueError("creationflags is only supported on Windows "
                                 "platforms")

        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None
        self.universal_newlines = universal_newlines

        # Input and output objects. The general principle is like
        # this:
        #
        # Parent                   Child
        # ------                   -----
        # p2cwrite   ---stdin--->  p2cread
        # c2pread    <--stdout---  c2pwrite
        # errread    <--stderr---  errwrite
        #
        # On POSIX, the child objects are file descriptors.  On
        # Windows, these are Windows file handles.  The parent objects
        # are file descriptors on both platforms.  The parent objects
        # are None when not using PIPEs. The child objects are None
        # when not redirecting.

        (p2cread, p2cwrite,
         c2pread, c2pwrite,
         errread, errwrite) = self._get_handles(stdin, stdout, stderr)

        try:
            self._execute_child(args, executable, preexec_fn, close_fds,
                                cwd, env, universal_newlines,
                                startupinfo, creationflags, shell,
                                p2cread, p2cwrite,
                                c2pread, c2pwrite,
                                errread, errwrite)
        except Exception:
            # Preserve original exception in case os.close raises.
            exc_type, exc_value, exc_trace = sys.exc_info()

            to_close = []
            # Only close the pipes we created.
            if stdin == PIPE:
                to_close.extend((p2cread, p2cwrite))
            if stdout == PIPE:
                to_close.extend((c2pread, c2pwrite))
            if stderr == PIPE:
                to_close.extend((errread, errwrite))

            for fd in to_close:
                try:
                    os.close(fd)
                except EnvironmentError:
                    pass

            raise exc_type, exc_value, exc_trace

        if mswindows:
            if p2cwrite is not None:
                p2cwrite = msvcrt.open_osfhandle(p2cwrite.Detach(), 0)
            if c2pread is not None:
                c2pread = msvcrt.open_osfhandle(c2pread.Detach(), 0)
            if errread is not None:
                errread = msvcrt.open_osfhandle(errread.Detach(), 0)

        if p2cwrite is not None:
            self.stdin = os.fdopen(p2cwrite, 'wb', bufsize)
        if c2pread is not None:
            if universal_newlines:
                self.stdout = os.fdopen(c2pread, 'rU', bufsize)
            else:
                self.stdout = os.fdopen(c2pread, 'rb', bufsize)
        if errread is not None:
            if universal_newlines:
                self.stderr = os.fdopen(errread, 'rU', bufsize)
            else:
                self.stderr = os.fdopen(errread, 'rb', bufsize)

Popen = PopenFix
