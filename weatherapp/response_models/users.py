def map_users_to_response(users):
    results = []
    for user in users:
        results.append(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "password_hash": user.password_hash,
                "role": user.role,
            }
        )
    return results
