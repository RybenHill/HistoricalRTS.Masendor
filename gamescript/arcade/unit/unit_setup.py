import numpy as np

from gamescript.common import utility

rotation_xy = utility.rotation_xy

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier


def leader_position_check(self, subunit_array):
    """
    Find position of leader
    :param self: Battle object
    :param subunit_array: Array of subunit
    :return: leader_position: Number position of leader from top left, return as tuple to make it compatible with other modes
    """
    leader_position = 0
    for row in subunit_array:
        for stuff in row:
            if stuff == "h":
                break
            elif stuff != "0":
                leader_position += 1
        else:
            continue
        break
    return (leader_position, )


def split_new_unit(self):
    """Split unit not existed in arcade mode"""
    pass


def setup_frontline(self):
    """
    Setup frontline array
    :param self: unit object
    """

    # v check if completely empty side row/col, then delete and re-adjust array
    stop_loop = False
    while stop_loop is False:  # loop until no longer find completely empty row/col
        stop_loop = True
        who_array = self.subunit_list
        full_who_array = [who_array, np.fliplr(who_array.swapaxes(0, 1)), np.rot90(who_array),
                        np.fliplr([who_array])[0]]  # rotate the array based on the side
        who_array = [who_array[0], full_who_array[1][0], full_who_array[2][0], full_who_array[3][0]]
        for index, who_frontline in enumerate(who_array):
            if any(subunit != 0 for subunit in who_frontline) is False:  # has completely empty outer row or column, remove them
                if index == 0:  # front side
                    self.subunit_list = self.subunit_list[1:]
                    for subunit in self.subunits:
                        subunit.unit_position = (subunit.unit_position[0], subunit.unit_position[1] - (self.image_size[1] / 8))
                elif index == 1:  # left side
                    self.subunit_list = np.delete(self.subunit_list, 0, 1)
                    for subunit in self.subunits:
                        subunit.unit_position = (subunit.unit_position[0] - (self.image_size[0] / 8), subunit.unit_position[1])
                elif index == 2:  # right side
                    self.subunit_list = np.delete(self.subunit_list, -1, 1)
                elif index == 3:  # rear side
                    self.subunit_list = np.delete(self.subunit_list, -1, 0)

                if len(self.subunit_list) > 0:  # still has row left
                    old_width_box, old_height_box = self.base_width_box, self.base_height_box
                    self.base_width_box, self.base_height_box = len(self.subunit_list[0]) * (self.image_size[0] + 10) / 20, \
                                                                len(self.subunit_list) * (self.image_size[1] + 2) / 20

                    number_pos = (self.base_pos[0] - self.base_width_box,
                                  (self.base_pos[1] + self.base_height_box))  # find position for number text
                    self.number_pos = rotation_xy(self.base_pos, number_pos, self.radians_angle)
                    self.change_pos_scale()

                    old_width_box = old_width_box - self.base_width_box
                    old_height_box = old_height_box - self.base_height_box
                    if index == 0:  # front
                        new_pos = (self.base_pos[0], self.base_pos[1] + old_height_box)
                    elif index == 1:  # left
                        new_pos = (self.base_pos[0] + old_width_box, self.base_pos[1])
                    elif index == 2:  # right
                        new_pos = (self.base_pos[0] - old_width_box, self.base_pos[1])
                    else:  # rear
                        new_pos = (self.base_pos[0], self.base_pos[1] - old_height_box)
                    self.base_pos = rotation_xy(self.base_pos, new_pos, self.radians_angle)
                    self.last_base_pos = self.base_pos

                    front_pos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
                    self.front_pos = rotation_xy(self.base_pos, front_pos, self.radians_angle)
                stop_loop = False
    # ^ End check completely empty row

    got_another = True  # keep finding another subunit while true

    for index, who_frontline in enumerate(who_array):
        new_frontline = who_frontline.copy()
        dead = np.where((new_frontline == 0))  # replace the dead in frontline with other subunit in the same column
        for dead_subunit in dead[0]:
            run = 0
            while got_another:
                if full_who_array[index][run, dead_subunit] != 0:
                    new_frontline[dead_subunit] = full_who_array[index][run, dead_subunit]
                    got_another = False
                else:
                    run += 1
                    if len(full_who_array[index]) == run:
                        new_frontline[dead_subunit] = 0
                        got_another = False
            got_another = True  # reset for another loop
        empty_array = new_frontline
        new_frontline = empty_array.copy()

        self.frontline[index] = new_frontline

    self.frontline_object = self.frontline.copy()  # frontline array as object instead of index
    for array_index, who_frontline in enumerate(list(self.frontline.values())):
        self.frontline_object[array_index] = self.frontline_object[array_index].tolist()
        for index, stuff in enumerate(who_frontline):
            for subunit in self.subunits:
                if subunit.game_id == stuff:
                    self.frontline_object[array_index][index] = subunit
                    break

    for subunit in self.subunits:  # assign frontline variable to subunit for only front side
        subunit.frontline = False
        if subunit in self.frontline_object[0]:
            subunit.frontline = True

    self.auth_penalty = 0
    for subunit in self.subunits:
        if subunit.state != 100:
            self.auth_penalty += subunit.auth_penalty  # add authority penalty of all alive subunit

