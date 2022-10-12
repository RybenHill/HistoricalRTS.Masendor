from gamescript import battleui
from gamescript.common import utility

change_group = utility.change_group


def setup_battle_ui(self, change):
    """Change can be either 'add' or 'remove' for adding or removing ui"""
    if change == "add":
        self.time_ui.change_pos((self.screen_rect.width - self.time_ui.image.get_width(),
                                 0), self.time_number)
        self.inspect_ui.change_pos((self.inspect_ui.image.get_width() / 6, self.inspect_ui.image.get_height() / 2))

        self.troop_card_ui.change_pos((self.inspect_ui.rect.bottomleft[0] + self.troop_card_ui.image.get_width() / 2,
                                       (self.inspect_ui.rect.bottomleft[
                                            1] + self.troop_card_ui.image.get_height() / 2)))

        self.battle_scale_ui.change_pos(self.time_ui.rect.bottomleft)
        self.test_button.change_pos((self.battle_scale_ui.rect.bottomleft[0] + (self.test_button.image.get_width() / 2),
                                     self.battle_scale_ui.rect.bottomleft[1] + (
                                                 self.test_button.image.get_height() / 2)))
        self.warning_msg.change_pos(self.test_button.rect.bottomleft)

        # self.speed_number.change_pos(self.time_ui.rect.center)  # self speed number on the time ui

        self.command_ui.change_pos((self.inspect_ui.image.get_width() + self.command_ui.image.get_width() / 2,
                                    self.command_ui.image.get_height() / 2))

        inspect_ui_pos = [self.inspect_ui.rect.topleft[0] + self.icon_sprite_width / 1.25,
                          self.inspect_ui.rect.topleft[1]]
        width, height = inspect_ui_pos[0], inspect_ui_pos[1]
        sub_unit_number = 0  # Number of subunit based on the position in row and column
        imgsize = (self.icon_sprite_width, self.icon_sprite_height)
        for _ in list(range(0, 25)):
            width += imgsize[0]
            self.inspect_subunit.append(battleui.InspectSubunit((width, height)))
            sub_unit_number += 1
            if sub_unit_number == 5:  # Reach the last subunit in the row, go to the next one
                width = inspect_ui_pos[0]
                height += imgsize[1]
                sub_unit_number = 0

        change_group(self.command_ui, self.battle_ui_updater, change)

        if self.mode == "unit_editor":
            change_group(self.unit_selector, self.battle_ui_updater, change)
            change_group(self.unit_selector.scroll, self.battle_ui_updater, change)

    else:
        change_group(self.unit_selector, self.battle_ui_updater, change)
        change_group(self.unit_selector.scroll, self.battle_ui_updater, change)

    change_group(self.battle_scale_ui, self.battle_ui_updater, change)
