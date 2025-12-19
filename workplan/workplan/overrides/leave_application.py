import datetime

import frappe
import hrms
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
from frappe.utils import add_days, cint, date_diff, flt, getdate
from hrms.hr.doctype.leave_application.leave_application import get_holidays, get_leave_balance_on
from hrms.utils.holiday_list import get_holiday_dates_between

from workplan.workplan.overrides.leave_allocation_new import get_current_workplan, get_next_workplan


def get_number_of_leave_working_days(
	employee: str,
	leave_type: str,
	from_date: datetime.date,
	to_date: datetime.date,
) -> float:
	"""Returns number of leave days between 2 dates after considering holidays
	(Based on the include_holiday setting in Leave Type). Does not consider wether the employee actually works on the days as per their workplan"""

	print(f"get_number_of_leave_days {employee} {leave_type} {from_date} {to_date}")
	number_of_weekdays = get_weekdays_diff(from_date, to_date)

	print(f"number_of_weekdays {number_of_weekdays} {from_date} { to_date}")

	if not frappe.db.get_value("Leave Type", leave_type, "include_holiday"):
		print(f"Leave Type {leave_type} not includes holidays as leaves")
		holiday_list_local = get_holiday_list_for_employee(employee)
		holidays_between_from_to: list[datetime.date] = get_holiday_dates_between(
			holiday_list_local, from_date.isoformat(), to_date.isoformat()
		)
		for holiday in holidays_between_from_to:
			number_of_weekdays[holiday.weekday()] = (
				number_of_weekdays[holiday.weekday()] - 1 if number_of_weekdays[holiday.weekday()] > 0 else 0
			)
	else:
		print(f"Leave Type {leave_type} includes holidays as leaves")
	return number_of_weekdays


def get_number_of_leave_days_for_workplan(
	employee: str,
	leave_type: str,
	from_date: datetime.date,
	to_date: datetime.date,
	workplan,
) -> float:
	"""Returns number of leave days between 2 dates after considering half day and holidays
	(Based on the include_holiday setting in Leave Type)"""

	print(f"get_number_of_leave_days {employee} {leave_type} {from_date} {to_date}")
	number_of_weekdays = get_weekdays_diff(from_date, to_date)

	print(f"number_of_weekdays {number_of_weekdays} {from_date} { to_date}")

	if not frappe.db.get_value("Leave Type", leave_type, "include_holiday"):
		print(f"Leave Type {leave_type} not includes holidays as leaves")
		holiday_list_local = get_holiday_list_for_employee(employee)
		holidays_between_from_to: list[datetime.date] = get_holiday_dates_between(
			holiday_list_local, from_date.isoformat(), to_date.isoformat()
		)
		for holiday in holidays_between_from_to:
			number_of_weekdays[holiday.weekday()] = (
				number_of_weekdays[holiday.weekday()] - 1 if number_of_weekdays[holiday.weekday()] > 0 else 0
			)
	else:
		print(f"Leave Type {leave_type} includes holidays as leaves")

	employee = frappe.get_doc("Employee", employee)
	sum_working_hours = 0
	for i, days in enumerate(number_of_weekdays):
		match i:
			case 0:
				sum_working_hours += workplan.monday * days
			case 1:
				sum_working_hours += workplan.tuesday * days
			case 2:
				sum_working_hours += workplan.wednesday * days
			case 3:
				sum_working_hours += workplan.thursday * days
			case 4:
				sum_working_hours += workplan.friday * days

	possible_leave_application = frappe.get_all(
		"Leave Application", filters={"to_date": to_date, "employee": employee.name}
	)

	if possible_leave_application:
		leave_application_doc = frappe.get_doc("Leave Application", possible_leave_application[0])
		last_work_day = get_last_workday_with_hours(employee, from_date, to_date)
		print(leave_application_doc.custom_fraction_of_day * 8)
		print(last_work_day.get("work_hours"))
		if (leave_application_doc.custom_fraction_of_day * 8) >= last_work_day.get("work_hours"):
			leave_application_doc.custom_fraction_of_day = 0
			leave_application_doc.save()
			return sum_working_hours / 8

	return sum_working_hours / 8 - leave_application_doc.custom_fraction_of_day


@frappe.whitelist()
def get_is_fractional_application(
	employee: str, leave_type: str, from_date: datetime.date, to_date: datetime.date
):
	employee_doc = frappe.get_doc("Employee", employee)
	val = get_number_of_leave_day_for_employee_doc(employee_doc, leave_type, from_date, to_date)
	leave_balance = get_leave_balance_on(
		employee,
		leave_type,
		from_date,
		to_date,
		consider_all_leaves_in_the_allocation_period=True,
		for_consumption=True,
	)
	leave_balance_for_consumption = flt(leave_balance.get("leave_balance_for_consumption"), 2)

	last_work_day = get_last_workday_with_hours(employee, from_date, to_date)

	if last_work_day.get("work_hours") == 0:
		return [0, 0, last_work_day.get("date")]

	if (-1 * last_work_day.get("work_hours")) / 8 > (leave_balance_for_consumption - val):
		return [0, 0, last_work_day.get("date")]

	if (leave_balance_for_consumption - val) >= 0:
		return [0, 0, last_work_day.get("date")]

	fractional_vacation = last_work_day.get("work_hours") / 8 + leave_balance_for_consumption - val
	fractional_work = last_work_day.get("work_hours") / 8 - fractional_vacation
	return [fractional_vacation, fractional_work, last_work_day.get("date")]


def get_last_workday_with_hours(employee, from_date, to_date):
	date_to_check = to_date
	holiday_list_local = get_holiday_list_for_employee(employee)
	holidays_between_from_to: list[datetime.date] = get_holiday_dates_between(
		holiday_list_local, from_date.isoformat(), to_date.isoformat()
	)
	holidays_set = set(holidays_between_from_to)
	while date_to_check >= from_date:
		while date_to_check >= from_date:
			is_weekday = date_to_check.weekday() < 5
			is_holiday = date_to_check in holidays_set

			if is_weekday and not is_holiday:
				work_hours = get_work_hours(employee, date_to_check)
				if work_hours > 0:
					return {"work_hours": work_hours, "date": date_to_check}

			date_to_check = add_days(date_to_check, -1)
	return {"work_hours": 0, "date": date_to_check}


def get_work_hours(employee, date: datetime.date):
	employee_doc = frappe.get_doc("Employee", employee)
	workplan = get_current_workplan(employee_doc, date)
	weekday = date.weekday()
	match weekday:
		case 0:
			return workplan.monday
		case 1:
			return workplan.tuesday
		case 2:
			return workplan.wednesday
		case 3:
			return workplan.thursday
		case 4:
			return workplan.friday


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

	## gucken ob is_fractional in db, wenn is fractional fuer den tag entsprechend wert einfach aus db nehmen
	# print(get_is_fractional_application(employee, leave_type, from_date, to_date))
	employee_doc = frappe.get_doc("Employee", employee)
	return get_number_of_leave_day_for_employee_doc(employee_doc, leave_type, from_date, to_date)


@frappe.whitelist()
def get_number_of_leave_days_leave_application(
	employee: str,
	leave_type: str,
	from_date: datetime.date,
	to_date: datetime.date,
	half_day: int | str | None = None,
	half_day_date: datetime.date | str | None = None,
	holiday_list: str | None = None,
):
	"""Returns number of leave days between 2 dates after considering half day and holidays
	(Based on the include_holiday setting in Leave Type)"""

	## gucken ob is_fractional in db, wenn is fractional fuer den tag entsprechend wert einfach aus db nehmen
	[fractional_vacation, fractional_work, date] = get_is_fractional_application(
		employee, leave_type, from_date, to_date
	)
	employee_doc = frappe.get_doc("Employee", employee)
	leave_without_fractional = get_number_of_leave_day_for_employee_doc(
		employee_doc, leave_type, from_date, to_date
	)
	leave_with_fractional = leave_without_fractional - 1 + fractional_vacation
	return {
		"fractional_value": fractional_vacation,
		"fractional_work": fractional_work,
		"total_leave_days": leave_with_fractional,
		"date": date,
		"weekday": date.weekday(),
	}


def get_number_of_leave_day_for_employee_doc(
	employee_doc,
	leave_type: str,
	from_date: datetime.date,
	to_date: datetime.date,
) -> float:
	"""Returns number of leave days between 2 dates after considering half day and holidays
	(Based on the include_holiday setting in Leave Type)"""
	workplan = get_current_workplan(employee_doc, from_date)
	result = 0
	start = from_date
	if not workplan:
		# check if there are actually vacations applied for
		frappe.throw(
			"Workplan for already applied Vacation missing. Cancel the Applications in the Workplan before deleting the Workplan itself."
		)
	if workplan.end:
		while workplan.end and getdate(workplan.end) < to_date:
			result += get_number_of_leave_days_for_workplan(
				employee_doc.name, leave_type, start, workplan.end, workplan
			)
			workplan = get_next_workplan(employee_doc, workplan.end)
			if not workplan:
				# check if there are actually vacations applied for
				frappe.throw(
					"Workplan for already applied Vacation missing. Cancel the Applications in the Workplan before deleting the Workplan itself."
				)
			start = workplan.start

		result += get_number_of_leave_days_for_workplan(
			employee_doc.name, leave_type, start, to_date, workplan
		)
		return result
	else:
		print(
			f"getnumber_for_employee{get_number_of_leave_days_for_workplan(employee_doc.name, leave_type, start, to_date, workplan)}"
		)
		return get_number_of_leave_days_for_workplan(employee_doc.name, leave_type, start, to_date, workplan)


def get_weekdays_diff(from_date: datetime.date, to_date: datetime.date):
	from_date = getdate(from_date)
	firstWeekday = from_date.weekday()
	numberOfDays = date_diff(to_date, from_date) + 1
	fullWeeks = int(numberOfDays / 7)
	additionalDays = numberOfDays - (fullWeeks * 7)

	result = [fullWeeks, fullWeeks, fullWeeks, fullWeeks, fullWeeks, fullWeeks, fullWeeks]

	for x in range(additionalDays):
		result[(firstWeekday + x) % 7] += 1

	return result


def update_application_days_value(employee_doc, method):
	# fuer jede application des employee die days neu berechnen
	current_year = getdate().year
	first_day_this_year = getdate(f"{current_year}-01-01")
	last_day_next_year = getdate(f"{current_year + 1}-12-31")
	applications = frappe.get_all(
		"Leave Application",
		filters={
			"employee": employee_doc.name,
			"from_date": (">=", first_day_this_year),
			"to_date": ("<=", last_day_next_year),
			"docstatus": ("!=", 2),
			"approval_state": ("!=", "Canceled"),
		},
		fields=[
			"name",
			"from_date",
			"to_date",
			"leave_type",
			"total_leave_days",
			"custom_fractional_day_value",
		],
	)
	for application in applications:
		last_work_day = get_last_workday_with_hours(
			employee_doc.name, application.from_date, application.to_date
		)
		if last_work_day.get("work_hours") / 8 <= flt(application.custom_fractional_day_value):
			application_doc = frappe.get_doc("Leave Application", application.name)
			application_doc.custom_fractional_day_value = 0
			application_doc.save()
		new_total_leave_days = get_number_of_leave_days(
			employee_doc.name, application.leave_type, application.from_date, application.to_date
		)
		print(f"update leave_days {new_total_leave_days}")
		frappe.db.set_value("Leave Application", application.name, "total_leave_days", new_total_leave_days)
