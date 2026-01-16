import frappe
from frappe.utils import add_days, flt, getdate
from hrms.hr.doctype.leave_allocation.leave_allocation import LeaveAllocation
from hrms.hr.doctype.leave_ledger_entry.leave_ledger_entry import create_leave_ledger_entry


class CustomLeaveAllocation(LeaveAllocation):
	def validate_against_leave_applications(self):
		return

	def on_update_after_submit(self):
		return
