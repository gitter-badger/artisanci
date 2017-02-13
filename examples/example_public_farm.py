""" Here is an simple example server configuration that allows anyone to
execute builds on the server between the hours of 11:00pm and 5:30pm
and only allows myself (@SethMichaelLarson) to execute tests between
the hours of 5:30pm and 11:00pm. This allows me to donate the cycles
that would otherwise be lost from me being at work to the Open Source
community. """
import datetime

import artisan
import artisan.worker
import artisan.executors
import artisan.auth

# Put your own artisan.io secret token here.
SECRET_ARTISAN_TOKEN = 'fill-in-this-value'


if __name__ == '__main__':
    farm = artisan.Farm(token=SECRET_ARTISAN_TOKEN)

    # Create the executor and allow it to automatically detect labels to use.
    # This executor in particular uses VirtualBox to run a Windows OS as a VM.
    # The image for this VM is found at the path: `vms/windows`.
    win_exec = artisan.executors.VirtualBoxExecutor('vms/windows')
    win_exec.auto_detect_labels()  # If there's any problems with the executor we'll find them here.

    # Creating the schedule to use the US/Central timezone that I live in.
    schedule = artisan.auth.Schedule(timezone=' US/Central')

    # This is the policy that allows others to use this executor while I'm at work or asleep.
    schedule.add_policy(start=datetime.time(hour=23),
                        end=datetime.time(hour=17, minute=30),
                        policy=artisan.auth.AllowAllPolicy())

    # Here's my policy that allows only me to use this executor when I come home from work.
    schedule.add_policy(start=datetime.time(hour=17, minute=30),
                        end=datetime.time(hour=23),
                        policy=artisan.auth.GitHubPolicy(allow_users=['SethMichaelLarson']))

    # Add the executor to the farm.
    farm.add_executor(win_exec)

    # Start the farm and run it until we exit out of it.
    farm.run_forever()
