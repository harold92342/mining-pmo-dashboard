# Power Query transformations

The CSV files in `data/` are the raw generator output. These steps run in Power Query when the files are loaded into Power BI.

## All tables

- **Promote headers**: the all-text dimension tables loaded with `Column1, Column2…`. Fix: remove the automatic *Changed Type* step, then *Use First Row as Headers*.
- **Data types with locale**: dates and decimals are set with *Using Locale → English (United States)*, so they parse correctly on a French-locale machine.

## Added columns

| Table | Column | M expression |
|---|---|---|
| Fact_SafetyIncident | `IsRecordable` | `if [IncidentType] = "Medical Treatment" or [IncidentType] = "Lost Time Injury" then 1 else 0` |
| Fact_WorkOrder | `CompletionDelayDays` | `Duration.Days([CompletedDate] - [ScheduledDate])` |
| Fact_Risk | `RiskScore` | `[Likelihood] * [Impact]` (1–25) |

## Data-quality fix: activity after project closure

The raw data books man-hours and safety incidents after some projects had stopped reporting. Those rows would inflate TRIFR, so they are removed.

1. **Helper_ProjectLastMonth**: a *Reference* of `Fact_ProjectMonthly`, grouped by project (load disabled):

   ```m
   = Table.Group(Source, {"ProjectID"},
       {{"LastReportMonth", each List.Max([MonthEnd]), type nullable date}})
   ```

2. **Merge** (Left Outer on `ProjectID`) into `Fact_ManHours` and `Fact_SafetyIncident`, then expand `LastReportMonth`.
3. Add a `KeepRow` column and keep only `TRUE` rows:
   - Fact_ManHours: `[MonthEnd] <= [LastReportMonth]`
   - Fact_SafetyIncident: `[IncidentDate] <= [LastReportMonth]`
4. Remove the helper columns.

| Table | Raw rows | After fix |
|---|---:|---:|
| Fact_ManHours | 507 | 450 |
| Fact_SafetyIncident | 750 | 669 |
