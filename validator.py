def validate(data, repo, user_id=None):
    errors = {}
    if len(data.get('name')) < 4:
        errors['name'] = "name is too short (min 4 symbols)"
    for current_id, current_user in repo.items():
        if current_id != user_id:
            if data.get('email') == current_user['email']:
                errors['email'] = 'This E-mail already registered'
                break
    return errors
