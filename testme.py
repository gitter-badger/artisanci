from artisan import SshWorker

s = SshWorker('prhel7am', 'ensitetest', password='endocardial')
print(s.is_directory('/tmp'))
print(s.is_directory('/ImageId'))