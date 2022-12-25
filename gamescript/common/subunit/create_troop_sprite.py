import math

import pygame
from PIL import Image, ImageFilter, ImageEnhance
from gamescript.common import utility, animation

rotation_xy = utility.rotation_xy

default_sprite_size = (200, 200)


def create_troop_sprite(animation_name, size, animation_part_list, troop_sprite_list, body_sprite_pool,
                        weapon_sprite_pool, armour_sprite_pool, effect_sprite_pool, animation_property,
                        weapon_joint_list, weapon, armour, colour_list, genre_sprite_size,
                        screen_scale, race_list):
    apply_colour = animation.apply_colour
    try:
        frame_property = animation_part_list["frame_property"].copy()
    except:
        print(animation_name)
        print(animation_part_list)
    animation_property = animation_property.copy()
    check_prop = frame_property + animation_property
    size = int(size)
    if size > 5:
        size = 5
    surface = pygame.Surface((default_sprite_size[0] * size, default_sprite_size[1] * size),
                             pygame.SRCALPHA)  # default size will scale down later

    except_list = ("eye", "mouth", "size", "property")
    pose_layer_list = {k: v[7] for k, v in animation_part_list.items() if v != [0] and v != "" and v != [""] and
                       any(ext in k for ext in except_list) is False and "weapon" not in k}  # layer list
    pose_layer_list.update({k: v[6] for k, v in animation_part_list.items() if v != [0] and v != "" and v != [""]
                            and "weapon" in k})
    pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))
    for index, layer in enumerate(pose_layer_list):
        part = animation_part_list[layer]
        new_part = part.copy()
        this_armour = None
        if any(ext in layer for ext in ("p1_", "p2_", "p3_", "p4_")) and "weapon" not in layer:
            part_race = [value["Name"] for value in race_list.values()].index(new_part[0])
            part_race = tuple(race_list.keys())[part_race]
            if race_list[part_race]["Mount Armour"] is False:
                this_armour = armour[0]
            else:
                this_armour = armour[1]
        if "head" in layer:
            image_part = generate_head(layer[:2], animation_part_list, part[:3], troop_sprite_list, body_sprite_pool,
                                       armour_sprite_pool,
                                       this_armour, colour_list)
        elif "weapon" in layer:
            new_part.insert(2, "Dummy")  # insert dummy value for weapon list so can use indexing similar as other part
            image_part = generate_body(layer, part[:2], troop_sprite_list, weapon_sprite_pool, weapon=weapon)
        elif "effect" in layer:
            if "dmg_" not in layer:
                image_part = generate_body(layer, part[:3], troop_sprite_list, effect_sprite_pool)
        else:  # other body part
            colour = troop_sprite_list[layer[:2] + "_skin"]
            if any(ext in part[2] for ext in race_list[part_race]["Special Hair Part"]):
                colour = troop_sprite_list[layer[:2] + "_hair"]
                if colour != "":
                    if len(colour) == 2:
                        colour = colour[1]
                    else:
                        colour = colour[0]
            if colour == "":  # no custom colour, use None
                colour = None
            image_part = generate_body(layer, part[:3], troop_sprite_list, body_sprite_pool,
                                       armour_sprite_pool=armour_sprite_pool, colour=colour,
                                       colour_list=colour_list, armour=this_armour)
        if image_part is not None:  # skip for empty image
            target = (new_part[3], new_part[4])
            flip = new_part[6]
            scale = new_part[8]

            new_target = target

            use_center = False

            p = layer[:3]

            if "weapon" in layer:  # only weapon use joint to calculate position
                part_name = weapon[1][0]  # main weapon
                if "sub" in layer:
                    part_name = weapon[1][1]  # sub weapon
                center = pygame.Vector2(image_part.get_width() / 2, image_part.get_height() / 2)
                use_center = True
                if (p + "main_" in layer and p + "fix_main_weapon" not in check_prop) or \
                        (p + "sub_" in layer and p + "fix_sub_weapon" not in check_prop):
                    use_center = False
                    if p + "main_weapon" in layer:  # main weapon
                        if part[1] != "sheath":  # change main weapon pos to right hand, if part is not sheath
                            target = (animation_part_list[p + "r_hand"][3], animation_part_list[p + "r_hand"][4])
                            use_center = False  # use weapon joint
                        else:
                            target = (animation_part_list[p + "body"][3],
                                      animation_part_list[p + "body"][4])  # put on back
                            use_center = True
                    elif p + "sub_weapon" in layer:  # sub weapon
                        if part[1] != "sheath":  # change weapon pos to hand, if part is not sheath
                            if "_Sub_" in animation_name and weapon[2][1] == 2:  # two-handed sub weapon use same animation as main for attack so put sub weapon in man hand, remove code if different
                                target = (animation_part_list[p + "r_hand"][3], animation_part_list[p + "r_hand"][4])
                            else:
                                target = (animation_part_list[p + "l_hand"][3], animation_part_list[p + "l_hand"][4])
                        else:
                            target = (animation_part_list[p + "body"][3],
                                      animation_part_list[p + "body"][4])  # put on back
                            use_center = True
                    new_target = target

            part_rotated = image_part.copy()
            if scale != 1:
                part_rotated = pygame.transform.scale(part_rotated, (part_rotated.get_width() * scale,
                                                                     part_rotated.get_height() * scale))
            if flip != 0:
                if flip == 1:
                    part_rotated = pygame.transform.flip(part_rotated, True, False)
                elif flip == 2:
                    part_rotated = pygame.transform.flip(part_rotated, False, True)
                elif flip == 3:
                    part_rotated = pygame.transform.flip(part_rotated, True, True)

            angle = new_part[5]

            if angle != 0:
                part_rotated = pygame.transform.rotate(part_rotated, angle)  # rotate part sprite

            if "weapon" in layer and weapon_joint_list[new_part[0]][
                part_name] != "center" and use_center is False:  # use weapon joint pos and hand pos for weapon position blit
                main_joint_pos = [weapon_joint_list[new_part[0]][part_name][0],
                                  weapon_joint_list[new_part[0]][part_name][1]]

                # change pos from flip
                if flip in (1, 3):  # horizontal flip
                    hori_diff = image_part.get_width() - main_joint_pos[0]
                    main_joint_pos = (hori_diff, main_joint_pos[1])
                if flip >= 2:  # vertical flip
                    vert_diff = image_part.get_height() - main_joint_pos[1]
                    main_joint_pos = (main_joint_pos[0], vert_diff)

                pos_different = center - main_joint_pos  # find distance between image center and connect point main_joint_pos
                new_target = new_target + pos_different
                if angle != 0:
                    radians_angle = math.radians(360 - angle)
                    if angle < 0:
                        radians_angle = math.radians(-angle)
                    new_target = rotation_xy(target, new_target,
                                             radians_angle)  # find new center point with rotation

            rect = part_rotated.get_rect(center=new_target)
            surface.blit(part_rotated, rect)

    for prop in check_prop:
        if "effect" in prop:
            if "grey" in prop:  # not work with just convert L for some reason
                width, height = surface.get_size()
                for x in range(width):
                    for y in range(height):
                        red, green, blue, alpha = surface.get_at((x, y))
                        average = (red + green + blue) // 3
                        gs_color = (average, average, average, alpha)
                        surface.set_at((x, y), gs_color)
            data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
            surface = Image.frombytes("RGBA", surface.get_size(), data)  # use PIL to get image data
            alpha = surface.split()[-1]  # save alpha
            if "blur" in prop:
                surface = surface.filter(
                    ImageFilter.GaussianBlur(
                        radius=float(prop[prop.rfind("_") + 1:])))  # blur Image (or apply other filter in future)
            if "contrast" in prop:
                enhancer = ImageEnhance.Contrast(surface)
                surface = enhancer.enhance(float(prop[prop.rfind("_") + 1:]))
            if "brightness" in prop:
                enhancer = ImageEnhance.Brightness(surface)
                surface = enhancer.enhance(float(prop[prop.rfind("_") + 1:]))
            if "fade" in prop:
                empty = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
                empty.fill((255, 255, 255, 255))
                empty = pygame.image.tostring(empty, "RGBA")  # convert image to string data for filtering effect
                empty = Image.frombytes("RGBA", surface.get_size(), empty)  # use PIL to get image data
                surface = Image.blend(surface, empty, alpha=float(prop[prop.rfind("_") + 1:]) / 10)
            surface.putalpha(alpha)  # put back alpha
            surface = surface.tobytes()
            surface = pygame.image.fromstring(surface, surface.get_size(),
                                              "RGBA")  # convert image back to a pygame surface
            if "colour" in prop:
                colour = prop[prop.rfind("_") + 1:]
                colour = [int(this_colour) for this_colour in colour.split(".")]
                surface = apply_colour(surface, colour)

            if prop in frame_property:
                frame_property.remove(prop)
            if prop in animation_property:
                animation_property.remove(prop)

    # change to whatever genre's specific size
    surface = pygame.transform.smoothscale(surface, (
    genre_sprite_size[0] * size * screen_scale[0], genre_sprite_size[1] * size * screen_scale[1]))

    return {"sprite": surface, "animation_property": tuple(animation_property), "frame_property": tuple(frame_property)}


def grab_face_part(pool, race, side, part, part_check, part_default=None):
    """For creating body part like eye or mouth in animation that accept any part (1) so use default instead"""
    surface = None
    if part_check != "":
        if part_check == 1:  # any part
            if part_default is not None:
                default = part_default
                if type(part_default) != str:
                    default = part_default[0]
                surface = pool[race][side][part][default].copy()
        else:
            check = part_check
            if type(part_check) != str:
                check = part_check[0]
            if check != "none":
                surface = pool[race][side][part][check].copy()
    return surface


def generate_head(p, animation_part_list, body_part_list, sprite_list, body_pool, armour_pool, armour,
                  colour_list):
    apply_colour = animation.apply_colour

    head_sprite_surface = None
    try:
        head_race = body_part_list[0]
        head_side = body_part_list[1]
        head = body_pool[head_race][head_side]["head"][body_part_list[2]].copy()
        head_sprite_surface = pygame.Surface((head.get_width(), head.get_height()), pygame.SRCALPHA)
        head_rect = head.get_rect(topleft=(0, 0))
        head_sprite_surface.blit(head, head_rect)
        if sprite_list[p + "_skin"] not in ("", "none"):
            head_sprite_surface = apply_colour(head_sprite_surface, sprite_list[p + "_skin"], colour_list, keep_white=False)
        face = [grab_face_part(body_pool, head_race, head_side, "eyebrow", sprite_list[p + "_eyebrow"]),
                grab_face_part(body_pool, head_race, head_side, "eye", animation_part_list[p + "_eye"],
                               part_default=sprite_list[p + "_eye"]),
                grab_face_part(body_pool, head_race, head_side, "beard", sprite_list[p + "_beard"]),
                grab_face_part(body_pool, head_race, head_side, "mouth", animation_part_list[p + "_mouth"],
                               part_default=sprite_list[p + "_mouth"])]

        for face_index, face_part in enumerate(("_eyebrow", "_eye", "_beard")):
            if face[face_index] is not None:
                face[face_index] = apply_colour(face[face_index], sprite_list[p + face_part][1], colour_list)

        for index, item in enumerate(face):
            if item is not None:
                rect = item.get_rect(center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
                head_sprite_surface.blit(item, rect)
    except KeyError:  # some head direction show no face
        pass
    except TypeError:  # empty
        pass

    if sprite_list[p + "_head"] != "none":
        try:
            gear_image = armour_pool[head_race][armour][sprite_list[p + "_head"]][head_side]["helmet"][
                body_part_list[2]]
            rect = gear_image.get_rect(
                center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
            head_sprite_surface.blit(gear_image, rect)
        except KeyError:  # helmet folder not existed
            pass

    return head_sprite_surface


def generate_body(part, body_part_list, troop_sprite_list, sprite_pool, armour_sprite_pool=None, colour=None,
                  weapon=None, armour=None, colour_list=None):
    apply_colour = animation.apply_colour

    # main/body first
    sprite_image = None
    try:
        if "weapon" in part:
            weapon_part = part[:3] + "primary_" + part[3:]  # primary set
            if weapon_part == 1:
                weapon_part = part[:3] + "secondary_" + part[3:]  # secondary set
            part_name = weapon[1][0]  # main weapon
            if "sub" in part:
                part_name = weapon[1][1]  # sub weapon
            if part_name is not None and part_name != "Unarmed":
                try:
                    sprite_image = sprite_pool[part_name][troop_sprite_list[weapon_part]][body_part_list[0]][
                        body_part_list[1]].copy()
                except KeyError:  # use common variant if specified not found
                    sprite_image = sprite_pool[part_name]["Common"][body_part_list[0]][body_part_list[1]].copy()
        else:
            new_part_name = part
            part_name = part
            if any(ext in part for ext in ("p1_", "p2_", "p3_", "p4_")):
                part_name = part[3:]  # remove person header
                new_part_name = part_name
            if "special" in part:
                new_part_name = "special"
            if "r_" in part_name[:2] or "l_" in part_name[:2]:
                new_part_name = part_name[2:]  # remove side
            sprite_image = sprite_pool[body_part_list[0]][body_part_list[1]][new_part_name][body_part_list[2]].copy()
            # if sprite_list[p + "_skin"] != "none":
            #     head_sprite_surface = apply_colour(head_sprite_surface, sprite_list[p + "_skin"], hair_colour_list)
        if colour is not None:  # apply skin colour, maybe add for armour colour later
            sprite_image = apply_colour(sprite_image, colour, colour_list, keep_white=False)

        if armour is not None and armour != "None":  # add armour if there is one
            part_name = part
            if any(ext in part for ext in ("p1_", "p2_", "p3_", "p4_")):
                part_name = part[3:]  # remove person prefix to get part name
            gear_image = \
            armour_sprite_pool[body_part_list[0]][armour][troop_sprite_list[part]][body_part_list[1]][part_name][
                body_part_list[2]]
            new_sprite_image = pygame.Surface(gear_image.get_size(),
                                              pygame.SRCALPHA)  # create sprite based on armour size since it can be larger than body part
            rect = sprite_image.get_rect(center=(new_sprite_image.get_width() / 2, new_sprite_image.get_height() / 2))
            new_sprite_image.blit(sprite_image, rect)
            rect = gear_image.get_rect(center=(new_sprite_image.get_width() / 2, new_sprite_image.get_height() / 2))
            new_sprite_image.blit(gear_image, rect)
            sprite_image = new_sprite_image
    except KeyError:  # sprite simply not existed
        pass

    return sprite_image
