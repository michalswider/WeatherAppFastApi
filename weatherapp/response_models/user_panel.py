def user_detail_to_response(user_model):
    return {
        "first_name": user_model.first_name,
        "last_name": user_model.last_name,
        "username": user_model.username,
        "role": user_model.role,
    }
