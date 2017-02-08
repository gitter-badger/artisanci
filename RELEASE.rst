How-To Release Artisan
======================

These are the steps to take to create a release for Artisan:

1. Within master change the CHANGELOG.rst entry to be equal to the next version.

  - ``CHANGELOG.rst``

2. Run the tests to make sure that documentation can build. Push the changes to master.

 .. code-block:: bash

   $ tox
   $ git push origin master

3. Switch to the release branch

 .. code-block:: bash
 
    $ git checkout release
    $ git merge master --no-commit

4. Update the module ``__version__`` to be the current version.

  - ``artisan/__init__.py``
    
5. Add and commit the changes.

 .. code-block:: bash
 
    $ git commit -a -m 'Release {VERSION}'
    $ git tag {VERSION} -m '{VERSION}'
    
6. Build the distributables and publish to release branch.

 .. code-block:: bash
 
    $ git push origin release
    $ python setup.py sdist bdist_wheel
    $ twine upload dist/*

7. Tag a new release on GitHub.

  - Go to the URL: https://github.com/artisanci/artisan/releases/new
  - Enter in the release version for tag and title.
  - Copy the changelog for the release into the description.
