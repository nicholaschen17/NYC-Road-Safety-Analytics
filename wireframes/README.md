# Wireframes

## Home page

Main page: [`nyc_crash_hotspot_dashboard_wireframe.html`](mock_design_html/nyc_crash_hotspot_dashboard_wireframe.html)

![NYC crash hotspot dashboard](images/nyc_crash_hotspot_dashboard.png)

## Secondary (supporting) pages

### `zone_grid_drilldown.html`

![Zone grid drill-down](images/zone_grid_drilldown.png)

- Zone drill-down is the core analytical surface — it's where a DOT analyst lands after clicking a cell on the main heatmap, giving them SHAP-level explainability, infrastructure context, and a direct path to recommending interventions.

### `incident_explorer_timeline.html`

![Incident explorer timeline](images/incident_explorer.png)

- Incident explorer is the audit trail, letting analysts cross-reference model predictions against ground truth.

### `reporting_export_center.html`

![Reporting export center](images/reporting_expore_center.png)

- Reporting center closes the loop for stakeholders who don't live in the app, with a GeoJSON webhook.

## ML model training

![ML model training](images/ml_model_training.png)
