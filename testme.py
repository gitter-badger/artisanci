from artisan import ArtisanYml, LocalBuilder
import os
a = ArtisanYml.from_path('local', os.getcwd())

b = LocalBuilder()
p = []
for job in a.jobs:
    p.append(b.build_job(job))
    if len(p) > 1:
        p[0].join()
        del p[0]
for x in p:
    x.join()
