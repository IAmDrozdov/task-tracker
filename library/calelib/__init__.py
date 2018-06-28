"""Calendoola Library

A library from which you can create your to-do application. There is also
support for users and transfer tasks between them. On the github repository
https://bitbucket.org/sashasashadrozdov/calendoola you can find examples of
integrating this library into a console or web application.


    First steps:

    >>> from calelib import configure_database
    >>> configure_database()
    >>> from calelib.crud import Calendoola
    >>> my_todo = Calendoola()

    First of all you should configure user database.
    Function 'configure_database' "works out of the box" with settings file
    if directory 'database settings' called 'settings.py'. So you can use
    your own settings file by passing its path as parameter to this function.
    Calendoola is main object of your application. When you create new instance
    of application config file and logging file creates automatically. To work
    with this application you must have at least one user.


    Usage:
    Below is a brief overview of the functionality of the library, for detailed
    use, use the help() function for the library modules.

    In the following examples of using the application, we will work with the
    object created in the section below.


        Users:
        The first instance you need to create for using this library. This
        entity holds all the plans, tasks and reminders. Through the nickname
        of the user you will get access to all data.

        To create user you need to:
        >>> my_todo.create_user(nickname='new_user')
        This function takes 1 required arguments - it is users nickname, using
        which you will work with application.
        For more details use help(crud) or help(customer).


        Tasks:
        The whole essence of this application lies in the tasks. You can do
        anything with them: create, delete, edit, transfer to users for shared
        deletion, move to archive, return all, by id or filtering.

        To create task you need to:
        >>> my_todo.create_task(username, info)
        This function takes 2 required arguments: username - nickname of user
        what create task and info - description of this task.
        Also you can add arguments like priority, deadline, tags and parent
        task id.
        For more details use help(crud) or help(task).


        Plans:
        Plans is an instance, that create tasks periodically. You can set
        time to create and period of creating, what can be interpreted as
        'create every N days in M:M o'clock'.

        To create plan you need to:
        >>> my_todo.create_plan(username, info, period_type, period_value)
        This function takes 4 required arguments, the first to you know
        from the 'tasks', next 2 are period_type - type of periodicity this
        plan(see 'constants.py') and period_value what will describe days
        when plan should create task. Also this function takes 1 more argument
        which calls 'time', its describe time, when plan should create task.
        For more details use help(crud) or help(plan).


        Reminders:
        Reminders is an instance, that will remind you about tasks deadline.
        You can set time before reminding what can be interpreted as 'remind
        me about the tasks N time before their deadline'.

        To create reminder you need to:
        >>> my_todo.create_reminder(username, remind_type, remind_before)
        THis function takes only 3 required arguments? the first you already
        know, the next 2 are remind_type - the unit of time(see 'constants.py')
        in which to be measured next argument remind_before - value of
        remind_type units, before this instance reminder will remind you about
        task.
        For more details use help(crud) or help(reminder).
"""

from .constants import Constants, Status
from .custom_exceptions import CycleError
from .database_settings.configurator import configure_database
