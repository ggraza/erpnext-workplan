__version__ = "0.0.5"

import hrms.hr.doctype.leave_application.leave_application
from workplan.workplan.overrides.leave_application import get_number_of_leave_days

# Monkey patching this method into the existing DocType, because the method is not a class method which can be extended/overridden
hrms.hr.doctype.leave_application.leave_application.get_number_of_leave_days = get_number_of_leave_days
