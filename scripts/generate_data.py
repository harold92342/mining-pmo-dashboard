"""
Mining PMO Dashboard - core data layer generator
Author: Timothy Kabwe
Creates a synthetic (fictional) capital project portfolio for a Copperbelt copper mine,
linked to a real public dataset (Kaggle "Quality Prediction in a Mining Process").

Cause-and-effect chains deliberately built into the data:
  1. Serious safety incidents on a project site -> stop-work days -> lower progress (SPI)
  2. Overdue risk mitigations -> slower progress
  3. Scope changes -> budget growth and cost overrun (CPI)
  4. Weak contractors -> more incidents, more overdue mitigations, worse CPI/SPI
  5. Concentrator breakdowns follow the REAL flotation data: more breakdowns on days
     where silica in concentrate is high and pulp flow is low
All names of projects, contractors and assets are fictional.
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)
KAGGLE_DAILY = ROOT / "data" / "source" / "flotation_daily_2017.csv"   # built by prepare_kaggle.py
SHIFT_YEARS = 9                      # 2017 -> 2026 (documented in the About page)
FLOTATION_GO_LIVE = pd.Timestamp("2026-06-01")
MONTHS = pd.date_range("2023-10-31", "2026-09-30", freq="ME")   # reporting months
SNAPSHOT = MONTHS[-1]

# ---------------------------------------------------------------- dimensions
sites = pd.DataFrame([
    ("S01", "Open Pit", "Mining"),
    ("S02", "Concentrator", "Processing"),
    ("S03", "SX-EW Plant", "Processing"),
    ("S04", "Tailings Facility", "Environment"),
    ("S05", "Power & Water", "Engineering"),
    ("S06", "Camp & Offices", "Support"),
], columns=["SiteID", "SiteName", "SiteArea"])

contractors = pd.DataFrame([
    ("C01", "Copperline Civils", "Civil", 0.95),
    ("C02", "Red Earth Mechanical", "Mechanical", 0.80),   # the weak one
    ("C03", "Malachite E&I Services", "Electrical & Instrumentation", 1.00),
    ("C04", "Kolwe Earthmoving", "Earthworks", 0.90),
    ("C05", "Upper Basin EPCM", "EPCM", 1.05),
    ("C06", "In-house Projects Team", "Owner team", 1.00),
], columns=["ContractorID", "ContractorName", "Discipline", "QualityFactor"])

project_defs = [
    # name, programme, site, category, complexity, priority, BAC $M, duration months
    ("Concentrator Flotation Optimisation", "Plant Performance", "S02", "Debottlenecking", "High", "Critical", 18, 14),
    ("Ball Mill 2 Liner Upgrade", "Plant Performance", "S02", "Sustaining", "Medium", "High", 6, 8),
    ("Concentrator Thickener Rebuild", "Plant Performance", "S02", "Sustaining", "Medium", "High", 9, 12),
    ("Flotation Reagent System Automation", "Digital & Automation", "S02", "Digital", "Medium", "Medium", 3, 9),
    ("SX-EW Tank House Expansion", "Growth", "S03", "Expansion", "Very High", "Critical", 85, 30),
    ("Electrowinning Rectifier Replacement", "Plant Performance", "S03", "Sustaining", "High", "High", 14, 15),
    ("Acid Plant Tie-in", "Growth", "S03", "Expansion", "High", "High", 22, 20),
    ("Haul Road Upgrade Phase 2", "Mine Development", "S01", "Infrastructure", "Low", "Medium", 7, 10),
    ("Pit Dewatering System", "Mine Development", "S01", "Sustaining", "Medium", "High", 11, 12),
    ("Fleet Dispatch System", "Digital & Automation", "S01", "Digital", "Medium", "Medium", 4, 9),
    ("Pushback 4 Pre-strip", "Mine Development", "S01", "Expansion", "High", "Critical", 40, 24),
    ("Truck Workshop Extension", "Mine Development", "S01", "Infrastructure", "Low", "Low", 5, 10),
    ("Tailings Dam Lift 3", "Environment & Compliance", "S04", "Compliance", "Very High", "Critical", 30, 22),
    ("Tailings Seepage Interception", "Environment & Compliance", "S04", "Compliance", "High", "Critical", 8, 12),
    ("Water Treatment Plant Upgrade", "Environment & Compliance", "S05", "Compliance", "High", "High", 16, 16),
    ("Dust Suppression Network", "Environment & Compliance", "S01", "Compliance", "Low", "Medium", 2, 6),
    ("120 kV Substation Upgrade", "Energy & Utilities", "S05", "Infrastructure", "Very High", "Critical", 35, 26),
    ("Solar PV Plant 20 MW", "Energy & Utilities", "S05", "Growth", "High", "High", 28, 20),
    ("Backup Generator Overhaul", "Energy & Utilities", "S05", "Sustaining", "Medium", "Medium", 3, 7),
    ("Raw Water Pipeline Replacement", "Energy & Utilities", "S05", "Sustaining", "Medium", "High", 12, 14),
    ("Camp Accommodation Block C", "Site Services", "S06", "Infrastructure", "Low", "Low", 6, 11),
    ("Site Clinic Upgrade", "Site Services", "S06", "Infrastructure", "Low", "Medium", 2, 8),
    ("ERP Maintenance Module Rollout", "Digital & Automation", "S06", "Digital", "High", "High", 5, 12),
    ("Site-wide Network Refresh", "Digital & Automation", "S06", "Digital", "Medium", "Medium", 3, 9),
    ("Lab Information System", "Digital & Automation", "S02", "Digital", "Medium", "Medium", 2, 8),
    ("Community Road Rehabilitation", "Site Services", "S06", "Social", "Low", "Medium", 4, 9),
    ("Primary Crusher Relocation", "Growth", "S02", "Expansion", "Very High", "High", 48, 28),
    ("Conveyor CV-05 Replacement", "Plant Performance", "S02", "Sustaining", "Medium", "High", 7, 10),
    ("Explosives Magazine Relocation", "Mine Development", "S01", "Compliance", "Low", "Medium", 3, 7),
    ("Fire Protection System Upgrade", "Environment & Compliance", "S03", "Compliance", "Medium", "High", 5, 10),
    ("Cobalt Hydroxide Circuit Study", "Growth", "S03", "Study", "High", "Medium", 2, 9),
    ("Underground Exploration Decline", "Growth", "S01", "Expansion", "Very High", "High", 60, 30),
]
contractor_by_discipline = {
    "Debottlenecking": ["C02", "C05"], "Sustaining": ["C02", "C03", "C06"],
    "Digital": ["C06", "C03"], "Expansion": ["C05", "C04", "C02"],
    "Infrastructure": ["C01", "C04"], "Compliance": ["C01", "C05", "C04"],
    "Growth": ["C05", "C03"], "Social": ["C01"], "Study": ["C06"],
}
cx_score = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}

rows = []
for i, (name, prog, site, cat, cx, prio, bac, dur) in enumerate(project_defs, start=1):
    pid = f"P{i:03d}"
    if name == "Concentrator Flotation Optimisation":
        start = pd.Timestamp("2025-04-01")          # finishes ~ June 2026 -> go-live
    else:
        start = pd.Timestamp("2023-06-01") + pd.DateOffset(months=int(rng.integers(0, 37)))
    cid = rng.choice(contractor_by_discipline[cat])
    if name == "Concentrator Flotation Optimisation":
        cid = "C05"
    rows.append(dict(
        ProjectID=pid, ProjectName=name, Programme=prog, SiteID=site, Category=cat,
        Complexity=cx, Priority=prio, ContractorID=cid,
        DeliveryModel="Owner-managed" if cid == "C06" else ("EPCM" if cid == "C05" else "Contracted"),
        StrategicAlignment=int(rng.integers(2, 6)),
        BaselineBudget_USD=bac * 1_000_000,
        PlannedStart=start, PlannedDurationMonths=dur,
        PlannedFinish=(start + pd.DateOffset(months=dur)) - pd.Timedelta(days=1),
        PlannedBenefit_USD=round(bac * 1_000_000 * rng.uniform(1.4, 3.2), -5) if cat != "Study" else 0,
    ))
projects = pd.DataFrame(rows)
qf = contractors.set_index("ContractorID")["QualityFactor"]

# ---------------------------------------------------------------- risks
risk_cats = ["Safety", "Technical", "Contractor", "Permit & Regulatory", "Supply Chain", "Environmental"]
risk_rows, rid = [], 1
for p in projects.itertuples():
    q = qf[p.ContractorID]
    for _ in range(int(rng.integers(4, 9)) + cx_score[p.Complexity]):
        raised = p.PlannedStart + pd.Timedelta(days=int(rng.integers(0, p.PlannedDurationMonths * 25)))
        due = raised + pd.Timedelta(days=int(rng.integers(20, 75)))
        late_prob = np.clip(0.25 + (1 - q) * 1.6 + 0.05 * cx_score[p.Complexity], 0.05, 0.9)
        if rng.random() < late_prob:
            closed = due + pd.Timedelta(days=int(rng.integers(15, 160)))
        else:
            closed = due - pd.Timedelta(days=int(rng.integers(0, 15)))
        if closed > SNAPSHOT:
            closed = pd.NaT
        lik, imp = int(rng.integers(1, 6)), int(rng.integers(1, 6))
        risk_rows.append(dict(
            RiskID=f"R{rid:04d}", ProjectID=p.ProjectID, SiteID=p.SiteID,
            RiskCategory=rng.choice(risk_cats), Likelihood=lik, Impact=imp,
            DateRaised=raised, MitigationDueDate=due, MitigationClosedDate=closed,
        ))
        rid += 1
risks = pd.DataFrame(risk_rows)
risks = risks[risks.DateRaised <= SNAPSHOT].reset_index(drop=True)

def overdue_count(pid, month_end):
    r = risks[risks.ProjectID == pid]
    open_ = (r.DateRaised <= month_end) & (r.MitigationDueDate < month_end) & \
            (r.MitigationClosedDate.isna() | (r.MitigationClosedDate > month_end))
    return int(open_.sum())

# ---------------------------------------------------------------- safety
inc_types = ["Near Miss", "First Aid", "Medical Treatment", "Lost Time Injury"]
safety_rows, man_rows, iid = [], [], 1
stop_work = {}                                    # (ProjectID, month) -> days
for p in projects.itertuples():
    q = qf[p.ContractorID]
    for m in MONTHS:
        if not (p.PlannedStart <= m <= p.PlannedFinish + pd.DateOffset(months=8)):
            continue
        hours = int(rng.normal(9000, 2500) * (1 + 0.5 * cx_score[p.Complexity]))
        man_rows.append(dict(MonthEnd=m, ProjectID=p.ProjectID, SiteID=p.SiteID,
                             ContractorID=p.ContractorID, ManHours=max(hours, 1500)))
        n = rng.poisson(0.9 * (1.9 - q) ** 2 * (1 + 0.3 * cx_score[p.Complexity]))
        for _ in range(n):
            t = rng.choice(inc_types, p=[0.55, 0.28, 0.12, 0.05] if q >= 0.95 else [0.45, 0.30, 0.16, 0.09])
            day = m - pd.Timedelta(days=int(rng.integers(0, 28)))
            lost = int(rng.integers(3, 30)) if t == "Lost Time Injury" else 0
            stop = int(rng.integers(2, 8)) if t in ("Medical Treatment", "Lost Time Injury") else 0
            stop_work[(p.ProjectID, m)] = stop_work.get((p.ProjectID, m), 0) + stop
            safety_rows.append(dict(IncidentID=f"I{iid:04d}", IncidentDate=day, SiteID=p.SiteID,
                                    ProjectID=p.ProjectID, ContractorID=p.ContractorID,
                                    IncidentType=t, LostDays=lost, StopWorkDays=stop))
            iid += 1
safety = pd.DataFrame(safety_rows)
manhours = pd.DataFrame(man_rows)

# ---------------------------------------------------------------- project monthly (EVM)
def s_curve(x):
    x = np.clip(x, 0, 1)
    return 3 * x**2 - 2 * x**3

scope_rows, pm_rows, status_rows = [], [], []
for p in projects.itertuples():
    q = qf[p.ContractorID]
    base_cpi = rng.normal(1.0, 0.04) - (1 - q) * 0.6 - 0.02 * cx_score[p.Complexity]
    base_spi = rng.normal(1.0, 0.04) - (1 - q) * 0.5 - 0.02 * cx_score[p.Complexity]
    if p.ProjectName == "Concentrator Flotation Optimisation":
        base_cpi, base_spi = 0.97, 1.0
    budget, pct, ac, scope_changes = p.BaselineBudget_USD, 0.0, 0.0, 0
    # fate: a few projects are paused, cancelled or simply stop reporting
    fate = rng.choice(["normal", "paused", "cancelled", "silent"], p=[0.84, 0.06, 0.05, 0.05])
    if p.ProjectName == "Concentrator Flotation Optimisation":
        fate = "normal"
    fate_month = p.PlannedStart + pd.DateOffset(months=int(p.PlannedDurationMonths * rng.uniform(0.3, 0.6)))
    status = "Active"
    for m in MONTHS:
        if m < p.PlannedStart:
            continue
        months_in = (m.year - p.PlannedStart.year) * 12 + m.month - p.PlannedStart.month + 1
        if status in ("Completed", "Cancelled"):
            break
        if fate == "silent" and m > fate_month:
            break                                     # stops reporting, no closure record
        if fate == "cancelled" and m > fate_month:
            status = "Cancelled"
        if fate == "paused" and m > fate_month:
            status = "On Hold"
        sc = 0
        if status == "Active" and rng.random() < 0.07 + 0.03 * cx_score[p.Complexity]:
            sc = 1
            scope_changes += 1
            growth = budget * rng.uniform(0.04, 0.10)
            budget += growth * 0.5            # only half of the scope growth gets funded
            scope_rows.append(dict(ProjectID=p.ProjectID, ChangeDate=m - pd.Timedelta(days=int(rng.integers(0, 25))),
                                   BudgetChange_USD=round(growth * 0.5, -3),
                                   UnfundedCost_USD=round(growth * 0.5, -3)))
        od = overdue_count(p.ProjectID, m)
        sw = stop_work.get((p.ProjectID, m), 0)
        planned_inc = s_curve(months_in / p.PlannedDurationMonths) - s_curve((months_in - 1) / p.PlannedDurationMonths)
        if status == "Active":
            spi_m = max(base_spi - 0.06 * od - 0.02 * scope_changes, 0.30) * (1 - min(sw, 25) / 30)
            if p.ProjectID == "P001":
                spi_m = 1.0                   # flotation project delivered on plan (go-live 1 Jun 2026)
            inc = planned_inc * spi_m if months_in <= p.PlannedDurationMonths else rng.uniform(0.03, 0.09)
            inc = min(inc, 1 - pct)
            cpi_m = max(base_cpi - 0.04 * scope_changes - (0.04 if sw else 0), 0.55)
            pct += inc
            ac += inc * budget / cpi_m + (sw * 15_000)
        pv = budget * s_curve(months_in / p.PlannedDurationMonths)
        ev = budget * pct
        cpi = ev / ac if ac else 1.0
        eac = ac + (budget - ev) / max(cpi, 0.4)
        spi = ev / pv if pv else 1.0
        fc_finish = p.PlannedStart + pd.Timedelta(days=int(p.PlannedDurationMonths * 30.4 / max(spi, 0.4)))
        if pct >= 0.999:
            status = "Completed"
        pm_rows.append(dict(ProjectID=p.ProjectID, MonthEnd=m, Status=status,
                            CurrentBudget_USD=round(budget, -3), PV_USD=round(pv, -3),
                            EV_USD=round(ev, -3), AC_USD=round(ac, -3), EAC_USD=round(eac, -3),
                            PctComplete=round(pct, 4), ForecastFinish=fc_finish.normalize(),
                            ScopeChangesInMonth=sc, OverdueMitigations=od, StopWorkDays=sw))
proj_monthly = pd.DataFrame(pm_rows)
scope = pd.DataFrame(scope_rows)

flo = "P001"

# ---------------------------------------------------------------- processing (REAL data, shifted)
proc = pd.read_csv(KAGGLE_DAILY, parse_dates=["date"])
proc["Date"] = proc["date"] + pd.DateOffset(years=SHIFT_YEARS)
proc = proc.drop(columns="date")
proc.insert(0, "Date", proc.pop("Date"))
proc.insert(1, "SiteID", "S02")
proc["PeriodVsGoLive"] = np.where(proc.Date >= FLOTATION_GO_LIVE, "After go-live", "Before go-live")

# ---------------------------------------------------------------- assets + work orders
asset_defs = [
    ("Flotation Column 01-03", "S02", "Flotation", "A"), ("Flotation Column 04-07", "S02", "Flotation", "A"),
    ("Ball Mill 1", "S02", "Milling", "A"), ("Ball Mill 2", "S02", "Milling", "A"),
    ("Primary Crusher", "S02", "Crushing", "A"), ("Conveyor CV-05", "S02", "Conveying", "B"),
    ("Slurry Pump Bank", "S02", "Pumping", "B"), ("Concentrate Thickener", "S02", "Thickening", "B"),
    ("EW Rectifier 1", "S03", "Electrical", "A"), ("SX Mixer-Settlers", "S03", "Process", "B"),
    ("Haul Truck Fleet", "S01", "Mobile Fleet", "A"), ("Dewatering Pumps", "S01", "Pumping", "B"),
    ("Tailings Pumps", "S04", "Pumping", "A"), ("Main Substation", "S05", "Electrical", "A"),
    ("Backup Generators", "S05", "Power Generation", "B"), ("Water Treatment Plant", "S05", "Water", "B"),
]
assets = pd.DataFrame([(f"A{i:02d}", n, s, c, k) for i, (n, s, c, k) in enumerate(asset_defs, 1)],
                      columns=["AssetID", "AssetName", "SiteID", "AssetClass", "Criticality"])

wo_rows, wid = [], 1
days = pd.date_range(MONTHS[0] - pd.offsets.MonthBegin(1), SNAPSHOT, freq="D")
proc_idx = proc.set_index("Date")
sil_mean, flow_mean = proc["% Silica Concentrate"].mean(), proc["Ore Pulp Flow"].mean()
for a in assets.itertuples():
    for d in days:
        if d.weekday() == 0 and rng.random() < 0.55:                    # preventive, weekly-ish
            sched = d
            done = d + pd.Timedelta(days=int(rng.integers(0, 4)))
            if d >= pd.Timestamp("2026-07-01") and a.SiteID == "S02" and rng.random() < 0.45:
                done = d + pd.Timedelta(days=int(rng.integers(14, 60)))  # backlog builds
            wo_rows.append(dict(WorkOrderID=f"W{wid:05d}", AssetID=a.AssetID, SiteID=a.SiteID,
                                WorkType="Preventive", RaisedDate=d, ScheduledDate=sched,
                                CompletedDate=done if done <= SNAPSHOT else pd.NaT,
                                DowntimeHours=round(rng.uniform(0, 3), 1),
                                LabourHours=round(rng.uniform(4, 16), 1)))
            wid += 1
        p_break = 0.012 if a.Criticality == "A" else 0.008
        if a.AssetClass == "Flotation" and d in proc_idx.index:
            p_break = 0.06
            r = proc_idx.loc[d]
            p_break *= np.clip((r["% Silica Concentrate"] / sil_mean) ** 3 *
                               (flow_mean / max(r["Ore Pulp Flow"], 1)) ** 4, 0.3, 6)
        if rng.random() < p_break:
            dt = round(rng.gamma(2.0, 4.0) * (1.5 if a.Criticality == "A" else 1), 1)
            wo_rows.append(dict(WorkOrderID=f"W{wid:05d}", AssetID=a.AssetID, SiteID=a.SiteID,
                                WorkType="Breakdown", RaisedDate=d, ScheduledDate=d,
                                CompletedDate=d + pd.Timedelta(days=int(rng.integers(0, 3))),
                                DowntimeHours=dt, LabourHours=round(dt * rng.uniform(1.5, 3), 1)))
            wid += 1
workorders = pd.DataFrame(wo_rows)

# ---------------------------------------------------------------- save
tables = {
    "Dim_Site": sites, "Dim_Contractor": contractors.drop(columns="QualityFactor"),
    "Dim_Project": projects, "Dim_Asset": assets,
    "Fact_ProjectMonthly": proj_monthly, "Fact_ScopeChange": scope, "Fact_Risk": risks,
    "Fact_SafetyIncident": safety, "Fact_ManHours": manhours,
    "Fact_WorkOrder": workorders, "Fact_ProcessingDaily": proc,
}
for name, df in tables.items():
    df.to_csv(OUT / f"{name}.csv", index=False, date_format="%Y-%m-%d")
    print(f"{name:22s} {len(df):>7,} rows")
