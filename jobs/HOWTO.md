## Running Cron Jobs on Linux Servers

### Edit Contab File
In order to tell your machine of the new job you want it to execute you need to edit the crontab file. Simply do

    crontab -e

Then you can add a number of scheduled tasks with the using the syntax introduced in the next section. Note that since this app is not yet in production, you must do this on every local machine you wish to run it on until it is deployed on a server or containerized. 
If you want to add a job as a different user, you can open the crontab as said user with the command

    crontab -u <other_username> -e

Note that you can list existing cron jobs using

    crontab -l

### Standard syntax for any job follows the form
    a b c d e /directory/command output

* The first five fields `a b c d e` specify the minute, hour, day, month, and day of the week to be run on, respectively.
* The next field `directory/command output` specifies the directory of your program and then the file to execute. There is an optional output which can be used to write to a file or send the user emails whenver the command is run. It is set to the later configuration by default.

### Operator Syntax
These operators can be replaced for each of `a b c d e` as they stand for different kinds of wildcard, instead of strict integer values.
* An asteriks (*) stands for all values (i.e. run for all values of said time)
* A comma (,) specifies several individual values
* A dash (-) indicates a range of values

A forward-slash (/) means to divide values into steps. E.g. if you wanted to run a program for every other hour, you would use

    0 */2 * * * /filepath/script.sh

Here is an example of a cron job that will backup your machine every Saturday and midnight

    0 0 * * 6 /root/backup.sh

**This tutorial was written thanks to https://phoenixnap.com/kb/set-up-cron-job-linux
