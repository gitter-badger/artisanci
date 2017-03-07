""" Here is an simple example server configuration that allows anyone to
execute builds on the server between the hours of 11:00pm and 5:30pm
and only allows myself (@SethMichaelLarson) to execute tests between
the hours of 5:30pm and 11:00pm. This allows me to donate the cycles
that would otherwise be lost from me being at work to the Open Source
community and earn me Karma so I may used community builders as well.

Of course you can add a lot more builders to this Farm, the more the
merrier as long as you're not over-working your computer. :) """
import datetime
import artisanci

# Put your own secret API key from https://artisan.ci here.
ARTISAN_API_KEY = 'your-secret-api-key'


if __name__ == '__main__':
    farm = artisanci.Farm(url='https://farms.artisan.ci',
                          user='gh:SethMichaelLarson',
                          api_key=ARTISAN_API_KEY)

    # Create the builder and allow it to automatically detect labels to use.
    # This builder in particular uses VirtualBox to run a Windows OS as a VM.
    # The VirtualBox machine ID for this machine is `windows-10`. We also give
    # the path for the Python installation with Artisan CI configured.
    windows_builder = artisanci.VirtualBoxBuilder(machine='windows-10',
                                                  username='username',
                                                  password='password',
                                                  python=r'C:\\Anaconda3\python.exe',
                                                  builders=5)  # Allow 5 instances to be run at once.

    # This is a local builder that can only be used by myself.
    local_builder = artisanci.LocalBuilder(builders=5)

    # Creating the schedule to use the US/Central timezone that I live in.
    schedule = artisanci.Schedule(timezone='US/Central')

    # This is the policy that allows others to use this builder while I'm at work or asleep.
    schedule.add_policy(artisanci.CommunityPolicy(start=datetime.time(hour=23),
                                                  end=datetime.time(hour=17, minute=30),
                                                  max_duration=30))

    # By setting `karma` equal to `True`, my farm will accrue
    # Karma when it is used by others which then allows me
    # additional access to the public farm.

    # Here's my policy that allows only me to use this builder when I come home from work.
    # The policy restricts the builder to only people who have my secret API key.
    schedule.add_policy(artisanci.KeyAuthPolicy(start=datetime.time(hour=17, minute=30),
                                                end=datetime.time(hour=23),
                                                api_key=ARTISAN_API_KEY))

    # Update the schedule to match
    windows_builder.set_schedule(schedule)

    # Now to create a schedule for my LocalBuilder.
    # Which will allow builds all day from only myself.
    schedule = artisanci.Schedule(timezone='US/Central')
    schedule.add_policy(artisanci.KeyAuthPolicy(all_day=True,
                                                api_key=ARTISAN_API_KEY))
    local_builder.set_schedule(schedule)

    # Add the builders to the farm.
    farm.add_builder(windows_builder)
    farm.add_builder(local_builder)

    # Start the farm and run it until we exit out of it.
    # This will also show the status of the farm in the
    # command line that is executing it.
    farm.run_forever()
