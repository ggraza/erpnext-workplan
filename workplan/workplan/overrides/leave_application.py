import frappe
import datetime
import hrms

from frappe.utils import (
	date_diff
)

from hrms.hr.doctype.leave_application.leave_application import (get_holidays)
from hrms.utils.holiday_list import (get_holiday_dates_between)
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee

frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("workplan", allow_site=True, file_count=50)


@frappe.whitelist()
def get_number_of_leave_days(
	employee: str,
	leave_type: str,
	from_date: datetime.date,
	to_date: datetime.date,
	half_day: int | str | None = None,
	half_day_date: datetime.date | str | None = None,
	holiday_list: str | None = None,
) -> float:
	"""Returns number of leave days between 2 dates after considering half day and holidays
	(Based on the include_holiday setting in Leave Type)"""

	logger.debug(f"get_number_of_leave_days {employee} {leave_type} {from_date} {to_date}")
	number_of_weekdays = get_weekdays_diff(from_date, to_date)

	logger.debug(f"number_of_weekdays {number_of_weekdays}")

	if not frappe.db.get_value("Leave Type", leave_type, "include_holiday"):
		logger.debug(f"Leave Type {leave_type} not includes holidays as leaves")
		holiday_list_local = get_holiday_list_for_employee(employee)
		holidays_between_from_to: list[datetime.date] = get_holiday_dates_between(
			holiday_list_local, from_date.isoformat(), to_date.isoformat())
		for holiday in holidays_between_from_to:
			number_of_weekdays[holiday.weekday()] = number_of_weekdays[holiday.weekday()] - 1 if \
				number_of_weekdays[holiday.weekday()] > 0 else 0
	else:
		logger.debug(f"Leave Type {leave_type} includes holidays as leaves")

	employee = frappe.get_doc("Employee", employee)
	sum_working_hours = 0
	for i, days in enumerate(number_of_weekdays):
		match i:
			case 0:
				sum_working_hours += employee.custom_monday * days
			case 1:
				sum_working_hours += employee.custom_tuesday * days
			case 2:
				sum_working_hours += employee.custom_wednesday * days
			case 3:
				sum_working_hours += employee.custom_thursday * days
			case 4:
				sum_working_hours += employee.custom_friday * days

	logger.debug(f"Sum_working_hours {sum_working_hours}")
	return sum_working_hours / 8


def get_weekdays_diff(from_date: datetime.date, to_date: datetime.date):
	firstWeekday = from_date.weekday()
	numberOfDays = date_diff(to_date, from_date) + 1
	fullWeeks = int(numberOfDays / 7)
	additionalDays = numberOfDays - (fullWeeks * 7)

	result = [
		fullWeeks, fullWeeks, fullWeeks, fullWeeks, fullWeeks, fullWeeks, fullWeeks
	]

	for x in range(additionalDays):
		result[(firstWeekday + x) % 7] += 1

	return result

