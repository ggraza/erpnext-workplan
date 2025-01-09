### ERPNext Workplan

This ERPNext App does two things:

- It adds a "workplan" to every Employee (under the "Attendance & Leaves" Tab) where they can define their expected working hours per weekday
- It adds a checkbox to the Leave Policy Assignment "Use workplan for allocation calculation", which will use the workplan data to calculate the base leave allowance (e.g. if you only work 32 hours per week according to your workplan, the entered amount of leave allowance will be multiplied by 32/40 = 0.8)
- It uses the workplan data for leave allowance calculations (e.g. your leave allowance will only be reduced by the amount of planned working hours on the given days)


### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app workplan
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/workplan
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

agpl-3.0
