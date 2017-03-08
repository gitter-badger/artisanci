How-To Release Artisan CI
=========================

These are the steps to take to create a release for Artisan CI:

1. Switch to the release branch

 .. code-block:: bash
 
    $ git checkout release
    $ git merge master --no-commit
    
2. Within master change the CHANGELOG.rst entry to be equal to the next version.
   Make sure to tag a date as well in the release.

  - ``CHANGELOG.rst``

3. Update the module ``__version__`` to be the current version.

  - ``artisanci/__init__.py``
    
4. Add and commit the changes.

 .. code-block:: bash
 
    $ git commit -a -m 'Release {VERSION}'
    $ git tag {VERSION} -m '{VERSION}'
    
5. Build the distributables and publish to release branch.

 .. code-block:: bash
 
    $ git push origin release
    $ python setup.py sdist bdist_wheel
    $ twine upload dist/*

6. Tag a new release on GitHub.

  - Go to the URL: https://github.com/artisanci/artisanci/releases/new
  - Enter in the release version for tag and title.
  - Copy the changelog for the release into the description.
  - Add the zip file as well as the wheel as distributables.
