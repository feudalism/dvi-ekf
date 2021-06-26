from Models import RigidSimpleProbe, Camera, Imu

import os, sys
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

def parse_arguments():
    def print_usage():
        print(f"Usage: {__file__} <regen> [<plot>]")
        print("\t <regen>  - regen / noregen")
        print("Optional arguments:")
        print("\t <plot>   - plot")
        sys.exit()

    try:
        do_regenerate = False or (sys.argv[1] == 'regen')
    except:
        print_usage()

    try:
        do_plot = (sys.argv[2] == 'plot')
    except:
        do_plot = False

    return do_regenerate, do_plot
do_regenerate, do_plot = parse_arguments()

# initialise robot, joint variables
probe_BtoC = RigidSimpleProbe(scope_length=0.5, theta_cam=sp.pi/6)

# parameters from camera
filepath_cam = './trajs/offline_mandala0_gt.txt'
cam = Camera(filepath=filepath_cam, max_vals=50)
min_t, max_t = cam.t[0], cam.t[-1]

# parameters from both cam + fwkin
R_BC = probe_BtoC.R

# generate IMU data
filepath_imu = './trajs/offline_mandala0_gt_imugen.txt'
imu = Imu(probe_BtoC, cam)
if do_regenerate:
    import time
    t_start = time.process_time()

    print(f"Generating IMU data ({cam.max_vals} values) and saving to {filepath_imu}...")

    if os.path.exists(filepath_imu):
        os.remove(filepath_imu)

    R_BW = imu.R_BW
    for n in range(cam.max_vals):
        imu.eval_expr_single(cam.t[n], cam.acc[:,n], cam.om[:,n], cam.alp[:,n],
                R_BW[n],
                *probe_BtoC.joint_dofs,
                append_array=True,
                filepath=filepath_imu)

    imu.init_trajectory()

    print(f"Time taken to generate data ({cam.max_vals} vals): {time.process_time() - t_start:.4f} s.")
else:
    print(f"Reading IMU data from {filepath_imu}...")
    imu.read_from_file(filepath_imu)

# interpolate IMU data
num_imu_between_frames = 10
imu.num_imu_between_frames = num_imu_between_frames

cam.traj.interpolate(num_imu_between_frames)
imu.traj.vis_data = cam.traj.interpolated

R_BW_interp = [R_BC @ R_WC.T for R_WC in imu.traj.vis_data.R]
imu.interpolate(cam.t)

# reconstruct camera trajectory from IMU data
imu.reconstruct_traj(R_BW_interp)
imu.traj.reconstructed.name = "imu (B) recon"

if do_plot:
    recon_axes_2d = cam.traj.plot(min_t=min_t, max_t=max_t)
    recon_axes_2d = imu.traj.reconstructed.plot(recon_axes_2d, min_t=min_t, max_t=max_t)

    recon_axes_3d = cam.traj.plot_3d()
    recon_axes_3d = imu.traj.reconstructed.plot_3d(ax=recon_axes_3d)

    plt.legend()
    plt.show()

# print and plot
if __name__ == '__main__':
    print(probe_BtoC)

    print(f"q: {probe_BtoC.q}")
    print(f"q_sym: {probe_BtoC.q_sym}")
    print(f"q_dot: {probe_BtoC.q_dot_sym}\n")

    probe_BtoC.plot(probe_BtoC.q)