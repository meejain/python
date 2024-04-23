import shutil
import os, sys, stat
original = r'/Users/meejain/PycharmProjects/pythonProject/dir1/cookbooks/ams/files/default/basicsudoers/dispatcher'
target = r'/Users/meejain/Downloads/power_users_group_sudoers'
shutil.copyfile(original, target)
os.chmod("/Users/meejain/Downloads/power_users_group_sudoers", stat.S_IRWXU)
