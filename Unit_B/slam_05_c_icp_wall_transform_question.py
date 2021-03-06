# Subsample the scan. For each point, find a closest point on the
# wall of the arena.
# From those point pairs, estimate a transform and apply this to the pose.
# Repeat the closest point - estimate transform loop.
# This is an ICP algorithm.
# 05_c_icp_wall_transform
# Claus Brenner, 17 NOV 2012
from lego_robot import *
from slam_b_library import filter_step, concatenate_transform, compute_cartesian_coordinates, write_cylinders
from math import sqrt, atan2
from slam_04_d_apply_transform_question import estimate_transform, apply_transform, correct_pose
from slam_05_a_find_wall_pairs_question import get_subsampled_points, get_corresponding_points_on_wall

# Given a point list, return the center of mass.
def compute_center(point_list):
    # Safeguard against empty list.
    if not point_list:
        return (0.0, 0.0)
    # If not empty, sum up and divide.
    sx = sum([p[0] for p in point_list])
    sy = sum([p[1] for p in point_list])
    return (float(sx) / len(point_list), float(sy) / len(point_list))


# Given a left_list of points and a right_list of points, compute
# the parameters of a similarity transform: scale, rotation, translation.
# If fix_scale is True, use the fixed scale of 1.0.
# The returned value is a tuple of:
# (scale, cos(angle), sin(angle), x_translation, y_translation)
# i.e., the rotation angle is not given in radians, but rather in terms
# of the cosine and sine.
def estimate_transform(left_list, right_list, fix_scale = False):
    if len(left_list) < 2 or len(right_list) < 2:
        return None
    elif left_list == right_list:
        return 1.0, 1.0, 0.0, 0.0, 0.0
    else:
        flag1, flag2 = 0, 0
        len_list = len(left_list)
        for i in range(len_list - 1):
            if left_list[i] == left_list[i + 1]:
                flag1 += 1
            if right_list[i] == right_list[i + 1]:
                flag2 += 1
        if flag1 == len_list - 1 or flag2 == len_list - 1:
            return None

    # Compute left and right center.
    lc = compute_center(left_list)
    rc = compute_center(right_list)
    lp_x = []
    lp_y = []
    rp_x = []
    rp_y = []

    # --->>> Insert here your code to compute lambda, c, s and tx, ty.
    for l in left_list:
        lp_x.append(l[0] - lc[0])
        lp_y.append(l[1] - lc[1])
    for r in right_list:
        rp_x.append(r[0] - rc[0])
        rp_y.append(r[1] - rc[1])

    cs, ss, rr, ll = 0.0, 0.0, 0.0, 0.0
    for i in range(len(left_list)):
        cs += rp_x[i] * lp_x[i] + rp_y[i] * lp_y[i]
        ss += -rp_x[i] * lp_y[i] + rp_y[i] * lp_x[i]
        rr += rp_x[i]**2 + rp_y[i]**2
        ll += lp_x[i] ** 2 + lp_y[i] ** 2

    if fix_scale:
        la = 1.0
    else:
        la = sqrt(rr/ll)

    norm = sqrt(cs**2 + ss**2)
    c = cs / norm
    s = ss / norm

    tx = rc[0] - la * (c * lc[0] - s * lc[1])
    ty = rc[1] - la * (s * lc[0] + c * lc[1])

    return la, c, s, tx, ty


# Given a similarity transformation:
# trafo = (scale, cos(angle), sin(angle), x_translation, y_translation)
# and a point p = (x, y), return the transformed point.
def apply_transform(trafo, p):
    la, c, s, tx, ty = trafo
    lac = la * c
    las = la * s
    x = lac * p[0] - las * p[1] + tx
    y = las * p[0] + lac * p[1] + ty
    return (x, y)


# Correct the pose = (x, y, heading) of the robot using the given
# similarity transform. Note this changes the position as well as
# the heading.
def correct_pose(pose, trafo):
    la, c, s, tx, ty = trafo
    # --->>> This is what you'll have to implement.

    theta = atan2(s, c)
    pose_c = apply_transform(trafo, (pose[0], pose[1]))

    alpha = pose[2] + theta
    alpha = alpha % (2 * pi)
    return (pose_c[0], pose_c[1], alpha)   # Replace this by the corrected pose.


# Takes one scan and subsamples the measurements, so that every sampling'th
# point is taken. Returns a list of (x, y) points in the scanner's
# coordinate system.
def get_subsampled_points(scan, sampling = 10):
    # Subsample from scan
    index_range_tuples = []
    for i in xrange(0, len(scan), sampling):
        index_range_tuples.append( (i, scan[i]) )
    return compute_cartesian_coordinates(index_range_tuples, 0.0)


# Given a set of points, checks for every point p if it is closer than
# eps to the left, right, upper or lower wall of the arena. If so,
# adds the point to left_list, and the closest point on the wall to
# right_list.
def get_corresponding_points_on_wall(points,
                                     arena_left = 0.0, arena_right = 2000.0,
                                     arena_bottom = 0.0, arena_top = 2000.0,
                                     eps = 150.0):
    left_list = []
    right_list = []

    # ---> Insert your previous solution here.
    for p in points:
        px, py = p

        if abs(px - arena_left) < eps:
            left_list.append(p)
            right_list.append((arena_left, p[1]))
        elif abs(px - arena_right) < eps:
            left_list.append(p)
            right_list.append((arena_right, p[1]))
        elif abs(py - arena_bottom) < eps:
            left_list.append(p)
            right_list.append((p[0], arena_bottom))
        elif abs(py - arena_top) < eps:
            left_list.append(p)
            right_list.append((p[0], arena_top))

    return left_list, right_list


# ICP: Iterate the steps of transforming the points, selecting point pairs, and
# estimating the transform. Returns the final transformation.
def get_icp_transform(world_points, iterations):

    # Iterate assignment and estimation of trafo a few times.

    # --->>> Implement your code here.
    
    # You may use the following strategy:
    # Start with the identity transform:
    #   overall_trafo = (1.0, 1.0, 0.0, 0.0, 0.0)
    # Then loop for j in xrange(iterations):
    #   Transform the world_points using the curent overall_trafo
    #     (see 05_b on how to do this)
    #   Call get_correspoinding_points_on_wall(...)
    #   Determine transformation which is needed "on top of" the current
    #     overall_trafo: trafo = estimate_transform(...)
    #   Concatenate the found transformation with the current overall_trafo
    #     to obtain a new, 'combined' transformation. You may use the function
    #     overall_trafo = concatenate_transform(trafo, overall_trafo)
    #     to concatenate two similarities.
    #   Note also that estimate_transform may return None.
    # 

    # Return the final transformation.
    overall_trafo = (1.0, 1.0, 0.0, 0.0, 0.0)


    for j in range(iterations):
        world_points_1 = [apply_transform(overall_trafo, p) for p in world_points]  # new usage
        left, right = get_corresponding_points_on_wall(world_points_1)
        trafo = estimate_transform(left, right, fix_scale=True)
        if trafo:
            overall_trafo = concatenate_transform(trafo, overall_trafo)
        else:
            overall_trafo = (1.0, 1.0, 0.0, 0.0, 0.0)

    return overall_trafo


if __name__ == '__main__':
    # The constants we used for the filter_step.
    scanner_displacement = 30.0
    ticks_to_mm = 0.349
    robot_width = 150.0

    # The start pose we obtained miraculously.
    pose = (1850.0, 1897.0, 3.717551306747922)

    # Read the logfile which contains all scans.
    logfile = LegoLogfile()
    logfile.read("robot4_motors.txt")
    logfile.read("robot4_scan.txt")

    # Iterate over all positions.
    out_file = file("icp_wall_transform.txt", "w")
    for i in xrange(len(logfile.scan_data)):
        # Compute the new pose.
        pose = filter_step(pose, logfile.motor_ticks[i],
                           ticks_to_mm, robot_width,
                           scanner_displacement)

        # Subsample points.
        subsampled_points = get_subsampled_points(logfile.scan_data[i])
        world_points = [LegoLogfile.scanner_to_world(pose, c)
                        for c in subsampled_points]

        # Get the transformation.
        # You may play withe the number of iterations here to see
        # the effect on the trajectory!
        trafo = get_icp_transform(world_points, iterations = 40)

        # Correct the initial position using trafo.
        pose = correct_pose(pose, trafo)

        # Write to file.
        # The pose.
        print >> out_file, "F %f %f %f" % pose
        # Write the scanner points and corresponding points.
        write_cylinders(out_file, "W C",
            [apply_transform(trafo, p) for p in world_points])

    out_file.close()
