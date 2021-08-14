from configuration import Config
from Filter import Filter

## initialise objects
config      = Config(__file__)
camera      = config.get_camera()
imu         = config.get_imu(camera, gen_ref=True)
x0, cov0    = config.get_IC(imu, camera)
kf          = Filter(config, imu, x0, cov0)

## filter main loop (t>=1)
config.print_config()
old_t = config.min_t
cap_t = config.cap_t

for i, t in enumerate(camera.t[1:]):
    # propagate
    kf.propagate_imu(old_t, t, config.real_joint_dofs)

    # update
    if not config.do_prop_only:
        current_cam = camera.traj.at_index(i + 1) # not counting IC
        K = kf.update(current_cam)
        if K is None: break

    # capping of simulation data
    if cap_t is not None and t >= cap_t: break

    old_t = t

## plot results
kf.plot(config, t, camera.traj)