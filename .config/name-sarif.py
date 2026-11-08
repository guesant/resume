import json
from pathlib import Path

reports = Path(".local/reports")
destination = reports / "code-scanning"
destination.mkdir(parents=True, exist_ok=True)
for path in sorted((reports / "sarif").glob("*.sarif")):
    try:
        report = json.loads(path.read_text())
        if report["version"] != "2.1.0" or not isinstance(report["runs"], list):
            raise ValueError("Unsupported SARIF")
        for index, run in enumerate(report["runs"]):
            run["automationDetails"] = {"id": f"{path.stem}/{index}"}
    except (KeyError, TypeError, ValueError) as error:
        print(f"SARIF rejected for Code Scanning: {path}: {error}")
        continue
    (destination / path.name).write_text(json.dumps(report) + "\n")
