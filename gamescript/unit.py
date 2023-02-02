import math
import os
import random
from pathlib import Path

import numpy as np
import pygame
import pygame.freetype

from gamescript.common import utility

rotation_xy = utility.rotation_xy

team_colour = {0: (200, 200, 200), 1: (144, 167, 255), 2: (255, 114, 114)}  # team colour, Neutral, 1, 2

script_dir = os.path.split(os.path.abspath(__file__))[0] + "/"


class Unit(pygame.sprite.Sprite):
    empty_method = utility.empty_method

    battle = None
    form_change_timer = 10

    set_rotate = utility.set_rotate

    # Import from common.unit
    assign_commander = empty_method
    cal_unit_stat = empty_method
    change_formation = empty_method
    enter_battle = empty_method
    find_retreat_target = empty_method
    placement = empty_method
    retreat_command = empty_method
    selection = empty_method
    set_target = empty_method
    setup_formation = empty_method
    setup_subunit_position_list = empty_method
    shift_line = empty_method
    subunit_formation_change = empty_method

    # Import from *genre*.unit
    authority_recalculation = empty_method
    change_pos_scale = empty_method
    check_split = empty_method
    destroyed = empty_method
    issue_order = empty_method
    morale_check_logic = empty_method
    movement_logic = empty_method
    player_input = empty_method
    reposition_leader = empty_method
    revert_move = empty_method
    rotate_logic = empty_method
    set_subunit_target = empty_method
    setup_stat = empty_method
    split_unit = empty_method
    state_reset_logic = empty_method
    swap_weapon_command = empty_method
    switch_faction = empty_method
    transfer_leader = empty_method
    unit_ai = empty_method

    for entry in os.scandir(Path(script_dir + "/common/unit/")):  # load and replace modules from common.unit
        if entry.is_file():
            if ".py" in entry.name:
                file_name = entry.name[:-3]
            elif ".pyc" in entry.name:
                file_name = entry.name[:-4]
            exec(f"from gamescript.common.unit import " + file_name)
            exec(f"" + file_name + " = " + file_name + "." + file_name)

    # Variable from *genre*.genre_setting
    max_unit_size = None
    order_to_place = None

    # Variable from troop_data that got added during change_ruleset function
    unit_formation_list = {}

    def __init__(self, game_id, start_pos, subunit_list, colour, player_control, coa, commander, start_angle,
                 start_hp=100, start_stamina=100, team=0):
        """Unit object represent a group of subunits, each unit can contain a specific number of subunits
        depending on the genre setting"""
        pygame.sprite.Sprite.__init__(self, self.containers)  # class unit as sprite for updater
        self.icon = None  # for linking with army selection ui, got linked when icon created in game_ui.ArmyIcon
        self.team_commander = None  # commander leader
        self.start_where = []
        self.subunit_list = []
        self.alive_subunit_list = []
        self.subunit_object_array = np.full(self.max_unit_size, None)
        self.subunit_id_array = subunit_list  # troop id array, will be converted to subunit game id array when creating subunit in generate_unit, must not contain empty row or column unlike subunit_object_array
        self.subunit_hitbox_size_array = np.full(self.max_unit_size, self.battle.subunit_hitbox_size)
        self.leader = []
        self.leader_subunit = None  # subunit that the main unit leader is in, get added in leader first update
        self.nearby_enemy = {}  # list dict of nearby enemy unit, sorted by distance
        self.game_id = game_id  # id of unit for reference in many function
        self.player_control = player_control  # player control or not
        self.start_hp = start_hp  # starting hp percentage
        self.start_stamina = start_stamina  # starting stamina percentage
        self.colour = colour  # box colour according to team
        self.commander = commander  # True if commander unit

        self.max_camera_zoom = self.battle.max_camera_zoom  # closest zoom allowed
        self.camera_zoom = self.max_camera_zoom  # start with the closest zoom

        self.screen_scale = self.battle.screen_scale
        self.map_corner = self.battle.map_corner

        self.base_pos = pygame.Vector2(start_pos)  # base_pos is for true pos that is used for battle calculation
        self.base_attack_pos = None  # position of attack base_target
        self.angle = start_angle  # start at this angle
        if self.angle == 360:  # 360 is 0 angle at the start, not doing this cause angle glitch when self start
            self.angle = 0
        self.new_angle = self.angle
        self.radians_angle = math.radians(
            360 - start_angle)  # radians for apply angle to position and subunit

        self.unit_box_width = 0
        self.unit_box_height = 0

        self.front_pos = (0, 0)  # front position of unit
        self.base_target = self.front_pos
        self.command_target = self.front_pos
        self.base_number_pos = (0, 0)  # position for number text
        self.change_pos_scale()

        # Setup default behaviour check # TODO add volley, divide behaviour ui into 3 types: combat, shoot, other (move)
        self.formation = "Original"
        self.formation_phase = "Skirmish Phase"
        self.formation_style = "Cavalry Flank"
        self.next_rotate = False
        self.selected = False  # for checking if it currently selected or not
        self.just_selected = False  # for light up subunit when click
        self.camera_zoom_change = False
        self.revert = False
        self.move_rotate = False  # for checking if the movement require rotation first or not
        self.rotate_cal = 0  # for calculate how much angle to rotate to the base_target
        self.rotate_check = 0  # for checking if the new angle rotate pass the base_target angle or not
        self.just_split = False  # subunit just got split
        self.leader_change = False
        self.direction_arrow = False
        self.rotate_only = False  # Order unit to rotate to base_target direction
        self.charging = False  # For subunit charge skill activation
        self.forced_melee = False  # Force unit to melee attack
        self.attack_place = False  # attack position instead of enemy
        self.retreat_start = False
        self.retreat_way = False
        self.broken = False
        self.collide = False  # for checking if subunit collide, if yes then stop moving
        self.attack_target = None  # attack base_target, can be either int or unit object
        self.got_killed = False  # for checking if destroyed() was performed when subunit destroyed yet
        self.forced_march = False
        self.change_faction = False  # For initiating change faction function
        self.input_delay = 0

        self.run_toggle = 0  # 0 = double right click to run, 1 = only one right click will make unit run
        self.shoot_mode = 0  # 0 = direct shot first if not able then try arc shot, 1 = No arc shot
        self.attack_mode = 0  # 10 = formation attack, 1 = free for all attack,
        self.hold = 0  # 0 = not hold, 1 = skirmish/scout/avoid, 2 = hold
        self.fire_at_will = 0  # 0 = fire at will, 1 = no fire

        # Setup default starting value
        self.troop_number = 0  # sum
        self.stamina = 0  # average from all subunit
        self.morale = 0  # average from all subunit
        self.ammo = 0  # total magazine_left left of the whole unit
        self.old_ammo = 0  # previous number of magazine_left for magazine_left bar checking
        self.min_range = 0  # minimum shoot range of all subunit inside this unit
        self.max_range = 0  # maximum shoot range of all subunit inside this unit
        self.use_min_range = 0  # use min or max range for walk/run (range) command
        self.skill_cond = 0  # skill condition for stamina reservation
        self.state = 0  # see battle_ui.py topbar for name of each state
        self.command_state = self.state
        self.dead_change = False  # for checking when subunit dead and run related code
        self.timer = random.random()
        self.state_delay = 3  # some state has delay before can change state, default at 3 seconds
        self.rotate_speed = 1

        # check if unit can split
        self.can_split_row = False
        if np.array_split(self.subunit_id_array, 2)[0].size > 10 and np.array_split(self.subunit_id_array, 2)[
            1].size > 10:
            self.can_split_row = True

        self.can_split_col = False
        if np.array_split(self.subunit_id_array, 2, axis=1)[0].size > 10 and \
                np.array_split(self.subunit_id_array, 2, axis=1)[1].size > 10:
            self.can_split_col = True

        self.authority = 0
        self.auth_penalty = 0  # authority penalty

        self.tactic_effect = {}
        self.coa = coa  # coat of arm image

        self.team = team  # team

        self.subunit_position_list = []

        self.battle.all_team_unit["alive"].add(self)
        self.subunit_type_count = {0: 0, 1: 0,  # melee and range infantry
                                   2: 0, 3: 0}  # melee and range cavalry
        self.ally_pos_list = {}
        self.enemy_pos_list = {}

        self.movement_queue = []

    def update(self, weather, squad_group, dt, camera_zoom, mouse_pos, mouse_up):
        if self.camera_zoom != camera_zoom:  # camera zoom change
            self.camera_zoom_change = True
            if self.camera_zoom == self.max_camera_zoom:  # revert to default layer at further zoom
                for subunit in self.alive_subunit_list:
                    self.battle.battle_camera.change_layer(subunit, 4)
            self.camera_zoom = camera_zoom  # save scale
            self.change_pos_scale()  # update position according to new scale

        if self.dead_change:  # setup frontline again when any subunit destroyed
            if self.alive_subunit_list:
                self.setup_formation()
                self.auth_penalty = 0
                for subunit in self.alive_subunit_list:
                    self.auth_penalty += subunit.auth_penalty  # add authority penalty of all alive subunit
                    subunit.base_morale -= (30 * subunit.mental)
                self.dead_change = False

            else:  # Unit enter dead state when no more troop left
                self.stamina, self.morale, self.speed = 0, 0, 0

                for leader in self.leader:  # leader retreat
                    if leader.state < 90:  # Leaders flee when unit destroyed
                        leader.state = 96
                        leader.gone()

                self.state = 100

        if self.state != 100:
            self.ally_pos_list[self] = self.base_pos  # update current position to team position list
            self.battle.team_pos_list["alive"][self] = self.base_pos

            self.selection()

            if dt > 0:  # Set timer for complex calculation that cannot happen every loop as it drop too much fps
                self.timer += dt
                if self.input_delay > 0:  # delay for command input
                    self.input_delay -= dt
                    if self.input_delay < 0:
                        self.input_delay = 0
                if self.timer >= 1:
                    self.setup_stat()

                    # Find near enemy base_target
                    self.nearby_enemy = {}  # Near base_target is enemy that is nearest
                    for team in self.enemy_pos_list.values():
                        for n, enemy_pos in team.items():
                            self.nearby_enemy[n] = pygame.Vector2(enemy_pos).distance_to(self.base_pos)
                    self.nearby_enemy = {k: v for k, v in sorted(self.nearby_enemy.items(),
                                                                 key=lambda item: item[1])}  # sort to the closest one
                    for n in self.enemy_pos_list:
                        self.nearby_enemy[n] = self.enemy_pos_list[
                            n]  # change back near base_target list value to vector with sorted order

                    self.state_reset_logic()

                    self.timer -= 1  # reset timer, not to 0 because higher speed can cause inconsistency in update timing

                if self.leader_change:  # recal stat involve leader if one destroyed
                    self.authority_recalculation()
                    self.command_buff = ((self.leader[0].melee_command - 5) * 0.1,
                                         (self.leader[0].range_command - 5) * 0.1,
                                         (self.leader[0].cav_command - 5) * 0.1)
                    self.leader_change = False

                self.unit_ai()

                if self.authority <= 0:  # unit disobey
                    self.state = 95
                    if random.randint(0, 100) == 100 and self.leader[0].state < 90:  # chance to recover
                        self.leader[0].authority += 20
                        self.authority_recalculation()

                self.morale_check_logic()

                self.rotate_logic(dt)  # Rotate Function

                self.movement_logic()

        else:  # destroyed unit
            if self.got_killed is False:
                self.destroyed(self.battle)
                self.battle.event_log.add_log((0, str(self.leader[0].name) + "'s unit is destroyed"),
                                              (0, 1))  # put destroyed event in troop and army log
