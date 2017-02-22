""" Here is an simple example server configuration that allows anyone to
execute builds on the server between the hours of 11:00pm and 5:30pm
and only allows myself (@SethMichaelLarson) to execute tests between
the hours of 5:30pm and 11:00pm. This allows me to donate the cycles
that would otherwise be lost from me being at work to the Open Source
community.

Of course you can add a lot more executors to this Farm, the more the
merrier as long as you're not over-working your computer. :) """
import datetime

import artisan
import artisan.policy

# Put your own artisan.io secret token here.
ARTISAN_API_KEY = 'fill-in-this-value'
ARTISAN_API_SECRET = 'this-value-is-secret'


if __name__ == '__main__':
    farm = artisan.Farm(key=ARTISAN_API_KEY,
                        secret=ARTISAN_API_SECRET)

    # Create the builder and allow it to automatically detect labels to use.
    # This builder in particular uses VirtualBox to run a Windows OS as a VM.
    # The image for this VM is found at the path: `windows-1`. We also give
    # the path that Python is installed on and has Artisan installed.
    win_exec = artisan.VirtualBoxBuilder('windows-1', r'C:\\Anaconda3\python.exe')
    win_exec.detect_labels()  # If there's any problems with the builder we'll find them here.

    # Creating the schedule to use the US/Central timezone that I live in.
    schedule = artisan.policy.Schedule(timezone=' US/Central')

    # This is the policy that allows others to use this builder while I'm at work or asleep.
    schedule.add_policy(start=datetime.time(hour=23),
                        end=datetime.time(hour=17, minute=30),
                        policy=artisan.policy.AllowAllPolicy())

    # Here's my policy that allows only me to use this builder when I come home from work.
    schedule.add_policy(start=datetime.time(hour=17, minute=30),
                        end=datetime.time(hour=23),
                        policy=artisan.policy.GitHubPolicy(allow_users=['SethMichaelLarson']))

    # Add the builder to the farm.
    farm.add_executor(win_exec)

    # Start the farm and run it until we exit out of it.
    farm.run_forever()
