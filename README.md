### ERPNext Workplan

This is an App for ERPNext allows leave calculations based on expected working hours per day. It will calculate the available leave budgets based on expected working hours per day (e.g. a person that works only 20 instead of 40 hours per week, will only receive 50% of the leave budget). For Leave Applications, it will also only deduct the actual work time on the given leave day (e.g. taking off a work day, where an Employee is scheduled to work only 4 hours, it will only deduct 4 hours from the leave budget).

- It adds a new "Workplan" DocType to every Employee (under the "Attendance & Leaves" Tab). A workplan is a schedule of expected/regular working hours per day (e.g. a Workplan could look like "Monday 8 h, Tuesday 6h, Wednesday 8h, Thursday 4h, Friday 4h"). A workplan also has a start and an end date (because people typically might change their work load sometimes due to changing circumstances)
- It adds a checkbox to the Leave Policy Assignment "Use workplan for allocation calculation", which will use the workplan data to calculate the base leave allowance (e.g. if you only work 32 hours per week according to your workplan, the entered amount of leave allowance will be multiplied by 32/40 = 0.8)


### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app workplan
```
