"""
Section 13 analytics: two techniques applied to the maintenance request history.

1. Hotspot clustering (KMeans): groups Building+Category combinations by request
   volume into Low/Medium/High activity tiers, surfacing recurring problem areas.

2. Anomaly detection (Z-score): flags days where total request volume was
   unusually high compared to the historical average, which could indicate a
   larger underlying issue (e.g. a burst pipe affecting many rooms at once).

Requires: pip install scikit-learn
"""
import sqlite3
from collections import defaultdict
from statistics import mean, stdev

DB_FILE = "maintenance.db"


def get_hotspots(n_clusters=3):
    """
    Returns a list of dicts: Building, Category, RequestCount, ActivityLevel.
    Uses KMeans to group (Building, Category) combinations into activity tiers
    based purely on request count -- an unsupervised way of separating
    "normal" combinations from clear hotspots, without hand-picking thresholds.
    """
    from sklearn.cluster import KMeans
    import numpy as np

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """SELECT b.BuildingName, c.CategoryName, COUNT(*) as cnt
           FROM MaintenanceRequest r
           JOIN Room rm ON r.RoomID = rm.RoomID
           JOIN Building b ON rm.BuildingID = b.BuildingID
           JOIN Category c ON r.CategoryID = c.CategoryID
           GROUP BY b.BuildingName, c.CategoryName;"""
    )
    rows = cur.fetchall()
    conn.close()

    if len(rows) < n_clusters:
        return [{"Building": r[0], "Category": r[1], "Requests": r[2], "Activity Level": "N/A"} for r in rows]

    counts = np.array([[r[2]] for r in rows])
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = kmeans.fit_predict(counts)

    # Map cluster labels to Low/Medium/High based on each cluster's average count
    cluster_avg = {}
    for cluster_id in set(labels):
        cluster_avg[cluster_id] = counts[labels == cluster_id].mean()
    sorted_clusters = sorted(cluster_avg, key=cluster_avg.get)
    tier_names = ["Low", "Medium", "High"][:n_clusters]
    cluster_to_tier = {cluster_id: tier_names[i] for i, cluster_id in enumerate(sorted_clusters)}

    results = []
    for (building, category, count), label in zip(rows, labels):
        results.append({
            "Building": building,
            "Category": category,
            "Requests": count,
            "Activity Level": cluster_to_tier[label],
        })
    results.sort(key=lambda x: x["Requests"], reverse=True)
    return results


def get_daily_series():
    """
    Returns a list of dicts: Date, Count -- the full daily request-volume
    series, used to draw the time-over-time chart (not just the flagged
    anomaly days).
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """SELECT DateReported, COUNT(*) as cnt
           FROM MaintenanceRequest
           GROUP BY DateReported
           ORDER BY DateReported;"""
    )
    rows = cur.fetchall()
    conn.close()
    return [{"Date": r[0], "Count": r[1]} for r in rows]


def get_anomalies(z_threshold=2.0):
    """
    Returns a list of dicts: Date, RequestCount, ZScore for any day where the
    request count is more than z_threshold standard deviations above the mean.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """SELECT DateReported, COUNT(*) as cnt
           FROM MaintenanceRequest
           GROUP BY DateReported;"""
    )
    rows = cur.fetchall()
    conn.close()

    if len(rows) < 3:
        return []

    counts = [r[1] for r in rows]
    avg = mean(counts)
    sd = stdev(counts) if len(counts) > 1 else 0

    if sd == 0:
        return []

    anomalies = []
    for date_str, count in rows:
        z = (count - avg) / sd
        if z > z_threshold:
            anomalies.append({"Date": date_str, "Request Count": count, "Z-Score": round(z, 2)})

    anomalies.sort(key=lambda x: x["Z-Score"], reverse=True)
    return anomalies


if __name__ == "__main__":
    print("=== Hotspots ===")
    for h in get_hotspots():
        print(h)

    print("\n=== Anomalies ===")
    for a in get_anomalies():
        print(a)