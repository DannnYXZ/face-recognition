NULL = 'NULL'


def get_quality_image(images, quality):
    return images[round(max(0, len(images) * quality - 1))]


def map_to_user_entity(user_dto, image_quality):
    user = {
        'id': user_dto["id"],
        'images': [],
        'friends_ids': user_dto['friends_ids'],
        'deactivated': 'deactivated' in user_dto,
        'first_name': user_dto['first_name'],
        'last_name': user_dto['last_name'],
        'is_closed': user_dto['is_closed'],
        'has_photo': user_dto['has_photo'],
        'domain': user_dto['domain'],
        'country_name': user_dto['country']['title'],
        'city_name': user_dto['city']['title'],
        'home_town': user_dto['home_town'],
        'interests': user_dto['interests'],
        'relation': user_dto['relation'],
        'can_send_friend_request': user_dto['can_send_friend_request'],
        'can_write_private_message': user_dto['can_write_private_message'],
        'sex': user_dto['sex'],
        'wave': -1
    }
    if user_dto['has_photo']:
        user['images'].append({'type': 'avatar', 'url': user_dto['photo_max_orig']})
    for profile_image in user_dto['profile_images']:
        user['images'].append({'type': 'profile', 'url': get_quality_image(profile_image['sizes'], image_quality)['url']})
    return user
