from repository import VkUser


def map_to_vk_user(response_user_data):
    user = VkUser()
    user.id = response_user_data["id"]
    user.images = []
    user.friends_ids = []
    return user
