import os
import sys
import argparse

def run_tests(run_all):
    """
    Runs unit tests for OnlyVans project.

    Options:
        --all Runs all tests together.
    """
    # Set Django environment settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'onlyvans.settings'
    os.environ['PYTHONPATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'onlyvans'))

    # List of applications to test
    apps = ['account', 'client', 'creator', 'finances', 'interactions']

    if run_all:
        print("Running tests for all applications together...")
        exit_code = os.system(f"python onlyvans/manage.py test {' '.join(apps)}")
        if exit_code != 0:
            print(f"Tests for all applications failed with exit code {exit_code}")
            sys.exit(exit_code)
    else:
        for app in apps:
            print(f"Running tests for {app}...")
            exit_code = os.system(f"python onlyvans/manage.py test {app}")
            if exit_code != 0:
                print(f"Tests for {app} failed with exit code {exit_code}")
                sys.exit(exit_code)

if __name__ == '__main__':
    # Command-line argument parser
    parser = argparse.ArgumentParser(description='Run tests for specified apps or all apps together.')
    parser.add_argument('--all', action='store_true', help='Test all apps together')

    # Parse command-line arguments
    args = parser.parse_args()

    # Run tests
    run_tests(args.all)
