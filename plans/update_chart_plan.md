
# 📊 Plan: Integrate Data with UI via `updateChartForSection`

This plan outlines how to dynamically update chart data when the selected option in `analysis-selector` changes, by modifying the `updateChartForSection` function.

---

## 🧱 Function to Modify
- `updateChartForSection`

---

## 🎯 Objective
- Update charts based on the selected analysis tab
- Parse data from the corresponding JSON file
- Format the data in the following structure for chart rendering:

```js
sectionData = [
  { month: 'Jan', patients: 65, revenue: 45, satisfaction: 50 },
  { month: 'Feb', patients: 58, revenue: 52, satisfaction: 45 },
  ...
]
```

---

## 🗂️ Data Sources by Analysis Type

| Analysis Option                     | Data File Path                                         |
|-------------------------------------|--------------------------------------------------------|
| Real-time bed occupancy by ward     | `root/backed/result/bed_snapshot_result.json`          |
| ALOS by procedure/ward              | `root/backed/result/average_los_result.json`           |
| Staff workload dashboard            | `root/backed/result/staff_load_result.json`            |
| Tool utilisation & idle time        | `root/backed/result/tool_utilisation_result.json`      |
| Inventory expiry radar              | `root/backed/result/inventory_expiry_result.json`      |
| Short-horizon bed census            | `root/backed/result/census_forecast_result.json`       |
| Elective vs emergency               | `root/backed/result/admission_split_result.json`       |
| Length-of-stay prediction           | `root/backed/result/los_prediction_result.json`        |

---

## 🔄 Implementation Steps

1. **Detect Selector Change**  
   In the event handler tied to `analysis-selector`, capture the selected value.

2. **Map to File Path**  
   Use a mapping dictionary to relate selector values to corresponding file paths.

3. **Fetch and Parse JSON**  
   Load the JSON file and parse its contents to match the required `sectionData` format.

4. **Update Chart**  
   Feed the formatted data into the chart rendering function already linked with `updateChartForSection`.

---

## 🧪 Example Code Stub

```js
const fileMap = {
  "bed_occupancy": "bed_snapshot_result.json",
  "average_los": "average_los_result.json",
  ...
};

function updateChartForSection(option) {
  const fileName = fileMap[option];
  fetch(`/backed/result/${fileName}`)
    .then(res => res.json())
    .then(data => {
      const sectionData = parseToChartFormat(data); // Implement parsing logic
      renderChart(sectionData); // Existing chart rendering call
    });
}
```

---

## ✅ Deliverable
- Fully dynamic chart updates on analysis tab switch
- No need to reload or restructure existing UI layout
- Maintains existing chart rendering pipeline
