import frappe
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
from frappe.utils import flt

from workplan.workplan.overrides.leave_application import create_leave_ledger_entry


def execute():
	leave_ledger_entries = frappe.get_all("Leave Ledger Entry", fields=["name", "leaves", "transaction_name"])

	processed_leave_applications = set()
	for entry in leave_ledger_entries:
		entry_doc = frappe.get_doc("Leave Ledger Entry", entry)
		if entry_doc.transaction_name in processed_leave_applications:
			continue
		if entry_doc.transaction_type == "Leave Application":
			processed_leave_applications.add(entry_doc.transaction_name)
			application_doc = frappe.get_doc("Leave Application", entry_doc.transaction_name)
			old_total_leave_days = 0
			# vielleicht brauche ich hier die docs
			old_total_leave_days = -1 * sum(
				entry.leaves
				for entry in leave_ledger_entries
				if entry.transaction_name == entry_doc.transaction_name
			)
			new_total_leave_days = application_doc.total_leave_days
			leaves_to_be_added = flt(
				(old_total_leave_days - new_total_leave_days),
			)

			if leaves_to_be_added:
				if application_doc.status != "Approved":
					return
				lwp = frappe.db.get_value("Leave Type", application_doc.leave_type, "is_lwp")

				args = dict(
					leaves=leaves_to_be_added,
					from_date=application_doc.from_date,
					to_date=application_doc.to_date,
					is_lwp=lwp,
					holiday_list=get_holiday_list_for_employee(
						application_doc.employee, raise_exception=False
					)
					or "",
				)
				create_leave_ledger_entry(application_doc, args, True)
