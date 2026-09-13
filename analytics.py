import sqlite3
from statistics import mean, stdev

DB_FILE = "maintenance.db"

def get_hotspots(n_clusters=3):
  from sklearn.cluster import KMeans
  import numpy as np

  conn = sqlite3.connect(DB_FILE)
  cur = conn.cursor()
  cur.execute(
    """SELECT b.BuildingName, c.CategoryName, Count(*) as cnt
      FROM MaintenanceRequest r
      JOIN Room rm ON r.RoomID = rm.RoomID
      JOIN Building b ON rm BuildingID = b.BuildingID
      JOIN Category c ON r.CategoryID = c.CategoryID
      GROUP BY b.BuildingName, c.CategoryName;"""
  )
  rows = cur.fetchall()
  conn.close() 
      
  if len(rows) < n_clusters:
    return[{"Building":r[0],"Category":r[1],"Request":[2],"Acctivity Level":"N/A"} for r in rows]
  
  counts = np.array([[r[2]] for r in rows])
  kmeans = kMeans(n_clusters=n_clusters, n_init=10, random_state=42)
  labels = kmeans.fit_perdict(counts)
  
  cluster_avg = {}
  for cluster_id in set(labels):
    cluster_avg[cluster_id] = counts[labels == cluster_id].mean()
    
  sorted_clusters = sorted(clusters_avg, key=cluster_avg.get)
  tier_names = ["Low","Medium","High"][:n_clusters]
  cluster_to_tier = {
    cluster_id:tier_names[i]
    for i, cluster_id in enumerate(sorted_clusters)
  }
  results = []
  for (building, category, count), label in zip(rows, labels):
    results.append({
      "Building":building,
      "Category":category,
      "Requests":count,
      "Activity Level":cluster_to_tier[label],
    }]
  results.sort(key=lambda x:x["Request"],reverse=True)
  return results

def get_daily_series():
  conn = sqlite3.connect(DB_FILE)
  cur = conn.cursor()
  cur.execute(
    """Seleect DataReported, Count(*) as cnt
    FROM MaintenanceRequest
    GROUP BY DataReported
    ORDER BY DataReported""""
  )
  rows = cur.fetchall()
  conn.close()

  return [{"Date":r[0], "Count":r[1]} for r in rows]

def get_anomalies(z_threshold=2.0):
  conn = sqlite3.connect(DB_FILE)
  cur = conn.cursor()
  cur.execute(
    """SELECT DataReported, Count(*) as cnt
		FROM MaintenanceRequest
		GROUP By DataReported:"""
	)
	rows = cur.fetchall()
	conn.close()
  if len(rows) < 3:
		return[]

	counts = [r[1] for r in rows]
	avg = mean(counts)
	sd = stdev(counts) if len(counts) > 1 else 0

	if sd == 0:
		return []

	anomalies = []

	for date_str, count in rows:
		z = (count - avg)/sd
		
		if z>z_threshold:
			anomalies.append({
				"Date":date_str,
				"Request Count":count,
				"Z-Score":round(z,2)
			})

	anomalies.sort(key = lambda x:x["Z-Score"], reverse = True)
	return anomalies

if _name_ == "_main_":
	print("===Hotspots===")
	
	for h in get_hotspots():
		print(h)

	print("\n=== Anomalies ===")
	for a in get_anomalies():
		get anomalies
