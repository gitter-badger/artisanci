Commands
========

.. autoclass:: artisan.BaseCommand

Example Usage
-------------

Here is an example usage of a :class:`artisan.BaseCommand` object.

.. code-block:: python

    def job(worker):
        # In this instance, `worker` is a LocalWorker instance.
        with worker.execute_command('sleep 1 && cat ~/.bashrc') as cmd:
            if cmd.wait(timeout=0.1):
                print('The above command finished very early!')
            if cmd.wait(timeout=1.0, error_on_timeout=True):
                bashrc = cmd.stdout.read()
                print('Here is your ~/.bashrc file: ')
                print(bashrc)
            else:
                stderr = cmd.stderr.read()
                print('Exit Status: %d Error: %s' % (cmd.exit_status,
                                                     stderr)
