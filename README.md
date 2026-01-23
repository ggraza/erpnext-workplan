### ERPNext Workplan

This is an App for ERPNext allows leave calculations based on expected working hours per day. It will calculate the available leave budgets based on expected working hours per day (e.g. a person that works only 20 instead of 40 hours per week, will only receive 50% of the regular leave budget). For Leave Applications, it will also only deduct the actual work time on the given leave days (e.g. taking off a work day, where an Employee is scheduled to work only 4 hours, it will only deduct 4 hours from the leave budget).

To save the expected working hours per day, it adds a new "Workplan" DocType to every Employee (under the "Attendance & Leaves" Tab). A workplan is a schedule of expected/regular working hours per day (e.g. a Workplan could look like "Monday 8 h, Tuesday 6h, Wednesday 8h, Thursday 4h, Friday 4h"). A workplan also has a start and an end date (because people typically might change their work load sometimes due to changing circumstances).


### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app workplan
```
