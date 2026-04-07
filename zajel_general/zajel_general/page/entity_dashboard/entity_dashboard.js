frappe.pages['entity-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Entity Dashboard',
		single_column: true
	});
$(wrapper).find('.layout-main-section').html(`
  <div class="row" style="margin-bottom: 12px;">
	<div class="col-sm-4">
	  <label>Company</label>
	  <select class="form-control" id="ed-company"></select>
	</div>
	<div class="col-sm-3">
	  <label>Date</label>
	  <input type="date" class="form-control" id="ed-date"/>
	</div>
	<div class="col-sm-2" style="margin-top: 24px;">
	  <button class="btn btn-primary" id="ed-refresh">Refresh</button>
	</div>
  </div>

  <div class="row" id="ed-kpis" style="margin-bottom: 12px;"></div>

  <div class="row">
	<div class="col-sm-6">
	  <div class="card p-3">
		<h5>Hourly Sales</h5>
		<div id="ed-hourly"></div>
	  </div>
	</div>
	<div class="col-sm-6">
	  <div class="card p-3">
		<h5>Weekly Sales (7 days)</h5>
		<div id="ed-weekly"></div>
	  </div>
	</div>
  </div>
`);

// Set default date
const today = frappe.datetime.get_today();
$('#ed-date').val(today);

// Load companies
frappe.db.get_list('Company', { fields: ['name'], limit: 1000 }).then(res => {
  const sel = $('#ed-company');
  res.forEach(r => sel.append(`<option value="${r.name}">${r.name}</option>`));
  // Try keep last selection
  const saved = localStorage.getItem('ed_company');
  if (saved) sel.val(saved);
  refresh();
});

$('#ed-refresh').on('click', refresh);
$('#ed-company').on('change', () => {
  localStorage.setItem('ed_company', $('#ed-company').val());
  refresh();
});
$('#ed-date').on('change', refresh);

let hourlyChart, weeklyChart;

function formatValue(title, v) {
	if (title === 'Daily Sales' || title === 'Net Profit / Loss') {
	  return frappe.format(v, { fieldtype: 'Currency' });
	}
	return (v || 0).toFixed(0);
  }
  
  function kpiTile(title, block) {
	const up = block.change >= 0;
	const arrow = up ? '↑' : '↓';
	const color = up ? 'green' : 'red';
	const pct = (block.pct || 0).toFixed(1) + '%';
  
	const changeText = (title === 'Daily Sales' || title === 'Net Profit / Loss')
	  ? frappe.format(block.change, { fieldtype: 'Currency' })
	  : (block.change || 0).toFixed(0);
  
	return `
	  <div class="col-sm-3">
		<div class="card p-3">
		  <div style="font-size:12px; color:#666;">${title}</div>
		  <div style="font-size:22px; font-weight:700;">${formatValue(title, block.value)}</div>
		  <div style="color:${color}; font-weight:600;">
			${arrow} ${changeText} (${pct}) vs yesterday
		  </div>
		</div>
	  </div>
	`;
  }

function refresh() {
  const company = $('#ed-company').val();
  const date = $('#ed-date').val();
  if (!company || !date) return;

  frappe.call({
	method: 'zajel_general.zajel_general.api.dashboard.get_entity_dashboard',
	args: { company, date },
	freeze: true,
	callback: (r) => {
	  const data = r.message;
	  if (!data) return;

	  // KPI tiles
	  const k = data.kpis;
	  $('#ed-kpis').html(
		kpiTile('Daily Sales', k.sales) +
		kpiTile('Visitors / Customers', k.visitors) +
		kpiTile('Transactions', k.transactions) +
		kpiTile('Net Profit / Loss', k.profit)
	  );

	  // Charts
	  const h = data.charts.hourly_sales;
	  const w = data.charts.weekly_sales;

	  $('#ed-hourly').empty();
	  $('#ed-weekly').empty();

	  hourlyChart = new frappe.Chart("#ed-hourly", {
		data: { labels: h.labels, datasets: [{ name: 'Sales', values: h.values }] },
		type: 'bar',
		height: 260
	  });

	  weeklyChart = new frappe.Chart("#ed-weekly", {
		data: { labels: w.labels, datasets: [{ name: 'Sales', values: w.values }] },
		type: 'line',
		height: 260
	  });
	}
  });
}
};