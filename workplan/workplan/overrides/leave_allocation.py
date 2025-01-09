import frappe

def update(doc, event):
	leave_policy_assignment = frappe.get_doc("Leave Policy Assignment", doc.leave_policy_assignment)
	
	if leave_policy_assignment.custom_use_workplan_for_allocation_calculation:
		employee = frappe.get_doc("Employee", doc.employee)
		weekly_hours = employee.custom_monday + employee.custom_tuesday + employee.custom_wednesday + employee.custom_thursday + employee.custom_friday
		doc.new_leaves_allocated = doc.new_leaves_allocated * (weekly_hours/40)

	return doc