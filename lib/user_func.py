from lib.user import User
from lib.task_func import rec_task_delete


def operation_create_user(container, options):
    for user in container['users']:
        if user.nickname == options.nickname:
            print('A user with the nickname "{}" already exists.'. format(options.nickname))
            return
    new_user = User(nickname=options.nickname)
    container['users'].append(new_user)
    if options.force:
        container['current_user'] = new_user.nickname


def operation_login_user(container, options):
    for user in container['users']:
        if user.nickname == options.nickname:
            container['current_user'] = options.nickname
            break
    else:
        print('User does not exist')


def operation_user_logout(container):
    for user in container['users']:
        if user.nickname == container['current_user']:
            container['current_user'] = None
            break
    else:
        print('User does not exist')


def operation_user_remove(container, options):
    print(options.nickname)
    for user in container['users']:
        if user.nickname == options.nickname:
            container['users'].remove(user)

    else:
        print('User does not exist')

