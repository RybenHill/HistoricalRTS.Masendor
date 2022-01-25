import ast
import csv
import datetime
import math
import os
import re

import pygame
import pygame.freetype
from gamescript import battleui, menu, popup


def change_group(item, group, change):
    if change == "add":
        group.add(item)
    elif change == "remove":
        group.remove(item)


def load_image(main_dir, screen_scale, file, subfolder=""):
    """loads an image, prepares it for play"""
    new_subfolder = subfolder
    if isinstance(new_subfolder, list):
        new_subfolder = ""
        for folder in subfolder:
            new_subfolder = os.path.join(new_subfolder, folder)
    this_file = os.path.join(main_dir, "data", new_subfolder, file)
    surface = pygame.image.load(this_file).convert_alpha()
    surface = pygame.transform.scale(surface, (surface.get_width() * screen_scale[0], surface.get_height() * screen_scale[1]))
    return surface


def load_images(main_dir, screen_scale, subfolder=None, load_order=True, return_order=False):
    """loads all images(files) in folder using loadorder list file use only png file"""
    images = {}
    dir_path = os.path.join(main_dir, "data")
    if subfolder is not None:
        for folder in subfolder:
            dir_path = os.path.join(dir_path, folder)

    if load_order:  # load in the order of load_order file
        load_order_file = open(os.path.join(dir_path, "load_order.txt"), "r")
        load_order_file = ast.literal_eval(load_order_file.read())
    else:  # load every file
        load_order_file = [f for f in os.listdir(dir_path) if f.endswith("." + "png")]  # read all file
        try:  # sort file name if all in number only
            load_order_file.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
        except TypeError:  # has character in file name
            pass
    for file in load_order_file:
        images[file] = load_image(main_dir, screen_scale, file, dir_path)

    if return_order is False:
        return images
    else:  # return order of the file as list
        load_order_file = [int(name.replace(".png", "")) for name in load_order_file]
        return images, load_order_file


def convert_str_time(event):
    for index, item in enumerate(event):
        new_time = datetime.datetime.strptime(item[1], "%H:%M:%S").time()
        new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
        event[index] = [item[0], new_time]
        if len(item) == 3:
            event[index].append(item[2])


def csv_read(maindir, file, subfolder=(), output_type=0):
    """output type 0 = dict, 1 = list"""
    main_dir = maindir
    return_output = {}
    if output_type == 1:
        return_output = []

    folder_dir = ""
    for folder in subfolder:
        folder_dir = os.path.join(folder_dir, folder)
    folder_dir = os.path.join(folder_dir, file)
    folder_dir = os.path.join(main_dir, folder_dir)
    with open(folder_dir, encoding="utf-8", mode="r") as edit_file:
        rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None):
                    row[n] = int(i)
            if output_type == 0:
                return_output[row[0]] = row[1:]
            elif output_type == 1:
                return_output.append(row)
        edit_file.close()
    return return_output


def load_sound(main_dir, file):
    file = os.path.join(main_dir, "data", "sound", file)
    sound = pygame.mixer.Sound(file)
    return sound


def edit_config(section, option, value, filename, config):
    config.set(section, option, value)
    with open(filename, "w") as configfile:
        config.write(configfile)


def make_long_text(surface, text, pos, font, color=pygame.Color("black")):
    """Blit long text into separate row of text"""
    if type(text) != list:
        text = [text]
    x, y = pos
    for this_text in text:
        words = [word.split(" ") for word in str(this_text).splitlines()]  # 2D array where each row is a list of words
        space = font.size(" ")[0]  # the width of a space
        max_width, max_height = surface.get_size()
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # reset x
                    y += word_height  # start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # reset x
            y += word_height  # start on new row


def make_bar_list(main_dir, screen_scale, list_to_do, menu_image):
    """Make a drop down bar list option button"""
    bar_list = []
    image = load_image(main_dir, screen_scale, "bar_normal.jpg", "ui\\mainmenu_ui")
    image2 = load_image(main_dir, screen_scale, "bar_mouse.jpg", "ui\\mainmenu_ui")
    image3 = image2
    for index, bar in enumerate(list_to_do):
        bar_image = (image.copy(), image2.copy(), image3.copy())
        bar = menu.MenuButton(screen_scale, images=bar_image,
                              pos=(menu_image.pos[0], menu_image.pos[1] + image.get_height() * (index + 1)), text=bar)
        bar_list.append(bar)
    return bar_list


def load_base_button(main_dir, screen_scale):
    image = load_image(main_dir, screen_scale, "idle_button.png", ["ui", "mainmenu_ui"])
    image2 = load_image(main_dir, screen_scale, "mouse_button.png", ["ui", "mainmenu_ui"])
    image3 = load_image(main_dir, screen_scale, "click_button.png", ["ui", "mainmenu_ui"])
    return [image, image2, image3]


def text_objects(text, font):
    text_surface = font.render(text, True, (200, 200, 200))
    return text_surface, text_surface.get_rect()


def trait_skill_blit(self):
    """For blitting skill and trait icon into subunit info ui"""
    screen_rect = self.screen_rect

    position = self.troop_card_ui.rect.topleft
    position = [position[0] + 70, position[1] + 60]  # start position
    start_row = position[0]

    for icon in self.skill_icon.sprites():
        icon.kill()

    for trait in self.troop_card_ui.value2[0]:
        self.skill_icon.add(
            battleui.SkillCardIcon(self.trait_images[0], (position[0], position[1]), 0,
                                   game_id=trait))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= screen_rect.width:
            position[1] += 30
            position[0] = start_row

    position = self.troop_card_ui.rect.topleft
    position = [position[0] + 70, position[1] + 100]
    start_row = position[0]

    for skill in self.troop_card_ui.value2[1]:
        self.skill_icon.add(
            battleui.SkillCardIcon(self.skill_images[0], (position[0], position[1]), 1,
                                   game_id=skill))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= screen_rect.width:
            position[1] += 30
            position[0] = start_row


def effect_icon_blit(self):
    """For blitting all status effect icon"""
    screen_rect = self.screen_rect

    position = self.troop_card_ui.rect.topleft
    position = [position[0] + 70, position[1] + 140]
    start_row = position[0]

    for icon in self.effect_icon.sprites():
        icon.kill()

    for status in self.troop_card_ui.value2[4]:
        self.effect_icon.add(battleui.SkillCardIcon(self.status_images[0], (position[0], position[1]), 4, game_id=status))
        position[0] += 40
        if position[0] >= screen_rect.width:
            position[1] += 30
            position[0] = start_row


def countdown_skill_icon(self):
    """Count down timer on skill icon for activate and cooldown time"""
    for skill in self.skill_icon:
        if skill.icon_type == 1:  # only do skill icon not trait
            cd = 0
            active_time = 0
            if skill.game_id in self.troop_card_ui.value2[2]:
                cd = int(self.troop_card_ui.value2[2][skill.game_id])
            if skill.game_id in self.troop_card_ui.value2[3]:
                active_time = int(self.troop_card_ui.value2[3][skill.game_id][3])
            skill.icon_change(cd, active_time)
    # for effect in self.effect_icon:
    #     cd = 0
    #     if effect.id in self.troop_card_ui.value2[4]:
    #         cd = int(self.troop_card_ui.value2[4][effect.id][3])
    #     effect.iconchange(cd, 0)


def rotation_xy(origin, point, angle):
    ox, oy = origin
    px, py = point
    x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return pygame.Vector2(x, y)


def set_rotate(self, set_target=None):
    """set base_target and new angle for sprite rotation"""
    if set_target is None:  # For auto chase rotate
        my_radians = math.atan2(self.base_target[1] - self.base_pos[1], self.base_target[0] - self.base_pos[0])
    else:  # Command move or rotate
        my_radians = math.atan2(set_target[1] - self.base_pos[1], set_target[0] - self.base_pos[0])
    new_angle = math.degrees(my_radians)

    # """upper left -"""
    if -180 <= new_angle <= -90:
        new_angle = -new_angle - 90

    # """upper right +"""
    elif -90 < new_angle < 0:
        new_angle = (-new_angle) - 90

    # """lower right -"""
    elif 0 <= new_angle <= 90:
        new_angle = -(new_angle + 90)

    # """lower left +"""
    elif 90 < new_angle <= 180:
        new_angle = 270 - new_angle

    return round(new_angle)


def kill_effect_icon(self):
    for icon in self.skill_icon.sprites():
        icon.kill()
        del icon
    for icon in self.effect_icon.sprites():
        icon.kill()
        del icon


def setup_list(screen_scale, item_class, current_row, show_list, item_group, box, ui_class, layer=15):
    """generate list of subsection of the left side of encyclopedia"""
    row = 5 * screen_scale[1]
    column = 5 * screen_scale[0]
    pos = box.rect.topleft
    if current_row > len(show_list) - box.max_show:
        current_row = len(show_list) - box.max_show

    if len(item_group) > 0:  # remove previous sprite in the group before generate new one
        for stuff in item_group:
            stuff.kill()
            del stuff

    for index, item in enumerate(show_list):
        if index >= current_row:
            new_item = item_class(screen_scale, box, (pos[0] + column, pos[1] + row), item,
                                      layer=layer)
            item_group.add(new_item)  # add new subsection sprite to group
            row += (new_item.font.get_height() * 1.4 * screen_scale[1])  # next row
            if len(item_group) > box.max_show:
                break  # will not generate more than space allowed

        ui_class.add(*item_group)


def list_scroll(screen_scale, mouse_scroll_up, mouse_scroll_down, scroll, box, current_row, name_list, group, ui_class, layer=15):
    if mouse_scroll_up:
        current_row -= 1
        if current_row < 0:
            current_row = 0
        else:
            setup_list(screen_scale, menu.NameList, current_row, name_list, group, box, ui_class, layer=layer)
            scroll.change_image(new_row=current_row, log_size=len(name_list))

    elif mouse_scroll_down:
        current_row += 1
        if current_row + box.max_show - 1 < len(name_list):
            setup_list(screen_scale, menu.NameList, current_row, name_list, group, box, ui_class, layer=layer)
            scroll.change_image(new_row=current_row, log_size=len(name_list))
        else:
            current_row -= 1
    return current_row


def popout_lorebook(self, section, game_id):
    """open and draw enclycopedia at the specified subsection,
    used for when user right click at icon that has encyclopedia section"""
    self.game_state = "menu"
    self.battle_menu.mode = "encyclopedia"
    self.battle_ui.add(self.encyclopedia, self.lore_name_list, self.lore_scroll, *self.lore_button_ui)

    self.encyclopedia.change_section(section, self.lore_name_list, self.subsection_name, self.lore_scroll, self.page_button,
                                 self.battle_ui)
    self.encyclopedia.change_subsection(game_id, self.page_button, self.battle_ui)
    self.lore_scroll.change_image(new_row=self.encyclopedia.current_subsection_row)


def popup_list_open(self, new_rect, new_list, ui_type):
    """Move popup_listbox and scroll sprite to new location and create new name list baesd on type"""
    self.current_popup_row = 0

    if ui_type == "leader" or ui_type == "genre":
        self.popup_listbox.rect = self.popup_listbox.image.get_rect(topleft=new_rect)
    else:
        self.popup_listbox.rect = self.popup_listbox.image.get_rect(midbottom=new_rect)

    setup_list(self.screen_scale, menu.NameList, 0, new_list, self.popup_namegroup,
               self.popup_listbox, self.battle_ui, layer=19)

    self.popup_list_scroll.pos = self.popup_listbox.rect.topright  # change position variable
    self.popup_list_scroll.rect = self.popup_list_scroll.image.get_rect(topleft=self.popup_listbox.rect.topright)  #
    self.popup_list_scroll.change_image(new_row=0, log_size=len(new_list))

    if ui_type == "genre":
        self.main_ui.add(self.popup_listbox, *self.popup_namegroup, self.popup_list_scroll)
    else:
        self.battle_ui.add(self.popup_listbox, *self.popup_namegroup, self.popup_list_scroll)  # add the option list to screen

    self.popup_listbox.type = ui_type
