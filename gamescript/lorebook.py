import pygame
import pygame.freetype

from gamescript.common import utility

from PIL import Image


class Lorebook(pygame.sprite.Sprite):
    concept_stat = None
    concept_lore = None
    history_stat = None
    history_lore = None

    faction_data = None
    troop_data = None
    leader_data = None
    battle_map_data = None
    preview_sprite_pool = None
    unit_state_text = None

    concept_section = 0
    history_section = 1
    faction_section = 2
    troop_section = 3
    equipment_section = 4
    status_section = 5
    skill_section = 6
    trait_section = 7
    leader_section = 8
    terrain_section = 9
    weather_section = 10
    leader_text = ("Detrimental", "Incompetent", "Inferior", "Unskilled", "Dull", "Average", "Decent", "Skilled",
                   "Master", "Genius", "Unmatched")

    def __init__(self, main_dir, screen_scale, screen_rect, image, textsize=24):
        """ Lorebook section: 0 = welcome/concept, 1 world history, 2 = faction, 3 = subunit, 4 = equipment, 5 = subunit status, 6 = subunit skill,
        7 = subunit trait, 8 = leader, 9 terrain, 10 = landmark"""
        self.main_dir = main_dir
        self.screen_rect = screen_rect
        self.screen_scale = screen_scale

        self._layer = 23
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("helvetica", int(textsize * self.screen_scale[1]))
        self.font_header = pygame.font.SysFont("oldenglishtext", int(52 * self.screen_scale[1]))
        self.image = image
        self.image_original = self.image.copy()
        self.section = 0
        self.subsection = 1  # subsection of that section e.g. swordmen subunit in subunit section
        self.stat_data = None  # for getting the section stat data
        self.lore_data = None  # for getting the section lore data
        self.current_subsection = None  # Subsection stat currently viewing
        self.current_subsection2 = None  # Subsection lore currently viewing
        self.subsection_list = None
        self.portrait = None
        self.preview_sprite = None

        # some sections get stat from multiple list, need to keep track of last item index
        self.equipment_stat = {}
        self.equipment_lore = {}
        self.skill_stat = {}
        self.skill_lore = {}
        self.section_list = ()

        self.current_subsection_row = 0
        self.max_row_show = 19
        self.row_size = 0
        self.page = 0
        self.max_page = 0
        self.rect = self.image.get_rect(center=(self.screen_rect.width / 1.9, self.screen_rect.height / 1.9))

    def change_ruleset(self):
        # Make new equipment list that contain all type weapon, armour, mount
        self.equipment_stat = {}
        run = 1
        for stat_list in (self.troop_data.weapon_list, self.troop_data.armour_list, self.troop_data.mount_list,
                          self.troop_data.mount_armour_list):
            for index in stat_list:
                if index != "ID":
                    self.equipment_stat[run] = stat_list[index]
                    run += 1

        self.equipment_lore = {}
        run = 1
        for stat_list in (self.troop_data.weapon_lore, self.troop_data.armour_lore, self.troop_data.mount_lore,
                          self.troop_data.mount_armour_lore):
            for index in stat_list:
                if index != "ID":
                    self.equipment_lore[run] = stat_list[index]
                    run += 1

        # Make new skill list that contain all troop and leader skills
        self.skill_stat = {}
        run = 1
        for stat_list in (self.troop_data.skill_list, self.leader_data.skill_list):
            for index in stat_list:
                if index != "ID":
                    self.skill_stat[run] = stat_list[index]
                    run += 1

        self.skill_lore = {}
        run = 1
        for stat_list in (self.troop_data.skill_lore, self.leader_data.skill_lore):
            for index in stat_list:
                if index != "ID":
                    self.skill_lore[run] = stat_list[index]
                    run += 1

        self.section_list = ((self.concept_stat, self.concept_lore), (self.history_stat, self.history_lore),
                             (self.faction_data.faction_list, self.faction_data.faction_lore),
                             (self.troop_data.troop_list, self.troop_data.troop_lore), (self.equipment_stat, self.equipment_lore),
                             (self.troop_data.status_list, self.troop_data.status_lore),
                             (self.skill_stat, self.skill_lore), (self.troop_data.trait_list, self.troop_data.trait_lore),
                             (self.leader_data.leader_list, self.leader_data.leader_lore),
                             (self.battle_map_data.feature_mod, self.battle_map_data.feature_mod_lore),
                             (self.battle_map_data.weather_data, self.battle_map_data.weather_lore))

    def change_page(self, page, page_button, main_ui, portrait=None):
        """Change page of the current subsection, either next or previous page"""
        self.page = page
        self.image = self.image_original.copy()  # reset encyclopedia image
        self.page_design()  # draw new pages

        # Add or remove next/previous page button
        if self.page >= self.max_page:  # remove next page button when reach last page
            main_ui.remove(page_button[1])
        else:
            main_ui.add(page_button[1])

        if self.page != 0:  # add previous page button when not at first page
            main_ui.add(page_button[0])
        else:
            main_ui.remove(page_button[0])
        # ^ End page button

    def change_section(self, section, list_surface, list_group, lore_scroll, page_button, main_ui):
        """Change to new section either by open encyclopedia or click section button"""
        self.portrait = None
        self.section = section  # get new section
        self.subsection = 1  # reset subsection to the first one
        self.stat_data = self.section_list[self.section][0]  # get new stat data of the new section
        self.lore_data = self.section_list[self.section][1]  # get new lore data of the new section
        self.max_page = 0  # reset max page
        self.current_subsection_row = 0  # reset subsection scroll to the top one
        this_list = list(self.stat_data.values())  # get list of subsection
        self.subsection_list = [name[0] if
                                type(name) is list and "Name" != name[0] else name["Name"] for name in
                                this_list]  # remove the header from subsection list
        if "Name" in self.subsection_list:
            self.subsection_list.remove("Name")
        self.row_size = len(self.subsection_list)  # get size of subsection list

        self.change_subsection(self.subsection, page_button, main_ui)
        self.setup_subsection_list(list_surface, list_group)

        lore_scroll.change_image(row_size=self.row_size)
        lore_scroll.change_image(new_row=self.current_subsection_row)

    def change_subsection(self, subsection, page_button, main_ui):
        self.subsection = subsection
        self.page = 0  # reset page to the first one
        self.image = self.image_original.copy()
        self.portrait = None  # reset portrait, possible for subsection to not have portrait
        main_ui.remove(page_button[0])
        main_ui.remove(page_button[1])
        self.max_page = 0  # some subsection may not have lore data in file (maxpage would be just 0)

        # Number of maximum page of lore for that subsection (4 para per page) and not count first one (name + description)
        if len(self.lore_data[self.subsection]) > 2:
            self.max_page = int((len(self.lore_data[subsection]) - 2) / 4)
            main_ui.add(page_button[1])

        if self.section == self.leader_section:  # leader section exclusive for now (will merge with other section when add portrait for others)
            try:
                image_name = str(self.subsection)
                self.portrait = self.leader_data.images[
                    image_name].copy()  # get leader portrait based on subsection number
            except KeyError:
                self.portrait = self.leader_data.images[
                    "9999999"].copy()  # Use Unknown leader image if there is none in list
                font = pygame.font.SysFont("timesnewroman", int(100 * self.screen_scale[1]))
                text_image = font.render(str(self.subsection), True, pygame.Color("white"))
                text_rect = text_image.get_rect(
                    center=(self.portrait.get_width() / 2, self.portrait.get_height() / 1.3))
                self.portrait.blit(text_image, text_rect)

            self.portrait = pygame.transform.scale(self.portrait, (int(200 * self.screen_scale[0]),
                                                                   int(200 * self.screen_scale[
                                                                       1])))

        elif self.section == self.troop_section:
            try:
                self.portrait = self.preview_sprite_pool[self.subsection]["sprite"].copy()

                self.portrait = pygame.transform.scale(self.portrait, (int(250 * self.screen_scale[0]),
                                                                       int(250 * self.screen_scale[
                                                                           1])))
            except KeyError:
                pass

        self.page_design()

    def setup_subsection_list(self, list_surface, list_group):
        """generate list of subsection of the left side of encyclopedia"""
        row = 15 * self.screen_scale[1]
        column = 15 * self.screen_scale[0]
        pos = list_surface.rect.topleft
        if self.current_subsection_row > self.row_size - self.max_row_show:
            self.current_subsection_row = self.row_size - self.max_row_show

        if len(list_group) > 0:  # remove previous subsection in the group before generate new one
            for stuff in list_group:
                stuff.kill()
                del stuff

        loop_list = [item for item in self.stat_data.keys() if type(item) != str]
        for index, item in enumerate(self.subsection_list):
            if index >= self.current_subsection_row:
                list_group.add(
                    SubsectionName(self.screen_scale, (pos[0] + column, pos[1] + row), item,
                                   loop_list[index]))  # add new subsection sprite to group
                row += (41 * self.screen_scale[1])  # next row
                if len(list_group) > self.max_row_show:
                    break  # will not generate more than space allowed

    def page_design(self):
        """Lore book format position of the text"""
        make_long_text = utility.make_long_text

        stat = self.stat_data[self.subsection]
        lore = self.lore_data[self.subsection]

        name = lore[0]
        description = lore[1]

        text_surface = self.font_header.render(str(name), True, (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(int(28 * self.screen_scale[0]), int(20 * self.screen_scale[1])))
        self.image.blit(text_surface, text_rect)  # add name of item to the top of page

        description_pos = (int(20 * self.screen_scale[1]), int(100 * self.screen_scale[0]))

        if self.portrait is not None:
            description_pos = (int(20 * self.screen_scale[1]), int(300 * self.screen_scale[0]))

            portrait_rect = self.portrait.get_rect(
                center=(int(300 * self.screen_scale[0]), int(200 * self.screen_scale[1])))
            self.image.blit(self.portrait, portrait_rect)

        description_surface = pygame.Surface((int(550 * self.screen_scale[0]), int(400 * self.screen_scale[1])),
                                             pygame.SRCALPHA)
        description_rect = description_surface.get_rect(topleft=description_pos)
        make_long_text(description_surface, description, (int(5 * self.screen_scale[1]), int(5 * self.screen_scale[0])),
                       self.font)
        self.image.blit(description_surface, description_rect)

        if self.page == 0:
            row = 350 * self.screen_scale[1]
            col = 60 * self.screen_scale[0]
            if self.portrait is not None:
                row = 600 * self.screen_scale[1]
                col = 60 * self.screen_scale[0]

            # concept, history, faction section is simply for processed and does not need specific column read
            if self.section in (self.concept_section, self.history_section, self.faction_section):
                for key, value in stat.items():
                    if key != "Description":
                        # blit text
                        if "IMAGE:" not in value:
                            text_surface = pygame.Surface(
                                (int(480 * self.screen_scale[1]), int(300 * self.screen_scale[0])), pygame.SRCALPHA)
                            text_rect = description_surface.get_rect(topleft=(col, row))
                            make_long_text(text_surface, str(value),
                                           (int(8 * self.screen_scale[1]), int(8 * self.screen_scale[0])), self.font)

                        # blit image instead of text
                        else:
                            if "FULLIMAGE:" in value:  # full image to whole two pages
                                filename = value[10:].split("\\")[-1]
                                text_surface = utility.load_image(self.main_dir, self.screen_scale, filename,
                                                                  value[10:].replace(filename, ""))
                                text_surface = pygame.transform.scale(text_surface,
                                                                      (self.image.get_width(), self.image.get_height()))
                                text_rect = description_surface.get_rect(topleft=(0, 0))
                            else:
                                filename = value[6:].split("\\")[-1]
                                text_surface = utility.load_image(self.main_dir, self.screen_scale, filename,
                                                                  value[6:].replace(filename, ""))
                                text_rect = description_surface.get_rect(topleft=(col, row))
                        self.image.blit(text_surface, text_rect)

                        row += (200 * self.screen_scale[1])
                        if row >= 750 * self.screen_scale[
                            1]:  # continue drawing on the right page after reaching the end of left page
                            if col == 520 * self.screen_scale[0]:  # already on the right page
                                break
                            else:
                                col = 650 * self.screen_scale[0]
                                row = 50 * self.screen_scale[1]

            # more complex section
            elif self.section in (
            self.troop_section, self.equipment_section, self.status_section, self.skill_section, self.trait_section,
            self.leader_section, self.terrain_section, self.weather_section):
                front_text = {key: value for key, value in stat.items() if
                              key not in ("Name", "Description", "Forcedimageid")}
                for key, value in front_text.items():
                    if value != "":
                        if self.section != self.equipment_section:  # equipment section need to be processed differently
                            create_text = key + ": " + str(value)
                            if key == "Ruleset":
                                create_text = ""
                            if self.section == self.troop_section or self.section == self.leader_section:  # troop section
                                if "Weapon" in key:  # weapon text with quality
                                    create_text = key + ": " + self.troop_data.equipment_grade_list[value[1]]["Name"] \
                                                  + " " + self.troop_data.weapon_list[value[0]]["Name"]

                                elif key == "Armour":  # armour text with quality
                                    create_text = key + ": " + self.troop_data.equipment_grade_list[value[1]]["Name"] \
                                                  + " " + self.troop_data.armour_list[value[0]]["Name"]

                                elif key == "Race":
                                    create_text = key + ": " + self.troop_data.race_list[value]["Name"]

                                elif key == "Mount":  # mount text with grade
                                    create_text = key + ": " + self.troop_data.mount_grade_list[value[1]][
                                        "Name"] + " " + \
                                                  self.troop_data.mount_list[value[0]]["Name"] + "//" + \
                                                  self.troop_data.mount_armour_list[value[2]]["Name"]
                                    if self.troop_data.mount_list[value[0]]["Name"] == "None":
                                        create_text = ""
                                        pass

                                elif key == "Trait":  # troop properties list
                                    trait_list = ""
                                    if 0 not in value:
                                        for this_text in value:
                                            if this_text in self.troop_data.trait_list:  # in case user put in trait not existed in ruleset
                                                trait_list += self.troop_data.trait_list[this_text]["Name"] + ", "
                                        trait_list = trait_list[0:-2]
                                        create_text = key + ": " + trait_list

                                    else:
                                        create_text = ""
                                        pass

                                if self.section == self.troop_section:  # troop section
                                    if key == "Grade":  # grade text instead of number
                                        create_text = key + ": " + self.troop_data.grade_list[value]["Name"]

                                    elif key == "Troop Type":
                                        create_text = key + ": " + self.troop_data.troop_class_list[value]["Name"]

                                    elif "Skill" in key:  # skill text instead of number
                                        skill_list = ""
                                        if key == "Charge Skill":
                                            if value in self.troop_data.skill_list:  # only include skill if exist in ruleset
                                                skill_list += self.troop_data.skill_list[value]["Name"]
                                            create_text = key + ": " + skill_list
                                            # + ", Base Speed: " + str(speed)  # add subunit speed after
                                        elif 0 not in value:
                                            for this_text in value:
                                                if this_text in self.troop_data.skill_list:  # only include skill in ruleset
                                                    skill_list += self.troop_data.skill_list[this_text]["Name"] + ", "
                                            skill_list = skill_list[0:-2]
                                            create_text = key + ": " + skill_list
                                        else:
                                            create_text = ""
                                            pass

                                    elif key == "Role":  # Replace imageid to subunit role in troop section
                                        role_list = {0: "None", 1: "Offensive", 2: "Defensive", 3: "Skirmisher",
                                                     4: "Shock", 5: "Support", 6: "Magic",
                                                     7: "Ambusher", 8: "Sniper", 9: "Recon", "": ""}
                                        role = [role_list[item] for item in
                                                value]  # role is not type, it represents subunit classification from base stat to tell what it excels
                                        create_text = "Specilaised Role: "
                                        if len(role) == 0:
                                            create_text += "None, "
                                        for this_role in role:
                                            create_text += this_role + ", "
                                        create_text = create_text[0:-2]

                                    elif key == "Type":
                                        create_text = ""
                                        pass

                                else:  # leader section
                                    if key in ("Melee Command", "Range Command", "Cavalry Command", "Combat"):
                                        create_text = key + ": " + self.leader_text[value]

                                    elif key == "Social Class":
                                        create_text = key + ": " + self.leader_data.leader_class[value][
                                            "Leader Social Class"]

                                    elif key == "Skill":  # skill text instead of number
                                        skill_list = ""
                                        if 0 not in value:
                                            for this_text in value:
                                                if this_text in self.leader_data.skill_list:  # only include skill in ruleset
                                                    skill_list += self.leader_data.skill_list[this_text]["Name"] + ", "
                                            skill_list = skill_list[0:-2]
                                            create_text = key + ": " + skill_list
                                        else:
                                            create_text = ""
                                            pass

                                    elif key == "Formation":
                                        create_text = key + ": " + str(value).replace("[", "").replace("]", ""). \
                                            replace("'", "")

                            elif self.section in (self.skill_section, self.trait_section, self.status_section):
                                if key == "Status" or key == "Enemy Status":  # status list
                                    status_list = ""
                                    if 0 not in value:
                                        for this_text in value:
                                            if this_text in self.troop_data.status_list:  # in case user put in trait not existed in ruleset
                                                status_list += self.troop_data.status_list[this_text]["Name"] + ", "
                                        status_list = status_list[0:-2]
                                        create_text = key + ": " + status_list
                                    else:
                                        create_text = ""
                                        pass
                                if self.section == self.skill_section:
                                    if key == "Restriction" or key == "Condition":  # skill restriction and condition
                                        state_list = ""
                                        if value != "":
                                            for this_text in value:
                                                state_list += self.unit_state_text[this_text] + ", "
                                            state_list = state_list[0:-2]  # remove the last ", "
                                            create_text = key + ": " + state_list
                                        else:
                                            create_text = ""
                                            pass

                                    elif key == "Troop Type":
                                        create_text = key + ": " + ("Any", "Infantry", "Cavalry")[value]

                                if value in (0, 1):
                                    create_text = ""

                        else:  # equipment section, header depends on equipment type
                            create_text = key + ": " + str(value)

                            if key == "ImageID":  # not used in encyclopedia
                                create_text = ""
                                pass

                            elif key == "Properties":
                                trait_list = ""
                                if 0 not in value:
                                    for this_text in value:
                                        if this_text in self.troop_data.trait_list:  # in case user put in trait not existed in ruleset
                                            trait_list += self.troop_data.trait_list[this_text][0] + ", "
                                    trait_list = trait_list[0:-2]
                                    create_text = key + ": " + trait_list
                                else:
                                    create_text = ""
                                    pass

                        if create_text != "":  # text not empty, draw it. Else do nothing
                            text_surface = self.font.render(create_text, True, (0, 0, 0))
                            text_rect = text_surface.get_rect(topleft=(col, row))
                            self.image.blit(text_surface, text_rect)
                            row += (30 * self.screen_scale[1])
                            if row >= 750 * self.screen_scale[1]:
                                col = 650 * self.screen_scale[0]
                                row = 50 * self.screen_scale[1]

        else:  # lore page, the paragraph can be in text or image (IMAGE:)
            if self.max_page != 0:
                if self.page == 1:  # first page skip first two paragraph (name and description)
                    lore = self.lore_data[self.subsection][2:]
                else:
                    lore = self.lore_data[self.subsection][(self.page * 4) + 2:]
                row = 420 * self.screen_scale[1]
                col = 60 * self.screen_scale[0]
                for index, text in enumerate(lore):
                    if text != "":
                        # blit paragraph of text
                        if "IMAGE:" not in text:
                            text_surface = pygame.Surface((500 * self.screen_scale[0], 300 * self.screen_scale[1]),
                                                          pygame.SRCALPHA)
                            make_long_text(text_surface, text, (5 * self.screen_scale[0], 5 * self.screen_scale[1]),
                                           self.font)
                            text_rect = description_surface.get_rect(topleft=(col, row))

                        # blit image
                        else:
                            if "FULLIMAGE:" in text:
                                filename = text[10:].split("\\")[-1]
                                text_surface = utility.load_image(self.main_dir, self.screen_scale, filename,
                                                                  text[10:].replace(filename, ""))
                                text_surface = pygame.transform.scale(text_surface,
                                                                      (self.image.get_width(), self.image.get_height()))
                                text_rect = description_surface.get_rect(topleft=(0, 0))
                            else:
                                filename = text[6:].split("\\")[-1]
                                text_surface = utility.load_image(self.main_dir, self.screen_scale, filename,
                                                                  text[6:].replace(filename, ""))
                                text_rect = description_surface.get_rect(topleft=(col, row))
                        self.image.blit(text_surface, text_rect)

                        row += (280 * self.screen_scale[1])
                        if row >= 600 * self.screen_scale[1]:
                            if col == 650 * self.screen_scale[0]:
                                break
                            else:
                                col = 650 * self.screen_scale[0]
                                row = 50 * self.screen_scale[1]


class SubsectionList(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 23
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.rect = self.image.get_rect(topright=pos)
        self.max_row_show = 19


class SubsectionName(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, name, subsection, text_size=28):
        self._layer = 24
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(text_size * screen_scale[1]))
        self.image = pygame.Surface((int(240 * screen_scale[0]), int(40 * screen_scale[1])))  # black corner
        self.image.fill((0, 0, 0))

        # v White body square
        small_image = pygame.Surface((int(230 * screen_scale[0]), int(34 * screen_scale[1])))
        small_image.fill((255, 255, 255))
        small_rect = small_image.get_rect(topleft=(int(1 * screen_scale[0]), int(1 * screen_scale[1])))
        self.image.blit(small_image, small_rect)
        # ^ End white body

        # v Subsection name text
        text_surface = self.font.render(str(name), True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(int(3 * screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        # ^ End subsection name

        self.subsection = subsection
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)


# class Selectionbox(pygame.sprite.Sprite):
#     def __init__(self, pos, lorebook):
#         self._layer = 13
#         pygame.sprite.Sprite.__init__(self, self.containers)
#         self.image = pygame.Surface(300, lorebook.image.get_height())


# class Searchbox(pygame.sprite.Sprite):
#     def __init__(self, text_size=16):
#         self._layer = 14
#         pygame.sprite.Sprite.__init__(self, self.containers)
#         self.font = pygame.font.SysFont("helvetica", text_size)
#         self.image = pygame.Surface(100, 50)
#         self.text = ""
#         self.text_surface = self.font.render(str(self.text), 1, (0, 0, 0))
#         self.text_rect = self.text_surface.get_rect(centerleft=(3, self.image.get_height() / 2))
#
#     def textchange(self, input):
#         newcharacter = pygame.key.name(input)
#         self.text += newcharacter

def lorebook_process(self, ui, mouse_up, mouse_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    """Lorebook user interaction"""
    command = None
    close = False
    if mouse_up or mouse_down:  # mouse down (hold click) only for subsection list scroll
        if mouse_up:
            for button in self.lore_button_ui:
                if button in ui and button.rect.collidepoint(self.mouse_pos):  # click button
                    if button.event in range(0, 11):  # section button
                        self.encyclopedia.change_section(button.event, self.lore_name_list, self.subsection_name,
                                                         self.lore_name_list.scroll,
                                                         self.page_button, ui)  # change to section of that button

                    elif button.event == "close" or esc_press:  # Close button
                        close = True

                    elif button.event == "previous":  # Previous page button
                        self.encyclopedia.change_page(self.encyclopedia.page - 1, self.page_button,
                                                      ui)  # go back 1 page

                    elif button.event == "next":  # Next page button
                        self.encyclopedia.change_page(self.encyclopedia.page + 1, self.page_button,
                                                      ui)  # go forward 1 page

                    break  # found clicked button, break loop

        if self.lore_name_list.scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
            self.encyclopedia.current_subsection_row = self.lore_name_list.scroll.player_input(
                self.mouse_pos)  # update the scroll and get new current subsection
            self.encyclopedia.setup_subsection_list(self.lore_name_list,
                                                    self.subsection_name)  # update subsection name list
        else:
            if mouse_up:
                for name in self.subsection_name:
                    if name.rect.collidepoint(self.mouse_pos):  # click on subsection name
                        self.encyclopedia.change_subsection(name.subsection, self.page_button, ui)  # change subsection
                        break  # found clicked subsection, break loop

    elif mouse_scroll_up:
        if self.lore_name_list.rect.collidepoint(self.mouse_pos):  # Scrolling at lore book subsection list
            self.encyclopedia.current_subsection_row -= 1
            if self.encyclopedia.current_subsection_row < 0:
                self.encyclopedia.current_subsection_row = 0
            else:
                self.encyclopedia.setup_subsection_list(self.lore_name_list, self.subsection_name)
                self.lore_name_list.scroll.change_image(new_row=self.encyclopedia.current_subsection_row)

    elif mouse_scroll_down:
        if self.lore_name_list.rect.collidepoint(self.mouse_pos):  # Scrolling at lore book subsection list
            self.encyclopedia.current_subsection_row += 1
            if self.encyclopedia.current_subsection_row + self.encyclopedia.max_row_show - 1 < self.encyclopedia.row_size:
                self.encyclopedia.setup_subsection_list(self.lore_name_list, self.subsection_name)
                self.lore_name_list.scroll.change_image(new_row=self.encyclopedia.current_subsection_row)
            else:
                self.encyclopedia.current_subsection_row -= 1

    if close or esc_press:
        ui.remove(self.encyclopedia, *self.lore_button_ui, self.lore_name_list.scroll,
                  self.lore_name_list)  # remove encyclopedia related sprites
        for name in self.subsection_name:  # remove subsection name
            name.kill()
            del name
        command = "exit"

    return command
