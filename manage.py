#!/usr/bin/env python
import os
import sys
import environ

if __name__ == '__main__':
    env = environ.Env(
        # set casting, default value
        DEBUG=(bool, False)
    )
    environ.Env.read_env(env_file=os.path.join(os.getcwd(), '.env'))
    RUN_ENV = env.str('RUN_ENV', 'local')

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.' + RUN_ENV)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
