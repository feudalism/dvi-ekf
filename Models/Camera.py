import numpy as np
from Filter import VisualTraj

class Camera(object):
    """ Class for the camera sensor which reads data from a text file.

        Provides trajectory data (positions p and rotations R or q)
        as well as the derivatives of the above
        (velocities: v and om,
        accelerations: acc and alp).

        Also provides the initial conditions of p, q, v, om.
    """

    def __init__(self, filepath, max_vals=None):
        self.traj_filepath = filepath
        self.traj = VisualTraj("camera", self.traj_filepath, cap=max_vals)
        self.max_vals = len(self.traj.t)

        self.t = self.traj.t
        self.dt = self.t[1] - self.t[0]

        self._p = None
        self._R = None
        self._q = None
        self._v = None
        self._om = None
        self._acc = None
        self._alp = None

        self.p0 = self.p[:,0]
        self.q0 = self.q[:,0]
        self.v0 = self.v[:,0]
        self.om0 = self.om[:,0]

    @property
    def p(self):
        self._p = np.array((self.traj.x, self.traj.y, self.traj.z))
        return self._p

    @property
    def v(self):
        self._v = np.asarray( (np.gradient(self.p[0,:], self.dt),
                            np.gradient(self.p[1,:], self.dt),
                            np.gradient(self.p[2,:], self.dt)) )
        return self._v

    @property
    def acc(self):
        self._acc = np.asarray( (np.gradient(self.v[0,:], self.dt),
                            np.gradient(self.v[1,:], self.dt),
                            np.gradient(self.v[2,:], self.dt)) )
        return self._acc

    @property
    def R(self):
        self._R = [q.rot for q in self.traj.quats]
        return self._R

    @property
    def q(self):
        self._q = np.array([q.xyzw for q in self.traj.quats]).T
        return self._q

    @property
    def om(self):
        ang_WC = np.asarray([q.euler_zyx for q in self.traj.quats])
        rz, ry, rx = ang_WC[:,0], ang_WC[:,1], ang_WC[:,2]

        self._om = np.asarray( (np.gradient(rx, self.dt),
                            np.gradient(ry, self.dt),
                            np.gradient(rz, self.dt)) )
        return self._om

    @property
    def alp(self):
        self._alp = np.asarray( (np.gradient(self.om[0,:], self.dt),
                            np.gradient(self.om[1,:], self.dt),
                            np.gradient(self.om[2,:], self.dt)) )
        return self._alp