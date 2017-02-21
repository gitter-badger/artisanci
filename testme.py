from artisan import LocalExecutor
from artisan.job import LocalJob
from artisan.report import CommandLineReport


if __name__ == '__main__':
    #from artisan.yml.labels import detect_labels
    #print(detect_labels())
    e = LocalExecutor()
    for j in [LocalJob('.artisan/flake8', '.')]:
        j.report = CommandLineReport()
        e.run(j)
