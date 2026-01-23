frappe.ui.form.on("Leave Application", {
	calculate_total_days: function (frm) {
		if (frm.doc.from_date && frm.doc.to_date && frm.doc.employee && frm.doc.leave_type) {
			return frappe.call({
				method: "workplan.workplan.overrides.leave_application.get_number_of_leave_days_leave_application",
				args: {
					employee: frm.doc.employee,
					leave_type: frm.doc.leave_type,
					from_date: frm.doc.from_date,
					to_date: frm.doc.to_date,
					half_day: frm.doc.half_day,
					half_day_date: frm.doc.half_day_date,
				},
				callback: function (r) {
					if (r && r.message && r.message.total_leave_days) {
						frm.set_value("total_leave_days", r.message.total_leave_days);
						frm.set_value("custom_fractional_day_value", r.message.fractional_value);
						if (r.message.fractional_value) {
							let weekday = "";
							switch (r.message.weekday) {
								case 0:
									weekday = "Monday";
									break;
								case 1:
									weekday = "Tuesday";
									break;
								case 2:
									weekday = "Wednesday";
									break;
								case 3:
									weekday = "Thursday";
									break;
								case 4:
									weekday = "Friday";
									break;
								default:
									weekday = "Unknown Weekday";
							}
							const total_hours = r.message.fractional_work * 8;
							const hours = Math.floor(total_hours);
							const minutes = Math.floor((total_hours - hours) * 60);

							const d = new Date(r.message.date);
							const formattedDate = d.toLocaleDateString("de-DE");

							var html = `
                                <div class="alert alert-warning" style="margin-top:10px; font-size: 20px; padding: 15px; font-weight: bold;">
                                    <strong>Fractional Day in Leave:</strong><br>
                                    You are applying for a total of ${r.message.total_leave_days} days of vacation. Note that on ${weekday} ${formattedDate} you have a <strong> partial day of vacation where you have to work ${hours} hours and ${minutes} minutes. </strong>
                                </div>
                            `;

							frm.set_df_property("custom_htmltest", "options", html);
						} else {
							frm.set_df_property("custom_htmltest", "options", `<div> </div>`);
						}

						frm.trigger("get_leave_balance");
					}
				},
			});
		}
	},
});
