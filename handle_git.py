import os
import sys

def commit():

    commit_message = input('Commit Message?')

    os.system('git add -A')

    os.system('git commit -m "{}"'.format(commit_message))

    os.system('git push')

def branch():

    branch_name = input('Branch Name?')

    os.system('git branch {}'.format(branch_name))

    os.system('git checkout {}'.format(branch_name))

    os.system('git push --set-upstream origin {}'.format(branch_name))

def on_master_branch():

    branch_data = os.popen('git branch -av')

    return '* master' in branch_data

def get_current_branch_name():

    process = os.popen('git branch -av')

    branch_data = process.read()

    process.close()

    for item in branch_data.split('\n'):

        if '* ' in item: return item.split(' ')[1]

def merge():

    if on_master_branch() == False:

        commit()

        current_branch_name = get_current_branch_name()

        os.system('git checkout master')

        os.system('git merge {}'.format(current_branch_name))

        os.system('git push')

        os.system('git push --delete origin {}'.format(current_branch_name))

        os.system('git branch -d {}'.format(current_branch_name))

def print_usage():

    print('Please provide one of the following arguments on start up:')

    print('\t1) COMMIT - To commit your current work.')

    print('\t2) BRANCH - To create a new branch.')

    print('\t3) MERGE - To merge the current branch.')

if __name__ == "__main__":

    try:

        arg = sys.argv[1].strip().upper()

        if arg == 'COMMIT': commit()

        elif arg == 'BRANCH': branch()

        elif arg == 'MERGE': merge()

        else: print_usage()

    except:

        print_usage()