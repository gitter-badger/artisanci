""" Here is an simple example server configuration that allows anyone to
execute builds on the server between the hours of 11:00pm and 5:30pm
and only allows myself (@SethMichaelLarson) to execute tests between
the hours of 5:30pm and 11:00pm. This allows me to donate the cycles
that would otherwise be lost from me being at work to the Open Source
community and earn me Karma so I may used community builders as well.

Of course you can add a lot more builders to this Farm, the more the
merrier as long as you're not over-working your computer. :) """
import datetime

import artisan
from artisan.policy import Schedule, CommunityPolicy, GitHubPolicy

# Put your own artisan.io secret token here.
ARTISAN_API_KEY = 'fill-in-this-value'


if __name__ == '__main__':
    farm = artisan.Farm(username='gh:SethMichaelLarson',
                        key=ARTISAN_API_KEY)

    # Create the builder and allow it to automatically detect labels to use.
    # This builder in particular uses VirtualBox to run a Windows OS as a VM.
    # The VirtualBox machine ID for this machine is `windows-10`. We also give
    # the path for the Python installation with Artisan CI configured.
    windows_builder = artisan.VirtualBoxBuilder(machine='windows-10',
                                                username='artisan',
                                                password='artisan',
                                                python=r'C:\\Anaconda3\python.exe',
                                                instances=5)  # Allow 5 instances to be run at once.

    # This is a local builder that can only be used by myself.
    local_builder = artisan.LocalBuilder(instances='*')  # Allow any number of instances.

    # If there's any problems with either builder we'll find them here.
    windows_builder.auto_detect_labels()
    local_builder.auto_detect_labels()

    # Creating the schedule to use the US/Central timezone that I live in.
    schedule = Schedule(timezone='US/Central')

    # This is the policy that allows others to use this builder while I'm at work or asleep.
    schedule.add_policy(CommunityPolicy(start=datetime.time(hour=23),
                                        end=datetime.time(hour=17, minute=30),
                                        karma=True,
                                        max_duration=30))

    # By setting `karma` equal to `True`, my farm will accrue
    # Karma when it is used by others which then allows me
    # additional access to the public farm.

    # Here's my policy that allows only me to use this builder when I come home from work.
    schedule.add_policy(GitHubPolicy(allow_users=['SethMichaelLarson'],
                                     start=datetime.time(hour=17, minute=30),
                                     end=datetime.time(hour=23),
                                     karma=False))

    # Setting `karma` to `False` means that Karma is not
    # required to execute jobs on this builder. I also
    # restrict the usage of this builder to GitHub projects
    # that I myself execute.

    # Update the schedule to match
    windows_builder.set_schedule(schedule)

    # Now to create a schedule for my LocalBuilder.
    # Which will allow builds all day from only myself.
    schedule = Schedule(timezone='US/Central')
    schedule.add_policy(GitHubPolicy(allow_users=['SethMichaelLarson'],
                                     all_day=True,
                                     karma=False))
    local_builder.set_schedule(schedule)

    # Add the builders to the farm.
    farm.add_builder(windows_builder)
    farm.add_builder(local_builder)

    # Start the farm and run it until we exit out of it.
    farm.run_forever()
