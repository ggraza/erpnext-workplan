__version__ = "0.0.6"

import hrms.hr.doctype.leave_application.leave_application

from workplan.workplan.overrides.leave_application import get_leaves_for_period, get_number_of_leave_days

# Monkey patching this method into the existing DocType, because the method is not a class method which can be extended/overridden
hrms.hr.doctype.leave_application.leave_application.get_number_of_leave_days = get_number_of_leave_days
hrms.hr.doctype.leave_application.leave_application.get_leaves_for_period = get_leaves_for_period
