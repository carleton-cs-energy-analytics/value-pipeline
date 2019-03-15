# value-pipeline

This is run using crontab. The command for the cron is like so

    30 05 * * * cd ~/value-pipeline/ && make email

It's currently deployed with the user `energy`. 

Files from the building control system are stored in `/var/data/uploads`. 
Files are initially dumped into `siemens` by the backend, and then this
will move them into `siemens/archive`. By running the script with the 
command line argument `all` (or by using the Make rule called `all`), all
files including those in the archive will be imported. 

TODO: It'd probably be a good idea to rearrange things so that the backend
initially puts files in the archive directory, and create a symbolic link 
to the archive file in some sort of todo directory, and set the permissions
on the files in the archive to read only, so a malfunction would be less 
likely to result in data loss. 
