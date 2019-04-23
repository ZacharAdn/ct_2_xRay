import os
import sys
import collections
import pydicom
from pydicom.data import get_testdata_files
import matplotlib.pyplot as plt


class Point3D(object):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


def ct2xray(xray_source, dest_board, ct_3d):
    # TODO  1 - check orthogonality of the x ray source to board
    #       2 - check if the cone in the limits of the ct scan
    #       3 - check if the cone end bigger than board (enough distance between them)
    #       4 - check that the source or the board not on the object

    # Check whether these are simple cases - the board is positioned straight
    # and there are no transitions between the y axis
    same_ys_top = dest_board[0].y == dest_board[1].y
    same_ys_bottom = dest_board[2].y == dest_board[3].y
    same_zs = all(corner.z == dest_board[0].z for corner in dest_board)
    same_xs = all(corner.x == dest_board[0].x for corner in dest_board)

    out_scan = []
    if same_ys_top and same_ys_bottom:
        # iterate over dcm files (y axis in the ct scan)
        board_ys = [corner.y for corner in dest_board]
        for y_i, dcm in enumerate(ct_3d[min(board_ys):max(board_ys)]):

            # simplest case - all the corners of the flat are in the same z axis
            if same_zs:
                row = []
                # check the direction of the x-ray and set the z range for the integral calculation
                if dest_board[0].z > xray_source.z:
                    z_range = range(xray_source.z, dest_board[0].z)
                else:
                    z_range = reversed(range(xray_source.z + 1, dest_board[0].z - 1))

                # iterate over x axis in the dcm
                board_xs = [corner.x for corner in dest_board]
                for x_i in range(len(dcm[0][min(board_xs):max(board_xs)])):
                    new_pixel_val = 0
                    # iterate over z axis and find calculate the integral
                    for z_i in z_range:
                        pixel_val = dcm[z_i][x_i]
                        if pixel_val >= 0: # in the cone range
                            # calculate the integral
                            new_pixel_val += pixel_val

                    row.append(new_pixel_val)
                out_scan.append(row)

            # all the corners of the flat are in the same x axis
            elif same_xs:
                row = []
                # check the direction of the x-ray and set the x range for integral calculation
                if dest_board[0].x > xray_source.x:
                    x_range = range(xray_source.x, dest_board[0].x)
                else:
                    x_range = reversed(range(xray_source.x + 1, dest_board[0].x - 1))

                # iterate over z axis in the dcm
                board_zs = [corner.z for corner in dest_board]
                for z_i in range(len(dcm[min(board_zs):max(board_zs)])):
                    new_pixel_val = 0
                    # iterate over X axis and find calculate the integral
                    for x_i in x_range:
                        pixel_val = dcm[z_i][x_i]
                        if pixel_val >= 0: # in the cone range
                            # calculate the integral
                            new_pixel_val += pixel_val

                    row.append(new_pixel_val)
                out_scan.append(row)
            print(f'\t{int(y_i/len(ct_3d) * 100)} %\r')
            # sys.stdout.write(f'\t{int(y_i/len(ct_3d) * 100)} %\r')
            # sys.stdout.flush()

    return out_scan


def dcm2ct3D():
    # get_testdata_files() read files by default from this path
    ct_dir = "C:/Users/user/AppData/Roaming/Python/Python37" \
             "/site-packages/pydicom/data/test_files/CT_scan_dir/"

    # read all dcm file into ct matrix and order by slice location
    ct_dict = {}
    for i, file in enumerate(os.listdir(ct_dir)):
        filename = get_testdata_files(file)[0]
        dataset = pydicom.dcmread(filename)
        ct_dict[dataset.get('SliceLocation', "(missing)")] = dataset.pixel_array

    ordered_dict = collections.OrderedDict(sorted(ct_dict.items(), reverse=True))
    return [y_layer for y_layer in ordered_dict.values()]


if __name__ == '__main__':
    X_ray_source = Point3D(256, 162, 50)
    destination_board = [Point3D(0, 225, 500), Point3D(500, 225, 500),
                         Point3D(0, 0, 500), Point3D(500, 0, 500)]

    # X_ray_source = Point3D(50, 162, 256)
    # destination_board = [Point3D(500, 225, 0), Point3D(500, 225, 500),
    #                      Point3D(500, 0, 0), Point3D(500, 0, 500)]

    CT_3D = dcm2ct3D()

    Xray_2D = ct2xray(X_ray_source, destination_board, CT_3D)

    plt.imshow(Xray_2D, cmap=plt.cm.bone)
    plt.show()