def get_quality_image(images, quality):
    return images[round(max(0, len(images) * quality - 1))]


def map_to_user_entity(user_dto, image_quality):
    user = {
        'images': [],
        'friends_ids': user_dto['friends_ids'] if 'friends_ids' in user_dto else [],
        'deactivated': 'deactivated' in user_dto,
        'country_name': user_dto['country']['title'] if 'country' in user_dto else None,
        'city_name': user_dto['city']['title'] if 'city' in user_dto else None,
        'wave': -1
    }
    for key in ['id', 'first_name', 'last_name', 'is_closed', 'has_photo', 'domain', 'home_town', 'interests',
                'can_send_friend_request', 'can_write_private_message', 'sex']:
        user[key] = user_dto[key] if key in user_dto else None
    if user_dto['has_photo']:
        user['images'].append({'type': 'avatar', 'url': user_dto['photo_max_orig']})
    if 'profile_images' in user_dto:
        for profile_image in user_dto['profile_images']:
            user['images'].append({'type': 'profile', 'url': get_quality_image(profile_image['sizes'], image_quality)['url']})
    return user
